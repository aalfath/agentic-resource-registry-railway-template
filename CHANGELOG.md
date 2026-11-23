# Changelog

Railway shows an update notice when this repository's `main` branch changes. Read the entry for the new version before you apply it.

## 1.17.1 (2026-11-23)

- First release: Agentic Resource Registry 1.17.1 (`observal-api` and `observal-web` 1.17.1) with ClickHouse 26.6.8.7, every image pinned by digest.
- The first super admin is created from `ADMIN_EMAIL` / `ADMIN_PASSWORD` on first boot; upstream's demo accounts are never seeded.
- JWT signing keys on the API's `/data` volume; ClickHouse data on its own volume.
- Deploy on Railway button added to this README (published template `agentic-resource-registry`).
