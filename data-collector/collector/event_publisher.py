from utils.logger import get_logger

logger = get_logger(__name__)

class EventPublisher:
    def publish(self, event_type: str, data: dict):
        logger.info(f"Evento publicado: {event_type} -> {len(data)} registros")
        # En el futuro: conexión RabbitMQ 
