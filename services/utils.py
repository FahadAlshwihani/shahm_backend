from .models import ReferenceSetting


def generate_reference(type):
    setting, _ = ReferenceSetting.objects.get_or_create(type=type)
    ref = f"{setting.prefix}-{setting.current_number:05d}"
    setting.current_number += 1
    setting.save()
    return ref
