/**
 * React Hook for Real-Time Project Progress Updates
 * Uses WebSocket for live progress tracking
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface ProgressUpdate {
  project_id: number;
  status: string;
  progress: number;
  current_phase: string;
  message?: string;
  error_message?: string;
  timestamp: string;
}

interface UseProjectProgressOptions {
  projectId: number;
  onProgress?: (update: ProgressUpdate) => void;
  onComplete?: (update: ProgressUpdate) => void;
  onError?: (error: string) => void;
}

/**
 * Hook for tracking project generation progress in real-time
 */
export const useProjectProgress = ({
  projectId,
  onProgress,
  onComplete,
  onError,
}: UseProjectProgressOptions) => {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  
  const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000; // 3 seconds
  
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(`${WS_URL}/progress/${projectId}`);
      
      ws.onopen = () => {
        console.log(`WebSocket connected for project ${projectId}`);
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
      };
      
      ws.onmessage = (event) => {
        try {
          const update: ProgressUpdate = JSON.parse(event.data);
          
          setProgress(update);
          
          // Call callbacks
          if (onProgress) {
            onProgress(update);
          }
          
          // Check if completed
          if (update.status === 'completed') {
            if (onComplete) {
              onComplete(update);
            }
            // Close connection on completion
            ws.close();
          } else if (update.status === 'failed') {
            setError(update.error_message || 'Generation failed');
            if (onError) {
              onError(update.error_message || 'Generation failed');
            }
            ws.close();
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        if (onError) {
          onError('Connection error');
        }
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        
        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          console.log(
            `Reconnecting... (attempt ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})`
          );
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, RECONNECT_DELAY);
        }
      };
      
      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      setError('Failed to establish connection');
      if (onError) {
        onError('Failed to establish connection');
      }
    }
  }, [projectId, onProgress, onComplete, onError, WS_URL]);
  
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
  }, []);
  
  // Connect on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);
  
  return {
    progress,
    isConnected,
    error,
    reconnect: connect,
    disconnect,
  };
};

/**
 * Hook for polling project status (fallback if WebSocket not available)
 */
export const useProjectStatusPolling = (
  projectId: number,
  interval = 2000
) => {
  const [status, setStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  
  useEffect(() => {
    if (!projectId) return;
    
    setIsPolling(true);
    
    const poll = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/projects/${projectId}`
        );
        
        if (!response.ok) {
          throw new Error('Failed to fetch project status');
        }
        
        const data = await response.json();
        setStatus(data);
        
        // Stop polling if completed or failed
        if (data.status === 'completed' || data.status === 'failed') {
          setIsPolling(false);
        }
      } catch (err) {
        console.error('Polling error:', err);
        setError(err instanceof Error ? err.message : 'Polling error');
      }
    };
    
    // Initial poll
    poll();
    
    // Set up interval
    const intervalId = setInterval(poll, interval);
    
    return () => {
      clearInterval(intervalId);
      setIsPolling(false);
    };
  }, [projectId, interval]);
  
  return {
    status,
    error,
    isPolling,
  };
};
