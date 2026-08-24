# External Changes Log

| Date | Action | Scope | Reversible | Notes |
|------|--------|-------|------------|-------|
| 2026-08-21 | Install Android SDK build-tools;36.0.0 via sdkmanager | device-wide (Android SDK) | yes — uninstall via sdkmanager or delete build-tools/36.0.0 folder | Required for Gradle release build (Expo SDK 57 needs build-tools 36.0.0) |
| 2026-08-22 | Create staging database `gem_unified` in website PostgreSQL | project-scoped (Docker container) | yes — `DROP DATABASE gem_unified` | Unified schema for merged website+mobile data |
| 2026-08-22 | Migrate website (`gem_price`) + mobile (`gem_prices`) → `gem_unified` | project-scoped (Docker container) | yes — restore from backup files | 160 products, 376 listings, 480 price history records migrated |
| 2026-08-22 | Backend API updated to use unified database (`gem_unified`) | project-scoped (Docker container) | yes — revert config | Config updated, models/schemas/routes merged, all 41 backend tests pass |
| 2026-08-22 | Pipeline code updated to use `availability` field | project-scoped | yes — revert code | Scraper pipeline now uses correct field name |