"""
Rust Simulation Wrapper
High-performance simulation wrapper that integrates Rust engine with Python
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import logging

# Try to import Rust engine, fallback to Python if not available
try:
    import rust_engine
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    rust_engine = None

from .fallback_engine import FallbackSimulationEngine

logger = logging.getLogger(__name__)


class RustSimulationWrapper:
    """
    High-performance simulation wrapper that uses Rust engine when available,
    with automatic fallback to Python implementation.
    """
    
    def __init__(self, width: float, height: float, use_rust: bool = True):
        """
        Initialize simulation wrapper
        
        Args:
            width: City width
            height: City height  
            use_rust: Whether to use Rust engine (if available)
        """
        self.width = width
        self.height = height
        self.use_rust = use_rust and RUST_AVAILABLE
        
        if self.use_rust and RUST_AVAILABLE:
            try:
                logger.info("Initializing Rust simulation engine")
                self.rust_engine = rust_engine.RustSimulationEngine(width, height)
                self.fallback_engine = None
            except Exception as e:
                logger.warning(f"Failed to initialize Rust engine: {e}, falling back to Python")
                self.use_rust = False
                self.rust_engine = None
                self.fallback_engine = FallbackSimulationEngine(width, height)
        else:
            logger.info("Using Python fallback engine")
            self.rust_engine = None
            self.fallback_engine = FallbackSimulationEngine(width, height)
        
        self.performance_metrics = {
            'total_updates': 0,
            'avg_update_time_ms': 0.0,
            'total_simulation_time': 0.0,
            'rust_engine_used': self.use_rust,
        }
    
    def add_citizen(self, x: float, y: float, personality: Dict[str, float]) -> int:
        """Add a citizen agent to the simulation"""
        if self.use_rust:
            return self.rust_engine.add_citizen(x, y, personality)
        else:
            return self.fallback_engine.add_citizen(x, y, personality)
    
    def add_business(self, x: float, y: float, business_type: str) -> int:
        """Add a business agent to the simulation"""
        if self.use_rust:
            return self.rust_engine.add_business(x, y, business_type)
        else:
            return self.fallback_engine.add_business(x, y, business_type)
    
    def add_government(self, x: float, y: float, policies: Dict[str, float]) -> int:
        """Add a government agent to the simulation"""
        if self.use_rust:
            return self.rust_engine.add_government(x, y, policies)
        else:
            return self.fallback_engine.add_government(x, y, policies)
    
    def update_simulation(self, delta_time: float = 0.1) -> Dict[str, Any]:
        """Update the simulation for one time step"""
        start_time = time.time()
        
        if self.use_rust:
            result = self.rust_engine.update_simulation(delta_time)
            # Convert Rust result to Python dict
            simulation_result = {
                'agents_updated': result.agents_updated,
                'interactions_calculated': result.interactions_calculated,
                'performance_metrics': {
                    'updates_per_second': result.performance_metrics.updates_per_second,
                    'memory_usage_mb': result.performance_metrics.memory_usage_mb,
                    'cpu_usage_percent': result.performance_metrics.cpu_usage_percent,
                    'total_updates': result.performance_metrics.total_updates,
                    'avg_update_time_ms': result.performance_metrics.avg_update_time_ms,
                }
            }
        else:
            simulation_result = self.fallback_engine.update_simulation(delta_time)
        
        # Update performance metrics
        update_time = time.time() - start_time
        self._update_performance_metrics(update_time)
        
        return simulation_result
    
    async def update_simulation_async(self, delta_time: float = 0.1) -> Dict[str, Any]:
        """Asynchronous version of update_simulation"""
        # Run simulation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.update_simulation, delta_time)
    
    def get_agent_positions(self) -> List[Dict[str, Any]]:
        """Get current positions of all agents"""
        if self.use_rust:
            positions = self.rust_engine.get_agent_positions()
            return [
                {
                    'id': pos.id,
                    'type': pos.agent_type,
                    'x': pos.x,
                    'y': pos.y,
                    'energy': pos.energy,
                    'velocity_x': pos.velocity_x,
                    'velocity_y': pos.velocity_y,
                }
                for pos in positions
            ]
        else:
            return self.fallback_engine.get_agent_positions()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if self.use_rust:
            metrics = self.rust_engine.get_performance_metrics()
            return {
                'updates_per_second': metrics.updates_per_second,
                'memory_usage_mb': metrics.memory_usage_mb,
                'cpu_usage_percent': metrics.cpu_usage_percent,
                'total_updates': metrics.total_updates,
                'avg_update_time_ms': metrics.avg_update_time_ms,
            }
        else:
            return self.fallback_engine.get_performance_metrics()
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        if self.use_rust:
            stats = self.rust_engine.get_simulation_stats()
            return {
                'total_agents': stats.total_agents,
                'citizens': stats.citizens,
                'businesses': stats.businesses,
                'government': stats.government,
                'avg_energy': stats.avg_energy,
                'city_width': stats.city_width,
                'city_height': stats.city_height,
            }
        else:
            return self.fallback_engine.get_simulation_stats()
    
    def get_agent_count(self) -> int:
        """Get total number of agents"""
        if self.use_rust:
            stats = self.rust_engine.get_simulation_stats()
            return stats.total_agents
        else:
            return self.fallback_engine.get_agent_count()
    
    def get_citizen_count(self) -> int:
        """Get number of citizens"""
        if self.use_rust:
            stats = self.rust_engine.get_simulation_stats()
            return stats.citizens
        else:
            return self.fallback_engine.get_citizen_count()
    
    def get_business_count(self) -> int:
        """Get number of businesses"""
        if self.use_rust:
            stats = self.rust_engine.get_simulation_stats()
            return stats.businesses
        else:
            return self.fallback_engine.get_business_count()
    
    def get_government_count(self) -> int:
        """Get number of government agents"""
        if self.use_rust:
            stats = self.rust_engine.get_simulation_stats()
            return stats.government
        else:
            return self.fallback_engine.get_government_count()
    
    def _update_performance_metrics(self, update_time: float):
        """Update internal performance metrics"""
        self.performance_metrics['total_updates'] += 1
        self.performance_metrics['total_simulation_time'] += update_time
        
        # Calculate average update time
        total_updates = self.performance_metrics['total_updates']
        total_time = self.performance_metrics['total_simulation_time']
        self.performance_metrics['avg_update_time_ms'] = (total_time / total_updates) * 1000
    
    def switch_to_fallback(self):
        """Switch to Python fallback engine"""
        if self.use_rust:
            logger.warning("Switching to Python fallback engine")
            self.use_rust = False
            self.fallback_engine = FallbackSimulationEngine(self.width, self.height)
            self.performance_metrics['rust_engine_used'] = False
    
    def switch_to_rust(self):
        """Switch to Rust engine (if available)"""
        if RUST_AVAILABLE and not self.use_rust:
            logger.info("Switching to Rust engine")
            self.use_rust = True
            self.rust_engine = rust_engine.RustSimulationEngine(self.width, self.height)
            self.fallback_engine = None
            self.performance_metrics['rust_engine_used'] = True
        elif not RUST_AVAILABLE:
            logger.warning("Rust engine not available, staying with Python fallback")
    
    def is_using_rust(self) -> bool:
        """Check if currently using Rust engine"""
        return self.use_rust
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the current engine"""
        return {
            'rust_available': RUST_AVAILABLE,
            'using_rust': self.use_rust,
            'engine_type': 'Rust' if self.use_rust else 'Python',
            'performance_metrics': self.performance_metrics,
        }
