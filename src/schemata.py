from functools import wraps

from cerberus import Validator

from src.exceptions import InvalidRequestException


def validate_input(schema):
    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            validator = Validator(schema, require_all=True)
            res = validator.validate(kwargs)
            if not res:
                raise InvalidRequestException(validator.errors)

            return func(*args, **kwargs)

        return decorated_func

    return decorator


UUID_REGEX = (
    "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
)
EMAIL_REGEX = "^.+@.+$"

UUID_RULE = {"type": "string", "regex": UUID_REGEX}
EMAIL_RULE = {"type": "string", "regex": EMAIL_REGEX}
NONNEGATIVE_NUMBER_RULE = {"type": "number", "min": 0}
OPTIONAL_NONNEGATIVE_NUMBER_RULE = {"type": "number", "min": 0, "required": False}

USER_AUTH_SCHEMA = {"email": EMAIL_RULE, "password": {"type": "string", "minlength": 6}}
CREATE_USER_SCHEMA = {
    "email": EMAIL_RULE,
    "full_name": {"type": "string"},
    "password": {"type": "string", "minlength": 6},
}
INVITE_SCHEMA = {"inviter_id": UUID_RULE, "invited_id": UUID_RULE}
CREATE_ORDER_SCHEMA = {
    "user_id": UUID_RULE,
    "number_of_shares": NONNEGATIVE_NUMBER_RULE,
    "price": NONNEGATIVE_NUMBER_RULE,
    "security_id": UUID_RULE,
}
EDIT_ORDER_SCHEMA = {
    "id": UUID_RULE,
    "subject_id": UUID_RULE,
    "new_number_of_shares": OPTIONAL_NONNEGATIVE_NUMBER_RULE,
    "new_price": OPTIONAL_NONNEGATIVE_NUMBER_RULE,
}
DELETE_ORDER_SCHEMA = {"id": UUID_RULE, "subject_id": UUID_RULE}

LINKEDIN_CODE_SCHEMA = {
    "code": {"type": "string", "required": True},
    "redirect_uri": {"type": "string", "required": True},
}
LINKEDIN_TOKEN_SCHEMA = {"token": {"type": "string", "required": True}}
LINKEDIN_BUYER_PRIVILEGES_SCHEMA = {
    "code": {"type": "string", "required": True},
    "redirect_uri": {"type": "string", "required": True},
    "user_email": {"type": "string", "required": True},
}
