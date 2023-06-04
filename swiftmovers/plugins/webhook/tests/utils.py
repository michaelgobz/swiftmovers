def generate_request_headers(event_type, domain, signature):
    return {
        "Content-Type": "application/json",
        # X- headers will be deprecated in swiftmovers 4.0, proper headers are without X-
        "X-swiftmovers-Event": event_type,
        "X-swiftmovers-Domain": domain,
        "X-swiftmovers-Signature": signature,
        "swiftmovers-Event": event_type,
        "swiftmovers-Domain": domain,
        "swiftmovers-Signature": signature,
        "swiftmovers-Api-Url": f"http://{domain}/graphql/",
    }
