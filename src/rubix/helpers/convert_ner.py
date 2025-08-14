from typing import List, Dict, Optional
from pydantic import BaseModel
from collections import defaultdict

from rubix.schemas.resume import ResumeSchema, Education

class ParsedResult(BaseModel):
    content: Optional[ResumeSchema] = None


def ner_to_resume_schema(ner_results: List[Dict]) -> ParsedResult:
    """
    Convert Hugging Face NER results to a ParsedResult with ResumeSchema in .content.
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

    return ParsedResult(content=ResumeSchema(**resume_data))

