import api from './client';
import type { AuthResponse, User } from '../types';

export async function login(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/login', { email, password });
  return data;
}

export async function register(payload: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  organization_name: string;
}): Promise<AuthResponse> {
  const { data } = await api.post('/auth/register', payload);
  return data;
}

export async function getProfile(): Promise<User> {
  const { data } = await api.get('/auth/me');
  return data.user;
}

export async function updateProfile(payload: Partial<User>): Promise<User> {
  const { data } = await api.put('/auth/me', payload);
  return data.user;
}
