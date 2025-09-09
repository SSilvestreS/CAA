//! Utilities module - Common utilities and helper functions
//! 
//! Provides utility functions for:
//! - Mathematical operations
//! - Data structures
//! - Performance monitoring
//! - Random number generation

use std::collections::HashMap;
use nalgebra::Vector2;
use rand::Rng;

/// Mathematical utilities
pub mod math {
    use super::*;
    
    /// Calculate distance between two points
    pub fn distance(x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
        ((x2 - x1).powi(2) + (y2 - y1).powi(2)).sqrt()
    }
    
    /// Calculate distance between two vectors
    pub fn distance_vec(v1: Vector2<f64>, v2: Vector2<f64>) -> f64 {
        (v2 - v1).magnitude()
    }
    
    /// Clamp value between min and max
    pub fn clamp(value: f64, min: f64, max: f64) -> f64 {
        value.max(min).min(max)
    }
    
    /// Linear interpolation between two values
    pub fn lerp(a: f64, b: f64, t: f64) -> f64 {
        a + (b - a) * t.clamp(0.0, 1.0)
    }
    
    /// Smooth step interpolation
    pub fn smoothstep(edge0: f64, edge1: f64, x: f64) -> f64 {
        let t = ((x - edge0) / (edge1 - edge0)).clamp(0.0, 1.0);
        t * t * (3.0 - 2.0 * t)
    }
    
    /// Normalize angle to [-π, π]
    pub fn normalize_angle(angle: f64) -> f64 {
        let two_pi = 2.0 * std::f64::consts::PI;
        angle - two_pi * (angle / two_pi).floor()
    }
    
    /// Convert degrees to radians
    pub fn deg_to_rad(degrees: f64) -> f64 {
        degrees * std::f64::consts::PI / 180.0
    }
    
    /// Convert radians to degrees
    pub fn rad_to_deg(radians: f64) -> f64 {
        radians * 180.0 / std::f64::consts::PI
    }
}

/// Random number generation utilities
pub mod random {
    use super::*;
    
    /// Generate random float between 0 and 1
    pub fn random_float() -> f64 {
        rand::thread_rng().gen::<f64>()
    }
    
    /// Generate random float between min and max
    pub fn random_range(min: f64, max: f64) -> f64 {
        rand::thread_rng().gen_range(min..max)
    }
    
    /// Generate random integer between min and max (inclusive)
    pub fn random_int(min: i32, max: i32) -> i32 {
        rand::thread_rng().gen_range(min..=max)
    }
    
    /// Generate random boolean
    pub fn random_bool() -> bool {
        rand::thread_rng().gen::<bool>()
    }
    
    /// Generate random vector within circle
    pub fn random_vector_in_circle(radius: f64) -> Vector2<f64> {
        let angle = random_range(0.0, 2.0 * std::f64::consts::PI);
        let distance = random_range(0.0, radius);
        
        Vector2::new(
            angle.cos() * distance,
            angle.sin() * distance,
        )
    }
    
    /// Generate random vector within rectangle
    pub fn random_vector_in_rect(width: f64, height: f64) -> Vector2<f64> {
        Vector2::new(
            random_range(0.0, width),
            random_range(0.0, height),
        )
    }
    
    /// Choose random element from slice
    pub fn random_choice<T>(items: &[T]) -> Option<&T> {
        if items.is_empty() {
            None
        } else {
            let index = random_int(0, items.len() as i32 - 1) as usize;
            Some(&items[index])
        }
    }
    
    /// Shuffle vector in place
    pub fn shuffle<T>(vec: &mut Vec<T>) {
        use rand::seq::SliceRandom;
        vec.shuffle(&mut rand::thread_rng());
    }
}

/// Data structure utilities
pub mod data_structures {
    use super::*;
    
    /// Circular buffer for storing recent values
    pub struct CircularBuffer<T> {
        buffer: Vec<T>,
        head: usize,
        size: usize,
        capacity: usize,
    }
    
    impl<T: Clone> CircularBuffer<T> {
        pub fn new(capacity: usize) -> Self {
            Self {
                buffer: Vec::with_capacity(capacity),
                head: 0,
                size: 0,
                capacity,
            }
        }
        
        pub fn push(&mut self, item: T) {
            if self.size < self.capacity {
                self.buffer.push(item);
                self.size += 1;
            } else {
                self.buffer[self.head] = item;
                self.head = (self.head + 1) % self.capacity;
            }
        }
        
        pub fn get(&self, index: usize) -> Option<&T> {
            if index >= self.size {
                None
            } else {
                let actual_index = (self.head + index) % self.capacity;
                self.buffer.get(actual_index)
            }
        }
        
        pub fn len(&self) -> usize {
            self.size
        }
        
        pub fn is_empty(&self) -> bool {
            self.size == 0
        }
        
        pub fn iter(&self) -> CircularBufferIterator<T> {
            CircularBufferIterator {
                buffer: self,
                index: 0,
            }
        }
    }
    
    pub struct CircularBufferIterator<'a, T> {
        buffer: &'a CircularBuffer<T>,
        index: usize,
    }
    
    impl<'a, T> Iterator for CircularBufferIterator<'a, T> {
        type Item = &'a T;
        
        fn next(&mut self) -> Option<Self::Item> {
            if self.index < self.buffer.size {
                let item = self.buffer.get(self.index);
                self.index += 1;
                item
            } else {
                None
            }
        }
    }
    
    /// Priority queue for efficient priority-based operations
    pub struct PriorityQueue<T> {
        items: Vec<(f64, T)>, // (priority, item)
    }
    
    impl<T: Clone> PriorityQueue<T> {
        pub fn new() -> Self {
            Self {
                items: Vec::new(),
            }
        }
        
        pub fn push(&mut self, item: T, priority: f64) {
            self.items.push((priority, item));
            self.items.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
        }
        
        pub fn pop(&mut self) -> Option<T> {
            self.items.pop().map(|(_, item)| item)
        }
        
        pub fn peek(&self) -> Option<&T> {
            self.items.last().map(|(_, item)| item)
        }
        
        pub fn len(&self) -> usize {
            self.items.len()
        }
        
        pub fn is_empty(&self) -> bool {
            self.items.is_empty()
        }
    }
}

/// Performance monitoring utilities
pub mod performance {
    use std::time::Instant;
    
    /// Simple timer for measuring execution time
    pub struct Timer {
        start_time: Option<Instant>,
    }
    
    impl Timer {
        pub fn new() -> Self {
            Self {
                start_time: None,
            }
        }
        
        pub fn start(&mut self) {
            self.start_time = Some(Instant::now());
        }
        
        pub fn stop(&mut self) -> Option<std::time::Duration> {
            self.start_time.take().map(|start| start.elapsed())
        }
        
        pub fn elapsed(&self) -> Option<std::time::Duration> {
            self.start_time.map(|start| start.elapsed())
        }
    }
    
    /// Performance counter for tracking metrics
    pub struct PerformanceCounter {
        count: u64,
        total_time: std::time::Duration,
        min_time: Option<std::time::Duration>,
        max_time: Option<std::time::Duration>,
    }
    
    impl PerformanceCounter {
        pub fn new() -> Self {
            Self {
                count: 0,
                total_time: std::time::Duration::ZERO,
                min_time: None,
                max_time: None,
            }
        }
        
        pub fn record(&mut self, duration: std::time::Duration) {
            self.count += 1;
            self.total_time += duration;
            
            self.min_time = Some(match self.min_time {
                Some(min) => min.min(duration),
                None => duration,
            });
            
            self.max_time = Some(match self.max_time {
                Some(max) => max.max(duration),
                None => duration,
            });
        }
        
        pub fn average_time(&self) -> std::time::Duration {
            if self.count > 0 {
                self.total_time / self.count as u32
            } else {
                std::time::Duration::ZERO
            }
        }
        
        pub fn count(&self) -> u64 {
            self.count
        }
        
        pub fn min_time(&self) -> Option<std::time::Duration> {
            self.min_time
        }
        
        pub fn max_time(&self) -> Option<std::time::Duration> {
            self.max_time
        }
    }
}

/// String utilities
pub mod string {
    /// Format number with appropriate precision
    pub fn format_float(value: f64, precision: usize) -> String {
        format!("{:.1$}", value, precision)
    }
    
    /// Format duration in human-readable format
    pub fn format_duration(duration: std::time::Duration) -> String {
        let millis = duration.as_millis();
        if millis < 1000 {
            format!("{}ms", millis)
        } else {
            format!("{:.2}s", millis as f64 / 1000.0)
        }
    }
    
    /// Truncate string to specified length
    pub fn truncate(s: &str, max_len: usize) -> String {
        if s.len() <= max_len {
            s.to_string()
        } else {
            format!("{}...", &s[..max_len.saturating_sub(3)])
        }
    }
}
