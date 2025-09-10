import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Agent, CityMetrics, SystemEvent } from '@/types';
import { debounce, throttle, sleep } from '@/utils';

// Hook para gerenciar estado de loading
export const useLoading = (initialState: boolean = false) => {
  const [isLoading, setIsLoading] = useState(initialState);
  const [error, setError] = useState<string | null>(null);

  const startLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
  }, []);

  const stopLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const setLoadingError = useCallback((error: string) => {
    setError(error);
    setIsLoading(false);
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    startLoading,
    stopLoading,
    setLoadingError,
    reset,
  };
};

// Hook para gerenciar estado de simulação
export const useSimulation = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState(new Date());

  const start = useCallback(() => {
    setIsRunning(true);
    setIsPaused(false);
  }, []);

  const pause = useCallback(() => {
    setIsPaused(true);
  }, []);

  const resume = useCallback(() => {
    setIsPaused(false);
  }, []);

  const stop = useCallback(() => {
    setIsRunning(false);
    setIsPaused(false);
  }, []);

  const reset = useCallback(() => {
    setIsRunning(false);
    setIsPaused(false);
    setCurrentTime(new Date());
  }, []);

  const updateSpeed = useCallback((newSpeed: number) => {
    setSpeed(Math.max(0.1, Math.min(10, newSpeed)));
  }, []);

  return {
    isRunning,
    isPaused,
    speed,
    currentTime,
    start,
    pause,
    resume,
    stop,
    reset,
    updateSpeed,
  };
};

// Hook para gerenciar agentes
export const useAgents = (initialAgents: Agent[] = []) => {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>(initialAgents);

  const addAgent = useCallback((agent: Agent) => {
    setAgents(prev => [...prev, agent]);
  }, []);

  const updateAgent = useCallback((id: string, updates: Partial<Agent>) => {
    setAgents(prev => 
      prev.map(agent => 
        agent.id === id ? { ...agent, ...updates } : agent
      )
    );
  }, []);

  const removeAgent = useCallback((id: string) => {
    setAgents(prev => prev.filter(agent => agent.id !== id));
    if (selectedAgent?.id === id) {
      setSelectedAgent(null);
    }
  }, [selectedAgent]);

  const getAgentById = useCallback((id: string) => {
    return agents.find(agent => agent.id === id);
  }, [agents]);

  const filterAgents = useCallback((predicate: (agent: Agent) => boolean) => {
    setFilteredAgents(agents.filter(predicate));
  }, [agents]);

  const clearFilters = useCallback(() => {
    setFilteredAgents(agents);
  }, [agents]);

  const selectAgent = useCallback((agent: Agent | null) => {
    setSelectedAgent(agent);
  }, []);

  return {
    agents,
    selectedAgent,
    filteredAgents,
    addAgent,
    updateAgent,
    removeAgent,
    getAgentById,
    filterAgents,
    clearFilters,
    selectAgent,
  };
};

// Hook para gerenciar métricas da cidade
export const useCityMetrics = (initialMetrics: CityMetrics) => {
  const [metrics, setMetrics] = useState<CityMetrics>(initialMetrics);
  const [history, setHistory] = useState<CityMetrics[]>([]);
  const [trends, setTrends] = useState<Record<string, 'up' | 'down' | 'stable'>>({});

  const updateMetrics = useCallback((newMetrics: Partial<CityMetrics>) => {
    setMetrics(prev => {
      const updated = { ...prev, ...newMetrics };
      
      // Calcular tendências
      const newTrends: Record<string, 'up' | 'down' | 'stable'> = {};
      Object.keys(newMetrics).forEach(key => {
        const current = updated[key as keyof CityMetrics] as number;
        const previous = prev[key as keyof CityMetrics] as number;
        if (typeof current === 'number' && typeof previous === 'number') {
          const diff = current - previous;
          if (Math.abs(diff) < 0.01) {
            newTrends[key] = 'stable';
          } else {
            newTrends[key] = diff > 0 ? 'up' : 'down';
          }
        }
      });
      
      setTrends(prev => ({ ...prev, ...newTrends }));
      
      // Adicionar ao histórico
      setHistory(prev => [...prev.slice(-99), updated]);
      
      return updated;
    });
  }, []);

  const resetMetrics = useCallback(() => {
    setMetrics(initialMetrics);
    setHistory([]);
    setTrends({});
  }, [initialMetrics]);

  const getMetricTrend = useCallback((key: keyof CityMetrics) => {
    return trends[key] || 'stable';
  }, [trends]);

  const getMetricHistory = useCallback((key: keyof CityMetrics, limit: number = 50) => {
    return history.slice(-limit).map(h => h[key] as number);
  }, [history]);

  return {
    metrics,
    history,
    trends,
    updateMetrics,
    resetMetrics,
    getMetricTrend,
    getMetricHistory,
  };
};

// Hook para gerenciar eventos do sistema
export const useSystemEvents = () => {
  const [events, setEvents] = useState<SystemEvent[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const addEvent = useCallback((event: SystemEvent) => {
    setEvents(prev => [event, ...prev.slice(0, 99)]);
    setUnreadCount(prev => prev + 1);
  }, []);

  const markAsRead = useCallback((eventId: string) => {
    setEvents(prev => 
      prev.map(event => 
        event.id === eventId ? { ...event, read: true } : event
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setEvents(prev => prev.map(event => ({ ...event, read: true })));
    setUnreadCount(0);
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setUnreadCount(0);
  }, []);

  const getEventsByType = useCallback((type: string) => {
    return events.filter(event => event.type === type);
  }, [events]);

  const getEventsBySeverity = useCallback((severity: string) => {
    return events.filter(event => event.severity === severity);
  }, [events]);

  return {
    events,
    unreadCount,
    addEvent,
    markAsRead,
    markAllAsRead,
    clearEvents,
    getEventsByType,
    getEventsBySeverity,
  };
};

// Hook para gerenciar configurações
export const useConfig = <T>(key: string, defaultValue: T) => {
  const [config, setConfig] = useState<T>(() => {
    try {
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  const updateConfig = useCallback((newConfig: Partial<T>) => {
    setConfig(prev => {
      const updated = { ...prev, ...newConfig };
      localStorage.setItem(key, JSON.stringify(updated));
      return updated;
    });
  }, [key]);

  const resetConfig = useCallback(() => {
    setConfig(defaultValue);
    localStorage.removeItem(key);
  }, [key, defaultValue]);

  return {
    config,
    updateConfig,
    resetConfig,
  };
};

// Hook para gerenciar tema
export const useTheme = () => {
  const { config: theme, updateConfig } = useConfig('theme', 'dark');

  const toggleTheme = useCallback(() => {
    updateConfig(theme === 'dark' ? 'light' : 'dark');
  }, [theme, updateConfig]);

  const setTheme = useCallback((newTheme: string) => {
    updateConfig(newTheme);
  }, [updateConfig]);

  return {
    theme,
    toggleTheme,
    setTheme,
  };
};

// Hook para gerenciar notificações
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [permission, setPermission] = useState<NotificationPermission>('default');

  useEffect(() => {
    if ('Notification' in window) {
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = useCallback(async () => {
    if ('Notification' in window) {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result;
    }
    return 'denied';
  }, []);

  const showNotification = useCallback((title: string, options?: NotificationOptions) => {
    if (permission === 'granted') {
      const notification = new Notification(title, options);
      setNotifications(prev => [...prev, notification]);
      
      notification.onclick = () => {
        window.focus();
        notification.close();
      };
      
      setTimeout(() => {
        notification.close();
        setNotifications(prev => prev.filter(n => n !== notification));
      }, 5000);
    }
  }, [permission]);

  const clearNotifications = useCallback(() => {
    notifications.forEach(notification => notification.close());
    setNotifications([]);
  }, [notifications]);

  return {
    notifications,
    permission,
    requestPermission,
    showNotification,
    clearNotifications,
  };
};

// Hook para gerenciar performance
export const usePerformance = () => {
  const [metrics, setMetrics] = useState({
    fps: 0,
    memoryUsage: 0,
    renderTime: 0,
  });

  const frameCount = useRef(0);
  const lastTime = useRef(performance.now());
  const animationId = useRef<number>();

  const measurePerformance = useCallback(() => {
    const now = performance.now();
    const delta = now - lastTime.current;
    
    frameCount.current++;
    
    if (delta >= 1000) {
      const fps = Math.round((frameCount.current * 1000) / delta);
      
      setMetrics(prev => ({
        ...prev,
        fps,
        memoryUsage: (performance as any).memory?.usedJSHeapSize || 0,
        renderTime: delta / frameCount.current,
      }));
      
      frameCount.current = 0;
      lastTime.current = now;
    }
    
    animationId.current = requestAnimationFrame(measurePerformance);
  }, []);

  useEffect(() => {
    measurePerformance();
    return () => {
      if (animationId.current) {
        cancelAnimationFrame(animationId.current);
      }
    };
  }, [measurePerformance]);

  return metrics;
};

// Hook para gerenciar scroll
export const useScroll = () => {
  const [scrollY, setScrollY] = useState(0);
  const [scrollDirection, setScrollDirection] = useState<'up' | 'down'>('up');
  const [isAtTop, setIsAtTop] = useState(true);
  const [isAtBottom, setIsAtBottom] = useState(false);

  const lastScrollY = useRef(0);

  useEffect(() => {
    const handleScroll = throttle(() => {
      const currentScrollY = window.scrollY;
      
      setScrollY(currentScrollY);
      setScrollDirection(currentScrollY > lastScrollY.current ? 'down' : 'up');
      setIsAtTop(currentScrollY === 0);
      setIsAtBottom(
        currentScrollY + window.innerHeight >= document.documentElement.scrollHeight
      );
      
      lastScrollY.current = currentScrollY;
    }, 100);

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const scrollToBottom = useCallback(() => {
    window.scrollTo({ 
      top: document.documentElement.scrollHeight, 
      behavior: 'smooth' 
    });
  }, []);

  const scrollTo = useCallback((position: number) => {
    window.scrollTo({ top: position, behavior: 'smooth' });
  }, []);

  return {
    scrollY,
    scrollDirection,
    isAtTop,
    isAtBottom,
    scrollToTop,
    scrollToBottom,
    scrollTo,
  };
};

// Hook para gerenciar resize
export const useResize = () => {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = throttle(() => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }, 100);

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobile = useMemo(() => dimensions.width < 768, [dimensions.width]);
  const isTablet = useMemo(() => dimensions.width >= 768 && dimensions.width < 1024, [dimensions.width]);
  const isDesktop = useMemo(() => dimensions.width >= 1024, [dimensions.width]);

  return {
    ...dimensions,
    isMobile,
    isTablet,
    isDesktop,
  };
};

// Hook para gerenciar local storage
export const useLocalStorage = <T>(key: string, defaultValue: T) => {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  const setStoredValue = useCallback((newValue: T | ((prev: T) => T)) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      setValue(valueToStore);
      localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }, [key, value]);

  const removeStoredValue = useCallback(() => {
    try {
      setValue(defaultValue);
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  }, [key, defaultValue]);

  return [value, setStoredValue, removeStoredValue] as const;
};

// Hook para gerenciar debounce
export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Hook para gerenciar throttle
export const useThrottle = <T>(value: T, delay: number): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastExecuted = useRef<number>(Date.now());

  useEffect(() => {
    if (Date.now() >= lastExecuted.current + delay) {
      lastExecuted.current = Date.now();
      setThrottledValue(value);
    } else {
      const timer = setTimeout(() => {
        lastExecuted.current = Date.now();
        setThrottledValue(value);
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [value, delay]);

  return throttledValue;
};

// Hook para gerenciar interval
export const useInterval = (callback: () => void, delay: number | null) => {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return;

    const id = setInterval(() => savedCallback.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
};

// Hook para gerenciar timeout
export const useTimeout = (callback: () => void, delay: number | null) => {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return;

    const id = setTimeout(() => savedCallback.current(), delay);
    return () => clearTimeout(id);
  }, [delay]);
};

// Hook para gerenciar previous value
export const usePrevious = <T>(value: T): T | undefined => {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  });
  
  return ref.current;
};

// Hook para gerenciar click outside
export const useClickOutside = (ref: React.RefObject<HTMLElement>, callback: () => void) => {
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [ref, callback]);
};

// Hook para gerenciar keyboard shortcuts
export const useKeyboardShortcut = (key: string, callback: () => void, deps: any[] = []) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === key) {
        event.preventDefault();
        callback();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [key, callback, ...deps]);
};
