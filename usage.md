## Route: /get-token

### Request Structure

```json
{
  "headers": {
    
  },
  "body": {
    "grant_type": "query_access",
    "username": "",
    "password": ""
  }
}
```
#### Fillable Fields
**No headers are required at this time for `/get-token`** <br>
**username**: plaintext username <br>
**password**: plaintext password

### Response Structure (success)

```json
{
  "data": {
    "code": 200,
    "token": "",
    "expires": ""
  },
  "message": "Issued Authorization token.",
  "status": "success"
}
```
#### Received Fields
**token**: generated token (save this, it will not appear again) <br>
**expires**: date formatted object (%Y-%m-%d %H:%M:%S.%f) of 1 hour after creation time

### Response Structure (error)

```json
{
  "data": {
    "code": "",
    "errors": []
  },
  "message": "Request validation failed.",
  "status": "error"
}
```
#### Received Fields
**code**: status code (see table below) <br>
**errors**: A List of errors encountered with passed 'Fillable Fields' (see above)

### Potential Errors

| status | message        | Description                                                   |
|--------|----------------|---------------------------------------------------------------|
| 401    |                | User not found in database                                    |
| 401    | Token Expired. | Expired token, must wait 24 hours before requesting a new one |
**Note:** Here the 401 message is intentionally left blank to avoid disclosing whether a username exists in the system.

## Route(s): /generator-2014 /generator-2024 /generator-random

### Request Structure

```json
{
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer "
  },
  "body": {
    "Edition": "",
    "Class": "",
    "Level": 1,
    "Quantity": 1
  }
}
```
#### Fillable Fields
**Authorization**: "Bearer " followed by the token received from `/get-token` <br>
**Edition**: "5e", "5.5e", or "random" or blank for random edition generation <br>
**Class**: Class of desired character sheet, only 2014 and 2024 SRD classes only <br>
&emsp; Class can be an SRD Class, blank string "", or null for a random class<br>
**Level**: Desired level of character, 1-20 for standard, or 0 for random level <br>
**Quantity**: How many character sheets you want returned, 1-10

### Response Structure (success)

```json
{
  "data": {
    "code": 200,
    "character": [
      {}
    ]
  },
  "message": "Generated {num} characters",
  "status": "success"
}
```
#### Received Fields
**character**: List of JSON objects containing character sheets <br>

### Response Structure (error)
```json
{
  "data": {
    "code": "",
    "errors": []
  },
  "message": "Request validation failed.",
  "status": "error"
}
```
#### Received Fields
**code**: status code (see table below) <br>
**errors**: A List of errors encountered with passed 'Fillable Fields' (see above)

### Potential Errors

| status | message                     | Description                                                                |
|--------|-----------------------------|----------------------------------------------------------------------------|
| 400    | Body cannot be empty.       | No body/data json was sent in request                                      |
| 422    | Request validation failed.  | Potential mismatch in passed Character Stats (see errors for more details) |

### List of 422 'errors' returned in data['errors']
 
| Reason                                                                 | Error Message                                                                           |
|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Edition is not `5e`, `5.5e`, `random`, blank, or `None`                | `Edition '{dnd_edition}' is not supported by this API, only 5e and 5.5e are supported.` |
| Class is not in SRD documents                                          | `Class '{dnd_class}' is not an accepted SRD Class.`                                     |
| Level is less than 0 or greater than 20                                | `Level '{dnd_level}' is outside bounds of 0-20.`                                        |
| Level is not a clean string or integer representation of an integer    | `Level '{dnd_level}' cannot be converted to an integer.`                                |
| Quantity is less than 1 or greater than 10                             | `Quantity '{dnd_quantity}' is outside bounds of 1-10.`                                  |
| Quantity is not a clean string or integer representation of an integer | `Quantity '{dnd_quantity}' cannot be converted to an integer.`                          |
