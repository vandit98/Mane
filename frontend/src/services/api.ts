import axios from 'axios';
import { Product, ProductListResponse, ChatResponse, ChatMessage } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { 'Content-Type': 'application/json' },
});

export async function getProducts(skip = 0, limit = 50): Promise<ProductListResponse> {
  const { data } = await api.get(`/products?skip=${skip}&limit=${limit}`);
  return data;
}

export async function getProduct(id: number): Promise<Product> {
  const { data } = await api.get(`/products/${id}`);
  return data;
}

export async function searchProducts(query: string): Promise<Product[]> {
  const { data } = await api.get(`/products/search?q=${encodeURIComponent(query)}`);
  return data;
}

export async function sendChatMessage(
  message: string,
  conversationHistory: ChatMessage[]
): Promise<ChatResponse> {
  const { data } = await api.post('/chat', {
    message,
    conversation_history: conversationHistory.map(m => ({
      role: m.role,
      content: m.content,
    })),
  });
  return data;
}

export async function runScraper(): Promise<{ status: string; message: string }> {
  const { data } = await api.post('/scraper/run');
  return data;
}
