from typing import Literal

from pydantic import Field

from ontology.utils import StrictModel

ScalarType = Literal["str", "int", "float", "bool"]


class Property(StrictModel):
    name: str = Field(..., description="Name in snake_case")
    description: str | None

    type: ScalarType
    optional: bool | None
    is_list: bool | None
