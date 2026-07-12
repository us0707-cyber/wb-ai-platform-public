from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.api.deps import ROLE_HIERARCHY
from src.schemas.auth import UserResponse


def test_role_hierarchy_order():
    assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["manager"] > ROLE_HIERARCHY["analyst"]


def test_user_response_contains_role():
    payload = UserResponse.model_validate(
        SimpleNamespace(id=1, email="admin@example.com", username="admin", is_active=True, role="admin")
    )
    assert payload.role == "admin"


def test_valid_roles_are_known():
    assert set(ROLE_HIERARCHY) == {"admin", "manager", "analyst"}
