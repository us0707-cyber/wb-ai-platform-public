import pytest
from pydantic import ValidationError

from src.schemas.product import ProductCreate, ProductUpdate


def test_product_create_accepts_catalog_fields():
    product = ProductCreate(
        store_id=1,
        title="Футболка базовая",
        vendor_code="TSHIRT-001",
        nm_id=123456,
        brand="WB AI",
        category="Одежда",
        price=1290,
        stock=25,
        status="active",
        image_url="https://example.com/image.jpg",
    )
    assert product.status == "active"
    assert product.stock == 25


def test_product_rejects_negative_values():
    with pytest.raises(ValidationError):
        ProductCreate(store_id=1, title="Товар", price=-1)


def test_product_rejects_unknown_status():
    with pytest.raises(ValidationError):
        ProductUpdate(status="deleted")
