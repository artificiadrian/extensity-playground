from typing import Optional

from pydantic import Field, create_model

from ontology.properties import Property, ScalarType
from ontology.utils import StrictModel


class NodeType(StrictModel):
    name: str = Field(..., description="Name in PascalCase")
    description: str

    properties: list[Property]


_scalar_to_python: dict[ScalarType, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def generate_field(prop: Property):
    type = _scalar_to_python[prop.type]
    if prop.is_list:
        type = list[type]

    if prop.optional:
        type = Optional[type]

    return (type, Field(..., description=prop.description))


def generate_class_for_node_type(node_type: NodeType):
    class_name = node_type.name
    class_properties = {
        prop.name: generate_field(prop) for prop in node_type.properties
    }

    return create_model(
        class_name,
        __base__=StrictModel,
        __doc__=node_type.description,
        **class_properties,  # type: ignore # Pylance complains because the props could - potentially - contain __config__ and others which would have wrong type
    )
