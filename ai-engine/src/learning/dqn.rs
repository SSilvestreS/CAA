//! Deep Q-Network (DQN) implementation for smart city agents
//! Version 1.2 - Advanced AI algorithms

use ndarray::{Array1, Array2, Array3, Axis};
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;
use tracing::{debug, info, warn};

/// Configuration for DQN
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DQNConfig {
    pub learning_rate: f64,
    pub gamma: f64,
    pub epsilon_start: f64,
    pub epsilon_end: f64,
    pub epsilon_decay: f64,
    pub batch_size: usize,
    pub memory_size: usize,
    pub target_update_frequency: usize,
    pub hidden_layers: Vec<usize>,
    pub input_size: usize,
    pub output_size: usize,
}

impl Default for DQNConfig {
    fn default() -> Self {
        Self {
            learning_rate: 0.001,
            gamma: 0.95,
            epsilon_start: 1.0,
            epsilon_end: 0.01,
            epsilon_decay: 0.995,
            batch_size: 32,
            memory_size: 10000,
            target_update_frequency: 100,
            hidden_layers: vec![128, 64, 32],
            input_size: 20,
            output_size: 10,
        }
    }
}

/// Experience for replay buffer
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Experience {
    pub state: Array1<f64>,
    pub action: usize,
    pub reward: f64,
    pub next_state: Array1<f64>,
    pub done: bool,
}

/// Neural Network layer
#[derive(Debug, Clone)]
pub struct Layer {
    weights: Array2<f64>,
    biases: Array1<f64>,
    activation: ActivationFunction,
}

#[derive(Debug, Clone)]
pub enum ActivationFunction {
    ReLU,
    Sigmoid,
    Tanh,
    Linear,
}

impl Layer {
    pub fn new(input_size: usize, output_size: usize, activation: ActivationFunction) -> Self {
        let mut rng = rand::thread_rng();
        let weights = Array2::from_shape_fn((output_size, input_size), |_| {
            rng.gen_range(-0.1..0.1)
        });
        let biases = Array1::zeros(output_size);

        Self {
            weights,
            biases,
            activation,
        }
    }

    pub fn forward(&self, input: &Array1<f64>) -> Array1<f64> {
        let output = &self.weights.dot(input) + &self.biases;
        self.activate(output)
    }

    fn activate(&self, input: &Array1<f64>) -> Array1<f64> {
        match &self.activation {
            ActivationFunction::ReLU => input.mapv(|x| if x > 0.0 { x } else { 0.0 }),
            ActivationFunction::Sigmoid => input.mapv(|x| 1.0 / (1.0 + (-x).exp())),
            ActivationFunction::Tanh => input.mapv(|x| x.tanh()),
            ActivationFunction::Linear => input.clone(),
        }
    }

    pub fn backward(&mut self, gradient: &Array1<f64>, learning_rate: f64) {
        // Simplified gradient descent update
        let weight_gradient = gradient.outer(&Array1::ones(self.weights.ncols()));
        self.weights = &self.weights - &(weight_gradient * learning_rate);
        self.biases = &self.biases - &(gradient * learning_rate);
    }
}

/// Deep Q-Network
pub struct DQN {
    config: DQNConfig,
    main_network: Vec<Layer>,
    target_network: Vec<Layer>,
    replay_buffer: VecDeque<Experience>,
    epsilon: f64,
    step_count: usize,
    rng: rand::rngs::ThreadRng,
}

impl DQN {
    pub fn new(config: DQNConfig) -> Self {
        let mut main_network = Vec::new();
        let mut target_network = Vec::new();

        // Build network layers
        let mut input_size = config.input_size;
        for &hidden_size in &config.hidden_layers {
            main_network.push(Layer::new(input_size, hidden_size, ActivationFunction::ReLU));
            target_network.push(Layer::new(input_size, hidden_size, ActivationFunction::ReLU));
            input_size = hidden_size;
        }
        
        // Output layer
        main_network.push(Layer::new(input_size, config.output_size, ActivationFunction::Linear));
        target_network.push(Layer::new(input_size, config.output_size, ActivationFunction::Linear));

        Self {
            config,
            main_network,
            target_network,
            replay_buffer: VecDeque::with_capacity(10000),
            epsilon: 1.0,
            step_count: 0,
            rng: rand::thread_rng(),
        }
    }

    /// Select action using epsilon-greedy policy
    pub fn select_action(&mut self, state: &Array1<f64>) -> usize {
        if self.rng.gen::<f64>() < self.epsilon {
            // Random action
            self.rng.gen_range(0..self.config.output_size)
        } else {
            // Greedy action
            self.get_q_values(state).argmax().unwrap()
        }
    }

    /// Get Q-values for given state
    pub fn get_q_values(&self, state: &Array1<f64>) -> Array1<f64> {
        let mut output = state.clone();
        for layer in &self.main_network {
            output = layer.forward(&output);
        }
        output
    }

    /// Store experience in replay buffer
    pub fn store_experience(&mut self, experience: Experience) {
        if self.replay_buffer.len() >= self.config.memory_size {
            self.replay_buffer.pop_front();
        }
        self.replay_buffer.push_back(experience);
    }

    /// Train the network on a batch of experiences
    pub fn train(&mut self) -> Result<f64, String> {
        if self.replay_buffer.len() < self.config.batch_size {
            return Ok(0.0);
        }

        // Sample batch
        let batch: Vec<Experience> = (0..self.config.batch_size)
            .map(|_| {
                let idx = self.rng.gen_range(0..self.replay_buffer.len());
                self.replay_buffer[idx].clone()
            })
            .collect();

        let mut total_loss = 0.0;

        for experience in &batch {
            // Current Q-values
            let current_q_values = self.get_q_values(&experience.state);
            let current_q = current_q_values[experience.action];

            // Target Q-values
            let target_q = if experience.done {
                experience.reward
            } else {
                let next_q_values = self.get_target_q_values(&experience.next_state);
                let max_next_q = next_q_values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
                experience.reward + self.config.gamma * max_next_q
            };

            // Calculate loss (simplified)
            let loss = (current_q - target_q).powi(2);
            total_loss += loss;

            // Update network (simplified backpropagation)
            self.update_network(&experience.state, experience.action, target_q);
        }

        // Update epsilon
        self.epsilon = (self.epsilon * self.config.epsilon_decay)
            .max(self.config.epsilon_end);

        // Update target network
        self.step_count += 1;
        if self.step_count % self.config.target_update_frequency == 0 {
            self.update_target_network();
            info!("Target network updated at step {}", self.step_count);
        }

        Ok(total_loss / self.config.batch_size as f64)
    }

    /// Get Q-values from target network
    fn get_target_q_values(&self, state: &Array1<f64>) -> Array1<f64> {
        let mut output = state.clone();
        for layer in &self.target_network {
            output = layer.forward(&output);
        }
        output
    }

    /// Update main network (simplified)
    fn update_network(&mut self, state: &Array1<f64>, action: usize, target: f64) {
        // Simplified gradient descent update
        let learning_rate = self.config.learning_rate;
        
        // Forward pass
        let mut activations = vec![state.clone()];
        let mut current = state.clone();
        
        for layer in &self.main_network {
            current = layer.forward(&current);
            activations.push(current.clone());
        }

        // Backward pass (simplified)
        let mut gradient = Array1::zeros(self.config.output_size);
        gradient[action] = target - activations.last().unwrap()[action];

        // Update layers
        for (i, layer) in self.main_network.iter_mut().enumerate().rev() {
            if i > 0 {
                layer.backward(&gradient, learning_rate);
            }
        }
    }

    /// Update target network with main network weights
    fn update_target_network(&mut self) {
        for (main_layer, target_layer) in self.main_network.iter().zip(self.target_network.iter_mut()) {
            target_layer.weights = main_layer.weights.clone();
            target_layer.biases = main_layer.biases.clone();
        }
    }

    /// Get current epsilon value
    pub fn get_epsilon(&self) -> f64 {
        self.epsilon
    }

    /// Get number of experiences in replay buffer
    pub fn get_memory_size(&self) -> usize {
        self.replay_buffer.len()
    }

    /// Save model to file
    pub fn save_model(&self, path: &str) -> Result<(), String> {
        let model_data = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(path, model_data).map_err(|e| e.to_string())?;
        info!("Model saved to {}", path);
        Ok(())
    }

    /// Load model from file
    pub fn load_model(path: &str) -> Result<Self, String> {
        let model_data = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        let model: Self = serde_json::from_str(&model_data).map_err(|e| e.to_string())?;
        info!("Model loaded from {}", path);
        Ok(model)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dqn_creation() {
        let config = DQNConfig::default();
        let dqn = DQN::new(config);
        assert_eq!(dqn.get_memory_size(), 0);
        assert_eq!(dqn.get_epsilon(), 1.0);
    }

    #[test]
    fn test_action_selection() {
        let config = DQNConfig::default();
        let mut dqn = DQN::new(config);
        let state = Array1::zeros(20);
        
        let action = dqn.select_action(&state);
        assert!(action < 10);
    }

    #[test]
    fn test_experience_storage() {
        let config = DQNConfig::default();
        let mut dqn = DQN::new(config);
        
        let experience = Experience {
            state: Array1::zeros(20),
            action: 0,
            reward: 1.0,
            next_state: Array1::zeros(20),
            done: false,
        };
        
        dqn.store_experience(experience);
        assert_eq!(dqn.get_memory_size(), 1);
    }
}
