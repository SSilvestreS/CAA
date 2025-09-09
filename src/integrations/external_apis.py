"""
Gerenciador de APIs Externas
Versão 1.6 - MLOps e Escalabilidade
"""

import aiohttp
import logging
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIType(str, Enum):
    """Tipos de APIs externas"""

    WEATHER = "weather"
    MAPS = "maps"
    TRANSPORT = "transport"
    DEMOGRAPHIC = "demographic"
    ECONOMIC = "economic"
    SOCIAL = "social"


class APIStatus(str, Enum):
    """Status das APIs"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


@dataclass
class APIResponse:
    """Resposta de uma API externa"""

    data: Any
    status_code: int
    headers: Dict[str, str]
    timestamp: datetime
    api_name: str
    success: bool
    error_message: Optional[str] = None


class APIConfig(BaseModel):
    """Configuração de uma API"""

    name: str
    api_type: APIType
    base_url: str
    api_key: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: int = 30
    rate_limit: int = 100  # requests per minute
    retry_attempts: int = 3
    retry_delay: int = 1  # seconds
    status: APIStatus = APIStatus.ACTIVE
    last_used: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class ExternalAPIManager:
    """Gerenciador de APIs externas"""

    def __init__(self):
        self.apis: Dict[str, APIConfig] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Inicia o gerenciador"""
        self.session = aiohttp.ClientSession()
        logger.info("External API Manager iniciado")

    async def stop(self):
        """Para o gerenciador"""
        if self.session:
            await self.session.close()
        logger.info("External API Manager parado")

    async def register_api(self, config: APIConfig) -> bool:
        """Registra uma nova API"""
        try:
            self.apis[config.name] = config
            self.rate_limits[config.name] = []
            logger.info(f"API registrada: {config.name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar API: {e}")
            return False

    async def unregister_api(self, name: str) -> bool:
        """Remove uma API"""
        try:
            if name in self.apis:
                del self.apis[name]
                if name in self.rate_limits:
                    del self.rate_limits[name]
                logger.info(f"API removida: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover API: {e}")
            return False

    async def make_request(
        self,
        api_name: str,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> APIResponse:
        """Faz uma requisição para uma API externa"""
        if not self.session:
            raise RuntimeError("Session não inicializada")

        if api_name not in self.apis:
            raise ValueError(f"API não encontrada: {api_name}")

        api_config = self.apis[api_name]

        # Verifica rate limit
        if not await self._check_rate_limit(api_name):
            return APIResponse(
                data=None,
                status_code=429,
                headers={},
                timestamp=datetime.now(),
                api_name=api_name,
                success=False,
                error_message="Rate limit exceeded",
            )

        # Prepara headers
        request_headers = api_config.headers.copy()
        if api_config.api_key:
            request_headers["Authorization"] = f"Bearer {api_config.api_key}"
        if headers:
            request_headers.update(headers)

        # Prepara URL
        url = f"{api_config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Faz a requisição com retry
        for attempt in range(api_config.retry_attempts):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=aiohttp.ClientTimeout(total=api_config.timeout),
                ) as response:

                    response_data = await response.json()

                    # Atualiza estatísticas
                    api_config.last_used = datetime.now()
                    if response.status == 200:
                        api_config.success_count += 1
                    else:
                        api_config.error_count += 1

                    # Registra uso para rate limiting
                    self.rate_limits[api_name].append(datetime.now())

                    return APIResponse(
                        data=response_data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        timestamp=datetime.now(),
                        api_name=api_name,
                        success=response.status == 200,
                        error_message=(
                            None
                            if response.status == 200
                            else f"HTTP {response.status}"
                        ),
                    )

            except asyncio.TimeoutError:
                if attempt == api_config.retry_attempts - 1:
                    api_config.error_count += 1
                    return APIResponse(
                        data=None,
                        status_code=408,
                        headers={},
                        timestamp=datetime.now(),
                        api_name=api_name,
                        success=False,
                        error_message="Timeout",
                    )
                await asyncio.sleep(api_config.retry_delay * (2**attempt))

            except Exception as e:
                if attempt == api_config.retry_attempts - 1:
                    api_config.error_count += 1
                    return APIResponse(
                        data=None,
                        status_code=500,
                        headers={},
                        timestamp=datetime.now(),
                        api_name=api_name,
                        success=False,
                        error_message=str(e),
                    )
                await asyncio.sleep(api_config.retry_delay * (2**attempt))

    async def _check_rate_limit(self, api_name: str) -> bool:
        """Verifica se a API está dentro do rate limit"""
        if api_name not in self.rate_limits:
            return True

        api_config = self.apis[api_name]
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Remove requisições antigas
        self.rate_limits[api_name] = [
            req_time for req_time in self.rate_limits[api_name] if req_time > minute_ago
        ]

        # Verifica se está dentro do limite
        return len(self.rate_limits[api_name]) < api_config.rate_limit

    async def get_weather_data(
        self, city: str, country: str = "BR"
    ) -> Optional[Dict[str, Any]]:
        """Obtém dados do clima"""
        try:
            # Busca API de clima
            weather_api = None
            for name, config in self.apis.items():
                if config.api_type == APIType.WEATHER:
                    weather_api = name
                    break

            if not weather_api:
                logger.warning("Nenhuma API de clima configurada")
                return None

            response = await self.make_request(
                api_name=weather_api,
                endpoint="weather",
                params={"q": f"{city},{country}", "units": "metric"},
            )

            if response.success:
                return response.data
            else:
                logger.error(f"Erro ao obter dados do clima: {response.error_message}")
                return None

        except Exception as e:
            logger.error(f"Erro ao obter dados do clima: {e}")
            return None

    async def get_map_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de geolocalização"""
        try:
            # Busca API de mapas
            maps_api = None
            for name, config in self.apis.items():
                if config.api_type == APIType.MAPS:
                    maps_api = name
                    break

            if not maps_api:
                logger.warning("Nenhuma API de mapas configurada")
                return None

            response = await self.make_request(
                api_name=maps_api, endpoint="geocode/json", params={"address": address}
            )

            if response.success:
                return response.data
            else:
                logger.error(f"Erro ao obter dados de mapas: {response.error_message}")
                return None

        except Exception as e:
            logger.error(f"Erro ao obter dados de mapas: {e}")
            return None

    async def get_transport_data(
        self, origin: str, destination: str
    ) -> Optional[Dict[str, Any]]:
        """Obtém dados de transporte"""
        try:
            # Busca API de transporte
            transport_api = None
            for name, config in self.apis.items():
                if config.api_type == APIType.TRANSPORT:
                    transport_api = name
                    break

            if not transport_api:
                logger.warning("Nenhuma API de transporte configurada")
                return None

            response = await self.make_request(
                api_name=transport_api,
                endpoint="directions/json",
                params={
                    "origin": origin,
                    "destination": destination,
                    "mode": "transit",
                },
            )

            if response.success:
                return response.data
            else:
                logger.error(
                    f"Erro ao obter dados de transporte: {response.error_message}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao obter dados de transporte: {e}")
            return None

    async def get_demographic_data(self, region: str) -> Optional[Dict[str, Any]]:
        """Obtém dados demográficos"""
        try:
            # Busca API demográfica
            demo_api = None
            for name, config in self.apis.items():
                if config.api_type == APIType.DEMOGRAPHIC:
                    demo_api = name
                    break

            if not demo_api:
                logger.warning("Nenhuma API demográfica configurada")
                return None

            response = await self.make_request(
                api_name=demo_api, endpoint="demographics", params={"region": region}
            )

            if response.success:
                return response.data
            else:
                logger.error(
                    f"Erro ao obter dados demográficos: {response.error_message}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao obter dados demográficos: {e}")
            return None

    async def get_api_status(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Obtém status de uma API"""
        if api_name not in self.apis:
            return None

        api_config = self.apis[api_name]

        return {
            "name": api_name,
            "type": api_config.api_type.value,
            "status": api_config.status.value,
            "last_used": api_config.last_used,
            "success_count": api_config.success_count,
            "error_count": api_config.error_count,
            "success_rate": (
                api_config.success_count
                / (api_config.success_count + api_config.error_count)
                if (api_config.success_count + api_config.error_count) > 0
                else 0
            ),
            "rate_limit_remaining": (
                api_config.rate_limit - len(self.rate_limits.get(api_name, []))
            ),
        }

    async def get_all_apis_status(self) -> List[Dict[str, Any]]:
        """Obtém status de todas as APIs"""
        status_list = []
        for api_name in self.apis:
            status = await self.get_api_status(api_name)
            if status:
                status_list.append(status)
        return status_list

    async def health_check(self) -> Dict[str, Any]:
        """Health check do gerenciador"""
        total_apis = len(self.apis)
        active_apis = len(
            [api for api in self.apis.values() if api.status == APIStatus.ACTIVE]
        )

        return {
            "total_apis": total_apis,
            "active_apis": active_apis,
            "health_percentage": (
                (active_apis / total_apis * 100) if total_apis > 0 else 0
            ),
            "last_check": datetime.now(),
        }
