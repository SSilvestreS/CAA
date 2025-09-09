"""
Python wrapper for Rust simulation engine
Provides high-performance simulation capabilities with Python integration
"""

import sys
import os
from pathlib import Path

# Add the rust_engine to the path
current_dir = Path(__file__).parent
rust_engine_path = current_dir.parent
sys.path.insert(0, str(rust_engine_path))

try:
    # Try to import the Rust engine
    import rust_engine
    RUST_AVAILABLE = True
except ImportError:
    # Fallback to Python implementation
    RUST_AVAILABLE = False
    print("Warning: Rust engine not available, using Python fallback")

from .rust_simulation_wrapper import RustSimulationWrapper
from .performance_monitor import PerformanceMonitor
from .fallback_engine import FallbackSimulationEngine

# Export main classes
__all__ = [
    'RustSimulationWrapper',
    'PerformanceMonitor', 
    'FallbackSimulationEngine',
    'RUST_AVAILABLE'
]

# Version info
__version__ = "0.1.0"
__author__ = "Cidades Autônomas com Agentes de IA"
