# DESIGN.md

# GeM Price Intelligence — Design System

## 1. Product Identity

Working product concept:

**GeM Price Intelligence**

Purpose:
A modern web platform that compares GeM product prices with relevant products from other e-marketplaces and converts that data into understandable price intelligence.

Core promise:

**Compare. Understand. Save.**

Experience goals:

**Trust + Transparency + Savings + Procurement Intelligence**

The product should look appropriate for a high-quality academic major project while feeling polished enough to resemble a real software product.

---

# 2. DESIGN PRINCIPLES

## 2.1 Clarity First

Users should understand quickly:
- what product is being compared
- where each price came from
- which option is cheaper
- how large the difference is
- how confident the match is
- when the data was updated

Do not hide core information behind excessive interaction.

## 2.2 Data Before Decoration

Charts, cards, badges, icons, and visual effects must communicate useful information.

Avoid decorative UI that does not improve comprehension.

## 2.3 Trust Through Transparency

Show, where relevant:
- source
- last updated time
- match confidence
- data availability
- whether the comparison is exact or approximate

Never make scraped data look officially endorsed by GeM.

## 2.4 Professional, Not Generic

The interface should feel like a real price-intelligence platform, not a generic shopping clone and not an over-designed admin dashboard.

## 2.5 Fast and Focused

Prefer:
- strong hierarchy
- compact information density
- fast search
- short interaction paths
- lightweight visuals
- useful whitespace

---

# 3. REFERENCE DIRECTION

Use Buyhatke and other relevant price-comparison/e-commerce products as UX references for:
- prominent product search
- multi-marketplace comparison
- price history
- price insights
- filters and sorting
- savings indicators
- comparison layouts
- responsive discovery flows

Do **not** copy:
- logos
- branding
- proprietary assets
- exact layouts
- exact wording
- distinctive visual identity

Create an original GeM-oriented design language.

---

# 4. BRAND

## 4.1 Personality

The product should feel:
- trustworthy
- intelligent
- transparent
- modern
- efficient
- analytical
- procurement-oriented

Avoid:
- childish visuals
- excessive gradients
- flashy shopping-ad aesthetics
- clutter
- unnecessary animation
- fake “AI” decoration

## 4.2 Product Naming

Preferred UI label:

**GeM Price Intelligence**

Possible supporting phrase:

**Compare GeM prices with the wider market.**

Do not imply official government ownership or endorsement unless that is actually authorized.

---

# 5. COLOR SYSTEM

Use a restrained professional palette.

### Primary
`#123B66`

Use for:
- primary actions
- active navigation
- key brand elements
- important interactive states

### Primary Dark
`#0B2743`

Use for:
- dark surfaces
- deep emphasis
- footer/deep UI sections

### Brand Accent (Golden)
`#F0C40A`

Use for:
- hero panel highlight
- primary CTA emphasis
- key savings/value highlights
- price-difference emphasis

Golden is the brand accent and should be used sparingly. Do not use it for general "cheaper" states — that is the role of the semantic success/teal colors below.

### Dark Header
`#1F2430`

Use for:
- the top navigation bar
- dark page headers
- surfaces behind the brand mark on dark backgrounds

### Secondary Accent
Teal: `#0F766E`

Use for:
- savings
- positive comparison insights
- analytical accents

### Success
`#15803D`

Use for:
- cheaper price
- savings
- positive price advantage

### Warning
`#B45309`

Use for:
- stale data
- caution
- medium-confidence states

### Error
`#B91C1C`

Use for:
- failures
- unavailable sources
- invalid states

### Neutrals
Primary text: `#172033`  
Secondary text: `#526071`  
Muted text: `#718096`  
Border: `#D9E0E8`  
Surface: `#FFFFFF`  
Page background: `#F6F8FB`

Do not use every color on every screen.

---

# 6. DARK MODE

Dark mode is optional unless supported by the project architecture.

Suggested palette:
- background: `#0B1220`
- surface: `#111827`
- elevated surface: `#172033`
- primary text: `#F3F6FA`
- muted text: `#A7B0BE`
- border: `#273449`

Maintain accessible contrast and do not simply invert colors.

---

# 7. TYPOGRAPHY

Preferred font:

**Inter**

Fallback:
`system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`

Hierarchy:

- Display: 40–56px, 700
- H1: 32–40px, 700
- H2: 24–30px, 700
- H3: 18–22px, 600
- Body: 14–16px, 400
- Small/meta: 12–13px
- Buttons: 14–15px, 600

Use typography for hierarchy instead of excessive color.

---

# 8. SPACING & SHAPE

Base spacing scale:

`4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64`

Suggested corner radius:
- inputs/buttons: 8–10px
- cards/panels: 10–14px
- larger containers: 14–18px

Use subtle borders and restrained shadows.

Avoid arbitrary spacing values unless needed for a specific component.

---

# 9. LAYOUT

Desktop content width:
- approximately 1200–1280px centered

Use responsive:
- grid
- flex
- content-driven sections
- consistent alignment

Avoid excessively wide text lines.

Major pages should share consistent left/right alignment and container behavior.

---

# 10. NAVIGATION

Recommended primary navigation:

**Logo | Compare | Categories | Price History | Analytics | About**

Primary action:

**Compare Prices**

Keep navigation simple.

Mobile navigation should collapse into a compact accessible menu.

---

# 11. HOME PAGE

## Hero

The first screen should explain the product immediately.

Include:
- concise headline
- one-sentence explanation
- large search field
- optional realistic example
- subtle supporting data visual

Suggested headline:

**Find the better price before you buy.**

Suggested supporting line:

**Compare GeM products with prices across major e-marketplaces and understand the difference.**

Do not overload the hero.

### Golden Hero Variant

The primary hero may use a large golden panel (`#F0C40A`) containing the headline and search field, on the light page background, with the dark header bar (`#1F2430`) above it. Use strong dark text on the golden panel for contrast. This matches the intended visual direction without copying any reference site's branding.

## Key Metrics

When real data exists, show a small number of useful metrics:
- Products Analyzed
- Products Matched
- Marketplaces Compared
- Potential Savings

Never fabricate metrics.

---

# 12. SEARCH EXPERIENCE

Search is a primary interaction.

Support:
- product name
- model
- brand
- common keywords

The main search control should provide:
- prominent placement
- clear search icon
- clear/reset affordance
- keyboard accessibility
- debounce
- loading feedback
- suggestions when available

Useful filters:
- category
- price range
- marketplace
- brand
- availability
- sort
- match confidence

---

# 13. SEARCH RESULTS

Each result should make the decision understandable quickly.

Recommended structure:
1. product image, if reliable
2. product name
3. brand/model
4. GeM price
5. best comparable market price
6. price difference
7. savings percentage
8. match confidence
9. source marketplace
10. last updated
11. view comparison CTA

The best relevant price should be obvious but not visually aggressive.

---

# 14. PRODUCT COMPARISON

This is the core experience.

## Header

Show:
- product name
- brand/model
- category
- match confidence
- last updated

## Price Summary

Present:

**GeM Price**  
vs.  
**Market Best Price**

Then clearly show:

**Potential Difference / Savings**

Use strong typography for price values.

## Marketplace Comparison

Use a responsive table on desktop and a stacked/card-based comparison on small screens.

Useful fields:
- marketplace
- listed price
- discount
- availability
- delivery information where reliable
- rating when reliable
- source
- last updated
- difference from GeM

Clearly identify the cheapest comparable option.

Do not use color alone to communicate “cheapest”.

---

# 15. PRICE HISTORY

Price history must answer a real question.

Preferred visualization:
- line chart

Show:
- current price
- lowest price
- highest price
- average price
- selected timeframe

Useful ranges:
- 7 days
- 30 days
- 90 days
- 1 year

Include:
- exact/hover values
- source indicator
- last updated state

Avoid decorative 3D charts.

---

# 16. PRICE INTELLIGENCE

Useful insight components:

### Price Advantage
How much cheaper one source is relative to another.

### Market Average
Average of relevant comparable market listings.

### Potential Savings
Difference between the GeM price and a chosen market benchmark.

### Price Trend
Whether recent prices are rising, falling, or stable.

### Match Confidence
Confidence that the listings represent the same or sufficiently similar product.

These are analytical indicators, not official procurement recommendations.

---

# 17. PRODUCT MATCHING TRANSPARENCY

Provide a simple “Why are these products matched?” explanation.

Possible signals:
- Brand: Matched
- Model: Matched
- Category: Matched
- Key specifications: X% matched
- Overall match confidence: X%

Keep technical ML details behind an expandable explanation when possible.

For uncertain matches, clearly indicate uncertainty.

---

# 18. ANALYTICS DASHBOARD

The dashboard should help users:
- understand market pricing
- identify price gaps
- identify savings opportunities
- see coverage and trends

Possible metrics:
- products analyzed
- products matched
- average GeM price
- average market price
- potential savings
- largest price gaps
- recent price changes

Possible charts:
- GeM vs Market average
- savings by category
- price-gap distribution
- marketplace comparison
- recent price trends

Only show charts when the underlying data exists.

---

# 19. CATEGORY EXPERIENCE

Categories should be:
- searchable
- scannable
- consistent
- data-driven

Each category may show:
- number of products
- average savings
- top price gaps

Avoid oversized decorative category tiles.

---

# 20. COMPONENT SYSTEM

## Buttons

Primary:
- filled primary color
- high contrast
- 8–10px radius
- concise label

Secondary:
- outlined/subtle fill

Danger:
- reserved for destructive actions

Do not create multiple competing primary actions on the same screen.

## Cards

Cards should use:
- consistent radius
- subtle border
- restrained shadow
- predictable padding

## Inputs

Inputs need:
- accessible labels
- clear placeholder
- visible focus state
- validation feedback
- keyboard support

## Badges

Use sparingly for:
- Cheapest
- Best Value
- Matched
- High Confidence
- Stale Data
- Unavailable

Do not turn every piece of metadata into a pill.

---

# 21. DATA STATES

## Loading

Use:
- skeletons for structured content
- stable layout
- minimal spinner usage

## Empty

Explain what happened and what the user can do next.

Example:

**No comparable listings found**

Try another model number or a broader product description.

## Partial Data

Clearly identify missing fields.

Never invent values.

## Stale Data

Show:
**Last updated: X**

and where useful:
**Data may be outdated.**

## Scraping/API Failure

Use actionable language.

Example:

**Market data is temporarily unavailable.**

Do not expose raw stack traces to users.

---

# 22. RESPONSIVE DESIGN

## Desktop
Use:
- comparison tables
- multi-column layouts
- side panels
- richer charts

## Tablet
Reduce:
- column count
- information density

Maintain readability.

## Mobile

Prioritize:
1. product
2. GeM price
3. best market price
4. savings/difference
5. source
6. last updated
7. details

Convert large tables into stacked comparison cards or limited horizontal scrollers.

Never make the entire page require horizontal scrolling.

---

# 23. ACCESSIBILITY

Required:
- semantic HTML
- keyboard navigation
- visible focus states
- accessible labels
- adequate color contrast
- readable type sizes
- meaningful alt text
- icons are not the sole carrier of meaning
- color is not the sole indicator
- charts include supporting text/context

---

# 24. MOTION

Motion should be subtle and functional.

Good:
- hover feedback
- button feedback
- skeleton transitions
- small panel transitions

Avoid:
- constant animation
- distracting parallax
- long transitions
- unnecessary animated charts

Never let motion reduce perceived performance.

---

# 25. IMAGES & ASSETS

Use product images only when:
- relevant
- reliable
- obtained through an appropriate source

Do not infer product specifications from decorative imagery.

For missing imagery, use a consistent neutral placeholder.

Do not use logos or proprietary visual assets from reference sites as project assets.

---

# 26. PERFORMANCE

UI should support:
- debounced search
- pagination/incremental loading
- lazy loading
- caching
- minimized unnecessary API calls
- efficient chart rendering
- responsive interactions

Avoid large client-side dependencies without justification.

---

# 27. CONTENT STYLE

UI copy should be:
- concise
- plain
- professional
- action-oriented

Prefer:
**Compare Prices**

over:
**Click here to initiate a comprehensive price-comparison operation**

Use technical terms only when they help the user.

---

# 28. TRUST & DISCLAIMERS

Where relevant, communicate:
- market data may change
- scraped data can become stale
- product matches are algorithmic
- results are informational
- GeM affiliation should not be implied unless officially authorized

Disclaimers should be visible but unobtrusive.

---

# 29. AGENT IMPLEMENTATION RULES

Before creating or reviewing a UI component:

1. Read `DESIGN.md`.
2. Find and reuse existing components before creating duplicates.
3. Reuse established design tokens.
4. Follow spacing, typography, color, and interaction rules.
5. Test responsive behavior.
6. Check accessibility.
7. Avoid arbitrary styles.
8. Keep UI consistent across screens.
9. Update this document only when the design system intentionally evolves.

---

# 30. DEFINITION OF A “BEST INTERFACE”

A successful implementation should let a new user answer these questions within seconds:

1. What product am I looking at?
2. What is the GeM price?
3. What is the best comparable market price?
4. How much is the difference?
5. Where is the cheaper listing?
6. Are these products really comparable?
7. When was the data collected?

If a screen does not make these answers clear for its relevant use case, improve the hierarchy before adding more decoration.


## 30.1 LOGO USAGE

The brand logo is a monochrome dark mark on a light background, located in:

`design reference/logo/`

Rules:
- Place the logo at a minimum display height of 28px in the header.
- Preserve clear space around the mark equal to roughly 1/4 of its height; do not crowd it with text or icons.
- On dark surfaces (`#1F2430`, `#0B2743`), use an inverted (white) variant of the mark.
- Never recolor, outline, rotate, or distort the logo.
- Use a simple logo-derived favicon (no proprietary third-party icon).
- The logo is the project-provided brand asset; treat it as the primary brand reference.

---

## 31. Governance

This document is the authoritative visual/UX reference for the project. When implementation decisions conflict with this document, resolve the conflict deliberately and update the design system when the visual rule has intentionally changed.
# Design References

The project contains visual references in:

`design reference/`

## Logo
Use the logo from:

`design reference/logo/`

The logo is a project-provided asset and should be treated as the primary brand reference.

## Website Visual References
Reference screenshots are stored in:

`design reference/website-samples/`

These images define the visual direction, layout inspiration, information hierarchy, spacing, and interaction patterns desired by the project owner.

Do not copy proprietary branding or exact layouts from reference websites.
Use the references to reproduce the intended visual quality and adapt the design to the GeM Price Comparison project.

When implementing UI:
1. Inspect the reference images.
2. Follow the project's `DESIGN.md`.
3. Use the provided logo.
4. Preserve the intended visual hierarchy and overall feel.
5. Improve usability where appropriate without changing the intended design direction.