import { Colors, Spacing, FontSize, MarketplaceColors, TapTarget } from '@/constants/design';

describe('design tokens', () => {
  it('exports correct color palette matching DESIGN.md', () => {
    expect(Colors.primary).toBe('#2563EB');
    expect(Colors.savingsGreen).toBe('#16A34A');
    expect(Colors.savingsGreenBg).toBe('#F0FDF4');
    expect(Colors.savingsBadgeBg).toBe('#DCFCE7');
    expect(Colors.savingsBadgeText).toBe('#166534');
    expect(Colors.priceUpAmber).toBe('#D97706');
    expect(Colors.priceUpBg).toBe('#FFFBEB');
    expect(Colors.priceUpText).toBe('#92400E');
    expect(Colors.error).toBe('#DC2626');
    expect(Colors.background).toBe('#F8FAFC');
    expect(Colors.surface).toBe('#FFFFFF');
    expect(Colors.border).toBe('#E2E8F0');
    expect(Colors.textPrimary).toBe('#0F172A');
    expect(Colors.textSecondary).toBe('#64748B');
    expect(Colors.textMuted).toBe('#94A3B8');
    expect(Colors.tabActive).toBe('#2563EB');
    expect(Colors.tabInactive).toBe('#94A3B8');
    expect(Colors.tabBarBg).toBe('#FFFFFF');
    expect(Colors.tabBarBorder).toBe('#E2E8F0');
    expect(Colors.accentTintBg).toBe('#EEF2FF');
    expect(Colors.accentTintIcon).toBe('#4338CA');
  });

  it('exports marketplace colors', () => {
    expect(MarketplaceColors.gem).toBe('#4338CA');
    expect(MarketplaceColors.amazon).toBe('#C2410C');
    expect(MarketplaceColors.flipkart).toBe('#0284C7');
    expect(MarketplaceColors.vijaysales).toBe('#7C3AED');
    expect(MarketplaceColors.snapdeal).toBe('#0F766E');
  });

  it('exports spacing scale', () => {
    expect(Spacing.xs).toBe(4);
    expect(Spacing.sm).toBe(8);
    expect(Spacing.md).toBe(16);
    expect(Spacing.lg).toBe(24);
    expect(Spacing.xl).toBe(32);
  });

  it('exports font size scale (12/14/16/20/28 per DESIGN.md)', () => {
    expect(FontSize.caption).toBe(12);
    expect(FontSize.body).toBe(14);
    expect(FontSize.subhead).toBe(16);
    expect(FontSize.heading).toBe(20);
    expect(FontSize.title).toBe(28);
  });

  it('exports tap target minimum 44px', () => {
    expect(TapTarget).toBe(44);
  });

  it('exports accent tint tokens for category icons', () => {
    expect(Colors.accentTintBg).toBe('#EEF2FF');
    expect(Colors.accentTintIcon).toBe('#4338CA');
  });
});