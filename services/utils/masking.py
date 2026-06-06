def mask_email(email):
    if not email or "@" not in email:
        return ""

    email = email.strip().lower()

    local_part, domain = email.split("@", 1)

    if len(local_part) <= 2:
        masked_local = (
            local_part[0] + "*"
        )
    else:
        masked_local = (
            local_part[:2]
            + "*" * (len(local_part) - 2)
        )

    domain_name, extension = domain.rsplit(".", 1)

    if len(domain_name) <= 2:
        masked_domain = (
            domain_name[0] + "*"
        )
    else:
        masked_domain = (
            domain_name[:2]
            + "*" * (len(domain_name) - 2)
        )

    return (
        f"{masked_local}@"
        f"{masked_domain}.{extension}"
    )