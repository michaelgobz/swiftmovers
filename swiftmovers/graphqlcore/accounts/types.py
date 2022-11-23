import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ...accounts.models import User
from ...accounts.error_codes import AccountErrorCode
from ...checkouts import AddressType
from ...core.tracing import traced_atomic_transaction

# from ..accounts.enums import Address, AddressInput, User
from ..core.enums import LanguageCodeEnum

BILLING_ADDRESS_FIELD = "default_billing_address"
SHIPPING_ADDRESS_FIELD = "default_shipping_address"
INVALID_TOKEN = "Invalid or expired token."


class UserInput(graphene.InputObjectType):
    first_name = graphene.String(description="Given name.")
    last_name = graphene.String(description="Family name.")
    email = graphene.String(description="The unique email address of the user.")
    is_active = graphene.Boolean(required=False, description="User account is active.")
    note = graphene.String(description="A note about the user.")


class UserAddressInput(graphene.InputObjectType):
    default_billing_address = AddressInput(
        description="Billing address of the customer."
    )
    default_shipping_address = AddressInput(
        description="Shipping address of the customer."
    )


class CustomerInput(UserInput, UserAddressInput):
    language_code = graphene.Field(
        LanguageCodeEnum, required=False, description="User language code."
    )


class UserCreateInput(CustomerInput):
    redirect_url = graphene.String(
        description=(
            "URL of a view where users should be redirected to "
            "set the password. URL in RFC 1808 format."
        )
    )


class BaseCustomerCreate(graphene.Mutation):
    """Base mutation for customer create used by staff and account."""

    class Arguments:
        input = UserCreateInput(
            description="Fields required to create a customer.", required=True
        )

    class Meta:
        abstract = True


    class AddressInput(graphene.InputObjectType):
        first_name = graphene.String(description="Given name.")
        last_name = graphene.String(description="Family name.")
        company_name = graphene.String(description="Company or organization.")
        street_address_1 = graphene.String(description="Address.")
        street_address_2 = graphene.String(description="Address.")
        city = graphene.String(description="City.")
        city_area = graphene.String(description="District.")
        postal_code = graphene.String(description="Postal code.")
        country = CountryCodeEnum(description="Country.")
        country_area = graphene.String(description="State or province.")
        phone = graphene.String(description="Phone number.")

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info, instance, cleaned_input):
        default_shipping_address = cleaned_input.get(SHIPPING_ADDRESS_FIELD)
        manager = User.__class__ # use clear context object
        if default_shipping_address:
            default_shipping_address = manager.change_user_address(
                default_shipping_address, "shipping", instance
            )
            default_shipping_address.save()
            instance.default_shipping_address = default_shipping_address
        default_billing_address = cleaned_input.get(BILLING_ADDRESS_FIELD)
        if default_billing_address:
            default_billing_address = manager.change_user_address(
                default_billing_address, "billing", instance
            )
            default_billing_address.save()
            instance.default_billing_address = default_billing_address

        is_creation = instance.pk is None
        super().save(info, instance, cleaned_input)
        if default_billing_address:
            instance.addresses.add(default_billing_address)
        if default_shipping_address:
            instance.addresses.add(default_shipping_address)

        instance.save(update_fields=["search_document", "updated_at"])

        # The instance is a new object in db, create an event
        if is_creation:
            manager.customer_created(customer=instance)
        else:
            manager.customer_updated(instance)
