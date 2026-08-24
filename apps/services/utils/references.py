from django.db import transaction
from apps.services.models import ReferenceSetting

@transaction.atomic
def generate_reference(type):

    setting = (
        ReferenceSetting.objects
        .select_for_update()
        .get_or_create(type=type)[0]
    )

    ref = (
        f"{setting.prefix}-"
        f"{setting.current_number:05d}"
    )

    setting.current_number += 1

    setting.save(
        update_fields=[
            "current_number",
        ]
    )

    return ref