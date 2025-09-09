"""
Sistema de autorização baseado em roles (RBAC) e permissões.
"""

from typing import Dict, List, Set, Optional
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback para ambientes sem pydantic
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class Permission(Enum):
    """Permissões do sistema."""

    # Agentes
    CREATE_AGENT = "create_agent"
    READ_AGENT = "read_agent"
    UPDATE_AGENT = "update_agent"
    DELETE_AGENT = "delete_agent"

    # Simulação
    START_SIMULATION = "start_simulation"
    STOP_SIMULATION = "stop_simulation"
    PAUSE_SIMULATION = "pause_simulation"
    READ_SIMULATION = "read_simulation"

    # Configurações
    READ_CONFIG = "read_config"
    UPDATE_CONFIG = "update_config"

    # Relatórios
    READ_REPORTS = "read_reports"
    EXPORT_REPORTS = "export_reports"

    # Sistema
    READ_LOGS = "read_logs"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"


class Resource(Enum):
    """Recursos do sistema."""

    AGENTS = "agents"
    SIMULATION = "simulation"
    CONFIG = "config"
    REPORTS = "reports"
    LOGS = "logs"
    USERS = "users"
    SYSTEM = "system"


@dataclass
class Role:
    """Definição de role com permissões."""

    name: str
    description: str
    permissions: Set[Permission]
    resources: Set[Resource]
    is_system: bool = False  # Roles do sistema não podem ser deletadas


class RBACService:
    """Serviço de autorização RBAC."""

    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}  # user_id -> roles
        self.resource_permissions: Dict[Resource, Set[Permission]] = {}
        self._initialize_default_roles()
        self._initialize_resource_permissions()

    def _initialize_default_roles(self):
        """Inicializa roles padrão do sistema."""
        # Admin - acesso total
        admin_role = Role(
            name="admin",
            description="Administrador do sistema com acesso total",
            permissions=set(Permission),
            resources=set(Resource),
            is_system=True,
        )
        self.roles["admin"] = admin_role

        # Operator - operações de simulação
        operator_permissions = {
            Permission.CREATE_AGENT,
            Permission.READ_AGENT,
            Permission.UPDATE_AGENT,
            Permission.START_SIMULATION,
            Permission.STOP_SIMULATION,
            Permission.PAUSE_SIMULATION,
            Permission.READ_SIMULATION,
            Permission.READ_CONFIG,
            Permission.READ_REPORTS,
            Permission.EXPORT_REPORTS,
            Permission.READ_LOGS,
        }

        operator_role = Role(
            name="operator",
            description="Operador de simulação",
            permissions=operator_permissions,
            resources={
                Resource.AGENTS,
                Resource.SIMULATION,
                Resource.CONFIG,
                Resource.REPORTS,
                Resource.LOGS,
            },
            is_system=True,
        )
        self.roles["operator"] = operator_role

        # Viewer - apenas leitura
        viewer_permissions = {
            Permission.READ_AGENT,
            Permission.READ_SIMULATION,
            Permission.READ_CONFIG,
            Permission.READ_REPORTS,
        }

        viewer_role = Role(
            name="viewer",
            description="Visualizador com acesso apenas de leitura",
            permissions=viewer_permissions,
            resources={
                Resource.AGENTS,
                Resource.SIMULATION,
                Resource.CONFIG,
                Resource.REPORTS,
            },
            is_system=True,
        )
        self.roles["viewer"] = viewer_role

        # Agent - permissões limitadas para agentes IA
        agent_permissions = {
            Permission.READ_AGENT,
            Permission.READ_SIMULATION,
            Permission.READ_CONFIG,
        }

        agent_role = Role(
            name="agent",
            description="Agente IA com permissões limitadas",
            permissions=agent_permissions,
            resources={Resource.AGENTS, Resource.SIMULATION, Resource.CONFIG},
            is_system=True,
        )
        self.roles["agent"] = agent_role

    def _initialize_resource_permissions(self):
        """Inicializa mapeamento de recursos para permissões."""
        self.resource_permissions = {
            Resource.AGENTS: {
                Permission.CREATE_AGENT,
                Permission.READ_AGENT,
                Permission.UPDATE_AGENT,
                Permission.DELETE_AGENT,
            },
            Resource.SIMULATION: {
                Permission.START_SIMULATION,
                Permission.STOP_SIMULATION,
                Permission.PAUSE_SIMULATION,
                Permission.READ_SIMULATION,
            },
            Resource.CONFIG: {Permission.READ_CONFIG, Permission.UPDATE_CONFIG},
            Resource.REPORTS: {Permission.READ_REPORTS, Permission.EXPORT_REPORTS},
            Resource.LOGS: {Permission.READ_LOGS},
            Resource.USERS: {Permission.MANAGE_USERS},
            Resource.SYSTEM: {Permission.SYSTEM_ADMIN},
        }

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Atribui role a um usuário."""
        if role_name not in self.roles:
            return False

        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()

        self.user_roles[user_id].add(role_name)
        return True

    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove role de um usuário."""
        if user_id not in self.user_roles:
            return False

        self.user_roles[user_id].discard(role_name)
        return True

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Retorna roles de um usuário."""
        return self.user_roles.get(user_id, set())

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Verifica se usuário tem permissão específica."""
        user_roles = self.get_user_roles(user_id)

        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if permission in role.permissions:
                    return True

        return False

    def has_resource_permission(
        self, user_id: str, resource: Resource, permission: Permission
    ) -> bool:
        """Verifica se usuário tem permissão em recurso específico."""
        # Verifica se a permissão é válida para o recurso
        if resource not in self.resource_permissions:
            return False

        if permission not in self.resource_permissions[resource]:
            return False

        # Verifica se usuário tem a permissão
        return self.has_permission(user_id, permission)

    def can_access_resource(self, user_id: str, resource: Resource) -> bool:
        """Verifica se usuário pode acessar recurso."""
        user_roles = self.get_user_roles(user_id)

        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if resource in role.resources:
                    return True

        return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Retorna todas as permissões de um usuário."""
        permissions = set()
        user_roles = self.get_user_roles(user_id)

        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                permissions.update(role.permissions)

        return permissions

    def create_role(
        self,
        name: str,
        description: str,
        permissions: Set[Permission],
        resources: Set[Resource],
    ) -> bool:
        """Cria nova role personalizada."""
        if name in self.roles:
            return False  # Role já existe

        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            resources=resources,
            is_system=False,
        )

        self.roles[name] = role
        return True

    def update_role(
        self,
        name: str,
        description: str = None,
        permissions: Set[Permission] = None,
        resources: Set[Resource] = None,
    ) -> bool:
        """Atualiza role existente."""
        if name not in self.roles:
            return False

        role = self.roles[name]

        if role.is_system:
            return False  # Não pode modificar roles do sistema

        if description is not None:
            role.description = description

        if permissions is not None:
            role.permissions = permissions

        if resources is not None:
            role.resources = resources

        return True

    def delete_role(self, name: str) -> bool:
        """Deleta role personalizada."""
        if name not in self.roles:
            return False

        role = self.roles[name]

        if role.is_system:
            return False  # Não pode deletar roles do sistema

        # Remove role de todos os usuários
        for user_id in self.user_roles:
            self.user_roles[user_id].discard(name)

        del self.roles[name]
        return True

    def get_role_info(self, name: str) -> Optional[Role]:
        """Retorna informações de uma role."""
        return self.roles.get(name)

    def list_roles(self) -> List[Role]:
        """Lista todas as roles."""
        return list(self.roles.values())

    def get_users_with_role(self, role_name: str) -> List[str]:
        """Retorna usuários que possuem uma role específica."""
        users = []
        for user_id, roles in self.user_roles.items():
            if role_name in roles:
                users.append(user_id)
        return users


class AccessControl:
    """Controle de acesso com verificação de contexto."""

    def __init__(self, rbac_service: RBACService):
        self.rbac = rbac_service

    def check_access(
        self, user_id: str, resource: Resource, action: Permission, context: Dict = None
    ) -> bool:
        """Verifica acesso com contexto adicional."""
        # Verificação básica de permissão
        if not self.rbac.has_resource_permission(user_id, resource, action):
            return False

        # Verificações de contexto podem ser adicionadas aqui
        if context:
            # Exemplo: verificar se usuário pode acessar dados de outros usuários
            if "target_user_id" in context:
                target_user_id = context["target_user_id"]
                if user_id != target_user_id:
                    # Apenas admins podem acessar dados de outros usuários
                    if not self.rbac.has_permission(user_id, Permission.SYSTEM_ADMIN):
                        return False

        return True

    def filter_resources(
        self, user_id: str, resources: List[Resource]
    ) -> List[Resource]:
        """Filtra recursos que o usuário pode acessar."""
        accessible = []
        for resource in resources:
            if self.rbac.can_access_resource(user_id, resource):
                accessible.append(resource)
        return accessible
