"""
Gerenciador de Modelos ML
Versão 1.6 - MLOps e Escalabilidade
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
from enum import Enum

import joblib
import numpy as np
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ModelStatus(str, Enum):
    """Status dos modelos"""

    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ModelType(str, Enum):
    """Tipos de modelos"""

    TRANSFORMER = "transformer"
    LSTM = "lstm"
    GAN = "gan"
    DQN = "dqn"
    PPO = "ppo"
    A3C = "a3c"


class ModelMetadata(BaseModel):
    """Metadados do modelo"""

    name: str
    version: str
    type: ModelType
    status: ModelStatus
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    training_data_size: int = 0
    model_size_mb: float = 0.0
    accuracy: Optional[float] = None
    loss: Optional[float] = None


class ModelVersion(BaseModel):
    """Versão de um modelo"""

    version: str
    metadata: ModelMetadata
    file_path: str
    is_current: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class ModelManager:
    """Gerenciador de modelos ML"""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.models: Dict[str, List[ModelVersion]] = {}
        self.current_models: Dict[str, str] = {}  # name -> version

    async def register_model(
        self,
        name: str,
        model_type: ModelType,
        model: Any,
        metadata: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
    ) -> str:
        """Registra um novo modelo"""
        try:
            # Gera versão se não fornecida
            if not version:
                version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Cria metadados
            model_metadata = ModelMetadata(
                name=name,
                version=version,
                type=model_type,
                status=ModelStatus.TRAINED,
                **(metadata or {}),
            )

            # Salva o modelo
            model_path = self.models_dir / name / version
            model_path.mkdir(parents=True, exist_ok=True)

            # Salva modelo (assumindo que tem método save ou é serializável)
            if hasattr(model, "save"):
                model.save(str(model_path / "model.pkl"))
            else:
                joblib.dump(model, str(model_path / "model.pkl"))

            # Calcula tamanho do arquivo
            file_size = (model_path / "model.pkl").stat().st_size / (1024 * 1024)
            model_metadata.model_size_mb = file_size

            # Salva metadados
            with open(model_path / "metadata.json", "w") as f:
                json.dump(model_metadata.dict(), f, indent=2, default=str)

            # Registra no gerenciador
            if name not in self.models:
                self.models[name] = []

            model_version = ModelVersion(
                version=version,
                metadata=model_metadata,
                file_path=str(model_path / "model.pkl"),
            )

            self.models[name].append(model_version)
            self.current_models[name] = version

            logger.info(f"Modelo registrado: {name} v{version}")
            return version

        except Exception as e:
            logger.error(f"Erro ao registrar modelo: {e}")
            raise

    async def load_model(self, name: str, version: Optional[str] = None) -> Any:
        """Carrega um modelo"""
        try:
            if name not in self.models:
                raise ValueError(f"Modelo não encontrado: {name}")

            # Usa versão atual se não especificada
            if not version:
                version = self.current_models.get(name)
                if not version:
                    raise ValueError(f"Nenhuma versão atual para modelo: {name}")

            # Encontra a versão
            model_version = None
            for v in self.models[name]:
                if v.version == version:
                    model_version = v
                    break

            if not model_version:
                raise ValueError(f"Versão não encontrada: {name} v{version}")

            # Carrega o modelo
            model = joblib.load(model_version.file_path)
            logger.info(f"Modelo carregado: {name} v{version}")
            return model

        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise

    async def list_models(self) -> Dict[str, List[ModelVersion]]:
        """Lista todos os modelos"""
        return self.models.copy()

    async def get_model_versions(self, name: str) -> List[ModelVersion]:
        """Obtém versões de um modelo"""
        return self.models.get(name, []).copy()

    async def get_current_version(self, name: str) -> Optional[str]:
        """Obtém versão atual de um modelo"""
        return self.current_models.get(name)

    async def set_current_version(self, name: str, version: str) -> bool:
        """Define versão atual de um modelo"""
        if name not in self.models:
            return False

        # Verifica se versão existe
        for v in self.models[name]:
            if v.version == version:
                self.current_models[name] = version
                logger.info(f"Versão atual definida: {name} v{version}")
                return True

        return False

    async def delete_model(self, name: str, version: Optional[str] = None) -> bool:
        """Remove um modelo ou versão"""
        try:
            if name not in self.models:
                return False

            if version:
                # Remove versão específica
                for i, v in enumerate(self.models[name]):
                    if v.version == version:
                        # Remove arquivos
                        model_path = Path(v.file_path).parent
                        if model_path.exists():
                            import shutil

                            shutil.rmtree(model_path)

                        # Remove da lista
                        del self.models[name][i]

                        # Atualiza versão atual se necessário
                        if self.current_models.get(name) == version:
                            if self.models[name]:
                                self.current_models[name] = self.models[name][
                                    -1
                                ].version
                            else:
                                del self.current_models[name]

                        logger.info(f"Versão removida: {name} v{version}")
                        return True

            else:
                # Remove modelo completo
                for v in self.models[name]:
                    model_path = Path(v.file_path).parent
                    if model_path.exists():
                        import shutil

                        shutil.rmtree(model_path)

                del self.models[name]
                if name in self.current_models:
                    del self.current_models[name]

                logger.info(f"Modelo removido: {name}")
                return True

        except Exception as e:
            logger.error(f"Erro ao remover modelo: {e}")
            return False

    async def update_metadata(
        self, name: str, version: str, metadata: Dict[str, Any]
    ) -> bool:
        """Atualiza metadados de um modelo"""
        try:
            if name not in self.models:
                return False

            # Encontra a versão
            for v in self.models[name]:
                if v.version == version:
                    # Atualiza metadados
                    for key, value in metadata.items():
                        if hasattr(v.metadata, key):
                            setattr(v.metadata, key, value)

                    v.metadata.updated_at = datetime.now()

                    # Salva metadados atualizados
                    model_path = Path(v.file_path).parent
                    with open(model_path / "metadata.json", "w") as f:
                        json.dump(v.metadata.dict(), f, indent=2, default=str)

                    logger.info(f"Metadados atualizados: {name} v{version}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Erro ao atualizar metadados: {e}")
            return False

    async def get_model_info(
        self, name: str, version: Optional[str] = None
    ) -> Optional[ModelMetadata]:
        """Obtém informações de um modelo"""
        if name not in self.models:
            return None

        if not version:
            version = self.current_models.get(name)
            if not version:
                return None

        for v in self.models[name]:
            if v.version == version:
                return v.metadata

        return None

    async def search_models(
        self,
        name_pattern: Optional[str] = None,
        model_type: Optional[ModelType] = None,
        status: Optional[ModelStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[ModelVersion]:
        """Busca modelos com filtros"""
        results = []

        for name, versions in self.models.items():
            for version in versions:
                # Filtra por nome
                if name_pattern and name_pattern.lower() not in name.lower():
                    continue

                # Filtra por tipo
                if model_type and version.metadata.type != model_type:
                    continue

                # Filtra por status
                if status and version.metadata.status != status:
                    continue

                # Filtra por tags
                if tags and not any(tag in version.metadata.tags for tag in tags):
                    continue

                results.append(version)

        return results

    async def export_model(self, name: str, version: str, export_path: str) -> bool:
        """Exporta um modelo para um arquivo"""
        try:
            if name not in self.models:
                return False

            # Encontra a versão
            model_version = None
            for v in self.models[name]:
                if v.version == version:
                    model_version = v
                    break

            if not model_version:
                return False

            # Copia arquivos
            import shutil

            source_path = Path(model_version.file_path).parent
            shutil.copytree(source_path, export_path)

            logger.info(f"Modelo exportado: {name} v{version} -> {export_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao exportar modelo: {e}")
            return False

    async def import_model(self, import_path: str, name: Optional[str] = None) -> bool:
        """Importa um modelo de um arquivo"""
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                return False

            # Lê metadados
            metadata_file = import_path / "metadata.json"
            if not metadata_file.exists():
                return False

            with open(metadata_file, "r") as f:
                metadata_dict = json.load(f)

            # Usa nome dos metadados se não fornecido
            if not name:
                name = metadata_dict["name"]

            # Registra o modelo
            version = metadata_dict["version"]
            model_type = ModelType(metadata_dict["type"])

            # Carrega modelo
            model_file = import_path / "model.pkl"
            if not model_file.exists():
                return False

            model = joblib.load(model_file)

            # Registra no gerenciador
            await self.register_model(
                name=name,
                model_type=model_type,
                model=model,
                metadata=metadata_dict,
                version=version,
            )

            logger.info(f"Modelo importado: {name} v{version}")
            return True

        except Exception as e:
            logger.error(f"Erro ao importar modelo: {e}")
            return False
