//! Rust Engine for Autonomous Cities with AI Agents
//! 
//! High-performance simulation engine that integrates with Python via PyO3.
//! Provides critical performance improvements for agent simulation, physics,
//! and optimization algorithms.

use pyo3::prelude::*;
use std::collections::HashMap;
use serde::{Deserialize, Serialize};

// Re-export modules
pub mod simulation;
pub mod agents;
pub mod optimization;
pub mod utils;

use simulation::CityPhysics;
use agents::AgentEngine;
use optimization::OptimizationEngine;

/// Main simulation engine that coordinates all components
#[pyclass]
#[derive(Clone)]
pub struct RustSimulationEngine {
    pub physics: CityPhysics,
    pub agents: AgentEngine,
    pub optimization: OptimizationEngine,
    pub performance_metrics: PerformanceMetrics,
}

#[pymethods]
impl RustSimulationEngine {
    /// Create a new simulation engine
    #[new]
    pub fn new(width: f64, height: f64) -> Self {
        let physics = CityPhysics::new(width, height);
        let agents = AgentEngine::new();
        let optimization = OptimizationEngine::new();
        let performance_metrics = PerformanceMetrics::new();
        
        Self {
            physics,
            agents,
            optimization,
            performance_metrics,
        }
    }
    
    /// Add a citizen agent to the simulation
    pub fn add_citizen(&mut self, x: f64, y: f64, personality: HashMap<String, f64>) -> PyResult<u32> {
        let agent_id = self.agents.add_citizen(x, y, personality);
        Ok(agent_id)
    }
    
    /// Add a business agent to the simulation
    pub fn add_business(&mut self, x: f64, y: f64, business_type: String) -> PyResult<u32> {
        let agent_id = self.agents.add_business(x, y, business_type);
        Ok(agent_id)
    }
    
    /// Add a government agent to the simulation
    pub fn add_government(&mut self, x: f64, y: f64, policies: HashMap<String, f64>) -> PyResult<u32> {
        let agent_id = self.agents.add_government(x, y, policies);
        Ok(agent_id)
    }
    
    /// Update the simulation for one time step
    pub fn update_simulation(&mut self, delta_time: f64) -> PyResult<SimulationResult> {
        let start_time = std::time::Instant::now();
        
        // Update physics
        self.physics.update_physics(&mut self.agents, delta_time);
        
        // Process agent behaviors
        self.agents.process_cycle(delta_time);
        
        // Run optimizations
        self.optimization.optimize_traffic(&mut self.agents);
        self.optimization.optimize_resources(&mut self.agents);
        
        // Update performance metrics
        let update_time = start_time.elapsed();
        self.performance_metrics.update(update_time, self.agents.get_agent_count());
        
        Ok(SimulationResult {
            agents_updated: self.agents.get_agent_count(),
            interactions_calculated: self.agents.get_interaction_count(),
            performance_metrics: self.performance_metrics.clone(),
        })
    }
    
    /// Get current agent positions
    pub fn get_agent_positions(&self) -> PyResult<Vec<AgentPosition>> {
        Ok(self.agents.get_positions())
    }
    
    /// Get performance metrics
    pub fn get_performance_metrics(&self) -> PyResult<PerformanceMetrics> {
        Ok(self.performance_metrics.clone())
    }
    
    /// Get simulation statistics
    pub fn get_simulation_stats(&self) -> PyResult<SimulationStats> {
        Ok(SimulationStats {
            total_agents: self.agents.get_agent_count(),
            citizens: self.agents.get_citizen_count(),
            businesses: self.agents.get_business_count(),
            government: self.agents.get_government_count(),
            avg_energy: self.agents.get_average_energy(),
            city_width: self.physics.width,
            city_height: self.physics.height,
        })
    }
}

/// Performance metrics for monitoring
#[pyclass]
#[derive(Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub updates_per_second: f64,
    pub memory_usage_mb: f64,
    pub cpu_usage_percent: f64,
    pub total_updates: u64,
    pub avg_update_time_ms: f64,
}

impl PerformanceMetrics {
    pub fn new() -> Self {
        Self {
            updates_per_second: 0.0,
            memory_usage_mb: 0.0,
            cpu_usage_percent: 0.0,
            total_updates: 0,
            avg_update_time_ms: 0.0,
        }
    }
    
    pub fn update(&mut self, update_time: std::time::Duration, agent_count: u32) {
        self.total_updates += 1;
        let update_time_ms = update_time.as_secs_f64() * 1000.0;
        self.avg_update_time_ms = (self.avg_update_time_ms * (self.total_updates - 1) as f64 + update_time_ms) / self.total_updates as f64;
        self.updates_per_second = 1000.0 / update_time_ms;
        self.memory_usage_mb = agent_count as f64 * 0.1; // Simulated
        self.cpu_usage_percent = (update_time_ms * 10.0).min(100.0); // Simulated
    }
}

/// Result of a simulation update
#[pyclass]
#[derive(Clone, Serialize, Deserialize)]
pub struct SimulationResult {
    pub agents_updated: u32,
    pub interactions_calculated: u32,
    pub performance_metrics: PerformanceMetrics,
}

/// Agent position information
#[pyclass]
#[derive(Clone, Serialize, Deserialize)]
pub struct AgentPosition {
    pub id: u32,
    pub agent_type: String,
    pub x: f64,
    pub y: f64,
    pub energy: f64,
    pub velocity_x: f64,
    pub velocity_y: f64,
}

/// Simulation statistics
#[pyclass]
#[derive(Clone, Serialize, Deserialize)]
pub struct SimulationStats {
    pub total_agents: u32,
    pub citizens: u32,
    pub businesses: u32,
    pub government: u32,
    pub avg_energy: f64,
    pub city_width: f64,
    pub city_height: f64,
}

/// Initialize the Python module
#[pymodule]
fn rust_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustSimulationEngine>()?;
    m.add_class::<PerformanceMetrics>()?;
    m.add_class::<SimulationResult>()?;
    m.add_class::<AgentPosition>()?;
    m.add_class::<SimulationStats>()?;
    
    // Add version info
    m.add("__version__", "0.1.0")?;
    m.add("__author__", "Cidades Autônomas com Agentes de IA")?;
    
    Ok(())
}
