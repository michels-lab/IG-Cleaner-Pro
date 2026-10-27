"""Prevent silent Windows Unfollow transport drift.

The owner-authorized Windows worker MUST select the browser-local reference
mutation for Unfollow; Cancel Pending still uses visible Requested controls.
These tests contain no Instagram session and perform no relationship changes.
"""
import ast
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import profile_actions


class ReferenceTransportRoutingTests(unittest.TestCase):
    def test_safe_default_for_explicit_unfollow_callers(self):
        default = inspect.signature(
            profile_actions.perform_visible_action
        ).parameters["use_reference_transport"].default
        self.assertIs(default, True,
            "Reference Unfollow default must not silently revert to visible clicks.")

    def test_real_windows_worker_must_pass_transport_explicitly(self):
        source = ast.parse((ROOT / "tools" / "profile_actions.py").read_text(
            encoding="utf-8"))
        worker = next(node for node in source.body
                      if isinstance(node, ast.ClassDef) and node.name == "ActionRobot")
        actual_calls = [
            node for method in worker.body if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
            for node in ast.walk(method) if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "perform_visible_action"
        ]
        self.assertEqual(len(actual_calls), 1,
            "Every Windows action worker entrypoint must be audited for reference routing.")
        bound = [kw for kw in actual_calls[0].keywords if kw.arg == "use_reference_transport"]
        self.assertEqual(len(bound), 1,
            "A missing explicit flag silently chooses the wrong Unfollow transport.")
        self.assertEqual(
            ast.dump(bound[0].value),
            ast.dump(ast.parse('self.task == "unfollow"', mode="eval").body),
            "Only Unfollow uses the owner-reference GraphQL mutation; Cancel Pending must not.")

    def test_mutation_branch_requires_durable_wal(self):
        src = inspect.getsource(profile_actions.perform_visible_action)
        self.assertIn('and on_pre_click is not None and use_reference_transport', src)
        self.assertIn('verify_after=_verify_unfollow_after_readonly_refresh', src)
        self.assertIn('on_pre_click=lambda phase:', (ROOT/"tools"/"profile_actions.py")
                      .read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
