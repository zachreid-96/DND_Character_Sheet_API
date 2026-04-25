# D&D Character Sheet API

A self-hosted Flask API that generates mechanically accurate D&D 5e and 5.5e character sheets on demand, derived from the Systems Reference Document. Built as the server side of a larger portfolio showcase demonstrating full-stack API design, from auth contract to concurrent client consumption to downstream data pipeline.

The character sheet generation logic originates from a separate encounter balancing project, where mechanical accuracy is a hard requirement. It serves here as the content layer for the API, producing structured, rule-compliant output rather than arbitrary placeholder data. Spell slots, class features, cantrips, and equipment are accumulated correctly across all 20 levels for each SRD-legal class.

---

## What This Is

This is not a hello world Flask app. It is a deliberately designed API with a defined auth contract, structured request validation, consistent response envelopes, and a layered security model. It is intended to be read alongside its companion client, which consumes it under concurrent load and feeds the results into a downstream PostgreSQL pipeline.

The design is informed by experience on the consuming side of real REST API integrations. Building the server from scratch against that experience was the point, to demonstrate that the knowledge runs in both directions.

---

## Architecture

**Auth layer:** Token-based authentication with TTL enforcement. Tokens are issued via a dedicated endpoint and must accompany all subsequent requests. There are no exposed paths for user management, no `/admin`, no `/add-user`, nothing of that nature. User provisioning happens directly at the database level, outside the API entirely, which keeps that surface area off the network completely.

**Request enforcement:** A global `before_request` hook validates every incoming request before any route handler runs. No route is reachable without passing that gate first.

**Response envelope:** All responses follow the JSend specification, consistent structure across success, failure, and error states. See `usage.md` for the full response schema and error code reference.

**Nginx layer:** An auth check at the nginx level turns away malformed or unauthorized requests before they reach Flask. Configuration included below.

**WSGI:** Gunicorn serves the Flask application in production.

---

## Stack

- Python with Flask
- Gunicorn (WSGI server)
- nginx (reverse proxy with auth check)
- SQLite (local user store)

---

## Endpoints

Four endpoints are implemented and functioning. Full request structure, response shape, and error codes are documented in `usage.md`.

| Method | Path                | Description                                   |
|--------|---------------------|-----------------------------------------------|
| POST   | `/get-token`        | Exchange credentials for a time-limited token |
| POST   | `/generator-2014`   | Generate Character Sheet for 5e SRD           |
| POST   | `/generator-2024`   | Generate Character Sheet for 5.5e SRD         |
| POST   | `/generator-random` | Generate Character Sheet for 5e or 5.5e SRD   |

---

## Nginx Configuration

The following nginx configuration sits in front of the Flask application. The auth check at this layer filters requests before they reach Gunicorn.

```nginx
# Placeholder — configuration to be included on first release
```

---

## Running Locally

> Full setup instructions to be added on first release. The API is designed to run on self-hosted infrastructure behind nginx, but can be run locally with Gunicorn or Flask's development server for testing purposes.

---

## Related Projects

- **Concurrent Client** — The intended consumer of this API. Dispatches up to 50 concurrent threads, ingests the character sheet payload from each response, and loads aggregated results into PostgreSQL. *(Repository link to be added)*
- **D&D Encounter Balancer** — The permanent home of the character sheet generation logic once this showcase is complete. *(Repository link to be added)*

---

## Documentation

`usage.md` — Request structure, response schema, and error code reference.