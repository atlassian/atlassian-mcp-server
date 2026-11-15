"""Run with python3 -B scripts/test_jql_builder.py."""

import importlib.util
from pathlib import Path
import sys
import unittest


def load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


REPO_ROOT = Path(__file__).resolve().parents[1]
JQL_PATHS = [
    REPO_ROOT / "skills" / "generate-status-report" / "scripts" / "jql_builder.py",
    REPO_ROOT / "skills" / "v1" / "generate-status-report" / "scripts" / "jql_builder.py",
]


class TestJQLBuilder(unittest.TestCase):
    def test_both_jql_modules(self):
        for path in JQL_PATHS:
            with self.subTest(path=str(path)):
                mod = load_module_from_path(f"jql_builder_{path.parent.parent.name}", path)
                self._run_all_tests_on_module(mod)

    def _run_all_tests_on_module(self, mod):
        # 1. sanitize_jql_value
        self.assertEqual(mod.sanitize_jql_value(""), "")
        self.assertEqual(mod.sanitize_jql_value("PROJ-123"), "PROJ-123")
        self.assertEqual(mod.sanitize_jql_value("In Progress"), "In Progress")
        self.assertEqual(mod.sanitize_jql_value("dev.user@example.com"), "dev.user@example.com")
        self.assertEqual(mod.sanitize_jql_value('Fix "urgent" bug'), 'Fix ""urgent"" bug')

        # Invalid characters should raise ValueError
        for invalid_val in [
            "PROJ; DROP TABLE",
            "status' OR '1'='1",
            "<script>",
            "test(value)",
            "flag$name",
        ]:
            with self.assertRaises(ValueError):
                mod.sanitize_jql_value(invalid_val)

        # 2. sanitize_order_by
        self.assertEqual(
            mod.sanitize_order_by("priority DESC, updated DESC"),
            "priority DESC, updated DESC",
        )
        self.assertEqual(mod.sanitize_order_by("created ASC"), "created ASC")
        self.assertEqual(
            mod.sanitize_order_by("priority DESC, updated DESC, created ASC"),
            "priority DESC, updated DESC, created ASC",
        )
        with self.assertRaises(ValueError):
            mod.sanitize_order_by("priority DESC; DROP TABLE")

        # 3. build_project_query with default order_by
        default_query = mod.build_project_query("PROJ")
        self.assertEqual(
            default_query,
            'project = "PROJ" AND status != Done ORDER BY priority DESC, updated DESC',
        )

        # build_project_query with options
        q_status = mod.build_project_query(
            "PROJ",
            statuses=["To Do", "In Progress"],
            priorities=["Highest", "High"],
            days_back=7,
            assignee="dev@example.com",
            order_by="created ASC",
        )
        self.assertIn('project = "PROJ"', q_status)
        self.assertIn('status IN ("To Do", "In Progress")', q_status)
        self.assertIn('priority IN ("Highest", "High")', q_status)
        self.assertIn("updated >= -7d", q_status)
        self.assertIn('assignee = "dev@example.com"', q_status)
        self.assertTrue(q_status.endswith("ORDER BY created ASC"))

        # Empty assignee check
        q_empty = mod.build_project_query("PROJ", assignee="EMPTY")
        self.assertIn("assignee is EMPTY", q_empty)

        # Negative days_back check
        with self.assertRaises(ValueError):
            mod.build_project_query("PROJ", days_back=-1)

        # 4. build_blocked_query
        q_blocked = mod.build_blocked_query("PROJ", high_priority_only=True)
        self.assertEqual(
            q_blocked,
            'project = "PROJ" AND status = Blocked AND priority IN (Highest, High) ORDER BY priority DESC, created ASC',
        )

        # 5. build_completed_query
        q_completed = mod.build_completed_query("PROJ", days_back=14)
        self.assertEqual(
            q_completed,
            'project = "PROJ" AND status = Done AND resolved >= -14d ORDER BY resolved DESC',
        )

        # 6. build_in_progress_query
        q_progress = mod.build_in_progress_query("PROJ", priorities=["Highest"])
        self.assertEqual(
            q_progress,
            'project = "PROJ" AND status IN ("In Progress", "In Review") AND priority IN ("Highest") ORDER BY priority DESC, updated DESC',
        )

        # 7. build_risk_query
        q_risk = mod.build_risk_query("PROJ", include_overdue=True)
        self.assertEqual(
            q_risk,
            'project = "PROJ" AND (status = Blocked OR (duedate < now() AND status != Done)) AND priority IN (Highest, High) ORDER BY priority DESC, duedate ASC',
        )

        # 8. build_unassigned_query
        q_unassigned = mod.build_unassigned_query("PROJ", exclude_done=True)
        self.assertEqual(
            q_unassigned,
            'project = "PROJ" AND assignee is EMPTY AND status != Done ORDER BY priority DESC, created ASC',
        )


if __name__ == "__main__":
    unittest.main()
