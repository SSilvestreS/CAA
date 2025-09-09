//! Optimization module - Advanced optimization algorithms
//! 
//! Implements various optimization algorithms for:
//! - Traffic flow optimization
//! - Resource allocation
//! - Agent behavior optimization
//! - City planning optimization

use crate::agents::AgentEngine;
use std::collections::HashMap;

/// Main optimization engine
#[derive(Clone)]
pub struct OptimizationEngine {
    pub traffic_optimizer: TrafficOptimizer,
    pub resource_optimizer: ResourceOptimizer,
    pub behavior_optimizer: BehaviorOptimizer,
}

impl OptimizationEngine {
    /// Create new optimization engine
    pub fn new() -> Self {
        Self {
            traffic_optimizer: TrafficOptimizer::new(),
            resource_optimizer: ResourceOptimizer::new(),
            behavior_optimizer: BehaviorOptimizer::new(),
        }
    }
    
    /// Optimize traffic flow
    pub fn optimize_traffic(&mut self, agents: &mut AgentEngine) {
        self.traffic_optimizer.optimize(agents);
    }
    
    /// Optimize resource allocation
    pub fn optimize_resources(&mut self, agents: &mut AgentEngine) {
        self.resource_optimizer.optimize(agents);
    }
    
    /// Optimize agent behavior
    pub fn optimize_behavior(&mut self, agents: &mut AgentEngine) {
        self.behavior_optimizer.optimize(agents);
    }
}

/// Traffic flow optimization
#[derive(Clone)]
pub struct TrafficOptimizer {
    pub congestion_threshold: f64,
    pub optimization_strength: f64,
    pub path_cache: HashMap<(u32, u32), Vec<(f64, f64)>>,
}

impl TrafficOptimizer {
    pub fn new() -> Self {
        Self {
            congestion_threshold: 10.0, // Minimum distance between agents
            optimization_strength: 0.1,
            path_cache: HashMap::new(),
        }
    }
    
    /// Optimize traffic flow for all agents
    pub fn optimize(&mut self, agents: &mut AgentEngine) {
        // Get all agent positions
        let positions = agents.get_all_positions();
        
        // Calculate congestion levels
        let congestion_map = self.calculate_congestion(&positions);
        
        // Apply traffic optimization
        self.apply_traffic_optimization(agents, &congestion_map);
    }
    
    /// Calculate congestion levels in different areas
    fn calculate_congestion(&self, positions: &[(u32, nalgebra::Vector2<f64>)]) -> HashMap<(i32, i32), f64> {
        let mut congestion_map = HashMap::new();
        let grid_size = 50.0; // Same as physics grid
        
        for (id1, pos1) in positions {
            let grid_x = (pos1.x / grid_size) as i32;
            let grid_y = (pos1.y / grid_size) as i32;
            
            let mut local_congestion = 0.0;
            for (id2, pos2) in positions {
                if id1 != id2 {
                    let distance = (pos2 - pos1).magnitude();
                    if distance < 30.0 { // Local area
                        local_congestion += 1.0 / (distance + 1.0);
                    }
                }
            }
            
            *congestion_map.entry((grid_x, grid_y)).or_insert(0.0) += local_congestion;
        }
        
        congestion_map
    }
    
    /// Apply traffic optimization to reduce congestion
    fn apply_traffic_optimization(&mut self, agents: &mut AgentEngine, congestion_map: &HashMap<(i32, i32), f64>) {
        // Simple traffic optimization: redirect agents away from congested areas
        for citizen in agents.citizens.values_mut() {
            let grid_x = (citizen.position.x / 50.0) as i32;
            let grid_y = (citizen.position.y / 50.0) as i32;
            
            if let Some(&congestion) = congestion_map.get(&(grid_x, grid_y)) {
                if congestion > self.congestion_threshold {
                    // Redirect agent away from congestion
                    let avoidance_force = self.calculate_avoidance_force(citizen.position, congestion_map);
                    citizen.velocity += avoidance_force * self.optimization_strength;
                }
            }
        }
    }
    
    /// Calculate avoidance force to reduce congestion
    fn calculate_avoidance_force(&self, position: nalgebra::Vector2<f64>, congestion_map: &HashMap<(i32, i32), f64>) -> nalgebra::Vector2<f64> {
        let mut force = nalgebra::Vector2::new(0.0, 0.0);
        let grid_size = 50.0;
        
        // Check surrounding grid cells
        for dx in -1..=1 {
            for dy in -1..=1 {
                let grid_x = (position.x / grid_size) as i32 + dx;
                let grid_y = (position.y / grid_size) as i32 + dy;
                
                if let Some(&congestion) = congestion_map.get(&(grid_x, grid_y)) {
                    if congestion > self.congestion_threshold {
                        // Calculate direction away from congested area
                        let target_x = (grid_x as f64 + 0.5) * grid_size;
                        let target_y = (grid_y as f64 + 0.5) * grid_size;
                        let direction = position - nalgebra::Vector2::new(target_x, target_y);
                        let normalized_direction = direction.normalize();
                        
                        force += normalized_direction * congestion;
                    }
                }
            }
        }
        
        force.normalize() * 0.1 // Scale down the force
    }
}

/// Resource allocation optimization
#[derive(Clone)]
pub struct ResourceOptimizer {
    pub resource_efficiency: f64,
    pub redistribution_rate: f64,
}

impl ResourceOptimizer {
    pub fn new() -> Self {
        Self {
            resource_efficiency: 0.8,
            redistribution_rate: 0.1,
        }
    }
    
    /// Optimize resource allocation among agents
    pub fn optimize(&mut self, agents: &mut AgentEngine) {
        // Calculate total resources
        let total_energy = agents.get_average_energy() * agents.get_agent_count() as f64;
        
        // Redistribute resources based on need
        self.redistribute_energy(agents, total_energy);
        
        // Optimize business resource allocation
        self.optimize_business_resources(agents);
    }
    
    /// Redistribute energy among agents
    fn redistribute_energy(&self, agents: &mut AgentEngine, total_energy: f64) {
        let target_energy = total_energy / agents.get_agent_count() as f64;
        
        // Redistribute among citizens
        for citizen in agents.citizens.values_mut() {
            if citizen.energy < target_energy * 0.5 {
                citizen.energy += (target_energy - citizen.energy) * self.redistribution_rate;
            }
        }
        
        // Redistribute among businesses
        for business in agents.businesses.values_mut() {
            if business.energy < target_energy * 0.5 {
                business.energy += (target_energy - business.energy) * self.redistribution_rate;
            }
        }
    }
    
    /// Optimize business resource allocation
    fn optimize_business_resources(&self, agents: &mut AgentEngine) {
        // Calculate average business performance
        let mut total_revenue = 0.0;
        let mut business_count = 0;
        
        for business in agents.businesses.values() {
            total_revenue += business.revenue;
            business_count += 1;
        }
        
        if business_count > 0 {
            let avg_revenue = total_revenue / business_count as f64;
            
            // Optimize based on performance
            for business in agents.businesses.values_mut() {
                if business.revenue < avg_revenue * 0.5 {
                    // Boost underperforming businesses
                    business.energy += 5.0;
                } else if business.revenue > avg_revenue * 1.5 {
                    // Reduce overperforming businesses to balance
                    business.energy = (business.energy - 2.0).max(50.0);
                }
            }
        }
    }
}

/// Agent behavior optimization
#[derive(Clone)]
pub struct BehaviorOptimizer {
    pub learning_rate: f64,
    pub adaptation_threshold: f64,
}

impl BehaviorOptimizer {
    pub fn new() -> Self {
        Self {
            learning_rate: 0.01,
            adaptation_threshold: 0.1,
        }
    }
    
    /// Optimize agent behavior based on performance
    pub fn optimize(&mut self, agents: &mut AgentEngine) {
        // Optimize citizen behavior
        self.optimize_citizen_behavior(agents);
        
        // Optimize business behavior
        self.optimize_business_behavior(agents);
    }
    
    /// Optimize citizen behavior
    fn optimize_citizen_behavior(&self, agents: &mut AgentEngine) {
        for citizen in agents.citizens.values_mut() {
            // Adjust personality based on success
            if citizen.energy > 80.0 {
                // Successful citizen - increase risk tolerance slightly
                if let Some(risk_tolerance) = citizen.personality.get_mut("risk_tolerance") {
                    *risk_tolerance = (*risk_tolerance + self.learning_rate).min(1.0);
                }
            } else if citizen.energy < 20.0 {
                // Struggling citizen - decrease risk tolerance
                if let Some(risk_tolerance) = citizen.personality.get_mut("risk_tolerance") {
                    *risk_tolerance = (*risk_tolerance - self.learning_rate).max(0.0);
                }
            }
            
            // Update needs based on current state
            let energy_need = 1.0 - (citizen.energy / 100.0);
            citizen.needs.insert("energy".to_string(), energy_need);
            
            let social_need = citizen.personality.get("social_preference").unwrap_or(&0.5) * 0.8;
            citizen.needs.insert("social".to_string(), social_need);
        }
    }
    
    /// Optimize business behavior
    fn optimize_business_behavior(&self, agents: &mut AgentEngine) {
        for business in agents.businesses.values_mut() {
            // Adjust business strategy based on performance
            if business.revenue > 100.0 {
                // Successful business - increase customer focus
                business.customers = (business.customers + 1).min(1000);
            } else if business.revenue < 10.0 {
                // Struggling business - try to attract more customers
                business.customers = (business.customers + 2).min(1000);
            }
            
            // Update products based on demand
            let demand_factor = business.customers as f64 / 100.0;
            business.products.insert("demand".to_string(), demand_factor);
        }
    }
}
