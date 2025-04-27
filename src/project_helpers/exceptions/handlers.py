# Id: handlers.py 202305 12/05/2023
#
# backend
# Copyright (c) 2011-2013 IntegraSoft S.R.L. All rights reserved.
#
# Author: cicada
#   Rev: 202305
#   Date: 12/05/2023
#
# License description...
import re

from apscheduler.jobstores.base import JobLookupError
from extensions.auth_jwt.exceptions import (
    AuthJWTException,
    MissingTokenError,
    JWTDecodeError,
    RevokedTokenError,
    AccessTokenRequired,
    FreshTokenRequired,
    RefreshTokenRequired,
    InvalidHeaderError,
)
from gridfs import NoFile
from jwt import DecodeError
from psycopg2.errorcodes import (
    UNIQUE_VIOLATION,
    FOREIGN_KEY_VIOLATION,
    STRING_DATA_RIGHT_TRUNCATION,
)
from pymongo.errors import OperationFailure

from extensions import api
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from .exceptions import ErrorException
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError, ProgrammingError, StatementError
from ..error import Error
from ..responses import ErrorResponse
from fastapi_mail.errors import (
    ConnectionErrors,
    WrongFile,
    PydanticClassRequired,
    TemplateFolderDoesNotExist,
    ApiError,
    DBProvaiderError,
)


@api.exception_handler(ValidationError)
@api.exception_handler(RequestValidationError)
@api.exception_handler(ResponseValidationError)
async def validation_exception(request: Request, exc: RequestValidationError):
    def join_fields(fields):
        return "->".join([str(field) for field in fields])

    data = (
        getattr(exc, "body_params", None)
        or getattr(exc, "path_params", None)
        or getattr(exc, "form_params", None)
        or getattr(exc, "query_params", None)
        or getattr(exc, "errors", None)
        and exc.errors()
        or None
    )

    return ErrorResponse(
        Error.INVALID_JSON_FORMAT,
        message=data and [d.get("msg") + ":" + join_fields(d.get("loc")) for d in data] or None,
        fields=data and [join_fields(d.get("loc")) for d in data] or None,
    )


@api.exception_handler(ErrorException)
async def error_exception(request: Request, exc: ErrorException):
    return ErrorResponse(error=exc.error, statusCode=exc.statusCode, message=exc.message)


@api.exception_handler(StatementError)
@api.exception_handler(IntegrityError)
def db_integrity_error(request: Request, e):
    if getattr(e.orig, "pgcode", None) == UNIQUE_VIOLATION:
        msg = f"Key{str(e.orig.pgerror).partition('Key')[2]}"
        fields = re.search(r"\((.*?)\)=", msg)
        if "lower(company_name::text)" == fields.group(1).split(",")[0]:
            newFields = ["company_name"]

            return ErrorResponse(Error.DB_UNIQUE_COLUMN_VALUE, fields=newFields, message=msg)

        return ErrorResponse(
            Error.DB_UNIQUE_COLUMN_VALUE,
            fields=fields and fields.group(1).split(",") or [],
            message=msg,
        )

    elif getattr(e.orig, "pgcode", None) == FOREIGN_KEY_VIOLATION:
        msg = f"Key{str(e.orig.pgerror).partition('Key')[2]}"
        fields = re.search(r"\((.*?)\)=", msg)
        return ErrorResponse(
            Error.DB_FOREIGN_KEY_VIOLATION,
            fields=fields and fields.group(1).split(",") or [],
            message=msg,
        )

    elif getattr(e.orig, "pgcode", None) == STRING_DATA_RIGHT_TRUNCATION:
        return ErrorResponse(Error.DB_COLUMN_VALUE_TOO_LONG)
    else:
        return ErrorResponse(Error.DB_INSERT_ERROR, message=str(e))


@api.exception_handler(ProgrammingError)
def db_programming_error(request: Request, e):
    return ErrorResponse(Error.DB_ACCESS_ERROR, message=str(e))


@api.exception_handler(KeyError)
@api.exception_handler(AttributeError)
@api.exception_handler(TypeError)
@api.exception_handler(ValueError)
@api.exception_handler(NotImplementedError)
def server_error(request: Request, e):
    return ErrorResponse(Error.SERVER_ERROR, message=str(e))


@api.exception_handler(MissingTokenError)
@api.exception_handler(AccessTokenRequired)
@api.exception_handler(RefreshTokenRequired)
def authjwt_missing_token_handler(request: Request, exc: AuthJWTException):
    return ErrorResponse(Error.TOKEN_NOT_FOUND, statusCode=exc.status_code, message=exc.message)


@api.exception_handler(JWTDecodeError)
@api.exception_handler(InvalidHeaderError)
def authjwt_token_deocode_handler(request: Request, exc: AuthJWTException):
    return ErrorResponse(Error.INVALID_TOKEN, statusCode=exc.status_code, message=exc.message)


@api.exception_handler(RevokedTokenError)
def authjwt_revoked_token_handler(request: Request, exc: AuthJWTException):
    return ErrorResponse(Error.REVOKED_TOKEN, statusCode=exc.status_code, message=exc.message)


@api.exception_handler(FreshTokenRequired)
def authjwt_fresh_token_handler(request: Request, exc: AuthJWTException):
    return ErrorResponse(Error.FRESH_TOKEN_REQUIRED, statusCode=exc.status_code, message=exc.message)


@api.exception_handler(ApiError)
@api.exception_handler(WrongFile)
@api.exception_handler(PydanticClassRequired)
@api.exception_handler(TemplateFolderDoesNotExist)
@api.exception_handler(ApiError)
@api.exception_handler(DBProvaiderError)
def mail_error_handler(request: Request, exc):
    return ErrorResponse(Error.MAIL_ERROR, message=str(exc))


@api.exception_handler(OperationFailure)
def mail_error_handler(request: Request, exc):
    return ErrorResponse(Error.FILE_OPERATION_ERROR, message=str(exc))


@api.exception_handler(NoFile)
def mail_error_handler(request: Request, exc):
    return ErrorResponse(Error.NO_FILE_ERROR, message=str(exc))


@api.exception_handler(DecodeError)
def mail_error_handler(request: Request, exc):
    return ErrorResponse(Error.INVALID_TOKEN, message=str(exc))


@api.exception_handler(JobLookupError)
def job_not_found_error(request: Request, exc):
    return ErrorResponse(Error.DB_MODEL_INSTANCE_DOES_NOT_EXISTS)


@api.middleware("http")
async def unknown_exception(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        response = ErrorResponse(error=Error.UNKNOWN, message=str(exc))
    return response
