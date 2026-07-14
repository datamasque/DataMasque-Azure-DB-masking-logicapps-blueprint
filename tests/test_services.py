"""Unit tests for shared service helpers."""
import importlib


def test_verify_tls_defaults_secure(monkeypatch):
    monkeypatch.delenv("DATAMASQUE_VERIFY_TLS", raising=False)
    mod = importlib.import_module("functions.services.datamasque")
    assert mod.verify_tls() is True


def test_verify_tls_can_be_disabled(monkeypatch):
    mod = importlib.import_module("functions.services.datamasque")
    for falsy in ("false", "0", "no", "FALSE"):
        monkeypatch.setenv("DATAMASQUE_VERIFY_TLS", falsy)
        assert mod.verify_tls() is False


def test_run_secret_from_env_not_literal(monkeypatch):
    mod = importlib.import_module("functions.services.datamasque")
    monkeypatch.delenv("DATAMASQUE_RUN_SECRET", raising=False)
    assert mod.run_secret() == ""
    monkeypatch.setenv("DATAMASQUE_RUN_SECRET", "configured-secret")
    assert mod.run_secret() == "configured-secret"


def test_service_principal_prefers_env(monkeypatch):
    mod = importlib.import_module("functions.services.credentials")
    monkeypatch.setenv("TENANT_ID", "env-tenant")
    monkeypatch.setenv("CLIENT_ID", "env-client")
    monkeypatch.setenv("CLIENT_SECRET", "env-secret")
    tenant, client, secret = mod.service_principal({"TenantID": "body", "ClientID": "body", "ClientSecret": "body"})
    assert (tenant, client, secret) == ("env-tenant", "env-client", "env-secret")
