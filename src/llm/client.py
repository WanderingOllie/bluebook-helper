import os
import re
from typing import TypeVar
import dotenv
from openai import OpenAI
from openai.types.responses import ResponseInputItemParam
from openai.types.shared_params import Reasoning
from pydantic import BaseModel, Field
from src.llm import prompts

T = TypeVar("T", bound=BaseModel)

# Default settings to use for OpenAI queries
OPENAI_MODEL = "gpt-5.6-luna"
OPENAI_REASONING: Reasoning = {"effort": "none"}


class ExtractedTextList(BaseModel):
    items: list[str] = Field(
        description=(
            "The exact text of each match, copied verbatim from the "
            "source, in the order they appear."
        )
    )


class LLM:
    """
    Manages interactions with LLM for structured data extraction.
    """

    def __init__(self) -> None:
        dotenv.load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Failed to load an API key when initializing LLM."
            )

        self._client = OpenAI(api_key=api_key)

    def _query_model(
        self, messages: list[ResponseInputItemParam], output_format: type[T],
        retries: int = 3
    ) -> T:
        """Sends messages and parses the reply as output_format."""
        last_error: Exception | None = None
        for _ in range(retries):
            try:
                response = self._client.responses.parse(
                    model=OPENAI_MODEL,
                    reasoning=OPENAI_REASONING,
                    input=messages,
                    text_format=output_format,
                )
                if response.output_parsed is not None:
                    return response.output_parsed
                last_error = ValueError("Model response failed to parse.")
            except Exception as error:
                last_error = error

        raise RuntimeError(
            f"Failed to query model after {retries} attempts."
        ) from last_error

    @staticmethod
    def _fidelity_check(source: str, extracted: str) -> bool:
        """
        Confirms extracted appears verbatim in source to guard against
        hallucination.
        """
        normalize = lambda s: re.sub(r"\s+", " ", s).strip()
        return normalize(extracted) in normalize(source)

    def _verify_extracted(self, source: str, items: list[str]) -> list[str]:
        """Runs each extracted item through the fidelity check."""
        for item in items:
            if not self._fidelity_check(source, item):
                raise ValueError(
                    f"Extracted text not found verbatim in source text: {item}"
                )
        return items

    def extract_citation_sentences(self, text: str) -> list[str]:
        """Uses the LLM to extract the citation sentences contained in text."""
        messages: list[ResponseInputItemParam] = [
            {
                "role": "system", 
                "content": prompts.CITATION_SENTENCE_SYSTEM_PROMPT
            },
            *prompts.CITATION_SENTENCE_EXAMPLES,
            {"role": "user", "content": f"TEXT:\n{text}"},
        ]
        result = self._query_model(messages, ExtractedTextList)
        return self._verify_extracted(text, result.items)

    def extract_citation_clauses(self, text: str) -> list[str]:
        """Uses the LLM to extract the citation clauses contained in text."""
        messages: list[ResponseInputItemParam] = [
            {
                "role": "system", 
                "content": prompts.CITATION_CLAUSE_SYSTEM_PROMPT
            },
            *prompts.CITATION_CLAUSE_EXAMPLES,
            {"role": "user", "content": f"TEXT:\n{text}"},
        ]
        result = self._query_model(messages, ExtractedTextList)
        return self._verify_extracted(text, result.items)
