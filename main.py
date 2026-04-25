import sqlite3, hashlib, os, secrets, bcrypt

from AppLogging import AppLogging
from random import randint, choice
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv, find_dotenv

from DND_generators.Classes_2014.Barbarian import Barbarian2014
from DND_generators.Classes_2014.Bard import Bard2014
from DND_generators.Classes_2014.Cleric import Cleric2014
from DND_generators.Classes_2014.Druid import Druid2014
from DND_generators.Classes_2014.Fighter import Fighter2014
from DND_generators.Classes_2014.Monk import Monk2014
from DND_generators.Classes_2014.Paladin import Paladin2014
from DND_generators.Classes_2014.Ranger import Ranger2014
from DND_generators.Classes_2014.Rogue import Rogue2014
from DND_generators.Classes_2014.Sorcerer import Sorcerer2014
from DND_generators.Classes_2014.Warlock import Warlock2014
from DND_generators.Classes_2014.Wizard import Wizard2014

from DND_generators.Classes_2024.Barbarian import Barbarian2024
from DND_generators.Classes_2024.Bard import Bard2024
from DND_generators.Classes_2024.Cleric import Cleric2024
from DND_generators.Classes_2024.Druid import Druid2024
from DND_generators.Classes_2024.Fighter import Fighter2024
from DND_generators.Classes_2024.Monk import Monk2024
from DND_generators.Classes_2024.Paladin import Paladin2024
from DND_generators.Classes_2024.Ranger import Ranger2024
from DND_generators.Classes_2024.Rogue import Rogue2024
from DND_generators.Classes_2024.Sorcerer import Sorcerer2024
from DND_generators.Classes_2024.Warlock import Warlock2024
from DND_generators.Classes_2024.Wizard import Wizard2024

app = Flask(__name__)

def _format_response_character(characters: list[dict]) -> dict:

    response = {
        "data": {
            "code": 200,
            "characters": characters
        },
        "message": f"Generated {len(characters)} characters",
        "status": "success"
    }

    return response

def _format_response_error(status: int, reasons: list[str]) -> dict:
    response = {
        "data": {
            "code": status,
            "errors": reasons
        },
        "message": "Request validation failed.",
        "status": "error"
    }
    return response

def _format_token_response(status: int, token: str, current_time: datetime) -> dict:
    expiration_time = datetime.strftime(current_time + timedelta(minutes=60), "%Y-%m-%d %H:%M:%S")
    response = {
        "data": {
            "code": status,
            "token": token,
            "expires": expiration_time
        },
        "message": "Issued Authorization token.",
        "status": "success"
    }
    return response

def _validate_body(body: dict) -> tuple[int, list[str], tuple]:

    status = 200
    reason = []

    dnd_edition = body.get("Edition", "random").strip().lower()
    dnd_class = body.get("Class", "random").strip().capitalize()
    dnd_level = body.get("Level", 0)
    dnd_quantity = body.get("Quantity", 1)
    # dnd_race = body.get("Race", None)
    # dnd_spells = body.get("Spells", None)
    # dnd_feats = body.get("Feats", None)
    # dnd_armor = body.get("Armor", None)
    # dnd_shields = body.get("Shields", None)
    # dnd_weapons = body.get("Weapons", None)
    # dnd_cantrips = body.get("Cantrips", None)

    accepted_editions = ["5e", "5.5e"]

    accepted_classnames = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    ]

    if dnd_edition not in accepted_editions:
        reason.append(f"Edition '{dnd_edition}' is not supported by this API, only 5e and 5.5e are supported.")

    if dnd_class not in accepted_classnames:
        reason.append(f"Class '{dnd_class}' is not an accepted SRD Class.")

    try:
        dnd_level = int(dnd_level)
        if dnd_level < 0 or dnd_level > 20:
            reason.append(f"Level '{dnd_level}' is outside bounds of 0-20.")
    except ValueError:
        reason.append(f"Level '{dnd_level}' cannot be converted to an integer.")

    try:
        dnd_quantity = int(dnd_quantity)
        if dnd_quantity < 1 or dnd_quantity > 10:
            reason.append(f"Quantity '{dnd_quantity}' is outside bounds of 1-10.")
    except ValueError:
        reason.append(f"Quantity '{dnd_quantity}' cannot be converted to an integer.")

    if len(reason) > 0:
        status = 422

    character_stats = (
        dnd_edition,
        dnd_class,
        dnd_level,
        dnd_quantity
    )

    return status, reason, character_stats

def _get_dnd_class_2014(dnd_class: str):
    dnd_classes = {
        "Barbarian": Barbarian2014,
        "Bard": Bard2014,
        "Cleric": Cleric2014,
        "Druid": Druid2014,
        "Fighter": Fighter2014,
        "Monk": Monk2014,
        "Paladin": Paladin2014,
        "Ranger": Ranger2014,
        "Rogue": Rogue2014,
        "Sorcerer": Sorcerer2014,
        "Warlock": Warlock2014,
        "Wizard": Wizard2014
    }

    if dnd_class == "random":
        dnd_class = choice(list(dnd_classes.keys()))

    return dnd_classes[dnd_class]

def _get_dnd_class_2024(dnd_class: str):
    dnd_classes = {
        "Barbarian": Barbarian2024,
        "Bard": Bard2024,
        "Cleric": Cleric2024,
        "Druid": Druid2024,
        "Fighter": Fighter2024,
        "Monk": Monk2024,
        "Paladin": Paladin2024,
        "Ranger": Ranger2024,
        "Rogue": Rogue2024,
        "Sorcerer": Sorcerer2024,
        "Warlock": Warlock2024,
        "Wizard": Wizard2024
    }

    if dnd_class == "random":
        dnd_class = choice(list(dnd_classes.keys()))

    return dnd_classes[dnd_class]

def _build_2014(character_stats: tuple) -> list[dict]:

    _, dnd_class, dnd_level, dnd_quantity = character_stats
    characters = []

    for _ in range(dnd_quantity):
        character_class = _get_dnd_class_2014(dnd_class)
        character = character_class()
        if dnd_level == 0:
            temp_level = randint(1, 20)
            character.build_character(level=temp_level)
        else:
            character.build_character(level=dnd_level)
        characters.append(character.__dict__)

    return characters


def _build_2024(character_stats: tuple) -> list[dict]:
    _, dnd_class, dnd_level, dnd_quantity = character_stats
    characters = []

    for _ in range(dnd_quantity):
        character = _get_dnd_class_2024(dnd_class)
        if dnd_level == 0:
            temp_level = randint(1, 20)
            character.build_character(level=temp_level)
        else:
            character.build_character(level=dnd_level)
        characters.append(character.__dict__)

    return characters

def _build_random(character_stats: tuple) -> list[dict]:
    _, dnd_class, dnd_level, dnd_quantity = character_stats
    characters = []

    for _ in range(dnd_quantity):
        edition = randint(1, 2)
        if edition == 1:
            character = _get_dnd_class_2014(dnd_class)
        else:
            character = _get_dnd_class_2024(dnd_class)
        if dnd_level == 0:
            temp_level = randint(1, 20)
            character.build_character(level=temp_level)
        else:
            character.build_character(level=dnd_level)
        characters.append(character.__dict__)

    return characters

def _build_characters(character_stats: tuple) -> list[dict]:

    dnd_edition, _, _, _ = character_stats
    characters = []

    if dnd_edition == "5e":
        characters = _build_2014(character_stats)
    elif dnd_edition == "5.5e":
        characters = _build_2024(character_stats)
    elif dnd_edition == "random":
        characters = _build_random(character_stats)

    return characters

def _create_database():
    database_name = "api_hammer.db"
    try:
        connection = sqlite3.connect(database_name)

        connection.commit()
        connection.close()

    except sqlite3.Error:
        raise RuntimeError("Database connection error")

def _create_table():
    database_name = "api_hammer.db"
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                api_token TEXT NULL,
                api_token_creation DATETIME NULL,
                api_token_last_used DATETIME NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

    except sqlite3.Error:
        raise RuntimeError("Database connection error")

def _query_token_time(token: str):
    database_name = "api_hammer.db"
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT api_token_creation, api_token_last_used
            FROM users
            WHERE api_token = ?
        """, (token,))

        result = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result

    except sqlite3.Error:
        raise RuntimeError("Database connection error")

    return None

def _query_full_user(username: str):
    database_name = "api_hammer.db"
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT user_id, password, api_token, api_token_creation, api_token_last_used 
            FROM users
            WHERE username = ?
        """, (username,))
        user_details = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return user_details
    except sqlite3.Error:
        raise RuntimeError("Database connection error")

def _insert_token(token: str, user_id: int, passed_username: str, current_time: datetime):
    database_name = "api_hammer.db"
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (user_id, api_token, api_token_creation, api_token_last_used)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET
                api_token = COALESCE(EXCLUDED.api_token, users.api_token),
                api_token_creation = COALESCE(EXCLUDED.api_token_creation, users.api_token_creation),
                api_token_last_used = COALESCE(EXCLUDED.api_token_last_used, users.api_token_last_used)
        """, (user_id, token, current_time, current_time,))

        connection.commit()
        cursor.close()
        connection.close()

    except sqlite3.Error:
        raise RuntimeError("Database connection error")

def _generate_token(user_id: str, passed_username: str, passed_grant_type: str, current_time: datetime) -> str:

    server_secret = os.getenv("SECRET")
    extra_bits = secrets.token_bytes(32)

    token_str_build = (f"{user_id}_\n"
                       f"{passed_username}_\n"
                       f"{passed_grant_type}_\n"
                       f"{current_time}_\n"
                       f"{server_secret}_\n"
                       f"{extra_bits}")

    token = hashlib.sha256(token_str_build.encode('utf-8')).hexdigest()
    return token

def _validate_token(token: str) -> tuple[int, str]:

    db_info = _query_token_time(token)
    if not db_info:
        return 401, ""

    token_creation, token_last_used = db_info
    current_time = datetime.now()

    time_difference_last_used = current_time - datetime.strptime(token_last_used, "%Y-%m-%d %H:%M:%S.%f")
    if time_difference_last_used > timedelta(minutes=5):
        return 401, "Token Expired."

    time_difference_creation = current_time - datetime.strptime(token_creation, "%Y-%m-%d %H:%M:%S.%f")
    if time_difference_creation > timedelta(minutes=65):
        return 401, "Token Expired."

    return 200, ""

def _validate_request() -> tuple[int, str]:
    headers = request.headers
    body = request.get_json() or {}
    path = request.path

    if path == r"/get-token" and any(not val for val in body.values()):
        return 401, ""
    elif path != r"/get-token":
        auth = headers.get("Authorization", None)
        if not auth:
            return 401, ""

        auth_token = auth.strip("Bearer ")
        status, reason = _validate_token(auth_token)
        if status != 200:
            return status, reason

    return 200, ""

@app.before_request
def enforce_policy():

    allowed_paths = {
        r"/generator-2014",
        r"/generator-2024",
        r"/generator-random",
        r"/get-token",
    }

    if request.path not in allowed_paths:
        abort(404)

    status, reason = _validate_request()
    if status != 200:
        return _format_response_error(status, [reason]), status

    return None


@app.route(rule='/generator-2014', methods=["POST"])
def generator_2014():

    body = request.get_json() or {}

    if not body:
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2014 = _build_characters(character_stats)
    if not character_sheet_2014:
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2014)

    return jsonify(response), 200

@app.route(rule='/generator-2024', methods=["POST"])
def generator_2024():

    body = request.get_json() or {}

    if not body:
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2024 = _build_characters(character_stats)
    if not character_sheet_2024:
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2024)

    return jsonify(response), 200

@app.route(rule='/generator-random', methods=["POST"])
def generator_random():

    body = request.get_json() or {}

    if not body:
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_random = _build_characters(character_stats)
    if not character_sheet_random:
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_random)

    return jsonify(response), 200

@app.route(rule='/get-token', methods=["POST"])
def get_token():
    data = request.get_json() or {}

    if not data:
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    passed_username = data.get("username", None)
    passed_password = data.get("password", None)
    passed_grant_type = data.get("grant_type", None)

    if not passed_username or not passed_password or not passed_grant_type:
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    current_time = datetime.now()

    user_details = _query_full_user(passed_username)
    if not user_details:
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    user_id, user_pw, _, api_token_creation, _ = user_details
    if not bcrypt.checkpw(passed_password.encode('utf-8'), user_pw):
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    if api_token_creation:
        time_difference = current_time - datetime.strptime(api_token_creation, "%Y-%m-%d %H:%M:%S.%f")
        if time_difference < timedelta(hours=24):
            return jsonify(_format_response_error(403, ["Token Expired"])), 403

    token = _generate_token(user_id, passed_username, passed_grant_type, current_time)
    _insert_token(token, user_id, passed_username, current_time)

    status = 200
    response = _format_token_response(status, token, current_time)

    return jsonify(response), status

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    app.run()
