"""S6 canonicalisation and validation: schema gate plus invariants V-1..V-7."""

from audiosheet.validate.invariants import check_invariants
from audiosheet.validate.jsonschema_gate import parse_document, validate_payload

__all__ = ["check_invariants", "parse_document", "validate_payload"]
