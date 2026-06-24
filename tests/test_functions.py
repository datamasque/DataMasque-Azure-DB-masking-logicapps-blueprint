"""Unit tests for the Azure Function pure logic (§5.12).

Run: pytest -q
"""
import importlib
import json

import pytest

import azure.functions as func  # stubbed in conftest


# --------------------------------------------------------------------------
# describe_source_database.checkDatabase selection
# --------------------------------------------------------------------------
def _db(name, db_id, created):
    return {
        "name": name,
        "location": "eastus",
        "sku": {"name": "S0"},
        "id": f"/dbs/{name}",
        "properties": {"databaseId": db_id, "creationDate": created},
    }


def test_check_database_prefers_matching_database_id():
    mod = importlib.import_module("functions.describe_source_database")
    databases = [
        _db("master", "master-id", "2020-01-01T00:00:00Z"),
        _db("older", "other-id", "2021-01-01T00:00:00Z"),
        _db("target", "db-id-target", "2022-01-01T00:00:00Z"),
    ]
    result = mod.checkDatabase(databases)
    assert result["name"] == "target"


def test_check_database_falls_back_to_newest_non_master():
    mod = importlib.import_module("functions.describe_source_database")
    databases = [
        _db("master", "master-id", "2099-01-01T00:00:00Z"),  # newest but excluded
        _db("old", "x", "2020-01-01T00:00:00Z"),
        _db("newest", "y", "2023-01-01T00:00:00Z"),
    ]
    result = mod.checkDatabase(databases)
    assert result["name"] == "newest"


def test_check_database_raises_on_empty():
    mod = importlib.import_module("functions.describe_source_database")
    import pytest
    with pytest.raises(ValueError):
        mod.checkDatabase([])


def test_check_database_skips_in_creating_db_without_creationdate():
    mod = importlib.import_module("functions.describe_source_database")
    creating = {
        "name": "creating",
        "location": "eastus",
        "sku": {"name": "S0"},
        "id": "/dbs/creating",
        "properties": {"databaseId": "z"},  # no creationDate yet
    }
    ready = _db("ready", "y", "2023-01-01T00:00:00Z")
    result = mod.checkDatabase([creating, ready])
    assert result["name"] == "ready"


# --------------------------------------------------------------------------
# create_firewall 0.0.0.0 rule-merge
# --------------------------------------------------------------------------
class _FakeSQL:
    """Records firewall rule create/update calls."""

    last = None

    def __init__(self, *args, **kwargs):
        _FakeSQL.last = self
        self.calls = []

    def creates_or_updates_a_firewall_rule(self, subscription_id, server, name, body):
        self.calls.append((name, body))

        class _Res:
            status_code = 200

        return _Res()


def _run_firewall(monkeypatch, source_rules, allow_azure_services):
    mod = importlib.import_module("functions.create_firewall_for_staging_sql_server")
    importlib.reload(mod)  # re-read env-driven module flag
    monkeypatch.setattr(mod, "MicrosoftSQL", _FakeSQL)
    monkeypatch.setattr(mod, "allow_azure_services", allow_azure_services)

    req = func.HttpRequest(body={
        "TenantID": "t", "ClientID": "c", "ClientSecret": "s",
        "SubscriptionID": "sub", "ResourceGroup": "rg",
        "DBInstanceIdentifier": "staging-server",
        "DBSnapshotIdentifier": {"name": "db"},
        "FirewallRules": json.dumps(source_rules),
        "DATAMASQUE_CONNECTION_ID": "conn", "DATAMASQUE_RULESET_ID": "rs",
    })
    mod.main(req)
    return _FakeSQL.last.calls


def test_firewall_does_not_add_open_rule_by_default(monkeypatch):
    rules = [{"name": "client-ip", "properties": {"startIpAddress": "10.0.0.1", "endIpAddress": "10.0.0.1"}}]
    calls = _run_firewall(monkeypatch, rules, allow_azure_services=False)
    names = [c[0] for c in calls]
    assert names == ["client-ip"]
    assert "AllowAzureServices" not in names


def test_firewall_adds_azure_services_rule_when_enabled(monkeypatch):
    rules = [{"name": "client-ip", "properties": {"startIpAddress": "10.0.0.1", "endIpAddress": "10.0.0.1"}}]
    calls = _run_firewall(monkeypatch, rules, allow_azure_services=True)
    names = [c[0] for c in calls]
    assert "AllowAzureServices" in names
    azure_rule = dict(calls)["AllowAzureServices"]
    assert azure_rule["properties"]["startIpAddress"] == "0.0.0.0"


def test_firewall_skips_duplicate_azure_rule_when_source_has_it(monkeypatch):
    rules = [{"name": "AllowAllAzure", "properties": {"startIpAddress": "0.0.0.0", "endIpAddress": "0.0.0.0"}}]
    calls = _run_firewall(monkeypatch, rules, allow_azure_services=True)
    names = [c[0] for c in calls]
    # source already carries the 0.0.0.0 rule, so we don't add a second one
    assert names == ["AllowAllAzure"]


# --------------------------------------------------------------------------
# wait_datamasque_job status gate
# --------------------------------------------------------------------------
def _wait_response(monkeypatch, status):
    mod = importlib.import_module("functions.wait_datamasque_job")

    class _Res:
        status_code = 200

        def json(self):
            return {"status": status}

    monkeypatch.setattr(mod, "check_run", lambda run_id: _Res())
    res = mod.main(func.HttpRequest(body={"RunID": "run-1"}))
    return res.status_code, json.loads(res.body)


@pytest.mark.parametrize("status", ["queued", "validating", "running", "cancelling"])
def test_wait_in_progress_statuses_keep_polling(monkeypatch, status):
    code, body = _wait_response(monkeypatch, status)
    assert code == 200
    assert body["in_progress"] is True


@pytest.mark.parametrize("status", ["finished", "finished_with_warnings"])
def test_wait_success_statuses_pass_the_gate(monkeypatch, status):
    code, body = _wait_response(monkeypatch, status)
    assert code == 200
    assert body["in_progress"] is False


@pytest.mark.parametrize("status", ["failed", "cancelled", "some_future_status"])
def test_wait_terminal_non_success_statuses_return_500(monkeypatch, status):
    code, body = _wait_response(monkeypatch, status)
    assert code == 500
    assert body["in_progress"] is False
