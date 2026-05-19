# D&D Character Sheet API

A self-hosted Flask API that generates mechanically accurate D&D 5e (2014) and 5.5e (2024) character sheets on demand, derived from the Systems Reference Document. Built as the server side of a larger portfolio showcase demonstrating full-stack API design, from auth contract to concurrent client consumption to downstream data pipeline.

The character sheet generation logic originates from a separate encounter balancing project, where mechanical accuracy is a hard requirement. It serves here as the content layer for the API, producing structured, rule-compliant output rather than arbitrary placeholder data. Spell slots, class features, cantrips, and equipment are accumulated correctly across all 20 levels for each SRD-legal class.

---

## What This Is

This is not a hello world Flask app. It is a deliberately designed API with a defined auth contract, structured request validation, consistent response envelopes, and a layered security model. It is intended to be read alongside its companion client, which consumes it under concurrent load and feeds the results into a downstream PostgreSQL pipeline.

The design is informed by experience on the consuming side of real REST API integrations. Building the server from scratch against that experience was the point, to demonstrate that the knowledge runs in both directions.

---

## Architecture

**Auth layer:** Token-based authentication using a Bearer token in the `Authorization` header. Tokens are manually issued by the API owner and stored in a private SQLite database. Authenticated users receive a 65-minute session window, a 6 requests/second rate limit, and a 12-hour cooldown between sessions. Tokens carry a 90-day hard expiry. Unauthenticated users are tracked by IP, receiving a 30-minute session window, a 3 requests/second rate limit, and a 24-hour cooldown after session expiry. There are no exposed paths for user management, provisioning happens directly at the database level, keeping that surface area off the network entirely.

**Request enforcement:** A global `before_request` hook validates every incoming request before any route handler runs. No route is reachable without passing that gate first.

**Session and rate limit state:** Redis handles session caching for both authenticated and unauthenticated users. Flask-Limiter is also backed by Redis, ensuring rate limit state is consistent across Gunicorn workers.

**Response envelope:** All responses follow the JSend specification — consistent structure across success, failure, and error states. Rate limit breaches return a `429` via a custom error template. See `usage.md` for the full response schema and error code reference.

**Nginx layer:** An auth check at the nginx level turns away malformed or unauthorized requests before they reach Flask. Configuration included below.

**WSGI:** Gunicorn serves the Flask application in production.

---

## Stack

- Python with Flask
- Gunicorn (WSGI server)
- nginx (reverse proxy with auth check)
- Redis (session cache and rate limit state)
- SQLite (local user store)
- Flask-Limiter
- AppLogging (personal PyPI package)
- python-dotenv

---

## Endpoints

Three generation endpoints are implemented and functioning, all accepting `POST` requests with a JSON body. Full request structure, response shape, and error codes are documented in `usage.md`.

| Method | Path                | Description                                   |
|--------|---------------------|-----------------------------------------------|
| POST   | `/get-token`        | Exchange credentials for a time-limited token |
| POST   | `/generator-2014`   | Generate character sheet for 5e (2014) SRD    |
| POST   | `/generator-2024`   | Generate character sheet for 5.5e (2024) SRD  |
| POST   | `/generator-random` | Generate character sheet for 5e or 5.5e SRD   |

### Request Body Fields

| Field           | Values                          | Description                                              |
|-----------------|---------------------------------|----------------------------------------------------------|
| `Edition`       | `5e`, `5.5e`, `random`          | Ruleset to generate against                              |
| `Class`         | Any SRD class, `random`         | Character class                                          |
| `Level`         | `0`–`20`                        | Character level (`0` selects randomly)                   |
| `Quantity`      | `1`–`10`                        | Number of character sheets to generate                   |

The following optional fields are organizational only — they are echoed back in the response as-is and have no effect on generation: `project_name`, `campaign_name`, `region`, `origin`, `sigil`, `codex`, `realm`, `guild`.

---

## Nginx Configuration

The following nginx configuration sits in front of the Flask application. The auth check at this layer filters requests before they reach Gunicorn.
Please see `/config/dnd_api.conf` for a sample nginx configuration server block.

---

## Running Locally

> Full setup instructions to be added on first release. The API is designed to run on self-hosted infrastructure behind nginx, but can be run locally with Gunicorn or Flask's development server for testing purposes.

---

## Related Projects

- **Concurrent Client** — The intended consumer of this API. Dispatches up to 4 concurrent threads, ingests the character sheet payload from each response, and loads aggregated results into PostgreSQL. *(Repository link to be added)*
- **D&D Encounter Balancer** — The permanent home of the character sheet generation logic once this showcase is complete. *(Repository link to be added)*

---

## Documentation

`usage.md` — Request structure, response schema, and error code reference.
