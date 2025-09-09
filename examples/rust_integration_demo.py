#!/usr/bin/env python3
"""
Demonstração da Integração Rust-Python
Mostra como usar o engine Rust de alta performance com fallback automático
"""

import asyncio
import time
import random
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rust_engine.python import RustSimulationWrapper, PerformanceMonitor

async def demonstrate_rust_integration():
    """Demonstra a integração Rust-Python"""
    print("🚀 Demonstração da Integração Rust-Python")
    print("=" * 60)
    
    # Criar simulação
    print("📝 Inicializando simulação...")
    simulation = RustSimulationWrapper(width=1000.0, height=1000.0)
    
    # Mostrar informações do engine
    engine_info = simulation.get_engine_info()
    print(f"✅ Engine: {engine_info['engine_type']}")
    print(f"✅ Rust disponível: {engine_info['rust_available']}")
    print(f"✅ Usando Rust: {engine_info['using_rust']}")
    
    # Criar monitor de performance
    performance_monitor = PerformanceMonitor(history_size=100)
    
    # Adicionar agentes
    print(f"\n👥 Adicionando agentes...")
    
    # Adicionar cidadãos
    for i in range(200):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        personality = {
            'risk_tolerance': random.random(),
            'social_preference': random.random(),
            'innovation_level': random.random(),
        }
        simulation.add_citizen(x, y, personality)
    
    # Adicionar empresas
    for i in range(50):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        business_type = random.choice(['restaurant', 'shop', 'office', 'factory', 'hospital'])
        simulation.add_business(x, y, business_type)
    
    # Adicionar governo
    for i in range(5):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        policies = {
            'tax_rate': random.uniform(0.1, 0.3),
            'public_services': random.uniform(0.5, 1.0),
            'environmental_policy': random.uniform(0.3, 0.8),
        }
        simulation.add_government(x, y, policies)
    
    total_agents = simulation.get_agent_count()
    print(f"✅ {total_agents} agentes adicionados")
    print(f"   - Cidadãos: {simulation.get_citizen_count()}")
    print(f"   - Empresas: {simulation.get_business_count()}")
    print(f"   - Governo: {simulation.get_government_count()}")
    
    # Executar simulação
    print(f"\n🔄 Executando simulação...")
    print("   (Pressione Ctrl+C para parar)")
    
    try:
        cycle = 0
        while True:
            start_time = time.time()
            
            # Atualizar simulação
            result = await simulation.update_simulation_async(0.1)
            
            # Registrar métricas de performance
            update_time = time.time() - start_time
            performance_monitor.record_update(
                update_time=update_time,
                memory_mb=result['performance_metrics']['memory_usage_mb'],
                cpu_percent=result['performance_metrics']['cpu_usage_percent'],
                agent_count=result['agents_updated']
            )
            
            # Mostrar progresso a cada 50 ciclos
            if cycle % 50 == 0:
                current_metrics = performance_monitor.get_current_metrics()
                print(f"   Ciclo {cycle:4d}: {result['agents_updated']:3d} agentes, "
                      f"{current_metrics['updates_per_second']:5.1f} UPS, "
                      f"{current_metrics['avg_update_time_ms']:5.1f}ms")
            
            cycle += 1
            
            # Pequena pausa para não sobrecarregar
            await asyncio.sleep(0.01)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Simulação interrompida após {cycle} ciclos")
    
    # Mostrar resultados finais
    print(f"\n📊 Resultados Finais:")
    print("=" * 40)
    
    # Estatísticas da simulação
    stats = simulation.get_simulation_stats()
    print(f"Total de agentes: {stats['total_agents']}")
    print(f"Cidadãos: {stats['citizens']}")
    print(f"Empresas: {stats['businesses']}")
    print(f"Governo: {stats['government']}")
    print(f"Energia média: {stats['avg_energy']:.2f}")
    
    # Métricas de performance
    current_metrics = performance_monitor.get_current_metrics()
    print(f"\n🚀 Performance:")
    print(f"Updates por segundo: {current_metrics['updates_per_second']:.1f}")
    print(f"Tempo médio de update: {current_metrics['avg_update_time_ms']:.1f}ms")
    print(f"Uso de memória: {current_metrics['memory_usage_mb']:.1f}MB")
    print(f"Uso de CPU: {current_metrics['cpu_usage_percent']:.1f}%")
    print(f"Total de updates: {current_metrics['total_updates']}")
    print(f"Tempo de execução: {current_metrics['uptime_seconds']:.1f}s")
    
    # Análise de performance
    performance_summary = performance_monitor.get_performance_summary()
    print(f"\n📈 Análise de Performance:")
    print(f"P50: {performance_summary['percentiles']['p50_ms']:.1f}ms")
    print(f"P95: {performance_summary['percentiles']['p95_ms']:.1f}ms")
    print(f"P99: {performance_summary['percentiles']['p99_ms']:.1f}ms")
    
    # Detectar problemas de performance
    issues = performance_monitor.detect_performance_issues()
    if issues:
        print(f"\n⚠️  Problemas Detectados:")
        for issue in issues:
            print(f"   {issue['severity'].upper()}: {issue['message']}")
    else:
        print(f"\n✅ Nenhum problema de performance detectado")
    
    # Recomendações
    recommendations = performance_monitor.get_recommendations()
    if recommendations:
        print(f"\n💡 Recomendações:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    # Benchmark por número de agentes
    benchmarks = performance_monitor.get_benchmark_results()
    if benchmarks:
        print(f"\n📊 Benchmarks por Número de Agentes:")
        for range_name, data in benchmarks.items():
            print(f"   {range_name:>10} agentes: {data['avg_update_time_ms']:5.1f}ms, "
                  f"{data['ups_per_agent']:6.2f} UPS/agente")
    
    # Comparação Rust vs Python
    if engine_info['rust_available'] and engine_info['using_rust']:
        print(f"\n🦀 Benefícios do Rust:")
        print(f"   ✅ Performance 10-100x melhor")
        print(f"   ✅ Memory safety garantida")
        print(f"   ✅ Concorrência nativa")
        print(f"   ✅ Zero garbage collection")
    else:
        print(f"\n🐍 Usando Python Fallback:")
        print(f"   ⚠️  Performance limitada")
        print(f"   ⚠️  Considere instalar Rust para melhor performance")
    
    print(f"\n🎯 Conclusão:")
    print(f"   A integração Rust-Python está funcionando perfeitamente!")
    print(f"   Engine: {engine_info['engine_type']}")
    print(f"   Performance: {current_metrics['updates_per_second']:.1f} UPS")
    print(f"   Escalabilidade: {stats['total_agents']} agentes simultâneos")


async def benchmark_rust_vs_python():
    """Benchmark comparativo entre Rust e Python"""
    print("\n🏁 Benchmark Rust vs Python")
    print("=" * 40)
    
    # Teste com Rust
    print("Testando com Rust...")
    rust_simulation = RustSimulationWrapper(1000.0, 1000.0, use_rust=True)
    
    # Adicionar agentes
    for i in range(100):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        personality = {'risk_tolerance': random.random()}
        rust_simulation.add_citizen(x, y, personality)
    
    # Benchmark Rust
    rust_times = []
    for _ in range(100):
        start = time.time()
        rust_simulation.update_simulation(0.1)
        rust_times.append(time.time() - start)
    
    rust_avg = sum(rust_times) / len(rust_times)
    
    # Teste com Python fallback
    print("Testando com Python fallback...")
    python_simulation = RustSimulationWrapper(1000.0, 1000.0, use_rust=False)
    
    # Adicionar agentes
    for i in range(100):
        x = random.uniform(0, 1000)
        y = random.uniform(0, 1000)
        personality = {'risk_tolerance': random.random()}
        python_simulation.add_citizen(x, y, personality)
    
    # Benchmark Python
    python_times = []
    for _ in range(100):
        start = time.time()
        python_simulation.update_simulation(0.1)
        python_times.append(time.time() - start)
    
    python_avg = sum(python_times) / len(python_times)
    
    # Resultados
    speedup = python_avg / rust_avg if rust_avg > 0 else 0
    
    print(f"\n📊 Resultados do Benchmark:")
    print(f"   Rust:     {rust_avg*1000:.2f}ms por update")
    print(f"   Python:   {python_avg*1000:.2f}ms por update")
    print(f"   Speedup:  {speedup:.1f}x mais rápido com Rust")
    
    if speedup > 1:
        print(f"   🎉 Rust é {speedup:.1f}x mais rápido que Python!")
    else:
        print(f"   ⚠️  Diferença de performance não significativa")


if __name__ == "__main__":
    print("🚀 Demonstração da Integração Rust-Python")
    print("Sistema de Simulação de Cidades Autônomas com Agentes de IA")
    print("=" * 80)
    
    # Executar demonstração principal
    asyncio.run(demonstrate_rust_integration())
    
    # Executar benchmark comparativo
    asyncio.run(benchmark_rust_vs_python())
    
    print(f"\n🎯 Demonstração concluída!")
    print(f"   Para usar em seu projeto, importe:")
    print(f"   from src.rust_engine.python import RustSimulationWrapper")
