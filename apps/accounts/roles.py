"""Role ranking used by user administration.

The dashboard roles are ordered. An actor may only assign roles at or below
their own rank, and may only administer accounts at or below their own rank,
so an ``admin`` can no longer create, promote, edit or delete a ``super_admin``.
"""

ROLE_RANKS = {
    "viewer": 1,
    "editor": 2,
    "admin": 3,
    "super_admin": 4,
}


def rank(role):
    """Return the numeric rank of ``role``; unknown roles rank lowest."""
    return ROLE_RANKS.get(role, 0)


def can_assign_role(actor, role):
    """Report whether ``actor`` may hand out ``role``."""
    if actor is None or not actor.is_authenticated:
        return False

    return rank(role) <= rank(actor.role)


def can_administer(actor, target):
    """Report whether ``actor`` may edit or delete the ``target`` account."""
    if actor is None or not actor.is_authenticated:
        return False

    return rank(target.role) <= rank(actor.role)
