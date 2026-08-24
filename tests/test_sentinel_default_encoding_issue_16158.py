"""
Regression test: encoding a sentinel default value (e.g. pydantic_core.MISSING)
in a validation error response shouldn't raise a 500 error.
See https://github.com/fastapi/fastapi/discussions/16158
"""

from typing import Annotated

import pydantic_core
import pytest
from fastapi import FastAPI, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

if not hasattr(pydantic_core, "MISSING"):
    pytest.skip(
        "pydantic_core.MISSING is not available in this pydantic version",
        allow_module_level=True,
    )

MISSING = pydantic_core.MISSING


class FindParams(BaseModel):
    item_id: str = Field(description="The item ID")
    vendor_id: int | MISSING = Field(MISSING, description="The vendor ID")


app = FastAPI()


@app.get("/items/")
async def list_items(params: Annotated[FindParams, Query()]):
    return params  # pragma: nocover


client = TestClient(app)


def test_sentinel_default_in_validation_error_response():
    response = client.get("/items/")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["input"]["vendor_id"] == "MISSING"
