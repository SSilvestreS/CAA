"""
Sistema de autenticação JWT com refresh tokens e validação robusta.
"""

from typing import Dict, List, Optional

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback para ambientes sem pydantic
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class UserRole(Enum):
    """Roles de usuário no sistema."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    AGENT = "agent"


@dataclass
class User:
    """Modelo de usuário do sistema."""

    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TokenPayload(BaseModel):
    """Payload do token JWT."""

    user_id: str
    username: str
    role: str
    exp: datetime
    iat: datetime
    jti: str  # JWT ID para invalidação


class AuthService:
    """Serviço de autenticação com JWT e refresh tokens."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.refresh_tokens: Dict[str, str] = {}  # jti -> user_id
        self.blacklisted_tokens: set = set()

    def hash_password(self, password: str) -> str:
        """Gera hash seguro da senha usando PBKDF2."""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return f"{salt}:{pwd_hash.hex()}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se a senha está correta."""
        try:
            salt, hash_part = password_hash.split(":")
            pwd_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return pwd_hash.hex() == hash_part
        except ValueError:
            return False

    def generate_tokens(self, user: User) -> Dict[str, str]:
        """Gera access token e refresh token para o usuário."""
        now = datetime.utcnow()
        jti = secrets.token_urlsafe(32)

        # Access token (15 minutos)
        access_payload = TokenPayload(
            user_id=user.id,
            username=user.username,
            role=user.role.value,
            exp=now + timedelta(minutes=15),
            iat=now,
            jti=jti,
        )

        access_token = jwt.encode(
            access_payload.__dict__, self.secret_key, algorithm=self.algorithm
        )

        # Refresh token (7 dias)
        refresh_jti = secrets.token_urlsafe(32)
        refresh_payload = {
            "user_id": user.id,
            "jti": refresh_jti,
            "exp": now + timedelta(days=7),
            "iat": now,
            "type": "refresh",
        }

        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        # Armazena refresh token
        self.refresh_tokens[refresh_jti] = user.id

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutos
        }

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verifica e decodifica o token JWT."""
        try:
            # Verifica se token está na blacklist
            if token in self.blacklisted_tokens:
                return None

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Converte para TokenPayload
            token_payload = TokenPayload(**payload)

            # Verifica se token não expirou
            if token_payload.exp < datetime.utcnow():
                return None

            return token_payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Gera novo access token usando refresh token."""
        try:
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            if payload.get("type") != "refresh":
                return None

            jti = payload.get("jti")
            user_id = self.refresh_tokens.get(jti)

            if not user_id:
                return None

            # Remove refresh token usado
            del self.refresh_tokens[jti]

            # Aqui você buscaria o usuário do banco de dados
            # Por simplicidade, vamos criar um usuário mock
            user = User(
                id=user_id,
                username=payload.get("username", "user"),
                email="user@example.com",
                password_hash="",
                role=UserRole.VIEWER,
            )

            return self.generate_tokens(user)

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def revoke_token(self, token: str) -> bool:
        """Adiciona token à blacklist."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            jti = payload.get("jti")
            if jti:
                self.blacklisted_tokens.add(token)
                return True
            return False

        except jwt.InvalidTokenError:
            return False

    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoga todos os tokens de um usuário."""
        revoked_count = 0

        # Remove refresh tokens
        tokens_to_remove = [
            jti for jti, uid in self.refresh_tokens.items() if uid == user_id
        ]

        for jti in tokens_to_remove:
            del self.refresh_tokens[jti]
            revoked_count += 1

        return revoked_count


class PasswordPolicy:
    """Política de senhas do sistema."""

    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True,
        max_attempts: int = 5,
        lockout_duration: int = 30,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration

    def validate_password(self, password: str) -> List[str]:
        """Valida senha contra a política."""
        errors = []

        if len(password) < self.min_length:
            errors.append(f"Senha deve ter pelo menos {self.min_length} caracteres")

        if self.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")

        if self.require_lowercase and not any(c.islower() for c in password):
            errors.append("Senha deve conter pelo menos uma letra minúscula")

        if self.require_numbers and not any(c.isdigit() for c in password):
            errors.append("Senha deve conter pelo menos um número")

        if self.require_special and not any(
            c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
        ):
            errors.append("Senha deve conter pelo menos um caractere especial")

        return errors

    def is_account_locked(self, user: User) -> bool:
        """Verifica se a conta está bloqueada."""
        if user.locked_until is None:
            return False

        if user.locked_until > datetime.utcnow():
            return True

        # Desbloqueia conta se tempo expirou
        user.locked_until = None
        user.failed_attempts = 0
        return False

    def handle_failed_login(self, user: User) -> bool:
        """Processa tentativa de login falhada."""
        user.failed_attempts += 1

        if user.failed_attempts >= self.max_attempts:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=self.lockout_duration
            )
            return True  # Conta bloqueada

        return False  # Conta ainda ativa

    def handle_successful_login(self, user: User):
        """Processa login bem-sucedido."""
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
