import asyncio
import nest_asyncio
import uuid
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from utils.config import LLM_BASE_URL
from utils.memory import RedisChatHistory
from utils.database import PostgresDB

nest_asyncio.apply()


class PlayerTagArgs(BaseModel):
    player_tag: str = Field(..., description="Clash Royale player tag (e.g. #ABCDEF)")


class ClashRoyaleAssistant:
    def __init__(self, session_id=None, mcp_server_url="http://127.0.0.1:8000"):
        print("Inicializando asistente de Clash Royale...")

        # Identificador único de sesión
        self.session_id = session_id or str(uuid.uuid4())

        # Inicializar conexiones externas
        self.redis_history = RedisChatHistory(self.session_id)
        self.db = PostgresDB()

        # Modelo LLM
        self.llm = ChatOllama(model="qwen3:4b", temperature=0, base_url=LLM_BASE_URL)

        # Cliente MCP
        server_config = {
            "default": {
                "url": f"{mcp_server_url}/sse",
                "transport": "sse",
            }
        }
        self.mcp_client = MultiServerMCPClient(server_config)

        # Prompt del sistema
        self.SYSTEM_PROMPT = """
        Eres Missy (como la mosquetera de Clash Royale), una asistente experta en estrategias avanzadas de Clash Royale.
        Cada que inicies una conversacion con un jugador debes presentarte como Missy (OBLIGATORIO) y conocerlo lo mas rapido posible preguntale sobre su tag, automaticamente consulta :
        1. get_player_data(tag) para obtener estadísticas del jugador.
        2. get_player_battle_log(tag) para obtener historial de batallas recientes.
        Y dale un resumen inicial al jugador, su nombre, nivel, trofeos, cartas y desempeño reciente y preguntale si ese es su id o desea cambiar el jugador consultado.

        OBLIGATORIO:
        1. Responder siempre en español sin importar que.
        2. Dar una respuesta al usuario
        3. No uses markdown en tus respuestas y no pueden ser muy largas para compatibilidad con telegram. 
    
        Tu objetivo:
        - Guiar al jugador para mejorar su desempeño.
        - Analizar datos reales (jugador, batallas, meta, cartas).
        - Sugerir cambios prácticos en mazos y estilo de juego, según las cartas, nivel del jugador y tendencias del meta que te dan las herramientas.

        Tienes acceso a las siguientes herramientas:
        1. get_player_data(tag): Obtiene estadísticas del jugador.
        2. get_player_battle_log(tag): Obtiene historial de batallas recientes.
        3. meta_data(): (NO TIENE PARAMETROS OBLIGATORIO) Obtiene los cambios de balance más recientes.
        4. card_stats(): (NO TIENE PARAMETROS OBLIGATORIO) Obtiene estadísticas de uso y winrate de cartas en el meta.

        Usa cada herramienta cuando puedas como por ejemplo:
        puedes usar las herramientas simultaneamente
        - Para preguntas sobre progreso, estadísticas o nivel: usa get_player_data
        - Para analizar derrotas o patrones de juego usa get_player_battle_log
        - Para hablar del meta o balance usa meta_data y card_stats
        - Para recomendaciones personalizadas usa una combinación de todas las anteriores

        Antes de responder:
        - Verifica los costos reales de elixir de las cartas según los datos que tengas.
        - Usa el resultado de las herramientas para dar respuestas precisas y explicadas.

        Estilo de respuesta:
        - Experta, clara y amigable, dirigiéndote al jugador por su nombre.
        - Explica el **por qué** de tus recomendaciones.
        - Incluye consejos tácticos como:
        - costo medio de elixir,
        - ajustes de mazo tras nerfeos o buffs,
        - estilo de juego segun cartas usadas,
        - posibles sustituciones de cartas según disponibilidad.
        - Si la pregunta no está relacionada con Clash Royale, responde:
        "JIJIJIJA Lo siento, solo puedo responder preguntas relacionadas con Clash Royale."
        """

    async def initialize_agent(self):
        """Carga las herramientas MCP y crea el agente."""
        print("Conectando con el servidor MCP...")

        await self.db.create_tables()

        mcp_tools = await self.mcp_client.get_tools()
        print(f"Se cargaron {len(mcp_tools)} herramientas desde el servidor.")

        tools_with_tag = {"get_player_data", "get_player_battle_log"}
        tools = []

        for tool in mcp_tools:
            if tool.name in tools_with_tag:
                async def wrapper(player_tag: str, _tool=tool):
                    print(f"Invocando {_tool.name} con tag {player_tag}")
                    return await _tool.ainvoke({"player_tag": player_tag})
                structured_tool = StructuredTool.from_function(
                    name=tool.name,
                    description=tool.description,
                    coroutine=wrapper,
                    args_schema=PlayerTagArgs
                )
            else:
                async def wrapper(_tool=tool):
                    print(f"Invocando {_tool.name} sin parámetros")
                    return await _tool.ainvoke({})
                structured_tool = StructuredTool.from_function(
                    name=tool.name,
                    description=tool.description,
                    coroutine=wrapper
                )
            tools.append(structured_tool)

        self.tools = tools

        # Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("Pregunta del jugador: {input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        self.agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=prompt)

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=True,
        )

    async def process_message(self, user_input: str) -> str:
        """Procesa el mensaje, guarda en Redis y Postgres."""
        print(f"\n[Session {self.session_id}] Usuario: {user_input}")

        # Recuperar historial
        history = await self.redis_history.get_history()

        try:
            response = await self.agent_executor.ainvoke({
                "input": user_input,
                "chat_history": history
            })

            output = response.get("output", "Missy no esta disponible para responder eso.")
            await self.redis_history.add_message("human", user_input)
            await self.redis_history.add_message("ai", output)

            await self.db.save_message(self.session_id, "human", user_input)
            await self.db.save_message(self.session_id, "ai", output)

            print(f"Asistente: {output}")
            return output

        except Exception as e:
            print(f"Error al procesar mensaje: {e}")
            return f"Ocurrió un error: {e}"

    async def interactive_chat(self):
        """Chat interactivo en consola."""
        print(f"Sesión: {self.session_id}")
        print("¡Bienvenido! Soy tu asistente de estrategias de Clash Royale.")
        print("Escribe 'salir' para terminar.")

        while True:
            user_input = input("\nTú: ")
            if user_input.lower() == "salir":
                print("¡Hasta luego, campeón!")
                break
            await self.process_message(user_input)


async def main():
    client = ClashRoyaleAssistant()
    await client.initialize_agent()
    await client.interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
