/**
 * API context for sharing client configuration and global request settings.
 */

import React, { createContext, useContext, ReactNode } from "react";
import { ApiRequestConfig } from "@/types/api";

interface ApiContextType {
  /**
   * Default request configuration.
   */
  defaultConfig: ApiRequestConfig;

  /**
   * Update default configuration.
   */
  setDefaultConfig: (config: Partial<ApiRequestConfig>) => void;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

interface ApiProviderProps {
  children: ReactNode;
  defaultConfig?: Partial<ApiRequestConfig>;
}

/**
 * API context provider component.
 */
export function ApiProvider({ children, defaultConfig = {} }: ApiProviderProps) {
  const [config, setConfig] = React.useState<ApiRequestConfig>({
    requireAuth: true,
    timeout: 30000,
    retry: true,
    maxRetries: 3,
    ...defaultConfig,
  });

  const setDefaultConfig = React.useCallback((newConfig: Partial<ApiRequestConfig>) => {
    setConfig((prev) => ({ ...prev, ...newConfig }));
  }, []);

  const value: ApiContextType = {
    defaultConfig: config,
    setDefaultConfig,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

/**
 * Hook to access API context.
 */
export function useApiContext(): ApiContextType {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error("useApiContext must be used within an ApiProvider");
  }
  return context;
}

