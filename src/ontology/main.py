from pathlib import Path

import tiktoken
from openai import OpenAI
from pydantic import Field, create_model

from ontology.types.node import NodeType, generate_class_for_node_type
from ontology.utils import StrictModel, read_dotenv


def chunked(encoding: list[int], chunk_size: int, overlap: int):
    return [
        encoding[i : i + chunk_size]
        for i in range(0, len(encoding), chunk_size - overlap)
    ]


MODEL_NAME = "gpt-4o-mini"
ENCODING_NAME = "o200k_base"
CHUNK_SIZE = 100_000
CHUNK_OVERLAP = CHUNK_SIZE // 20


def main():
    dotenv = read_dotenv()

    client = OpenAI(api_key=dotenv["OPENAI_API_KEY"])

    encoding = tiktoken.get_encoding(
        ENCODING_NAME
    )  # source: https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken

    text = Path("examples/moby_dick.txt").read_text(encoding="utf-8")

    resp = client.beta.chat.completions.parse(
        messages=[
            {"role": "user", "content": "Create a node type for characters in a book"}
        ],
        response_format=NodeType,
        model=MODEL_NAME,
    )

    model = generate_class_for_node_type(resp.choices[0].message.parsed)

    # allow for partial responses s.t. they can then be merged again

    model_list = create_model(
        "ModelList", __base__=StrictModel, models=(list[model], Field(...))
    )

    print(
        model_list.model_json_schema()
    )  # TODO if you use openai completions parse, then you will NOT benefit from reduced data!

    enc = encoding.encode(text)

    for chunk in chunked(enc, CHUNK_SIZE, CHUNK_OVERLAP):
        completion = client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": "Extract all data from the given text chunk",
                },
                {"role": "user", "content": encoding.decode(chunk)},
            ],
            response_format=model_list,
            model=MODEL_NAME,
        )

        print(completion.choices[0].message.parsed.model_dump_json())
