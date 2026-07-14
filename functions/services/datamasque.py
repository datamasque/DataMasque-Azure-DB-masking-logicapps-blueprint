"""Shared DataMasque API helpers for the Azure Functions.

Centralises TLS-verification and run-secret config so the individual functions
do not each hardcode insecure defaults.
"""
import os


def verify_tls() -> bool:
    """Whether to verify the DataMasque instance's TLS certificate.

    Defaults to True (secure). Set DATAMASQUE_VERIFY_TLS to 'false'/'0'/'no'
    only for a trusted self-signed/private instance.
    """
    return os.environ.get("DATAMASQUE_VERIFY_TLS", "true").strip().lower() not in (
        "false",
        "0",
        "no",
    )


def run_secret() -> str:
    """The DataMasque run secret, sourced from configuration.

    Returns an empty string when unset (DataMasque treats this as no secret),
    never a committed literal.
    """
    return os.environ.get("DATAMASQUE_RUN_SECRET", "")
