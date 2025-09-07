"""
Sistema de auditoria e logging de segurança.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib


class AuditEventType(Enum):
    """Tipos de eventos de auditoria."""
    # Autenticação
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    
    # Autorização
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Dados
    DATA_ACCESS = "data_access"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # Sistema
    CONFIG_CHANGED = "config_changed"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    ERROR_OCCURRED = "error_occurred"
    
    # Simulação
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_STOPPED = "simulation_stopped"
    SIMULATION_PAUSED = "simulation_paused"
    SIMULATION_RESUMED = "simulation_resumed"
    
    # Agentes
    AGENT_CREATED = "agent_created"
    AGENT_UPDATED = "agent_updated"
    AGENT_DELETED = "agent_deleted"
    AGENT_ACTION = "agent_action"


class AuditSeverity(Enum):
    """Níveis de severidade dos eventos."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Evento de auditoria."""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    details: Dict[str, Any]
    result: str  # success, failure, error
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        data['severity'] = self.severity.value
        return data
    
    def to_json(self) -> str:
        """Converte evento para JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class AuditLogger:
    """Logger de auditoria com diferentes backends."""
    
    def __init__(self, log_directory: str = "logs/audit"):
        self.log_directory = log_directory
        self.ensure_log_directory()
        self.event_counter = 0
    
    def ensure_log_directory(self):
        """Garante que o diretório de logs existe."""
        os.makedirs(self.log_directory, exist_ok=True)
    
    def generate_event_id(self) -> str:
        """Gera ID único para evento."""
        self.event_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"AUDIT_{timestamp}_{self.event_counter:06d}"
    
    def log_event(self, event: AuditEvent) -> bool:
        """
        Registra evento de auditoria.
        
        Args:
            event: Evento de auditoria para registrar
            
        Returns:
            True se evento foi registrado com sucesso
        """
        try:
            # Gera ID se não fornecido
            if not event.event_id:
                event.event_id = self.generate_event_id()
            
            # Salva em arquivo JSON
            self._save_to_file(event)
            
            # Salva em log estruturado
            self._save_to_structured_log(event)
            
            return True
            
        except Exception as e:
            print(f"Erro ao registrar evento de auditoria: {e}")
            return False
    
    def _save_to_file(self, event: AuditEvent):
        """Salva evento em arquivo JSON."""
        filename = f"audit_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.log_directory, filename)
        
        # Lê eventos existentes
        events = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                events = []
        
        # Adiciona novo evento
        events.append(event.to_dict())
        
        # Salva arquivo atualizado
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    
    def _save_to_structured_log(self, event: AuditEvent):
        """Salva evento em log estruturado."""
        filename = f"audit_structured_{datetime.now().strftime('%Y%m%d')}.log"
        filepath = os.path.join(self.log_directory, filename)
        
        log_entry = {
            "timestamp": event.timestamp.isoformat(),
            "event_id": event.event_id,
            "type": event.event_type.value,
            "severity": event.severity.value,
            "user_id": event.user_id,
            "resource": event.resource,
            "action": event.action,
            "result": event.result,
            "message": event.message
        }
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def query_events(self, 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None,
                    event_type: Optional[AuditEventType] = None,
                    user_id: Optional[str] = None,
                    severity: Optional[AuditSeverity] = None,
                    limit: int = 1000) -> List[AuditEvent]:
        """
        Consulta eventos de auditoria com filtros.
        
        Args:
            start_date: Data de início do filtro
            end_date: Data de fim do filtro
            event_type: Tipo de evento para filtrar
            user_id: ID do usuário para filtrar
            severity: Severidade para filtrar
            limit: Limite de resultados
            
        Returns:
            Lista de eventos filtrados
        """
        events = []
        
        # Lista arquivos de log
        log_files = [f for f in os.listdir(self.log_directory) 
                    if f.startswith('audit_') and f.endswith('.json')]
        
        for log_file in sorted(log_files, reverse=True):
            if len(events) >= limit:
                break
                
            filepath = os.path.join(self.log_directory, log_file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_events = json.load(f)
                
                for event_data in file_events:
                    if len(events) >= limit:
                        break
                    
                    # Aplica filtros
                    if self._matches_filters(event_data, start_date, end_date, 
                                           event_type, user_id, severity):
                        event = self._dict_to_event(event_data)
                        events.append(event)
                        
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return events[:limit]
    
    def _matches_filters(self, event_data: Dict, start_date: Optional[datetime],
                        end_date: Optional[datetime], event_type: Optional[AuditEventType],
                        user_id: Optional[str], severity: Optional[AuditSeverity]) -> bool:
        """Verifica se evento atende aos filtros."""
        # Filtro por data
        if start_date or end_date:
            event_time = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            if start_date and event_time < start_date:
                return False
            if end_date and event_time > end_date:
                return False
        
        # Filtro por tipo
        if event_type and event_data.get('event_type') != event_type.value:
            return False
        
        # Filtro por usuário
        if user_id and event_data.get('user_id') != user_id:
            return False
        
        # Filtro por severidade
        if severity and event_data.get('severity') != severity.value:
            return False
        
        return True
    
    def _dict_to_event(self, event_data: Dict) -> AuditEvent:
        """Converte dicionário para AuditEvent."""
        return AuditEvent(
            event_id=event_data['event_id'],
            event_type=AuditEventType(event_data['event_type']),
            severity=AuditSeverity(event_data['severity']),
            timestamp=datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')),
            user_id=event_data.get('user_id'),
            session_id=event_data.get('session_id'),
            ip_address=event_data.get('ip_address'),
            user_agent=event_data.get('user_agent'),
            resource=event_data.get('resource'),
            action=event_data.get('action'),
            details=event_data.get('details', {}),
            result=event_data['result'],
            message=event_data['message']
        )
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditEvent]:
        """Retorna atividade de um usuário nos últimos N dias."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date.replace(day=end_date.day - days)
        
        return self.query_events(
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
    
    def get_security_events(self, hours: int = 24) -> List[AuditEvent]:
        """Retorna eventos de segurança das últimas N horas."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date.replace(hour=end_date.hour - hours)
        
        security_types = [
            AuditEventType.LOGIN_FAILED,
            AuditEventType.ACCOUNT_LOCKED,
            AuditEventType.PERMISSION_DENIED,
            AuditEventType.ERROR_OCCURRED
        ]
        
        events = []
        for event_type in security_types:
            events.extend(self.query_events(
                start_date=start_date,
                end_date=end_date,
                event_type=event_type,
                severity=AuditSeverity.MEDIUM
            ))
        
        return events


class SecurityMonitor:
    """Monitor de segurança com detecção de anomalias."""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.failed_login_threshold = 5  # Tentativas de login falhadas
        self.time_window_minutes = 15    # Janela de tempo para análise
    
    def detect_brute_force(self, user_id: str) -> bool:
        """Detecta tentativas de força bruta."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time.replace(minute=end_time.minute - self.time_window_minutes)
        
        failed_logins = self.audit_logger.query_events(
            start_date=start_time,
            end_date=end_time,
            event_type=AuditEventType.LOGIN_FAILED,
            user_id=user_id
        )
        
        return len(failed_logins) >= self.failed_login_threshold
    
    def detect_privilege_escalation(self, user_id: str) -> bool:
        """Detecta tentativas de escalação de privilégios."""
        recent_events = self.audit_logger.query_events(
            user_id=user_id,
            limit=100
        )
        
        # Verifica múltiplas tentativas de acesso negado
        denied_access = [e for e in recent_events 
                        if e.event_type == AuditEventType.PERMISSION_DENIED]
        
        return len(denied_access) >= 3
    
    def detect_unusual_activity(self, user_id: str) -> List[str]:
        """Detecta atividade incomum de um usuário."""
        alerts = []
        
        # Verifica força bruta
        if self.detect_brute_force(user_id):
            alerts.append("Tentativas de força bruta detectadas")
        
        # Verifica escalação de privilégios
        if self.detect_privilege_escalation(user_id):
            alerts.append("Possível tentativa de escalação de privilégios")
        
        return alerts
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Gera relatório de segurança."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time.replace(hour=end_time.hour - hours)
        
        security_events = self.audit_logger.get_security_events(hours)
        
        report = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(security_events),
            "event_types": {},
            "severity_distribution": {},
            "top_users": {},
            "alerts": []
        }
        
        # Conta tipos de eventos
        for event in security_events:
            event_type = event.event_type.value
            report["event_types"][event_type] = report["event_types"].get(event_type, 0) + 1
            
            severity = event.severity.value
            report["severity_distribution"][severity] = report["severity_distribution"].get(severity, 0) + 1
            
            if event.user_id:
                report["top_users"][event.user_id] = report["top_users"].get(event.user_id, 0) + 1
        
        # Gera alertas
        unique_users = set(e.user_id for e in security_events if e.user_id)
        for user_id in unique_users:
            alerts = self.detect_unusual_activity(user_id)
            if alerts:
                report["alerts"].append({
                    "user_id": user_id,
                    "alerts": alerts
                })
        
        return report
