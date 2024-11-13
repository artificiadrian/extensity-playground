from pathlib import Path

from pydantic import BaseModel, ConfigDict


def read_dotenv():
    return {
        k: v
        for k, v in [line.split("=") for line in Path(".env").read_text().splitlines()]
    }


def remove_key_recursively(d: dict, key: str):
    if key in d:
        del d[key]

    for v in filter(lambda v: isinstance(v, dict), d.values()):
        remove_key_recursively(v, key)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def reduced_json_schema(cls, **kwargs):
        schema = cls.model_json_schema(**kwargs)
        remove_key_recursively(
            schema, "title"
        )  # title is a redundant property that we do not need for OpenAI api call
        return schema
