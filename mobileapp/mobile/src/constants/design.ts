export const Colors = {
  background: '#F8FAFC',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  textPrimary: '#0F172A',
  textSecondary: '#64748B',
  textMuted: '#94A3B8',
  primary: '#2563EB',
  savingsGreen: '#16A34A',
  savingsGreenBg: '#F0FDF4',
  savingsBadgeBg: '#DCFCE7',
  savingsBadgeText: '#166534',
  priceUpAmber: '#D97706',
  priceUpBg: '#FFFBEB',
  priceUpText: '#92400E',
  error: '#DC2626',
  tabInactive: '#94A3B8',
  tabActive: '#2563EB',
  tabBarBg: '#FFFFFF',
  tabBarBorder: '#E2E8F0',
  accentTintBg: '#EEF2FF',
  accentTintIcon: '#4338CA',
} as const;

export const MarketplaceColors: Record<string, string> = {
  gem: '#4338CA',
  amazon: '#C2410C',
  flipkart: '#0284C7',
  vijaysales: '#7C3AED',
  snapdeal: '#0F766E',
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

export const FontSize = {
  caption: 12,
  body: 14,
  subhead: 16,
  heading: 20,
  title: 28,
} as const;

export const TapTarget = 44 as const;
