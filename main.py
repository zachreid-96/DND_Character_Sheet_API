import sqlite3, hashlib, os, secrets, bcrypt, inspect, redis

from pathlib import Path
from AppLogging import AppLogging
from random import randint, choice
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort, Response, make_response, render_template
from dotenv import load_dotenv, find_dotenv
from flask_limiter import Limiter, RequestLimit
from flask_limiter.util import get_remote_address

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

load_dotenv(find_dotenv())
dnd_log_path = os.getenv("DND_LOG_PATH")
AppLogging.setup_logger(name="dnd_api", dir_log=Path(dnd_log_path), file_level="INFO", console_level="CRITICAL")
app = Flask(__name__)

redis_port = int(os.getenv("REDIS_PORT"))
redis_host = os.getenv("REDIS_HOST")

def _default_limit_exceeded(request_limit: RequestLimit):
    return make_response(
        render_template("my_ratelimit_template.tmpl", request_limit=request_limit),
        429
    )

def _get_dynamic_rate_limit():
    if request.headers.get("Authorization", None):
        return "6 per second"
    return "3 per second"

def _get_dynamic_key_func():
    _token = request.headers.get("Authorization", None)
    if _token:
        return _token.removeprefix("Bearer ")
    return get_remote_address()

limiter = Limiter(
    key_func=_get_dynamic_key_func,
    app=app,
    storage_uri=f"redis://{redis_host}:{redis_port}",
    default_limits=[_get_dynamic_rate_limit],
    on_breach=_default_limit_exceeded
)

redis_cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


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
    expiration_time = datetime.strftime(current_time + timedelta(minutes=60), "%Y-%m-%d %H:%M:%S.%f")
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

def _validate_body(body: dict) -> tuple[int, list[str], tuple[str, str, int, int]]:

    status = 200
    reasons = []

    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

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
        reasons.append(f"Edition '{dnd_edition}' is not supported by this API, only 5e and 5.5e are supported.")

    if dnd_class not in accepted_classnames:
        reasons.append(f"Class '{dnd_class}' is not an accepted SRD Class.")

    try:
        dnd_level = int(dnd_level)
        if dnd_level < 0 or dnd_level > 20:
            reasons.append(f"Level '{dnd_level}' is outside bounds of 0-20.")
    except ValueError:
        reasons.append(f"Level '{dnd_level}' cannot be converted to an integer.")

    try:
        dnd_quantity = int(dnd_quantity)
        if dnd_quantity < 1 or dnd_quantity > 10:
            reasons.append(f"Quantity '{dnd_quantity}' is outside bounds of 1-10.")
    except ValueError:
        reasons.append(f"Quantity '{dnd_quantity}' cannot be converted to an integer.")

    if len(reasons) > 0:
        status = 422
        logger.info(reasons)

    character_stats = (
        dnd_edition,
        dnd_class,
        dnd_level,
        dnd_quantity
    )

    return status, reasons, character_stats

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
        character_class = _get_dnd_class_2024(dnd_class)
        character = character_class()
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
            character_class = _get_dnd_class_2014(dnd_class)
        else:
            character_class = _get_dnd_class_2024(dnd_class)

        character = character_class()
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

def _create_database() -> None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    try:
        connection = sqlite3.connect(database_name)

        connection.commit()
        connection.close()

    except sqlite3.Error:
        logger.error("Unable to create database")
        raise RuntimeError("Database connection error")

def _create_table() -> None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_email TEXT,
                user_project TEXT,
                api_token TEXT NULL,
                api_token_creation DATETIME NULL,
                api_token_last_used DATETIME NULL
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

    except sqlite3.Error:
        logger.error("Unable to create table")
        raise RuntimeError("Database connection error")

def _query_token_time(token: str) -> tuple[str, str] | None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
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
        logger.error("Unable to query token")
        raise RuntimeError("Database connection error")

def _query_full_user(username: str) -> tuple[int, bytes, str, str, str] | None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
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
        logger.error("Unable to query full user")
        raise RuntimeError("Database connection error")

def _query_full_user_redis(token: str) -> tuple[int, str, str, str, str, str, str] | None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
                SELECT user_id, user_name, user_email, user_project, api_token, api_token_creation, api_token_last_expired 
                FROM users
                WHERE api_token = ?
            """, (token,))
        user_details = cursor.fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return user_details
    except sqlite3.Error:
        logger.error("Unable to query full user")
        raise RuntimeError("Database connection error")

def _insert_token(token: str, user_id: int, current_time: datetime) -> None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE users
            SET api_token = ?, api_token_creation = ?, api_token_last_used = ?
            WHERE user_id = ?
        """, (token, current_time, current_time, user_id))

        connection.commit()
        cursor.close()
        connection.close()

    except sqlite3.Error:
        logger.error("Unable to insert token")
        raise RuntimeError("Database connection error")

def _generate_token(user_id: int, passed_username: str, passed_grant_type: str, current_time: datetime) -> str:

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
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    db_info = _query_token_time(token)
    if not db_info:
        logger.error("Token not found in database")
        return 401, ""

    token_creation, token_last_used = db_info
    current_time = datetime.now()

    time_difference_creation = current_time - datetime.strptime(token_creation, "%Y-%m-%d %H:%M:%S.%f")
    if time_difference_creation > timedelta(minutes=65):
        logger.info("Token expired after 65 minutes")
        return 403, "Token Expired."

    time_difference_last_used = current_time - datetime.strptime(token_last_used, "%Y-%m-%d %H:%M:%S.%f")
    if time_difference_last_used > timedelta(minutes=5):
        logger.info("Token expired after 5 minutes")
        return 403, "Token Expired."

    return 200, ""

def _refresh_token_time(token: str) -> None:
    database_name = os.getenv("DB_PATH")
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    current_time = datetime.now()

    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        cursor.execute("""
                UPDATE users
                SET api_token_last_used = ?
                WHERE api_token = ?
            """, (current_time, token))

        connection.commit()
        cursor.close()
        connection.close()

    except sqlite3.Error:
        logger.error("Unable to refresh token")
        raise RuntimeError("Database connection error")

def _set_redis_cache_values(token: str) -> None:
    try:
        _, _, _, _, api_token, api_token_creation, api_token_last_used = _query_full_user_redis(token)
        redis_cache.hset(f'user-session:{api_token}', mapping={
            "api_token": api_token,
            "api_token_creation": api_token_creation,
            "api_token_last_used": api_token_last_used
        })
    except Exception:
        redis_cache.hset('user-session:None', mapping={})

def _validate_request() -> tuple[int, str]:
    headers = request.headers
    body = request.get_json() or {}
    path = request.path

    required_body_keys = {"grant_type", "username", "password"}
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    if path == r"/get-token":
        if set(body.keys()) != required_body_keys:
            logger.error("Request Body does not match structure")
            return 401, ""
        if any(not body[field] for field in required_body_keys):
            logger.error("Request Body has missing/null fields")
            return 401, ""
    elif path != r"/get-token":
        auth = headers.get("Authorization", None)

        cached_info = redis_cache.hgetall(auth)
        if cached_info:
            return 200, ""
        else:
            _set_redis_cache_values(auth)

        if not auth:
            logger.error("Authorization header is missing")
            return 401, ""

        auth_token = auth.removeprefix("Bearer ")
        status, reason = _validate_token(auth_token)
        if status != 200:
            return status, reason

        _refresh_token_time(auth_token)

    return 200, ""

@app.before_request
def enforce_policy() -> tuple[Response, int] | None:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    allowed_paths = {
        r"/generator-2014",
        r"/generator-2024",
        r"/generator-random",
        r"/get-token",
    }

    if request.path not in allowed_paths:
        logger.error(f"Request path {request.path} not allowed")
        abort(404)

    status, reason = _validate_request()
    if status != 200:
        logger.error(f"Request status {status} with reason: {reason}")
        return jsonify(_format_response_error(status, [reason])), status

    return None


@app.route(rule='/generator-2014', methods=["POST"])
def generator_2014() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2014 = _build_characters(character_stats)
    if not character_sheet_2014:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2014)

    return jsonify(response), 200

@app.route(rule='/generator-2024', methods=["POST"])
def generator_2024() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2024 = _build_characters(character_stats)
    if not character_sheet_2024:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2024)

    return jsonify(response), 200

@app.route(rule='/generator-random', methods=["POST"])
def generator_random() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body)

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_random = _build_characters(character_stats)
    if not character_sheet_random:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_random)

    return jsonify(response), 200

@app.route(rule='/get-token', methods=["POST"])
def get_token() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    data = request.get_json() or {}

    if not data:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    passed_username = data.get("username", None)
    passed_password = data.get("password", None)
    passed_grant_type = data.get("grant_type", None)

    if not passed_username or not passed_password or not passed_grant_type:
        logger.error("Request body has missing/null fields")
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    current_time = datetime.now()

    user_details = _query_full_user(passed_username)
    if not user_details:
        logger.error("User details are not in database")
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    user_id, user_pw, _, api_token_creation, _ = user_details
    if not bcrypt.checkpw(passed_password.encode('utf-8'), user_pw):
        logger.error("Password does not match")
        return jsonify(_format_response_error(403, ["Access Denied"])), 403

    if api_token_creation:
        time_difference_creation = current_time - datetime.strptime(api_token_creation, "%Y-%m-%d %H:%M:%S.%f")
        if time_difference_creation < timedelta(hours=24):
            logger.info("Token on 24 hours cooldown")
            return jsonify(_format_response_error(403, ["Token cooldown active"])), 403

    token = _generate_token(user_id, passed_username, passed_grant_type, current_time)
    _insert_token(token, user_id, current_time)

    status = 200
    response = _format_token_response(status, token, current_time)

    return jsonify(response), status

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    AppLogging.setup_logger(name="dnd_api", dir_log=Path(r"/var/log/dnd-api/"), file_level="INFO", console_level="CRITICAL")
    app.run()
