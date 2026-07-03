import importlib.util
import sys
from types import ModuleType, SimpleNamespace


if importlib.util.find_spec("asyncua") is None:
    asyncua = ModuleType("asyncua")
    asyncua.Client = object
    asyncua.ua = SimpleNamespace(
        VariantType=SimpleNamespace(),
        DataValue=object,
        Variant=object,
    )
    sys.modules["asyncua"] = asyncua

if importlib.util.find_spec("xmlschema") is None:
    xmlschema = ModuleType("xmlschema")
    xmlschema.validate = lambda *args, **kwargs: None
    sys.modules["xmlschema"] = xmlschema

from src.backend import control


def _fail_on_input(*args, **kwargs):
    raise AssertionError("Recipe execution must not request confirmation.")


def test_run_from_files_starts_without_confirmation(monkeypatch):
    procedure = object()
    mtps = object()
    calls = []

    monkeypatch.setattr(
        control,
        "build_execution_procedure",
        lambda recipe_files=None, mtp_files=None: (procedure, mtps),
    )
    monkeypatch.setattr(control, "main", lambda proc, modules: calls.append((proc, modules)))
    monkeypatch.setattr("builtins.input", _fail_on_input)

    control.run_from_files(mtp_files=["module.aml"], recipe_files=["recipe.xml"])

    assert calls == [(procedure, mtps)]


def test_material_requirement_does_not_request_confirmation(monkeypatch):
    bml_step = SimpleNamespace(
        name="Mixing",
        reqs=[SimpleNamespace(const="Material=H2O")],
        getName=lambda: "Mixing",
        getId=lambda: "mixing",
    )
    procedure = [{"bml": bml_step, "inst": None}]

    monkeypatch.setattr(control.seq, "drawSequenceDiagram", lambda item, proc: None)
    monkeypatch.setattr("builtins.input", _fail_on_input)

    control.main(procedure, [])
