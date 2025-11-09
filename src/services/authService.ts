import apiClient from '../api/client';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  status: string;
  access_token: string;
  refresh_token: string;
  user: {
    username: string;
    role: string;
  };
}

export interface User {
  username: string;
  role: 'admin' | 'auditor' | 'monitor';
}

const TOKEN_KEY = 'biascheck_access_token';
const REFRESH_TOKEN_KEY = 'biascheck_refresh_token';
const USER_KEY = 'biascheck_user';

class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    
    if (response.data.access_token) {
      this.setToken(response.data.access_token);
      this.setRefreshToken(response.data.refresh_token);
      this.setUser(response.data.user);
    }
    
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuth();
    }
  }

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  setRefreshToken(token: string): void {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  setUser(user: { username: string; role: string }): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.getUser();
  }

  hasRole(role: string): boolean {
    const user = this.getUser();
    return user?.role === role;
  }

  hasAnyRole(roles: string[]): boolean {
    const user = this.getUser();
    return user ? roles.includes(user.role) : false;
  }

  clearAuth(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

export const authService = new AuthService();
