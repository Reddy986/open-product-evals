"""Transparent keyword baseline for checking the evaluation pipeline.

This is intentionally not an LLM. It gives contributors a zero-setup way to
exercise loading, scoring, error analysis, and reporting before running models.
"""

from __future__ import annotations

from typing import Any


BILLING_TERMS = {
    "bill",
    "billing",
    "card",
    "charge",
    "charged",
    "coupon",
    "discount",
    "invoice",
    "pay",
    "payment",
    "price",
    "refund",
    "renewal",
    "subscription",
}
ACCOUNT_TERMS = {
    "account",
    "delete my",
    "device",
    "email address",
    "identity",
    "login",
    "password",
    "personal data",
    "profile",
    "security page",
    "sign in",
    "two-factor",
    "verification",
}
FEATURE_PHRASES = {
    "add a",
    "add custom",
    "could you add",
    "do you plan",
    "it would be useful",
    "please add",
    "we would like to",
}
TECHNICAL_TERMS = {
    "api",
    "app",
    "blank page",
    "button",
    "crash",
    "dashboard",
    "disappeared",
    "export",
    "freeze",
    "integration",
    "late",
    "load",
    "nothing happened",
    "processing",
    "rate limit",
    "report",
    "search",
    "sync",
    "upload",
    "vanished",
}

URGENT_TERMS = {
    "another country",
    "compromised",
    "every user",
    "never used",
    "nobody recognizes",
    "not me",
    "unauthorized",
    "vanished",
}
HIGH_TERMS = {
    "cannot access",
    "cannot sign in",
    "crash",
    "delete my",
    "disappeared",
    "former employee",
    "lawyer",
    "no longer control",
    "personal data",
    "refund",
    "stopped",
    "tax id",
}
LOW_TERMS = {
    "copy of",
    "difference between",
    "everything still works",
    "guide",
    "how api",
    "it works now",
    "where can i",
}
ESCALATION_TERMS = URGENT_TERMS | HIGH_TERMS | {
    "charged twice",
    "discuss a formal partnership",
    "full year",
    "missing from the invoice",
    "received another charge",
}


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def predict(ticket: str) -> dict[str, Any]:
    """Return a deterministic triage prediction for one ticket."""

    text = ticket.casefold()

    if _contains_any(text, BILLING_TERMS):
        category = "billing"
    elif _contains_any(text, ACCOUNT_TERMS):
        category = "account_access"
    elif _contains_any(text, FEATURE_PHRASES):
        category = "feature_request"
    elif _contains_any(text, TECHNICAL_TERMS):
        category = "technical_issue"
    else:
        category = "general_question"

    if _contains_any(text, URGENT_TERMS):
        priority = "urgent"
    elif _contains_any(text, HIGH_TERMS):
        priority = "high"
    elif _contains_any(text, LOW_TERMS):
        priority = "low"
    else:
        priority = "medium"

    return {
        "category": category,
        "priority": priority,
        "escalate": _contains_any(text, ESCALATION_TERMS),
    }

