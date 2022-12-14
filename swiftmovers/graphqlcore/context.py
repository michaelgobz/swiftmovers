from typing import Optional, cast

from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject

from ..core.auth import get_token_from_request
from ..core.jwt import jwt_decode_with_exception_handler
from .core import SwiftContext


def get_context_value(request: HttpRequest) -> SwiftContext:
    request = cast(SwiftContext, request)
    request.is_mutation = False
    set_auth_on_context(request)
    set_decoded_auth_token(request)
    return request


UserType = Optional[""] | ""

# should have the user type 


class RequestWithUser(HttpRequest):
    _cached_user = UserType


def set_decoded_auth_token(request: SwiftContext):
    auth_token = get_token_from_request(request)
    if auth_token:
        request.decoded_auth_token = jwt_decode_with_exception_handler(auth_token)
    else:
        request.decoded_auth_token = None


def get_user(request: SwiftContext) -> UserType:
    if not hasattr(request, "_cached_user"):
        request._cached_user = cast(UserType, authenticate(request=request))
    return request._cached_user


def set_auth_on_context(request: SwiftContext):
    if hasattr(request, "app") and request.app:
        request.user = SimpleLazyObject(lambda: None)  # type: ignore
        return request

    def user():
        return get_user(request) or None

    request.user = SimpleLazyObject(user)  # type: ignore
