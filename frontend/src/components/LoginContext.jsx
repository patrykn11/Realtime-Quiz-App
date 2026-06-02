import { createContext, useCallback, useEffect, useRef, useState } from "react";

import { API_URL } from "../config";

const ACCESS_TOKEN_KEY = "accessToken";
const REFRESH_TOKEN_KEY = "refreshToken";


export const AuthContext = createContext({
  token: "",
  user: null,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  apiFetch: async () => {},
});

const readTokenExpiry = (token) => {
  try {
    return JSON.parse(atob(token.split(".")[1])).exp * 1000;
  } catch {
    return 0;
  }
};

const readError = async (response) => {
  const body = await response.json().catch(() => ({}));
  const firstError = Object.values(body).flat()[0];
  throw new Error(firstError || body.detail || "Authentication request failed.");
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(
    () => localStorage.getItem(ACCESS_TOKEN_KEY) || "",
  );
  const [user, setUser] = useState(null);
  const refreshPromise = useRef(null);

  const clearSession = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem("token");
    setToken("");
    setUser(null);
  }, []);

  const saveSession = useCallback((data) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
    if (data.refresh) {
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
    }
    setToken(data.access);
    if (data.user) {
      setUser(data.user);
    }
  }, []);

  const refreshAccessToken = useCallback(async () => {
    if (refreshPromise.current) {
      return refreshPromise.current;
    }

    const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refresh) {
      clearSession();
      return null;
    }

    refreshPromise.current = (async () => {
      const response = await fetch(`${API_URL}/api/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });

      if (!response.ok) {
        clearSession();
        return null;
      }

      const data = await response.json();
      saveSession(data);
      return data.access;
    })().finally(() => {
      refreshPromise.current = null;
    });

    return refreshPromise.current;
  }, [clearSession, saveSession]);

  const apiFetch = useCallback(async (path, options = {}) => {
    const send = (access) => {
      const headers = new Headers(options.headers || {});
      if (access) {
        headers.set("Authorization", `Bearer ${access}`);
      }
      return fetch(`${API_URL}${path}`, { ...options, headers });
    };

    let access = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!access && localStorage.getItem(REFRESH_TOKEN_KEY)) {
      access = await refreshAccessToken();
    }

    let response = await send(access);
    if (response.status === 401 && localStorage.getItem(REFRESH_TOKEN_KEY)) {
      access = await refreshAccessToken();
      if (access) {
        response = await send(access);
      }
    }
    return response;
  }, [refreshAccessToken]);

  const login = useCallback(async (credentials) => {
    const response = await fetch(`${API_URL}/api/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    if (!response.ok) await readError(response);
    const data = await response.json();
    saveSession(data);
    return data.user;
  }, [saveSession]);

  const register = useCallback(async (details) => {
    const response = await fetch(`${API_URL}/api/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(details),
    });
    if (!response.ok) await readError(response);
    const data = await response.json();
    saveSession(data);
    return data.user;
  }, [saveSession]);

  const logout = useCallback(async () => {
    try {
      let access = localStorage.getItem(ACCESS_TOKEN_KEY);
      let refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!access || readTokenExpiry(access) <= Date.now()) {
        access = await refreshAccessToken();
        refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
      }
      if (access && refresh) {
        await fetch(`${API_URL}/api/logout/`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${access}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh }),
        });
      }
    } finally {
      clearSession();
    }
  }, [clearSession, refreshAccessToken]);

  useEffect(() => {
    const safelyRefresh = () => refreshAccessToken().catch(clearSession);

    if (!token) {
      if (localStorage.getItem(REFRESH_TOKEN_KEY)) {
        safelyRefresh();
      }
      return undefined;
    }

    const refreshIn = readTokenExpiry(token) - Date.now() - 30_000;
    if (refreshIn <= 0) {
      safelyRefresh();
      return undefined;
    }

    const timer = window.setTimeout(safelyRefresh, refreshIn);
    return () => window.clearTimeout(timer);
  }, [token, clearSession, refreshAccessToken]);

  useEffect(() => {
    if (!token || user) return;

    apiFetch("/api/me/")
      .then((response) => (response.ok ? response.json() : null))
      .then((currentUser) => {
        if (currentUser) setUser(currentUser);
      })
      .catch(() => null);
  }, [apiFetch, token, user]);

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, apiFetch }}>
      {children}
    </AuthContext.Provider>
  );
};
