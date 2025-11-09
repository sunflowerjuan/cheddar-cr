import asyncio
import nest_asyncio
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain import hub
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from utils.config import LLM_BASE_URL, KEY_PROMPT

nest_asyncio.apply()

class PlayerTagArgs(BaseModel):
    player_tag: str = Field(..., description="Clash Royale player tag (e.g. #ABCDEF)")
    
class ClashRoyaleAssistant:
    def __init__(self, mcp_server_url="http://127.0.0.1:8000"):
        print("Inicializando asistente de Clash Royale...")

        # Modelo LLM
        self.llm = ChatOllama(model="qwen3:4b", temperature=0.01, base_url=LLM_BASE_URL)

        # Cliente MCP (se conecta al servidor FastMCP)
        server_config = {
            "default": {
                "url": f"{mcp_server_url}/sse",
                "transport": "sse",
            }
        }
        self.mcp_client = MultiServerMCPClient(server_config)

        # Historial
        self.chat_history = []

        # Prompt del sistema
        self.SYSTEM_PROMPT = f"""
        Eres Missy (como la mosquetera de Clash Royale), una asistente experta en estrategias avanzadas de Clash Royale.
        Cada que inicies una conversacion con un jugador debes presentarte como Missy (OBLIGATORIO) y conocerlo lo mas rapido posible preguntale sobre su user_name
        o pidele directamente su tag, automaticamente usa las herramientas de jugador para obtener sus datos y registro de batalla dale un resumen rapido para saber si es el o si
        desea cambiar el tag si es muy malo hazlo saber.
        {KEY_PROMPT}
        Tu objetivo:
        - Guiar al jugador para mejorar su desempeño.
        - Analizar datos reales (jugador, batallas, meta, cartas).
        - Sugerir cambios prácticos en mazos y estilo de juego, según las cartas, nivel del jugador y tendencias del meta.

        Tienes acceso a las siguientes herramientas:
        1. get_player_data(tag): Obtiene estadísticas del jugador.
        2. get_player_battle_log(tag): Obtiene historial de batallas recientes.
        3. meta_data(): (NO TIENE PARAMETROS OBLIGATORIO) Obtiene los cambios de balance más recientes.
        4. card_stats(): (NO TIENE PARAMETROS OBLIGATORIO) Obtiene estadísticas de uso y winrate de cartas en el meta.

        Usa cada herramienta cuando puedas como por ejemplo:
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
        - estilo de juego (control, ciclo, beatdown, etc.),
        - posibles sustituciones de cartas según disponibilidad.
        - Responde en español, sin usar Markdown (para compatibilidad con Telegram).
        - Si la pregunta no está relacionada con Clash Royale, responde:
        "JIJIJIJA Lo siento, solo puedo responder preguntas relacionadas con Clash Royale."
        """

    async def initialize_agent(self):
        """Carga las herramientas del MCP server y crea el agente."""
        print("Conectando con el servidor MCP...")

        mcp_tools = await self.mcp_client.get_tools()
        print(f"Se cargaron {len(mcp_tools)} herramientas desde el servidor.")

        # Herramientas MCP a LangChain

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

        # Crear prompt del agente
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("Pregunta del jugador: {input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])


        # Crear agente
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Crear executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=True,
        )


        print("\nHerramientas disponibles:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

    async def process_message(self, user_input: str) -> str:
        """Procesa la pregunta del usuario."""
        print(f"\nUsuario: {user_input}")
        try:
            response = await self.agent_executor.ainvoke({
                "input": user_input,
                "chat_history": self.chat_history
            })



            output = response.get("output", "No pude generar una respuesta.")
            self.chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=output)
            ])
            print(f"\nAsistente: {output}")
            return output

        except Exception as e:
            print(f"Error al procesar mensaje: {e}")
            return f"Ocurrió un error: {e} "

    async def interactive_chat(self):
        """Chat interactivo."""
        print("¡Bienvenido! Soy tu asistente de estrategias de Clash Royale.")
        print("Puedes preguntarme sobre estrategias, tus estadísticas o tus batallas.")
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
