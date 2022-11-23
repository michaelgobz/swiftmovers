import graphene


from swiftmovers.core.tracing import traced_atomic_transaction
from ...accounts.types import BILLING_ADDRESS_FIELD, SHIPPING_ADDRESS_FIELD, AddressInput


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
    channel = graphene.String(
        description=(
            "Slug of a channel which will be used for notify user. Optional when "
            "only one channel exists."
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

    @classmethod
    def clean_input(cls, info, instance, data):
        shipping_address_data = data.pop(SHIPPING_ADDRESS_FIELD, None)
        billing_address_data = data.pop(BILLING_ADDRESS_FIELD, None)
        cleaned_input = super().clean_input(info, instance, data)

        if shipping_address_data:
            shipping_address = cls.validate_address(
                shipping_address_data,
                address_type=AddressType.SHIPPING,
                instance=getattr(instance, SHIPPING_ADDRESS_FIELD),
                info=info,
            )
            cleaned_input[SHIPPING_ADDRESS_FIELD] = shipping_address

        if billing_address_data:
            billing_address = cls.validate_address(
                billing_address_data,
                address_type=AddressType.BILLING,
                instance=getattr(instance, BILLING_ADDRESS_FIELD),
                info=info,
            )
            cleaned_input[BILLING_ADDRESS_FIELD] = billing_address

        if cleaned_input.get("redirect_url"):
            try:
                validate_storefront_url(cleaned_input.get("redirect_url"))
            except ValidationError as error:
                raise ValidationError(
                    {"redirect_url": error}, code=AccountErrorCode.INVALID
                )

        return cleaned_input

    @classmethod
    @traced_atomic_transaction()
    def save(cls, info, instance, cleaned_input):
        default_shipping_address = cleaned_input.get(SHIPPING_ADDRESS_FIELD)
        manager = load_plugin_manager(info.context)
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

        instance.search_document = prepare_user_search_document_value(instance)
        instance.save(update_fields=["search_document", "updated_at"])

        # The instance is a new object in db, create an event
        if is_creation:
            manager.customer_created(customer=instance)
        else:
            manager.customer_updated(instance)
