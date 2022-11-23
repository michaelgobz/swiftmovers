import graphene
from django_countries import countries

from ...checkouts import AddressType
from ...graphqlcore.core.enums import to_enum
from ..core.enums import str_to_enum

AddressTypeEnum = to_enum(AddressType, type_name="AddressTypeEnum")


CountryCodeEnum = graphene.Enum(
    "CountryCode", [(str_to_enum(country[0]), country[0]) for country in countries]
)


class StaffMemberStatus(graphene.Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"

    @property
    def description(self):
        if self == StaffMemberStatus.ACTIVE:
            return "User account has been activated."
        elif self == StaffMemberStatus.DEACTIVATED:
            return "User account has not been activated yet."
        return None
