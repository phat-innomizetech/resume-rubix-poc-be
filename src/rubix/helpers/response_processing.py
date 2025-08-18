"""
Helper utilities for post-processing model responses.

This module includes functions to:
- Convert Hugging Face NER outputs to the app's `ResumeSchema`
- Recover and parse near-JSON text by balancing missing brackets/braces
- Extract and parse embedded JSON content from LLM responses
"""

import json
import logging
from typing import List, Dict, Any
from collections import defaultdict

from rubix.schemas.resume import ResumeSchema, Education

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def ner_to_resume_schema(ner_results: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Convert Hugging Face NER results into a `ResumeSchema` instance.

    The function groups B-/I- tagged tokens into entities, merges WordPiece
    fragments ("##"), and maps coarse entity types to fields of
    `ResumeSchema` (e.g., PER -> name, ORG -> education entries, LOC ->
    interests, MISC -> skills).

    Args:
        ner_results: List of token-level NER dicts produced by a HF pipeline,
            each item typically containing keys like "entity" and "word".

    Returns:
        ResumeSchema: A pydantic model populated with the mapped fields.

    Notes:
        - This mapping is heuristic and intentionally simple.
        - Only a subset of possible entity labels is supported.
    """
    grouped_entities = defaultdict(list)
    current_entity: list[str] = []
    current_label = None

    for token in ner_results:
        label = token["entity"]
        word = token["word"].replace("##", "")  # merge WordPiece tokens
        if label.startswith("B-"):
            if current_entity and current_label:
                grouped_entities[current_label].append(" ".join(current_entity))
            current_entity = [word]
            current_label = label[2:]
        elif label.startswith("I-") and current_label == label[2:]:
            current_entity.append(word)
        else:
            if current_entity and current_label:
                grouped_entities[current_label].append(" ".join(current_entity))
            current_entity = None
            current_label = None

    if current_entity and current_label:
        grouped_entities[current_label].append(" ".join(current_entity))

    # Map grouped entities to ResumeSchema fields
    resume_data: Dict[str, Any] = {}

    if "PER" in grouped_entities:
        resume_data["name"] = grouped_entities["PER"][0]

    if "ORG" in grouped_entities:
        resume_data["education"] = [
            Education(university=org) for org in grouped_entities["ORG"]
        ]

    if "LOC" in grouped_entities:
        resume_data["interests"] = grouped_entities["LOC"]

    if "MISC" in grouped_entities:
        resume_data["skills"] = grouped_entities["MISC"]

    return resume_data


def salvage_json_brackets(response_text: str) -> Any | None:
    """
    Attempt to recover and parse JSON-like content from free-form text.

    This function searches for the first JSON structure (object or array),
    then balances any missing closing braces/brackets and attempts to parse the
    recovered string as JSON.

    Args:
        response_text: Text that may contain a partial JSON object/array.

    Returns:
        dict | list | None: Parsed JSON data if recovery succeeds; otherwise
        None.
    """
    if not response_text:
        return None

    # Find JSON start and end
    start_obj = response_text.find("{")
    start_arr = response_text.find("[")
    starts = [x for x in (start_obj, start_arr) if x != -1]
    if not starts:
        return None
    start = min(starts)

    last_curly = response_text.rfind("}")
    last_bracket = response_text.rfind("]")
    ends = [x for x in (last_curly, last_bracket) if x > start]
    candidate = response_text[start : (max(ends) + 1) if ends else None]
    s = candidate.strip()

    # Balance brackets/braces
    pairs = {"{": "}", "[": "]"}
    stack = []
    for ch in s:
        if ch in pairs:
            stack.append(ch)
        elif ch in pairs.values():
            if stack and pairs[stack[-1]] == ch:
                stack.pop()
    while stack:
        s += pairs[stack.pop()]

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def extract_json_content(text) -> Any | None:
    """
    Extract and parse JSON content embedded in a larger text string.

    The function locates the substring between the first '{' and the last '}',
    then attempts to parse it as JSON. If parsing fails, it falls back to
    `salvage_json_brackets` which tries to auto-close missing braces/brackets.

    Args:
        text (str): The raw string potentially containing a JSON object.

    Returns:
        dict | None: A `ResumeSchema` instance when valid JSON
        maps to the schema; a dict/list when recovery parsing is used; or None
        if no JSON-like content can be parsed.
    """
    # Find the index of the first opening curly brace
    start_index = text.find("{")

    # Find the index of the last closing curly brace
    end_index = text.rfind("}")
    logger.info("Start Index %s, End Index %s", start_index, end_index)
    # Check if both braces were found and the end is after the start
    if start_index != -1 and end_index != -1 and end_index > start_index:
        # Extract the content between the braces
        # We add 1 to the start_index to exclude the brace itself
        parsed_text = text[start_index : end_index + 1]
        try:
            json_str = json.loads(parsed_text)
            return json_str
        except json.JSONDecodeError as e:
            logger.info("JSON parsed fail. Detail: %s", e)
            return salvage_json_brackets(
                parsed_text
            )  # We also return the parsed text because it can be a JSON-uncomplete sentence.
    else:
        return None
