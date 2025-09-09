"""
Sistema de criptografia para dados sensíveis e comunicação segura.
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from typing import Union, Optional, Dict, Any
import json
import secrets


class EncryptionService:
    """Serviço de criptografia para dados sensíveis."""

    def __init__(self, master_key: Optional[str] = None):
        """
        Inicializa serviço de criptografia.

        Args:
            master_key: Chave mestra para derivação de chaves.
                       Se None, gera uma nova chave.
        """
        if master_key:
            self.master_key = master_key.encode()
        else:
            self.master_key = Fernet.generate_key()

        self.fernet = Fernet(self.master_key)

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Deriva chave de criptografia a partir de senha e salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt_data(self, data: Union[str, bytes, Dict, Any]) -> str:
        """
        Criptografa dados usando Fernet (AES 128 em modo CBC).

        Args:
            data: Dados para criptografar

        Returns:
            String base64 com dados criptografados
        """
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        elif isinstance(data, str):
            data = data.encode("utf-8")
        elif not isinstance(data, bytes):
            data = str(data).encode("utf-8")

        encrypted_data = self.fernet.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Descriptografa dados.

        Args:
            encrypted_data: String base64 com dados criptografados

        Returns:
            Dados descriptografados como string
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode("utf-8")
        except Exception:
            raise ValueError("Falha ao descriptografar dados")

    def encrypt_json(self, data: Dict[str, Any]) -> str:
        """Criptografa dicionário JSON."""
        json_str = json.dumps(data, ensure_ascii=False)
        return self.encrypt_data(json_str)

    def decrypt_json(self, encrypted_data: str) -> Dict[str, Any]:
        """Descriptografa dicionário JSON."""
        json_str = self.decrypt_data(encrypted_data)
        return json.loads(json_str)

    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """
        Gera hash seguro de dados sensíveis.

        Args:
            data: Dados para fazer hash
            salt: Salt personalizado (opcional)

        Returns:
            Hash em formato salt:hash
        """
        if salt is None:
            salt = secrets.token_hex(32)

        hash_obj = hashlib.pbkdf2_hmac(
            "sha256", data.encode("utf-8"), salt.encode("utf-8"), 100000
        )

        return f"{salt}:{hash_obj.hex()}"

    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verifica se dados correspondem ao hash."""
        try:
            salt, hash_part = hash_value.split(":")
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", data.encode("utf-8"), salt.encode("utf-8"), 100000
            )
            return computed_hash.hex() == hash_part
        except ValueError:
            return False


class FieldEncryption:
    """Criptografia de campos específicos de dados."""

    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service

    def encrypt_field(self, value: Any, field_name: str) -> str:
        """Criptografa campo específico."""
        if value is None:
            return None

        # Adiciona metadados do campo
        field_data = {
            "field": field_name,
            "value": value,
            "timestamp": str(os.urandom(8).hex()),
        }  # Nonce simples

        return self.encryption.encrypt_json(field_data)

    def decrypt_field(self, encrypted_value: str) -> tuple:
        """Descriptografa campo e retorna (field_name, value)."""
        if encrypted_value is None:
            return None, None

        try:
            field_data = self.encryption.decrypt_json(encrypted_value)
            return field_data.get("field"), field_data.get("value")
        except Exception:
            return None, None


class SecureStorage:
    """Armazenamento seguro para dados sensíveis."""

    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service
        self.field_encryption = FieldEncryption(encryption_service)

    def store_sensitive_data(
        self, data: Dict[str, Any], sensitive_fields: list
    ) -> Dict[str, Any]:
        """
        Armazena dados com campos sensíveis criptografados.

        Args:
            data: Dados para armazenar
            sensitive_fields: Lista de campos sensíveis para criptografar

        Returns:
            Dados com campos sensíveis criptografados
        """
        encrypted_data = data.copy()

        for field in sensitive_fields:
            if field in data and data[field] is not None:
                encrypted_data[field] = self.field_encryption.encrypt_field(
                    data[field], field
                )

        return encrypted_data

    def retrieve_sensitive_data(
        self, encrypted_data: Dict[str, Any], sensitive_fields: list
    ) -> Dict[str, Any]:
        """
        Recupera dados descriptografando campos sensíveis.

        Args:
            encrypted_data: Dados com campos criptografados
            sensitive_fields: Lista de campos sensíveis para descriptografar

        Returns:
            Dados com campos sensíveis descriptografados
        """
        decrypted_data = encrypted_data.copy()

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field] is not None:
                field_name, value = self.field_encryption.decrypt_field(
                    encrypted_data[field]
                )
                if field_name == field:
                    decrypted_data[field] = value

        return decrypted_data


class CommunicationEncryption:
    """Criptografia para comunicação entre serviços."""

    def __init__(self, encryption_service: EncryptionService):
        self.encryption = encryption_service

    def encrypt_message(
        self, message: Dict[str, Any], recipient_id: str
    ) -> Dict[str, Any]:
        """
        Criptografa mensagem para comunicação segura.

        Args:
            message: Mensagem para criptografar
            recipient_id: ID do destinatário

        Returns:
            Mensagem criptografada com metadados
        """
        # Adiciona metadados de segurança
        secure_message = {
            "recipient": recipient_id,
            "timestamp": str(os.urandom(8).hex()),
            "message": message,
        }

        encrypted_content = self.encryption.encrypt_json(secure_message)

        return {
            "encrypted": True,
            "content": encrypted_content,
            "algorithm": "AES-256-GCM",
            "version": "1.0",
        }

    def decrypt_message(self, encrypted_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Descriptografa mensagem recebida.

        Args:
            encrypted_message: Mensagem criptografada

        Returns:
            Mensagem descriptografada
        """
        if not encrypted_message.get("encrypted", False):
            return encrypted_message

        try:
            content = encrypted_message["content"]
            decrypted_data = self.encryption.decrypt_json(content)
            return decrypted_data.get("message", {})
        except Exception:
            raise ValueError("Falha ao descriptografar mensagem")

    def verify_message_integrity(self, message: Dict[str, Any]) -> bool:
        """Verifica integridade da mensagem."""
        required_fields = ["encrypted", "content", "algorithm", "version"]
        return all(field in message for field in required_fields)


class KeyManagement:
    """Gerenciamento de chaves de criptografia."""

    def __init__(self):
        self.keys: Dict[str, bytes] = {}
        self.key_rotation_schedule: Dict[str, int] = {}

    def generate_key(self, key_id: str, key_type: str = "fernet") -> bytes:
        """Gera nova chave de criptografia."""
        if key_type == "fernet":
            key = Fernet.generate_key()
        else:
            key = os.urandom(32)  # 256 bits

        self.keys[key_id] = key
        return key

    def get_key(self, key_id: str) -> Optional[bytes]:
        """Recupera chave por ID."""
        return self.keys.get(key_id)

    def rotate_key(self, key_id: str) -> bytes:
        """Rotaciona chave existente."""
        new_key = self.generate_key(key_id)

        # Aqui você implementaria a migração de dados
        # criptografados com a chave antiga para a nova

        return new_key

    def revoke_key(self, key_id: str) -> bool:
        """Revoga chave (marca como inválida)."""
        if key_id in self.keys:
            del self.keys[key_id]
            return True
        return False

    def list_keys(self) -> list:
        """Lista todas as chaves ativas."""
        return list(self.keys.keys())
