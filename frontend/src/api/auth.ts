import client from './client'
import type { AuthResponse, User } from '../types'

interface LoginData {
  username: string
  password: string
}

interface RegisterData {
  username: string
  email: string
  phone?: string
  role: string
  password: string
}

export function login(data: LoginData) {
  return client.post<AuthResponse>('/auth/login', data)
}

export function register(data: RegisterData) {
  return client.post('/auth/register', data)
}

export function refreshToken() {
  return client.post<AuthResponse>('/auth/refresh')
}

export function logout() {
  return client.post('/auth/logout')
}

export function fetchMe() {
  return client.get<User>('/auth/me')
}
