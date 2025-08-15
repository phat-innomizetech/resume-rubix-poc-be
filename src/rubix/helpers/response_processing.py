import json
import logging
from typing import List, Dict
from collections import defaultdict

from rubix.schemas.resume import ResumeSchema, Education

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

def ner_to_resume_schema(ner_results: List[Dict]) -> ResumeSchema:
    """
    Convert Hugging Face NER results to a ResumeSchema.
    """
    grouped_entities = defaultdict(list)
    current_entity = None
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
    resume_data = {}

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

    return ResumeSchema(**resume_data)

def extract_json_content(text):
    """
    Extracts content between the first and last curly braces.
    This function is useful for cleaning up API responses that
    may contain extra text before or after a JSON object.

    Args:
        text (str): The string containing the JSON object.

    Returns:
        str or None: The extracted content as a string, or None if
                     no curly braces are found.
    """
    # Find the index of the first opening curly brace
    start_index = text.find('{')

    # Find the index of the last closing curly brace
    end_index = text.rfind('}')

    # Check if both braces were found and the end is after the start
    if start_index != -1 and end_index != -1 and end_index > start_index:
        # Extract the content between the braces
        # We add 1 to the start_index to exclude the brace itself
        parsed_text = text[start_index:end_index+1]
        try:
            json_str = json.loads(parsed_text)
            return ResumeSchema(**json_str)
        except json.JSONDecodeError as e:
            logger.info("JSON parsed fail. Detail: %s", e)
            return ResumeSchema()
    else:
        return ResumeSchema()

