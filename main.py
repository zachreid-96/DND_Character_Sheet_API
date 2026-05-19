import os, inspect, redis

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

from database_ops.database_helper import write_session_expiration
from redis_ops.redis_helper import (
    get_redis_mapping,
    validate_redis_cache_creation,
    validate_redis_cache
)

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


def _format_response_character(characters: list[dict], body: dict) -> dict:

    project_name = body.get("project_name", "").strip()
    campaign_name = body.get("campaign_name", "").strip()
    region = body.get("region", "").strip()
    origin = body.get("origin", "").strip()
    sigil = body.get("sigil", "").strip()
    codex = body.get("codex", "").strip()
    realm = body.get("realm", "").strip()
    guild = body.get("guild", "").strip()

    response = {
        "data": {
            "code": 200,
            "characters": characters,
            "project_name": project_name,
            "campaign_name": campaign_name,
            "region": region,
            "origin": origin,
            "sigil": sigil,
            "codex": codex,
            "realm": realm,
            "guild": guild
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

def _validate_body(body: dict, route: str) -> tuple[int, list[str], tuple[str, str, int, int]]:

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

    accepted_editions = ["5e", "5.5e", "random"]

    accepted_classnames = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "random"
    ]

    if dnd_edition not in accepted_editions:
        reasons.append(f"Edition '{dnd_edition}' is not supported by this API, only 5e and 5.5e are supported.")

    if dnd_class not in accepted_classnames:
        reasons.append(f"Class '{dnd_class}' is not an accepted SRD Class.")

    if dnd_edition == "5e" and route == "/generator-2024":
        reasons.append(f"Edition '{dnd_edition}' and route '{route}' are mismatched")

    if dnd_edition == "5.5e" and route == "/generator-2014":
        reasons.append(f"Edition '{dnd_edition}' and route '{route}' are mismatched")

    if dnd_edition == "random" and route != "/generator-random":
        reasons.append(f"Edition '{dnd_edition}' and route '{route}' are mismatched")

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

def _set_redis_cache_values(token: str) -> None:
    m, n, t = get_redis_mapping(token)
    redis_cache.hset(name=n, mapping=m)
    redis_cache.expire(name=n, time=t)

def _handle_non_auth():
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    ip = get_remote_address()
    ip_key = f"ip-session:{ip}"
    ip_cache = redis_cache.hgetall(ip_key)

    if ip_cache:
        redis_cache.expire(ip_key, 30 * 60)
        return 200, ""
    else:
        last_used = redis_cache.get(f"ip-cooldown:{ip}")
        if last_used:
            last_used_time = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S.%f")
            cooldown_ends = last_used_time + timedelta(hours=24)
            if datetime.now() < cooldown_ends:
                logger.warning(f"IP is in cooldown: {ip}")
                return 429, "IP is in cooldown"

        session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        projected_expiration = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S.%f")
        redis_cache.hset(ip_key, mapping={
            "ip": ip,
            "session_start": session_start,
        })
        redis_cache.expire(ip_key, 30 * 60)
        redis_cache.set(f"ip-cooldown:{ip}", projected_expiration, ex=24 * 60 * 60 + 30 * 60)
        return 200, ""

def _validate_request() -> tuple[int, str]:
    headers = request.headers
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    auth = headers.get("Authorization", None)

    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return 400, "Body cannot be empty"

    if not auth:
        return _handle_non_auth()

    auth_token = auth.removeprefix("Bearer ")
    redis_key = f"user-session:{auth_token}"

    cached_info = redis_cache.hgetall(redis_key)

    if cached_info:
        status, reason = validate_redis_cache(auth, cached_info, body, redis_cache)
        return status, reason

    else:

        status, reason = validate_redis_cache_creation(auth_token, body)
        if status != 200:
            return status, reason

        # All gates passed — start session
        projected_expiration = datetime.now() + timedelta(minutes=65)
        _set_redis_cache_values(auth_token)
        write_session_expiration(auth_token, projected_expiration)

    return 200, ""

@app.before_request
def enforce_policy() -> tuple[Response, int] | None:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")

    allowed_paths = {
        r"/generator-2014",
        r"/generator-2024",
        r"/generator-random",
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

    status, reason, character_stats = _validate_body(body, "/generator-2014")

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2014 = _build_characters(character_stats)
    if not character_sheet_2014:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2014, body)

    return jsonify(response), 200

@app.route(rule='/generator-2024', methods=["POST"])
def generator_2024() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body, "/generator-2024")

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_2024 = _build_characters(character_stats)
    if not character_sheet_2024:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_2024, body)

    return jsonify(response), 200

@app.route(rule='/generator-random', methods=["POST"])
def generator_random() -> tuple[Response, int]:
    logger = AppLogging.get_logger(name=f"{inspect.currentframe().f_code.co_name}")
    body = request.get_json() or {}

    if not body:
        logger.error("Request body is empty")
        return jsonify(_format_response_error(400, ["Body cannot be empty."])), 400

    status, reason, character_stats = _validate_body(body, "/generator-random")

    if status != 200:
        return jsonify(_format_response_error(status, reason)), status

    character_sheet_random = _build_characters(character_stats)
    if not character_sheet_random:
        logger.error("Character sheet is empty")
        return jsonify(_format_response_error(422, ["Failed to generate character sheets"])), 422

    response = _format_response_character(character_sheet_random, body)

    return jsonify(response), 200

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    AppLogging.setup_logger(name="dnd_api", dir_log=Path(r"/var/log/dnd-api/"), file_level="INFO", console_level="CRITICAL")
    app.run()
