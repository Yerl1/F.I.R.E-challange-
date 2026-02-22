"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { isMockMode } from "./api";
import { MOCK_PROFILE } from "./mock-data";
import type { SpecialistProfile } from "./types";

interface AuthState {
  token: string | null;
  profile: SpecialistProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [profile, setProfile] = useState<SpecialistProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("fb_token");
    if (stored) {
      setToken(stored);
      setProfile(MOCK_PROFILE);
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error("Username and password are required");
    }
    const issuedToken = isMockMode()
      ? "mock-jwt-token-" + Date.now()
      : "local-session-token-" + Date.now();
    localStorage.setItem("fb_token", issuedToken);
    setToken(issuedToken);
    setProfile(MOCK_PROFILE);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("fb_token");
    setToken(null);
    setProfile(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        token,
        profile,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
