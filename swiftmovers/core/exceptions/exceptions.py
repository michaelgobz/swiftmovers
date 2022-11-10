from enum import Enum
from typing import Iterable


class ReadOnlyException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "API runs in read-only mode"
        super().__init__(msg)


class PermissionDenied(Exception):
    def __init__(self, message=None, *, permissions: Iterable[Enum] = None):
        if not message:
            if permissions:
                permission_list = ", ".join(p.name for p in permissions)
                message = (
                    f"You need one of the following permissions: {permission_list}"
                )
            else:
                message = "You do not have permission to perform this action"
        super().__init__(message)
        self.permissions = permissions
