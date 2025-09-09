//! Agents module - AI agents for the simulation
//! 
//! Implements different types of agents:
//! - Citizens with personality and needs
//! - Businesses with economic behavior
//! - Government with policy enforcement

use std::collections::HashMap;
use nalgebra::Vector2;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Agent types in the simulation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AgentType {
    Citizen,
    Business,
    Government,
}

/// Citizen agent with personality and behavior
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Citizen {
    pub id: u32,
    pub position: Vector2<f64>,
    pub velocity: Vector2<f64>,
    pub energy: f64,
    pub personality: HashMap<String, f64>,
    pub needs: HashMap<String, f64>,
    pub decisions: Vec<String>,
    pub learning_data: Vec<f64>,
}

/// Business agent with economic behavior
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Business {
    pub id: u32,
    pub position: Vector2<f64>,
    pub velocity: Vector2<f64>,
    pub energy: f64,
    pub business_type: String,
    pub revenue: f64,
    pub customers: u32,
    pub products: HashMap<String, f64>,
}

/// Government agent with policy enforcement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Government {
    pub id: u32,
    pub position: Vector2<f64>,
    pub velocity: Vector2<f64>,
    pub energy: f64,
    pub policies: HashMap<String, f64>,
    pub budget: f64,
    pub approval_rating: f64,
}

/// Main agent engine that manages all agents
#[derive(Clone)]
pub struct AgentEngine {
    pub citizens: HashMap<u32, Citizen>,
    pub businesses: HashMap<u32, Business>,
    pub government: HashMap<u32, Government>,
    pub next_id: u32,
    pub interaction_count: u32,
}

impl AgentEngine {
    /// Create new agent engine
    pub fn new() -> Self {
        Self {
            citizens: HashMap::new(),
            businesses: HashMap::new(),
            government: HashMap::new(),
            next_id: 1,
            interaction_count: 0,
        }
    }
    
    /// Add a citizen agent
    pub fn add_citizen(&mut self, x: f64, y: f64, personality: HashMap<String, f64>) -> u32 {
        let id = self.next_id;
        self.next_id += 1;
        
        let citizen = Citizen {
            id,
            position: Vector2::new(x, y),
            velocity: Vector2::new(0.0, 0.0),
            energy: 100.0,
            personality,
            needs: HashMap::new(),
            decisions: Vec::new(),
            learning_data: Vec::new(),
        };
        
        self.citizens.insert(id, citizen);
        id
    }
    
    /// Add a business agent
    pub fn add_business(&mut self, x: f64, y: f64, business_type: String) -> u32 {
        let id = self.next_id;
        self.next_id += 1;
        
        let business = Business {
            id,
            position: Vector2::new(x, y),
            velocity: Vector2::new(0.0, 0.0),
            energy: 100.0,
            business_type,
            revenue: 0.0,
            customers: 0,
            products: HashMap::new(),
        };
        
        self.businesses.insert(id, business);
        id
    }
    
    /// Add a government agent
    pub fn add_government(&mut self, x: f64, y: f64, policies: HashMap<String, f64>) -> u32 {
        let id = self.next_id;
        self.next_id += 1;
        
        let government = Government {
            id,
            position: Vector2::new(x, y),
            velocity: Vector2::new(0.0, 0.0),
            energy: 100.0,
            policies,
            budget: 10000.0,
            approval_rating: 0.5,
        };
        
        self.government.insert(id, government);
        id
    }
    
    /// Process one cycle of agent behavior
    pub fn process_cycle(&mut self, delta_time: f64) {
        // Process citizens
        for citizen in self.citizens.values_mut() {
            self.process_citizen(citizen, delta_time);
        }
        
        // Process businesses
        for business in self.businesses.values_mut() {
            self.process_business(business, delta_time);
        }
        
        // Process government
        for government in self.government.values_mut() {
            self.process_government(government, delta_time);
        }
        
        // Calculate interactions
        self.calculate_interactions();
    }
    
    /// Process citizen behavior
    fn process_citizen(&mut self, citizen: &mut Citizen, delta_time: f64) {
        // Update energy
        citizen.energy = (citizen.energy - 0.1 * delta_time).max(0.0);
        
        // Simple movement based on personality
        let risk_tolerance = citizen.personality.get("risk_tolerance").unwrap_or(&0.5);
        let social_preference = citizen.personality.get("social_preference").unwrap_or(&0.5);
        
        // Random movement influenced by personality
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        let move_x = (rng.gen::<f64>() - 0.5) * 2.0 * risk_tolerance;
        let move_y = (rng.gen::<f64>() - 0.5) * 2.0 * social_preference;
        
        citizen.velocity = Vector2::new(move_x, move_y);
        
        // Make decisions based on personality
        if rng.gen::<f64>() < 0.1 {
            let decision = format!("Decision based on risk_tolerance: {:.2}", risk_tolerance);
            citizen.decisions.push(decision);
        }
        
        // Learn from experience
        if rng.gen::<f64>() < 0.05 {
            let learning = rng.gen::<f64>();
            citizen.learning_data.push(learning);
        }
    }
    
    /// Process business behavior
    fn process_business(&mut self, business: &mut Business, delta_time: f64) {
        // Update energy
        business.energy = (business.energy - 0.05 * delta_time).max(0.0);
        
        // Economic behavior
        business.revenue += 1.0 * delta_time;
        business.customers = (business.customers as f64 + 0.1 * delta_time) as u32;
        
        // Simple movement
        use rand::Rng;
        let mut rng = rand::thread_rng();
        
        let move_x = (rng.gen::<f64>() - 0.5) * 0.5;
        let move_y = (rng.gen::<f64>() - 0.5) * 0.5;
        
        business.velocity = Vector2::new(move_x, move_y);
    }
    
    /// Process government behavior
    fn process_government(&mut self, government: &mut Government, delta_time: f64) {
        // Update energy
        government.energy = (government.energy - 0.02 * delta_time).max(0.0);
        
        // Policy enforcement
        government.budget += 10.0 * delta_time;
        government.approval_rating = (government.approval_rating + 0.001 * delta_time).min(1.0);
        
        // Minimal movement
        government.velocity = Vector2::new(0.0, 0.0);
    }
    
    /// Update agent positions
    pub fn update_positions(&mut self, delta_time: f64) {
        // Update citizen positions
        for citizen in self.citizens.values_mut() {
            citizen.position += citizen.velocity * delta_time;
        }
        
        // Update business positions
        for business in self.businesses.values_mut() {
            business.position += business.velocity * delta_time;
        }
        
        // Update government positions
        for government in self.government.values_mut() {
            government.position += government.velocity * delta_time;
        }
    }
    
    /// Apply boundary constraints
    pub fn apply_boundary_constraints(&mut self, width: f64, height: f64) {
        // Constrain citizens
        for citizen in self.citizens.values_mut() {
            citizen.position.x = citizen.position.x.max(0.0).min(width);
            citizen.position.y = citizen.position.y.max(0.0).min(height);
        }
        
        // Constrain businesses
        for business in self.businesses.values_mut() {
            business.position.x = business.position.x.max(0.0).min(width);
            business.position.y = business.position.y.max(0.0).min(height);
        }
        
        // Constrain government
        for government in self.government.values_mut() {
            government.position.x = government.position.x.max(0.0).min(width);
            government.position.y = government.position.y.max(0.0).min(height);
        }
    }
    
    /// Handle collisions between agents
    pub fn handle_collisions(&mut self, collision_radius: f64) {
        // Simple collision handling - just separate overlapping agents
        let mut positions: Vec<(u32, Vector2<f64>)> = Vec::new();
        
        // Collect all positions
        for citizen in self.citizens.values() {
            positions.push((citizen.id, citizen.position));
        }
        for business in self.businesses.values() {
            positions.push((business.id, business.position));
        }
        for government in self.government.values() {
            positions.push((government.id, government.position));
        }
        
        // Check for collisions and separate
        for i in 0..positions.len() {
            for j in i+1..positions.len() {
                let (id1, pos1) = positions[i];
                let (id2, pos2) = positions[j];
                
                let distance = (pos2 - pos1).magnitude();
                if distance < collision_radius * 2.0 {
                    // Separate agents
                    let separation = (collision_radius * 2.0 - distance) / 2.0;
                    let direction = (pos2 - pos1).normalize();
                    
                    // Apply separation to both agents
                    if let Some(citizen) = self.citizens.get_mut(&id1) {
                        citizen.position -= direction * separation;
                    }
                    if let Some(business) = self.businesses.get_mut(&id1) {
                        business.position -= direction * separation;
                    }
                    if let Some(government) = self.government.get_mut(&id1) {
                        government.position -= direction * separation;
                    }
                    
                    if let Some(citizen) = self.citizens.get_mut(&id2) {
                        citizen.position += direction * separation;
                    }
                    if let Some(business) = self.businesses.get_mut(&id2) {
                        business.position += direction * separation;
                    }
                    if let Some(government) = self.government.get_mut(&id2) {
                        government.position += direction * separation;
                    }
                }
            }
        }
    }
    
    /// Calculate interactions between agents
    fn calculate_interactions(&mut self) {
        self.interaction_count = 0;
        
        // Count interactions between citizens and businesses
        for citizen in self.citizens.values() {
            for business in self.businesses.values() {
                let distance = (business.position - citizen.position).magnitude();
                if distance < 20.0 { // Interaction radius
                    self.interaction_count += 1;
                }
            }
        }
    }
    
    /// Get total number of agents
    pub fn get_agent_count(&self) -> u32 {
        self.citizens.len() as u32 + self.businesses.len() as u32 + self.government.len() as u32
    }
    
    /// Get number of citizens
    pub fn get_citizen_count(&self) -> u32 {
        self.citizens.len() as u32
    }
    
    /// Get number of businesses
    pub fn get_business_count(&self) -> u32 {
        self.businesses.len() as u32
    }
    
    /// Get number of government agents
    pub fn get_government_count(&self) -> u32 {
        self.government.len() as u32
    }
    
    /// Get interaction count
    pub fn get_interaction_count(&self) -> u32 {
        self.interaction_count
    }
    
    /// Get average energy of all agents
    pub fn get_average_energy(&self) -> f64 {
        let mut total_energy = 0.0;
        let mut count = 0;
        
        for citizen in self.citizens.values() {
            total_energy += citizen.energy;
            count += 1;
        }
        for business in self.businesses.values() {
            total_energy += business.energy;
            count += 1;
        }
        for government in self.government.values() {
            total_energy += government.energy;
            count += 1;
        }
        
        if count > 0 {
            total_energy / count as f64
        } else {
            0.0
        }
    }
    
    /// Get all agent positions
    pub fn get_all_positions(&self) -> Vec<(u32, Vector2<f64>)> {
        let mut positions = Vec::new();
        
        for citizen in self.citizens.values() {
            positions.push((citizen.id, citizen.position));
        }
        for business in self.businesses.values() {
            positions.push((business.id, business.position));
        }
        for government in self.government.values() {
            positions.push((government.id, government.position));
        }
        
        positions
    }
    
    /// Get agent positions for Python
    pub fn get_positions(&self) -> Vec<crate::AgentPosition> {
        let mut positions = Vec::new();
        
        for citizen in self.citizens.values() {
            positions.push(crate::AgentPosition {
                id: citizen.id,
                agent_type: "citizen".to_string(),
                x: citizen.position.x,
                y: citizen.position.y,
                energy: citizen.energy,
                velocity_x: citizen.velocity.x,
                velocity_y: citizen.velocity.y,
            });
        }
        
        for business in self.businesses.values() {
            positions.push(crate::AgentPosition {
                id: business.id,
                agent_type: "business".to_string(),
                x: business.position.x,
                y: business.position.y,
                energy: business.energy,
                velocity_x: business.velocity.x,
                velocity_y: business.velocity.y,
            });
        }
        
        for government in self.government.values() {
            positions.push(crate::AgentPosition {
                id: government.id,
                agent_type: "government".to_string(),
                x: government.position.x,
                y: government.position.y,
                energy: government.energy,
                velocity_x: government.velocity.x,
                velocity_y: government.velocity.y,
            });
        }
        
        positions
    }
}
