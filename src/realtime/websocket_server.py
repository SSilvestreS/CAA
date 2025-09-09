"""
Servidor WebSocket para comunicação em tempo real.
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import uuid

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosed, WebSocketException
except ImportError:
    # Fallback para ambientes sem websockets
    class WebSocketServerProtocol:
        pass

    class ConnectionClosed(Exception):
        pass

    class WebSocketException(Exception):
        pass


class MessageType(Enum):
    """Tipos de mensagens WebSocket."""

    # Autenticação
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    AUTH_ERROR = "auth_error"

    # Simulação
    SIMULATION_START = "simulation_start"
    SIMULATION_STOP = "simulation_stop"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_RESUME = "simulation_resume"
    SIMULATION_STATUS = "simulation_status"

    # Agentes
    AGENT_UPDATE = "agent_update"
    AGENT_ACTION = "agent_action"
    AGENT_MESSAGE = "agent_message"

    # Eventos
    EVENT_OCCURRED = "event_occurred"
    EVENT_HANDLED = "event_handled"

    # Sistema
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    NOTIFICATION = "notification"

    # Dados
    DATA_UPDATE = "data_update"
    METRICS_UPDATE = "metrics_update"


class ConnectionState(Enum):
    """Estados da conexão WebSocket."""

    CONNECTING = "connecting"
    AUTHENTICATED = "authenticated"
    SUBSCRIBED = "subscribed"
    DISCONNECTED = "disconnected"


@dataclass
class WebSocketMessage:
    """Mensagem WebSocket estruturada."""

    id: str
    type: MessageType
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte mensagem para dicionário."""
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "user_id": self.user_id,
            "session_id": self.session_id,
        }

    def to_json(self) -> str:
        """Converte mensagem para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class WebSocketConnection:
    """Representa uma conexão WebSocket individual."""

    def __init__(self, websocket: WebSocketServerProtocol, connection_id: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.state = ConnectionState.CONNECTING
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.subscriptions: Set[str] = set()
        self.last_heartbeat = datetime.now()
        self.created_at = datetime.now()

    async def send_message(self, message: WebSocketMessage) -> bool:
        """Envia mensagem para o cliente."""
        try:
            await self.websocket.send(message.to_json())
            return True
        except (ConnectionClosed, WebSocketException) as e:
            logging.warning(f"Erro ao enviar mensagem: {e}")
            return False

    async def send_error(self, error_message: str, error_code: str = "GENERIC_ERROR"):
        """Envia mensagem de erro."""
        error_msg = WebSocketMessage(
            id=str(uuid.uuid4()),
            type=MessageType.ERROR,
            timestamp=datetime.now(),
            data={"error": error_message, "code": error_code},
            user_id=self.user_id,
            session_id=self.session_id,
        )
        await self.send_message(error_msg)

    def is_authenticated(self) -> bool:
        """Verifica se conexão está autenticada."""
        return self.state == ConnectionState.AUTHENTICATED and self.user_id is not None

    def is_subscribed_to(self, topic: str) -> bool:
        """Verifica se está inscrito em um tópico."""
        return topic in self.subscriptions

    def update_heartbeat(self):
        """Atualiza timestamp do último heartbeat."""
        self.last_heartbeat = datetime.now()

    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """Verifica se conexão está ativa."""
        return (datetime.now() - self.last_heartbeat).total_seconds() < timeout_seconds


class WebSocketServer:
    """Servidor WebSocket principal."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.topic_subscribers: Dict[str, Set[str]] = {}  # topic -> connection_ids
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.heartbeat_interval = 30  # segundos
        self.running = False

        # Configura logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def register_handler(self, message_type: MessageType, handler: Callable):
        """Registra handler para tipo de mensagem."""
        self.message_handlers[message_type] = handler

    async def start(self):
        """Inicia servidor WebSocket."""
        self.running = True
        self.logger.info(f"Iniciando servidor WebSocket em {self.host}:{self.port}")

        # Inicia task de heartbeat
        asyncio.create_task(self._heartbeat_task())

        # Inicia servidor
        async with websockets.serve(self._handle_connection, self.host, self.port):
            self.logger.info("Servidor WebSocket iniciado")
            await asyncio.Future()  # Mantém servidor rodando

    async def stop(self):
        """Para servidor WebSocket."""
        self.running = False
        self.logger.info("Parando servidor WebSocket")

        # Fecha todas as conexões
        for connection in self.connections.values():
            await connection.websocket.close()

    async def _handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Manipula nova conexão WebSocket."""
        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(websocket, connection_id)

        self.connections[connection_id] = connection
        self.logger.info(f"Nova conexão: {connection_id}")

        try:
            async for message in websocket:
                await self._process_message(connection, message)

        except ConnectionClosed:
            self.logger.info(f"Conexão fechada: {connection_id}")
        except WebSocketException as e:
            self.logger.error(f"Erro WebSocket: {e}")
        finally:
            await self._cleanup_connection(connection)

    async def _process_message(self, connection: WebSocketConnection, raw_message: str):
        """Processa mensagem recebida."""
        try:
            message_data = json.loads(raw_message)
            message_type = MessageType(message_data.get("type"))

            # Atualiza heartbeat
            if message_type == MessageType.HEARTBEAT:
                connection.update_heartbeat()
                return

            # Processa mensagem
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                await handler(connection, message_data)
            else:
                await connection.send_error(f"Tipo de mensagem não suportado: {message_type}")

        except json.JSONDecodeError:
            await connection.send_error("Mensagem JSON inválida")
        except ValueError as e:
            await connection.send_error(f"Tipo de mensagem inválido: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
            await connection.send_error("Erro interno do servidor")

    async def _cleanup_connection(self, connection: WebSocketConnection):
        """Limpa recursos da conexão."""
        connection_id = connection.connection_id

        # Remove de todas as listas
        if connection_id in self.connections:
            del self.connections[connection_id]

        if connection.user_id:
            if connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

        # Remove de tópicos
        for topic, subscribers in self.topic_subscribers.items():
            subscribers.discard(connection_id)

    async def _heartbeat_task(self):
        """Task de verificação de heartbeat."""
        while self.running:
            await asyncio.sleep(self.heartbeat_interval)

            # Remove conexões inativas
            inactive_connections = []
            for connection_id, connection in self.connections.items():
                if not connection.is_alive():
                    inactive_connections.append(connection_id)

            for connection_id in inactive_connections:
                connection = self.connections[connection_id]
                await connection.websocket.close()
                await self._cleanup_connection(connection)
                self.logger.info(f"Conexão inativa removida: {connection_id}")

    async def broadcast_message(self, message: WebSocketMessage, topic: Optional[str] = None):
        """Envia mensagem para todas as conexões ou tópico específico."""
        target_connections = []

        if topic:
            # Envia para tópico específico
            if topic in self.topic_subscribers:
                for connection_id in self.topic_subscribers[topic]:
                    if connection_id in self.connections:
                        target_connections.append(self.connections[connection_id])
        else:
            # Envia para todas as conexões
            target_connections = list(self.connections.values())

        # Envia mensagem
        for connection in target_connections:
            await connection.send_message(message)

    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Envia mensagem para usuário específico."""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.connections:
                    connection = self.connections[connection_id]
                    await connection.send_message(message)

    async def subscribe_to_topic(self, connection: WebSocketConnection, topic: str):
        """Inscreve conexão em tópico."""
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = set()

        self.topic_subscribers[topic].add(connection.connection_id)
        connection.subscriptions.add(topic)

        self.logger.info(f"Conexão {connection.connection_id} inscrita em {topic}")

    async def unsubscribe_from_topic(self, connection: WebSocketConnection, topic: str):
        """Remove inscrição de conexão em tópico."""
        if topic in self.topic_subscribers:
            self.topic_subscribers[topic].discard(connection.connection_id)

        connection.subscriptions.discard(topic)

        self.logger.info(f"Conexão {connection.connection_id} desinscrita de {topic}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das conexões."""
        return {
            "total_connections": len(self.connections),
            "authenticated_connections": len([c for c in self.connections.values() if c.is_authenticated()]),
            "topics": len(self.topic_subscribers),
            "users_online": len(self.user_connections),
        }


class WebSocketClient:
    """Cliente WebSocket para testes e integração."""

    def __init__(self, uri: str = "ws://localhost:8765"):
        self.uri = uri
        self.websocket = None
        self.connected = False
        self.message_handlers: Dict[MessageType, Callable] = {}

    async def connect(self):
        """Conecta ao servidor WebSocket."""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    async def disconnect(self):
        """Desconecta do servidor."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

    async def send_message(self, message: WebSocketMessage):
        """Envia mensagem para o servidor."""
        if self.connected and self.websocket:
            await self.websocket.send(message.to_json())

    async def listen(self):
        """Escuta mensagens do servidor."""
        if not self.connected or not self.websocket:
            return

        try:
            async for message in self.websocket:
                await self._process_message(message)
        except websockets.exceptions.ConnectionClosed:
            self.connected = False

    async def _process_message(self, raw_message: str):
        """Processa mensagem recebida."""
        try:
            message_data = json.loads(raw_message)
            message_type = MessageType(message_data.get("type"))

            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                await handler(message_data)

        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")

    def register_handler(self, message_type: MessageType, handler: Callable):
        """Registra handler para tipo de mensagem."""
        self.message_handlers[message_type] = handler
