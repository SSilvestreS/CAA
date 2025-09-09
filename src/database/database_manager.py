"""
Sistema de Gerenciamento de Banco de Dados para Simulação de Cidade Inteligente
Versão 1.1 - Persistência de dados e histórico de simulações
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path


class DatabaseManager:
    """Gerenciador de banco de dados para persistir dados da simulação"""

    def __init__(self, db_path: str = "data/simulation.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabela de simulações
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'running',
                    config TEXT,
                    metrics TEXT
                )
            """
            )

            # Tabela de agentes
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER,
                    agent_type TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    state TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                )
            """
            )

            # Tabela de eventos
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    agent_id TEXT,
                    description TEXT,
                    data TEXT,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                )
            """
            )

            # Tabela de métricas
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                )
            """
            )

            # Tabela de interações
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent_from TEXT NOT NULL,
                    agent_to TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    data TEXT,
                    result TEXT,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                )
            """
            )

            conn.commit()
            self.logger.info("Banco de dados inicializado com sucesso")

    def create_simulation(self, name: str, config: Dict[str, Any]) -> int:
        """Cria uma nova simulação no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO simulations (name, config)
                VALUES (?, ?)
            """,
                (name, json.dumps(config)),
            )
            simulation_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Simulação '{name}' criada com ID {simulation_id}")
            return simulation_id

    def update_simulation_status(self, simulation_id: int, status: str, metrics: Optional[Dict] = None):
        """Atualiza o status de uma simulação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status == "completed":
                cursor.execute(
                    """
                    UPDATE simulations 
                    SET end_time = CURRENT_TIMESTAMP, status = ?, metrics = ?
                    WHERE id = ?
                """,
                    (status, json.dumps(metrics) if metrics else None, simulation_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE simulations 
                    SET status = ?
                    WHERE id = ?
                """,
                    (status, simulation_id),
                )
            conn.commit()

    def save_agent_state(self, simulation_id: int, agent_type: str, agent_id: str, state: Dict[str, Any]):
        """Salva o estado de um agente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agents (simulation_id, agent_type, agent_id, state)
                VALUES (?, ?, ?, ?)
            """,
                (simulation_id, agent_type, agent_id, json.dumps(state)),
            )
            conn.commit()

    def log_event(
        self,
        simulation_id: int,
        event_type: str,
        description: str,
        agent_id: Optional[str] = None,
        data: Optional[Dict] = None,
    ):
        """Registra um evento na simulação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO events (simulation_id, event_type, agent_id, description, data)
                VALUES (?, ?, ?, ?, ?)
            """,
                (simulation_id, event_type, agent_id, description, json.dumps(data) if data else None),
            )
            conn.commit()

    def save_metric(self, simulation_id: int, metric_name: str, value: float, metadata: Optional[Dict] = None):
        """Salva uma métrica da simulação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO metrics (simulation_id, metric_name, value, metadata)
                VALUES (?, ?, ?, ?)
            """,
                (simulation_id, metric_name, value, json.dumps(metadata) if metadata else None),
            )
            conn.commit()

    def log_interaction(
        self,
        simulation_id: int,
        agent_from: str,
        agent_to: str,
        interaction_type: str,
        data: Optional[Dict] = None,
        result: Optional[str] = None,
    ):
        """Registra uma interação entre agentes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO interactions (simulation_id, agent_from, agent_to, 
                                        interaction_type, data, result)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (simulation_id, agent_from, agent_to, interaction_type, json.dumps(data) if data else None, result),
            )
            conn.commit()

    def get_simulation_history(self, limit: int = 10) -> List[Dict]:
        """Recupera o histórico de simulações"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM simulations 
                ORDER BY start_time DESC 
                LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_simulation_metrics(self, simulation_id: int) -> List[Dict]:
        """Recupera métricas de uma simulação específica"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM metrics 
                WHERE simulation_id = ?
                ORDER BY timestamp
            """,
                (simulation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_agent_events(self, simulation_id: int, agent_id: str) -> List[Dict]:
        """Recupera eventos de um agente específico"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM events 
                WHERE simulation_id = ? AND agent_id = ?
                ORDER BY timestamp
            """,
                (simulation_id, agent_id),
            )
            return [dict(row) for row in cursor.fetchall()]

    def export_simulation_data(self, simulation_id: int) -> Dict[str, Any]:
        """Exporta todos os dados de uma simulação"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Dados da simulação
            cursor.execute("SELECT * FROM simulations WHERE id = ?", (simulation_id,))
            simulation = dict(cursor.fetchone())

            # Agentes
            cursor.execute("SELECT * FROM agents WHERE simulation_id = ?", (simulation_id,))
            agents = [dict(row) for row in cursor.fetchall()]

            # Eventos
            cursor.execute("SELECT * FROM events WHERE simulation_id = ?", (simulation_id,))
            events = [dict(row) for row in cursor.fetchall()]

            # Métricas
            cursor.execute("SELECT * FROM metrics WHERE simulation_id = ?", (simulation_id,))
            metrics = [dict(row) for row in cursor.fetchall()]

            # Interações
            cursor.execute("SELECT * FROM interactions WHERE simulation_id = ?", (simulation_id,))
            interactions = [dict(row) for row in cursor.fetchall()]

            return {
                "simulation": simulation,
                "agents": agents,
                "events": events,
                "metrics": metrics,
                "interactions": interactions,
            }
