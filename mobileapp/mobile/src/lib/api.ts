import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

const DEFAULT_PORT = 8000;
const STORAGE_KEY = 'apiBaseUrlOverride';

let overrideUrl: string | null = null;
let initialized = false;

async function loadOverride() {
  if (initialized) return;
  try {
    const stored = await AsyncStorage.getItem(STORAGE_KEY);
    overrideUrl = stored ?? null;
  } catch {
    overrideUrl = null;
  }
  initialized = true;
}

export async function setApiBaseUrl(url: string | null) {
  overrideUrl = url;
  try {
    if (url) {
      await AsyncStorage.setItem(STORAGE_KEY, url);
    } else {
      await AsyncStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // ignore storage errors
  }
}

export async function getApiBaseUrl(): Promise<string> {
  await loadOverride();
  if (overrideUrl) return overrideUrl;

  const configured = Constants.expoConfig?.extra?.apiBaseUrl as string | undefined;
  if (configured) return configured;

  if (Platform.OS === 'android') {
    const hostUri = Constants.expoConfig?.hostUri;
    if (hostUri) {
      const host = hostUri.split(':')[0];
      return `http://${host}:${DEFAULT_PORT}`;
    }
    return `http://10.0.2.2:${DEFAULT_PORT}`;
  }

  return `http://localhost:${DEFAULT_PORT}`;
}

export async function apiGet<T>(path: string): Promise<T> {
  const base = await getApiBaseUrl();
  const res = await fetch(`${base}${path}`);
  if (!res.ok) {
    throw new Error(`API ${path} failed with ${res.status}`);
  }
  return res.json() as Promise<T>;
}