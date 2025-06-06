from enum import Enum

from ..schemas import ErrorSchema


class Error(Enum):
    # User authentication errors [E0010 - E0029]
    INVALID_CREDENTIALS = ErrorSchema(code="E0010", message="Invalid credentials", level="info")
    INVALID_CREDENTIALS_RECAPTCHA_TOKEN_IS_REQUIRED = ErrorSchema(
        code="E0011", message="Recaptcha token is required", level="info"
    )
    USER_ALREADY_EXIST = ErrorSchema(code="E0012", message="User already exists", level="info")
    TOKEN_IS_EXPIRED = ErrorSchema(code="E0013", message="The token has expired", level="info")

    REVOKED_TOKEN = ErrorSchema(code="E0014", message="The token has expired", level="info")
    INVALID_TOKEN = ErrorSchema(code="E0015", message="Signature verification failed", level="info")
    TOKEN_NOT_FOUND = ErrorSchema(code="E0016", message="The request does not contain a token", level="info")
    FRESH_TOKEN_REQUIRED = ErrorSchema(code="E0017", message="Token not fresh", level="info")
    USER_ALREADY_IS_LOGGED_OUT = ErrorSchema(code="E0018", message="User already is logged out!", level="info")
    USER_UNAUTHORIZED = ErrorSchema(code="E0019", message="User permission denied!", level="info")
    USER_NOT_FOUND = ErrorSchema(code="E0020", message="User not found", level="info")
    USER_HIERARCHY_ERROR = ErrorSchema(
        code="E0021", message="User parents role must be higher level than the created user", level="warning"
    )
    PARENT_USER_NOT_FOUND_ERROR = ErrorSchema(code="E0022", message="Parent user not found", level="warning")
    PASSWORD_RESET_CODE_IS_EXPIRED = ErrorSchema(code="E0023", message="Password reset code has expired", level="info")
    USER_ACCOUNT_IS_DEACTIVATED = ErrorSchema(code="E0024", message="User account is deactivated", level="info")
    USER_CANNOT_DELETE_HIMSELF = ErrorSchema(code="E0025", message="User cannot delete himself", level="info")
    USER_CANNOT_DELETE_LAST_ADMIN = ErrorSchema(code="E0026", message="User cannot delete last admin", level="info")
    PASSWORDS_DO_NOT_MATCH = ErrorSchema(code="E0028", message="Passwords do not match", level="info")
    EMAIL_CONFIRMATION_CODE_IS_EXPIRED = ErrorSchema(
        code="E0029", message="Confirmation code has expired", level="info"
    )
    ACCOUNT_EMAIL_CONFIRMATION_FAILED = ErrorSchema(code="E0027", message="Account confirmation failed", level="info")

    INVALID_JSON_FORMAT = ErrorSchema(code="E0030", message="Invalid JSON format", level="error")
    INVALID_SMTP_CREDENTIALS = ErrorSchema(
        code="E0031", message="Failed to send email, the credentials are invalid!", level="error"
    )
    NO_FILE_ERROR = ErrorSchema(code="E0032", message="File doesn't exist", level="error")
    SERVER_ERROR = ErrorSchema(code="E0033", message="Server error", level="error")
    INVALID_QUERY_FORMAT = ErrorSchema(code="E0034", message="Invalid query parameters format", level="error")

    INVALID_FILE = ErrorSchema(code="E0040", message="Invalid file error", level="error")
    FILE_OPERATION_ERROR = ErrorSchema(code="E0041", message="File operation error", level="error")

    MAIL_ERROR = ErrorSchema(code="E0050", message="Email sending error", level="warning")

    DB_INSERT_ERROR = ErrorSchema(code="E0101", message="Failed to insert object into the database", level="error")
    DB_ACCESS_ERROR = ErrorSchema(code="E0102", message="Failed to access the database", level="error")
    DB_MODEL_INSTANCE_ALREADY_EXISTS = ErrorSchema(
        code="E0103", message="Database model instance already exists", level="info"
    )
    DB_MODEL_INSTANCE_DOES_NOT_EXISTS = ErrorSchema(code="E0104", message="Database model does not exist", level="info")
    DB_COLUMN_VALUE_TOO_LONG = ErrorSchema(
        code="E0105", message="Database model column value too long", level="warning"
    )
    DB_UNIQUE_COLUMN_VALUE = ErrorSchema(
        code="E0106", message="Database model column value must be unique", level="info"
    )
    DB_FOREIGN_KEY_VIOLATION = ErrorSchema(
        code="E0107", message="Database model can't update or delete until it has a relationship", level="warning"
    )
    DB_INVALID_TEXT_REPRESENTATION = ErrorSchema(
        code="E0108", message="Database model column value format is not correct", level="info"
    )

    JOB_FUNCTION_NOT_FOUND = ErrorSchema(
        code="E0301",
        message="Job function not found. Please implement the job function here -> jobs/manual_start",
        level="info",
    )
    UNKNOWN = ErrorSchema(code="E9999", message="Unknown error!", level="error")

    def print(self):
        self.value.print()

    def to_dict(self):
        return {"code": self.code, "message": self.message, "fields": self.fields}
