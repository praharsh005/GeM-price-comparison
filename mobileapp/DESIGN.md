# DESIGN.md — GeM price comparison design system

**Reference inspiration:** BuyHatke and similar price-discovery platforms (MySmartPrice, PriceRaja) — sites whose entire job is making "where's this cheapest, and by how much" obvious in seconds. This system adapts that philosophy with an original visual language for this project — not a copy of any site's actual styling.

## Design philosophy

Every screen should let a user answer *"where's this cheapest, and how much am I saving?"* in under 3 seconds. Function and information clarity beat decoration everywhere in this app.

## Reference mockup — approved

The screens below (search, compare, price history, home/categories, alerts) are the approved visual reference. Match these pixel-for-pixel where they overlap with a screen you're building; extend the same patterns for anything not explicitly shown.

**Screen inventory:**
1. **Home** — app header, search entry, category grid (icon + label), "Trending savings" list
2. **Search results** — list of products, each showing lowest price + "Compare across N stores"
3. **Compare** — one row per marketplace; cheapest row gets the "best price" treatment below
4. **Price history** — line chart, one line per marketplace, all-time-low caption
5. **Alerts** — list of price-drop notifications with source + relative time

Persistent bottom tab bar across all screens: Home / Search / Alerts / Profile, white background, `#E2E8F0` top border, active icon `#2563EB`, inactive `#94A3B8`.

## Color system

Exact values, as built in the reference mockup:

- **Primary (trust/actions):** `#2563EB` — header backgrounds, buttons, links, active nav icon
- **Savings green (reserved, meaningful):** `#16A34A` — cheapest price text, "Save ₹X" badges. Best-price card specifically: border `#16A34A`, background wash `#F0FDF4`, solid "Best price" pill (`#16A34A` background, white text). Savings badge elsewhere (e.g. home screen "Trending savings"): background `#DCFCE7`, text `#166534`. Green is never used decoratively — only where a real savings/best-price fact is being shown.
- **Price-increase amber:** `#D97706` — a price that rose since last check, or a data-mismatch warning, background wash `#FFFBEB`, text `#92400E`. Real errors stay on red, kept separate from amber.
- **Neutrals:** background `#F8FAFC`, card border `#E2E8F0`, text primary `#0F172A`, text secondary `#64748B`, text muted `#94A3B8`.
- **Marketplace source tags:** a small 7px colored dot + gray label text — not a solid colored badge, so it doesn't compete with the savings green or primary blue. GeM = `#4338CA` (indigo), Amazon = `#C2410C` (coral), Flipkart = `#0284C7` (sky blue). Category icons (home screen) reuse the indigo tint (`#EEF2FF` background, `#4338CA` icon) as the app's general accent tint, separate from the marketplace-identity use of the same hue.

## Typography

- Inter or system-ui stack — legible at small sizes, important since prices are digit-heavy
- Prices use tabular-nums and a bolder weight than surrounding text, so digits align in comparison tables
- Type scale: 12 / 14 / 16 / 20 / 28px for caption / body / subhead / heading

## Core components

- **Search bar** — prominent on every screen, autocomplete dropdown shows thumbnail + lowest price inline
- **Comparison card** — one product, one row per marketplace; the cheapest row gets a full green border + light green background wash + solid "Best price" pill (see Color system for exact values); other rows are plain white cards with a gray border. Each row has a "Go to site" CTA on the cheapest row.
- **Price trend chart** — line chart, x = date, y = price, one line per marketplace in its tag color, all-time-low point highlighted
- **Savings badge** — green pill, "Save ₹X (Y%)" — shown only where a genuine comparison exists, never decoratively
- **Category browse** — simple icon + label grid, no unnecessary imagery

## Layout principles

- One clear focal action per screen — don't compete CTAs against each other
- Mobile-first spacing scale: 4 / 8 / 16 / 24 / 32px, minimum 44px tap targets (this system also backs the mobile app)
- Comparison tables collapse into stacked cards below 640px width

## Motion

Subtle only — skeleton loaders while fetching (never a blank screen), a brief highlight flash on the cheapest price. No gratuitous animation.

## Tech mapping

- Define the tokens above as CSS variables in the Tailwind config so web (React) and mobile (React Native/NativeWind) can share the same design tokens
- Restyle shadcn/ui primitives (button, card, badge, input) with these tokens rather than using shadcn defaults out of the box

## What not to do

- Don't use red or amber decoratively — reserve for real warnings/errors
- Don't let marketplace source colors dominate a layout — they're identifiers, not brand elements
- No gradients, drop shadows, or skeuomorphism — flat, confident, information-dense
