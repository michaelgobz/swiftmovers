from typing import Iterable, List

TRANSACTION_REGISTRATION = "TR"
TRANSACTION_CANCELLATION = "TC"
TRANSACTION_CHANGE = "CH"
FULFILLMENT_REPORT = "FR"


def add_action_to_code(action: str, error_code: str) -> str:
    return f"{action}#{error_code}"


def get_error_messages_from_codes(action: str, error_codes: Iterable[str]) -> List[str]:
    return [add_action_to_code(action, code) for code in error_codes]


# connection error codes
NP_CONNECTION_ERROR = "swiftmoversNP000"

# address error codes
NO_BILLING_ADDRESS = "swiftmoversNP001"
NO_SHIPPING_ADDRESS = "swiftmoversNP002"
BILLING_ADDRESS_INVALID = "swiftmoversNP003"
SHIPPING_ADDRESS_INVALID = "swiftmoversNP004"

# payment error codes
NO_PSP_REFERENCE = "swiftmoversNP005"
PAYMENT_DOES_NOT_EXIST = "swiftmoversNP006"

# fulfillment error codes
NO_TRACKING_NUMBER = "swiftmoversNP007"
SHIPPING_COMPANY_CODE_INVALID = "swiftmoversNP008"
