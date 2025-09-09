//! Simulation module - City physics and environment
//! 
//! Handles the physical simulation of the city including:
//! - Agent movement and collisions
//! - Environmental factors
//! - Spatial queries and optimizations

use crate::agents::AgentEngine;
use nalgebra::Vector2;
use std::collections::HashMap;

/// City physics engine
#[derive(Clone)]
pub struct CityPhysics {
    pub width: f64,
    pub height: f64,
    pub gravity: f64,
    pub friction: f64,
    pub collision_radius: f64,
    pub spatial_grid: HashMap<(i32, i32), Vec<u32>>,
    pub grid_size: f64,
}

impl CityPhysics {
    /// Create new city physics engine
    pub fn new(width: f64, height: f64) -> Self {
        let grid_size = 50.0; // Grid cell size for spatial optimization
        Self {
            width,
            height,
            gravity: 0.0, // No gravity in 2D city simulation
            friction: 0.95, // Air resistance
            collision_radius: 5.0,
            spatial_grid: HashMap::new(),
            grid_size,
        }
    }
    
    /// Update physics for all agents
    pub fn update_physics(&mut self, agents: &mut AgentEngine, delta_time: f64) {
        // Clear spatial grid
        self.spatial_grid.clear();
        
        // Update agent positions and velocities
        agents.update_positions(delta_time);
        
        // Apply physics constraints
        self.apply_boundary_constraints(agents);
        
        // Handle collisions
        self.handle_collisions(agents);
        
        // Update spatial grid for next frame
        self.update_spatial_grid(agents);
    }
    
    /// Apply boundary constraints to keep agents within city bounds
    fn apply_boundary_constraints(&self, agents: &mut AgentEngine) {
        agents.apply_boundary_constraints(self.width, self.height);
    }
    
    /// Handle collisions between agents
    fn handle_collisions(&self, agents: &mut AgentEngine) {
        agents.handle_collisions(self.collision_radius);
    }
    
    /// Update spatial grid for efficient neighbor queries
    fn update_spatial_grid(&mut self, agents: &AgentEngine) {
        for (agent_id, position) in agents.get_all_positions() {
            let grid_x = (position.x / self.grid_size) as i32;
            let grid_y = (position.y / self.grid_size) as i32;
            self.spatial_grid.entry((grid_x, grid_y)).or_insert_with(Vec::new).push(agent_id);
        }
    }
    
    /// Get agents in a specific area (for spatial queries)
    pub fn get_agents_in_area(&self, x: f64, y: f64, radius: f64) -> Vec<u32> {
        let mut agents_in_area = Vec::new();
        let grid_radius = (radius / self.grid_size).ceil() as i32;
        let center_grid_x = (x / self.grid_size) as i32;
        let center_grid_y = (y / self.grid_size) as i32;
        
        for dx in -grid_radius..=grid_radius {
            for dy in -grid_radius..=grid_radius {
                let grid_x = center_grid_x + dx;
                let grid_y = center_grid_y + dy;
                
                if let Some(agent_ids) = self.spatial_grid.get(&(grid_x, grid_y)) {
                    for &agent_id in agent_ids {
                        agents_in_area.push(agent_id);
                    }
                }
            }
        }
        
        agents_in_area
    }
    
    /// Calculate distance between two points
    pub fn distance(&self, x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
        ((x2 - x1).powi(2) + (y2 - y1).powi(2)).sqrt()
    }
    
    /// Check if two agents are colliding
    pub fn are_colliding(&self, pos1: (f64, f64), pos2: (f64, f64)) -> bool {
        self.distance(pos1.0, pos1.1, pos2.0, pos2.1) < self.collision_radius * 2.0
    }
    
    /// Apply force to an agent
    pub fn apply_force(&self, velocity: &mut Vector2<f64>, force: Vector2<f64>, delta_time: f64) {
        *velocity += force * delta_time;
        *velocity *= self.friction; // Apply friction
    }
    
    /// Get city bounds
    pub fn get_bounds(&self) -> (f64, f64, f64, f64) {
        (0.0, 0.0, self.width, self.height)
    }
    
    /// Check if position is within city bounds
    pub fn is_within_bounds(&self, x: f64, y: f64) -> bool {
        x >= 0.0 && x < self.width && y >= 0.0 && y < self.height
    }
    
    /// Get random position within city bounds
    pub fn get_random_position(&self) -> (f64, f64) {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        (
            rng.gen_range(0.0..self.width),
            rng.gen_range(0.0..self.height),
        )
    }
}
