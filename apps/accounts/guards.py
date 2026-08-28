"""Guards that need the user table, kept out of the pure role ranking."""

from .models import User


def leaves_no_active_super_admin(user):
    """Report whether removing or disabling ``user`` empties the top role.

    The dashboard has no recovery path once the last active super admin is
    gone, so deleting or deactivating that account is refused.
    """
    if user.role != "super_admin" or not user.is_active:
        return False

    return not (
        User.objects
        .filter(role="super_admin", is_active=True)
        .exclude(pk=user.pk)
        .exists()
    )
