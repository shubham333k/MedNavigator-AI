"""
PHI de-identification utility.
Strips all 18 HIPAA identifiers from text before processing.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


# Patterns for the 18 HIPAA identifiers
HIPAA_PATTERNS: List[Tuple[str, str, str, bool]] = [
    # (Pattern name, regex pattern, replacement, ignore_case)
    ("Names", r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', "[REDACTED_NAME]", False),
    ("Phone Numbers", r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', "[REDACTED_PHONE]", True),
    ("Fax Numbers", r'\bfax[:\s]*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', "[REDACTED_FAX]", True),
    ("Email Addresses", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "[REDACTED_EMAIL]", True),
    ("SSN", r'\b\d{3}-\d{2}-\d{4}\b', "[REDACTED_SSN]", True),
    ("Medical Record Numbers", r'\b(?:MRN|MR#|Medical Record)[:\s#]*\d+\b', "[REDACTED_MRN]", True),
    ("Health Plan Numbers", r'\b(?:Health Plan|Insurance|Policy)[:\s#]*[A-Z0-9]+\b', "[REDACTED_HEALTH_PLAN]", True),
    ("Account Numbers", r'\b(?:Account|Acct)[:\s#]*\d+\b', "[REDACTED_ACCOUNT]", True),
    ("License/Certificate Numbers", r'\b(?:License|Certificate|DEA)[:\s#]*[A-Z0-9]+\b', "[REDACTED_LICENSE]", True),
    ("Vehicle IDs", r'\b(?:VIN|Vehicle)[:\s#]*[A-Z0-9]{17}\b', "[REDACTED_VEHICLE]", True),
    ("URLs", r'https?://(?:(?!pubmed|ncbi|nih|doi|jamanetwork|nejm|bmj|lancet|diabetesjournals|kdigo|aafp)[^\s])+', "[REDACTED_URL]", True),
    ("IP Addresses", r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "[REDACTED_IP]", True),
    ("Dates of Birth", r'\b(?:DOB|Date of Birth|Born)[:\s]*\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', "[REDACTED_DOB]", True),
    ("Dates (specific)", r'\b(?:0[1-9]|1[0-2])[/\-](?:0[1-9]|[12]\d|3[01])[/\-](?:19|20)\d{2}\b', "[REDACTED_DATE]", True),
    ("Zip Codes (full)", r'\b\d{5}-\d{4}\b', "[REDACTED_ZIP]", True),
]

# Medical terms that should NOT be redacted (common false positives)
MEDICAL_TERM_WHITELIST = {
    "type", "stage", "grade", "class", "group", "level", "phase",
    "blood", "pressure", "heart", "rate", "body", "mass", "index",
    "white", "cell", "count", "red", "hemoglobin", "platelet",
}


def deidentify_text(text: str, aggressive: bool = False) -> str:
    """
    Remove PHI (Protected Health Information) from text.

    Args:
        text: Input text potentially containing PHI
        aggressive: If True, apply more aggressive pattern matching

    Returns:
        De-identified text with PHI replaced by [REDACTED_*] markers
    """
    if not text:
        return text

    result = text
    redaction_count = 0

    for name, pattern, replacement, ignore_case in HIPAA_PATTERNS:
        flags = re.IGNORECASE if ignore_case else 0
        matches = re.findall(pattern, result, flags)
        if matches:
            result = re.sub(pattern, replacement, result, flags=flags)
            redaction_count += len(matches)

    if redaction_count > 0:
        logger.info(f"De-identified text: {redaction_count} PHI instances redacted")

    return result


def contains_phi(text: str) -> bool:
    """
    Check if text potentially contains PHI.

    Returns True if any HIPAA identifier patterns are detected.
    """
    for name, pattern, _, ignore_case in HIPAA_PATTERNS:
        flags = re.IGNORECASE if ignore_case else 0
        if re.search(pattern, text, flags):
            return True
    return False


def deidentify_dict(data: dict) -> dict:
    """De-identify all string values in a dictionary."""
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = deidentify_text(value)
        elif isinstance(value, dict):
            result[key] = deidentify_dict(value)
        elif isinstance(value, list):
            result[key] = [
                deidentify_text(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result
