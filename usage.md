# D&D Character Sheet API — Usage Reference

This document covers request structure, response schema, and error code reference for all API endpoints. Authentication is optional, unauthenticated access is supported with reduced rate limits and session windows. Tokens are manually issued by the API owner; there is no self-service registration endpoint.

---

## Authentication

### Authenticated Access

Include a Bearer token in the `Authorization` header on all generation requests:

Authorization: Bearer <your_token>

| Property          | Value       |
|-------------------|-------------|
| Session window    | 65 minutes  |
| Rate limit        | 6 req/sec   |
| Session cooldown  | 12 hours    |
| Token hard expiry | 90 days     |

Once a session expires, a 12-hour cooldown is enforced before a new session can begin. Tokens are non-renewable after the 90-day hard expiry.

### Unauthenticated Access

Requests without an `Authorization` header are permitted and tracked by IP.

| Property         | Value       |
|------------------|-------------|
| Session window   | 30 minutes  |
| Rate limit       | 3 req/sec   |
| Session cooldown | 24 hours    |

---

## Response Envelope

All responses follow the [JSend specification](https://github.com/omniti-labs/jsend). Every response includes `status`, `message`, and `data` fields. Rate limit breaches return `429` via a custom error template.

**Success:**
```json
{
  "status": "success",
  "message": "",
  "data": {
    "code": 200,
    ...
  }
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Request validation failed.",
  "data": {
    "code": "",
    "errors": []
  }
}
```

---

## Routes

### /generator-2014 · /generator-2024 · /generator-random

All three generation endpoints share the same request and response structure.

#### Request Structure

```json
{
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer <token>"
  },
  "body": {
    "Edition": "",
    "Class": "",
    "Level": 1,
    "Quantity": 1,
    "project_name": "",
    "campaign_name": "",
    "region": "",
    "origin": "",
    "sigil": "",
    "codex": "",
    "realm": "",
    "guild": ""
  }
}
```

#### Required Fields

**Authorization**: `Bearer ` followed by your issued token. Omit entirely for unauthenticated access (see above). <br>
**Edition**: `"5e"`, `"5.5e"`, `"random"`, or blank for random edition selection. <br>
**Class**: Any SRD class name, `"random"`, blank string `""`, or `null` for a random class. <br>
**Level**: `1`–`20` for a specific level, or `0` for random. <br>
**Quantity**: Number of character sheets to return, `1`–`10`.

#### Optional Organizational Fields

The following fields have no effect on character sheet generation. Any values provided are echoed back in the response as-is, and exist solely for the caller's organizational purposes.

| Field           | Description                        |
|-----------------|------------------------------------|
| `project_name`  | Arbitrary project identifier       |
| `campaign_name` | Campaign name or label             |
| `region`        | Region or setting label            |
| `origin`        | Origin or backstory tag            |
| `sigil`         | Faction or sigil label             |
| `codex`         | Codex or ruleset tag               |
| `realm`         | Realm or world label               |
| `guild`         | Guild or organization label        |

#### Response Structure (success)

```json
{
  "status": "success",
  "message": "Generated {num} characters",
  "data": {
    "code": 200,
    "character": [
      {}
    ]
  }
}
```

**character**: List of JSON objects, one per generated character sheet.

#### Response Structure (error)

```json
{
  "status": "error",
  "message": "Request validation failed.",
  "data": {
    "code": "",
    "errors": []
  }
}
```

**code**: HTTP status code (see table below). <br>
**errors**: List of validation errors encountered against the provided fields.

#### Potential Errors

| Status | Message                    | Description                                                    |
|--------|----------------------------|----------------------------------------------------------------|
| 400    | Body cannot be empty.      | No JSON body was sent with the request                         |
| 422    | Request validation failed. | One or more fields failed validation, see `errors` for details |
| 429    |                            | Rate limit exceeded, wait before retrying                      |

#### 422 Validation Errors

| Reason                                                                  | Error Message                                                                           |
|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Edition is not `5e`, `5.5e`, `random`, blank, or `None`                 | `Edition '{dnd_edition}' is not supported by this API, only 5e and 5.5e are supported.` |
| Class is not in SRD documents                                           | `Class '{dnd_class}' is not an accepted SRD Class.`                                     |
| Level is less than 0 or greater than 20                                 | `Level '{dnd_level}' is outside bounds of 0-20.`                                        |
| Level is not a clean string or integer representation of an integer     | `Level '{dnd_level}' cannot be converted to an integer.`                                |
| Quantity is less than 1 or greater than 10                              | `Quantity '{dnd_quantity}' is outside bounds of 1-10.`                                  |
| Quantity is not a clean string or integer representation of an integer  | `Quantity '{dnd_quantity}' cannot be converted to an integer.`                          |