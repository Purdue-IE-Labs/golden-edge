# reserved: 0-99 (TODO: check in outward facing functions that they don't violate this)

from gedge.node.method_response import ResponseConfig, ResponseType
from gedge.node.reply import Response


DONE = 10
METHOD_ERROR = 20
TAG_ERROR = 30

# NEW METHOD RESPONSE STRUCTURE
OK = 10
OK_CONFIG = ResponseConfig.from_json5(
    {
        "code": OK,
        "type": "ok",
        "props": {
            "description": "generic OK method response if user does not define their own"
        },
    }
)

ERR = 20
ERR_CONFIG = ResponseConfig.from_json5(
    {
        "code": ERR,
        "type": "err",
        "props": {
            "description": "generic ERR method response if user does not define their own"
        },
    }
)

CALLBACK_ERR = 30
CALLBACK_ERR_CONFIG = ResponseConfig.from_json5(
    {
        "code": ERR,
        "type": "err",
        "body": [
            {
                "path": "reason",
                "base_type": "string",
            },
        ],
        "props": {
            "description": "Python exception thrown in user-defined method or user-defined method is improperly structured",
        },
    }
)

def config_from_code(code: int, responses: list[ResponseConfig]) -> ResponseConfig:
    r = {r.code: r for r in responses}
    if code in r:
        return r[code]
    return config_from_predefined_code(code)

def config_from_predefined_code(code: int) -> ResponseConfig:
    mapping = {
        OK: OK_CONFIG,
        ERR: ERR_CONFIG,
        CALLBACK_ERR: CALLBACK_ERR_CONFIG
    }
    if code not in mapping:
        raise ValueError(f"invalid built-in code used in response: {code}")

    return mapping[code]

def is_predefined_code(code: int) -> bool:
    return code in {OK, ERR, CALLBACK_ERR}

def is_final_method_response(response: Response) -> bool:
    return is_predefined_code(response.code) or response.type in {ResponseType.OK, ResponseType.ERR}

def is_ok(code: int) -> bool:
    return code == OK

def is_err(code: int) -> bool:
    return code in {ERR, CALLBACK_ERR}