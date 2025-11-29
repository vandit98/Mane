export interface Product {
  id: number;
  external_id: string;
  title: string;
  price: number;
  compare_price?: number;
  description?: string;
  features?: string;
  image_url?: string;
  images?: string[];
  category?: string;
  vendor?: string;
  product_type?: string;
  tags?: string[];
  url?: string;
}

export interface ProductListResponse {
  products: Product[];
  total: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  products?: Product[];
}

export interface ChatResponse {
  message: string;
  products: Product[];
  needs_clarification: boolean;
}

