import { apiGet } from '@/lib/api';

export interface ProductSummary {
  id: number;
  name: string;
  brand: string | null;
  category: string;
  image_url: string | null;
  lowest_price: number | null;
  marketplace_count: number;
}

export interface Listing {
  id: number;
  marketplace_id: number;
  marketplace_name: string;
  marketplace_slug: string;
  price: number;
  currency: string;
  url: string;
  available: boolean;
  is_cheapest: boolean;
}

export interface ProductCompare {
  id: number;
  name: string;
  brand: string | null;
  category: string;
  description: string | null;
  image_url: string | null;
  listings: Listing[];
  best_price: number | null;
  best_marketplace: string | null;
}

export interface PricePoint {
  price: number;
  recorded_at: string;
}

export interface PriceSeries {
  listing_id: number;
  marketplace_name: string;
  marketplace_slug: string;
  points: PricePoint[];
}

export interface PriceHistory {
  id: number;
  name: string;
  brand: string | null;
  category: string;
  series: PriceSeries[];
}

export interface CategorySavings {
  category: string;
  products_with_gem: number;
  avg_savings: number;
  total_savings: number;
}

export interface Insights {
  categories: CategorySavings[];
  overall: CategorySavings;
}

export interface TrendingProduct {
  id: number;
  name: string;
  brand: string | null;
  category: string;
  image_url: string | null;
  best_price: number | null;
  best_marketplace: string | null;
  second_best_price: number | null;
  savings: number | null;
  savings_pct: number | null;
}

export interface PriceDropAlert {
  product_id: number;
  product_name: string;
  marketplace_name: string;
  marketplace_slug: string;
  old_price: number;
  new_price: number;
  drop_amount: number;
  percent_drop: number;
  dropped_at: string;
}

export function searchProducts(query: string, category?: string) {
  const params = new URLSearchParams();
  if (query.trim()) params.set('q', query.trim());
  if (category) params.set('category', category);
  return apiGet<ProductSummary[]>(`/search?${params.toString()}`);
}

export function getProductCompare(id: number) {
  return apiGet<ProductCompare>(`/products/${id}/compare`);
}

export function getPriceHistory(id: number) {
  return apiGet<PriceHistory>(`/products/${id}/price-history`);
}

export function getInsights() {
  return apiGet<Insights>('/insights');
}

export function getTrending() {
  return apiGet<TrendingProduct[]>('/trending');
}

export function getAlerts() {
  return apiGet<PriceDropAlert[]>('/alerts');
}
