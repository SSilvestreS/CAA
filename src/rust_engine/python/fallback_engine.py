"""
Fallback Simulation Engine
Python implementation that provides the same interface as Rust engine
Used when Rust engine is not available or fails to load
"""

import time
import random
import math
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FallbackSimulationEngine:
    """
    Python fallback implementation of the simulation engine
    Provides the same interface as Rust engine but with lower performance
    """
    
    def __init__(self, width: float, height: float):
        """Initialize fallback engine"""
        self.width = width
        self.height = height
        self.agents = {}
        self.next_id = 1
        self.performance_metrics = {
            'updates_per_second': 0.0,
            'memory_usage_mb': 0.0,
            'cpu_usage_percent': 0.0,
            'total_updates': 0,
            'avg_update_time_ms': 0.0,
        }
        self.interaction_count = 0
        
        logger.info("Fallback simulation engine initialized")
    
    def add_citizen(self, x: float, y: float, personality: Dict[str, float]) -> int:
        """Add a citizen agent"""
        agent_id = self.next_id
        self.next_id += 1
        
        self.agents[agent_id] = {
            'id': agent_id,
            'type': 'citizen',
            'x': x,
            'y': y,
            'velocity_x': 0.0,
            'velocity_y': 0.0,
            'energy': 100.0,
            'personality': personality.copy(),
            'needs': {},
            'decisions': [],
            'learning_data': [],
        }
        
        return agent_id
    
    def add_business(self, x: float, y: float, business_type: str) -> int:
        """Add a business agent"""
        agent_id = self.next_id
        self.next_id += 1
        
        self.agents[agent_id] = {
            'id': agent_id,
            'type': 'business',
            'x': x,
            'y': y,
            'velocity_x': 0.0,
            'velocity_y': 0.0,
            'energy': 100.0,
            'business_type': business_type,
            'revenue': 0.0,
            'customers': 0,
            'products': {},
        }
        
        return agent_id
    
    def add_government(self, x: float, y: float, policies: Dict[str, float]) -> int:
        """Add a government agent"""
        agent_id = self.next_id
        self.next_id += 1
        
        self.agents[agent_id] = {
            'id': agent_id,
            'type': 'government',
            'x': x,
            'y': y,
            'velocity_x': 0.0,
            'velocity_y': 0.0,
            'energy': 100.0,
            'policies': policies.copy(),
            'budget': 10000.0,
            'approval_rating': 0.5,
        }
        
        return agent_id
    
    def update_simulation(self, delta_time: float) -> Dict[str, Any]:
        """Update simulation for one time step"""
        start_time = time.time()
        
        # Update all agents
        self._update_agents(delta_time)
        
        # Handle collisions
        self._handle_collisions()
        
        # Calculate interactions
        self._calculate_interactions()
        
        # Update performance metrics
        update_time = time.time() - start_time
        self._update_performance_metrics(update_time)
        
        return {
            'agents_updated': len(self.agents),
            'interactions_calculated': self.interaction_count,
            'performance_metrics': self.performance_metrics.copy(),
        }
    
    def _update_agents(self, delta_time: float):
        """Update all agents"""
        for agent in self.agents.values():
            if agent['type'] == 'citizen':
                self._update_citizen(agent, delta_time)
            elif agent['type'] == 'business':
                self._update_business(agent, delta_time)
            elif agent['type'] == 'government':
                self._update_government(agent, delta_time)
    
    def _update_citizen(self, agent: Dict[str, Any], delta_time: float):
        """Update citizen agent"""
        # Update energy
        agent['energy'] = max(0.0, agent['energy'] - 0.1 * delta_time)
        
        # Get personality traits
        risk_tolerance = agent['personality'].get('risk_tolerance', 0.5)
        social_preference = agent['personality'].get('social_preference', 0.5)
        
        # Random movement based on personality
        move_x = (random.random() - 0.5) * 2.0 * risk_tolerance
        move_y = (random.random() - 0.5) * 2.0 * social_preference
        
        agent['velocity_x'] = move_x
        agent['velocity_y'] = move_y
        
        # Update position
        agent['x'] += agent['velocity_x'] * delta_time
        agent['y'] += agent['velocity_y'] * delta_time
        
        # Apply boundary constraints
        agent['x'] = max(0.0, min(self.width, agent['x']))
        agent['y'] = max(0.0, min(self.height, agent['y']))
        
        # Make decisions
        if random.random() < 0.1:
            decision = f"Decision based on risk_tolerance: {risk_tolerance:.2f}"
            agent['decisions'].append(decision)
        
        # Learn from experience
        if random.random() < 0.05:
            learning = random.random()
            agent['learning_data'].append(learning)
    
    def _update_business(self, agent: Dict[str, Any], delta_time: float):
        """Update business agent"""
        # Update energy
        agent['energy'] = max(0.0, agent['energy'] - 0.05 * delta_time)
        
        # Economic behavior
        agent['revenue'] += 1.0 * delta_time
        agent['customers'] = int(agent['customers'] + 0.1 * delta_time)
        
        # Simple movement
        move_x = (random.random() - 0.5) * 0.5
        move_y = (random.random() - 0.5) * 0.5
        
        agent['velocity_x'] = move_x
        agent['velocity_y'] = move_y
        
        # Update position
        agent['x'] += agent['velocity_x'] * delta_time
        agent['y'] += agent['velocity_y'] * delta_time
        
        # Apply boundary constraints
        agent['x'] = max(0.0, min(self.width, agent['x']))
        agent['y'] = max(0.0, min(self.height, agent['y']))
    
    def _update_government(self, agent: Dict[str, Any], delta_time: float):
        """Update government agent"""
        # Update energy
        agent['energy'] = max(0.0, agent['energy'] - 0.02 * delta_time)
        
        # Policy enforcement
        agent['budget'] += 10.0 * delta_time
        agent['approval_rating'] = min(1.0, agent['approval_rating'] + 0.001 * delta_time)
        
        # Minimal movement
        agent['velocity_x'] = 0.0
        agent['velocity_y'] = 0.0
    
    def _handle_collisions(self):
        """Handle collisions between agents"""
        collision_radius = 5.0
        agent_list = list(self.agents.values())
        
        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                agent1 = agent_list[i]
                agent2 = agent_list[j]
                
                distance = math.sqrt(
                    (agent2['x'] - agent1['x'])**2 + 
                    (agent2['y'] - agent1['y'])**2
                )
                
                if distance < collision_radius * 2.0:
                    # Separate agents
                    separation = (collision_radius * 2.0 - distance) / 2.0
                    dx = agent2['x'] - agent1['x']
                    dy = agent2['y'] - agent1['y']
                    
                    if distance > 0:
                        # Normalize direction
                        dx /= distance
                        dy /= distance
                        
                        # Apply separation
                        agent1['x'] -= dx * separation
                        agent1['y'] -= dy * separation
                        agent2['x'] += dx * separation
                        agent2['y'] += dy * separation
    
    def _calculate_interactions(self):
        """Calculate interactions between agents"""
        self.interaction_count = 0
        agent_list = list(self.agents.values())
        
        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                agent1 = agent_list[i]
                agent2 = agent_list[j]
                
                distance = math.sqrt(
                    (agent2['x'] - agent1['x'])**2 + 
                    (agent2['y'] - agent1['y'])**2
                )
                
                if distance < 20.0:  # Interaction radius
                    self.interaction_count += 1
    
    def _update_performance_metrics(self, update_time: float):
        """Update performance metrics"""
        self.performance_metrics['total_updates'] += 1
        update_time_ms = update_time * 1000.0
        
        # Calculate average update time
        total_updates = self.performance_metrics['total_updates']
        avg_time = self.performance_metrics['avg_update_time_ms']
        self.performance_metrics['avg_update_time_ms'] = (
            (avg_time * (total_updates - 1) + update_time_ms) / total_updates
        )
        
        # Calculate updates per second
        self.performance_metrics['updates_per_second'] = 1000.0 / update_time_ms
        
        # Simulate memory and CPU usage
        self.performance_metrics['memory_usage_mb'] = len(self.agents) * 0.1
        self.performance_metrics['cpu_usage_percent'] = min(100.0, update_time_ms * 10.0)
    
    def get_agent_positions(self) -> List[Dict[str, Any]]:
        """Get current agent positions"""
        return [
            {
                'id': agent['id'],
                'type': agent['type'],
                'x': agent['x'],
                'y': agent['y'],
                'energy': agent['energy'],
                'velocity_x': agent['velocity_x'],
                'velocity_y': agent['velocity_y'],
            }
            for agent in self.agents.values()
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        citizens = sum(1 for agent in self.agents.values() if agent['type'] == 'citizen')
        businesses = sum(1 for agent in self.agents.values() if agent['type'] == 'business')
        government = sum(1 for agent in self.agents.values() if agent['type'] == 'government')
        
        total_energy = sum(agent['energy'] for agent in self.agents.values())
        avg_energy = total_energy / len(self.agents) if self.agents else 0.0
        
        return {
            'total_agents': len(self.agents),
            'citizens': citizens,
            'businesses': businesses,
            'government': government,
            'avg_energy': avg_energy,
            'city_width': self.width,
            'city_height': self.height,
        }
    
    def get_agent_count(self) -> int:
        """Get total number of agents"""
        return len(self.agents)
    
    def get_citizen_count(self) -> int:
        """Get number of citizens"""
        return sum(1 for agent in self.agents.values() if agent['type'] == 'citizen')
    
    def get_business_count(self) -> int:
        """Get number of businesses"""
        return sum(1 for agent in self.agents.values() if agent['type'] == 'business')
    
    def get_government_count(self) -> int:
        """Get number of government agents"""
        return sum(1 for agent in self.agents.values() if agent['type'] == 'government')
