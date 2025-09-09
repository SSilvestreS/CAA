"""
Script de teste para a versão 1.7 - MLOps e Escalabilidade
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from src.config.v1_7_config import get_config, Environment  # noqa: E402
from src.microservices.agent_service.agent_manager import (
    AgentManager,
    AgentType,
)  # noqa: E402
from src.mlops import ModelManager, ModelType  # noqa: E402
from src.integrations import ExternalAPIManager, APIType, APIConfig  # noqa: E402
from src.analytics import (
    DashboardManager,
    DashboardType,
    WidgetType,
    Widget,
)  # noqa: E402


async def test_agent_service():
    """Testa o Agent Service"""
    print("🧪 Testando Agent Service...")

    try:
        # Inicializa o gerenciador
        agent_manager = AgentManager()
        await agent_manager.start()

        # Cria um agente
        agent = await agent_manager.create_agent(
            agent_type=AgentType.CITIZEN,
            name="Test Citizen",
            description="Agente de teste",
        )

        print(f"✅ Agente criado: {agent.id}")

        # Lista agentes
        agents = await agent_manager.list_agents()
        print(f"✅ Total de agentes: {len(agents)}")

        # Atualiza agente
        updated_agent = await agent_manager.update_agent(
            agent.id, {"name": "Updated Test Citizen"}
        )
        print(f"✅ Agente atualizado: {updated_agent.name}")

        # Inicia agente
        success = await agent_manager.start_agent(agent.id)
        print(f"✅ Agente iniciado: {success}")

        # Health check
        health = await agent_manager.health_check(agent.id)
        print(f"✅ Health check: {health.is_healthy}")

        # Para o gerenciador
        await agent_manager.stop()
        print("✅ Agent Service testado com sucesso!")

    except Exception as e:
        print(f"❌ Erro no Agent Service: {e}")


async def test_mlops():
    """Testa o sistema MLOps"""
    print("🧪 Testando MLOps...")

    try:
        # Inicializa o gerenciador de modelos
        model_manager = ModelManager()

        # Simula um modelo (usando um dict simples)
        mock_model = {"type": "test_model", "accuracy": 0.95}

        # Registra modelo
        version = await model_manager.register_model(
            name="test_model",
            model_type=ModelType.LSTM,
            model=mock_model,
            metadata={"accuracy": 0.95, "dataset": "test_data"},
        )

        print(f"✅ Modelo registrado: v{version}")

        # Lista modelos
        models = await model_manager.list_models()
        print(f"✅ Total de modelos: {len(models)}")

        # Carrega modelo
        loaded_model = await model_manager.load_model("test_model", version)
        print(f"✅ Modelo carregado: {loaded_model}")

        # Busca modelos
        search_results = await model_manager.search_models(
            name_pattern="test", model_type=ModelType.LSTM
        )
        print(f"✅ Resultados da busca: {len(search_results)}")

        print("✅ MLOps testado com sucesso!")

    except Exception as e:
        print(f"❌ Erro no MLOps: {e}")


async def test_integrations():
    """Testa as integrações externas"""
    print("🧪 Testando Integrações...")

    try:
        # Inicializa o gerenciador de APIs
        api_manager = ExternalAPIManager()
        await api_manager.start()

        # Registra uma API de teste
        api_config = APIConfig(
            name="test_api",
            api_type=APIType.WEATHER,
            base_url="https://api.test.com",
            api_key="test-key",
        )

        success = await api_manager.register_api(api_config)
        print(f"✅ API registrada: {success}")

        # Lista APIs
        apis = await api_manager.get_all_apis_status()
        print(f"✅ Total de APIs: {len(apis)}")

        # Health check
        health = await api_manager.health_check()
        print(f"✅ Health check: {health}")

        # Para o gerenciador
        await api_manager.stop()
        print("✅ Integrações testadas com sucesso!")

    except Exception as e:
        print(f"❌ Erro nas Integrações: {e}")


async def test_analytics():
    """Testa o sistema de analytics"""
    print("🧪 Testando Analytics...")

    try:
        # Inicializa o gerenciador de dashboards
        dashboard_manager = DashboardManager()
        await dashboard_manager.start()

        # Cria um dashboard
        dashboard = await dashboard_manager.create_dashboard(
            name="Test Dashboard",
            description="Dashboard de teste",
            dashboard_type=DashboardType.CUSTOM,
        )

        print(f"✅ Dashboard criado: {dashboard.id}")

        # Cria um widget
        widget = Widget(
            id="test_widget",
            title="Test Widget",
            widget_type=WidgetType.METRIC,
            data_source="test_source",
        )

        # Adiciona widget ao dashboard
        success = await dashboard_manager.add_widget(dashboard.id, widget)
        print(f"✅ Widget adicionado: {success}")

        # Lista dashboards
        dashboards = await dashboard_manager.list_dashboards()
        print(f"✅ Total de dashboards: {len(dashboards)}")

        # Obtém dados do widget
        widget_data = await dashboard_manager.get_widget_data(dashboard.id, widget.id)
        print(f"✅ Dados do widget: {widget_data is not None}")

        # Analytics do sistema
        analytics = await dashboard_manager.get_dashboard_analytics()
        print(f"✅ Analytics: {analytics}")

        # Para o gerenciador
        await dashboard_manager.stop()
        print("✅ Analytics testado com sucesso!")

    except Exception as e:
        print(f"❌ Erro no Analytics: {e}")


async def test_configuration():
    """Testa o sistema de configuração"""
    print("🧪 Testando Configuração...")

    try:
        # Testa configuração de desenvolvimento
        dev_config = get_config(Environment.DEVELOPMENT)
        print(f"✅ Config desenvolvimento: {dev_config.environment}")

        # Testa configuração de produção
        prod_config = get_config(Environment.PRODUCTION)
        print(f"✅ Config produção: {prod_config.environment}")

        # Verifica configurações específicas
        assert dev_config.database.pool_size == 5
        assert prod_config.database.pool_size == 20
        print("✅ Configurações específicas verificadas")

        print("✅ Configuração testada com sucesso!")

    except Exception as e:
        print(f"❌ Erro na Configuração: {e}")


async def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da versão 1.7...")
    print("=" * 50)

    # Executa testes
    await test_configuration()
    print()

    await test_agent_service()
    print()

    await test_mlops()
    print()

    await test_integrations()
    print()

    await test_analytics()
    print()

    print("=" * 50)
    print("🎉 Todos os testes concluídos!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
