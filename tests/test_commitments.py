import json
import os
import tempfile
import unittest
from pathlib import Path

import commitments


class CommitmentsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_state = commitments.STATE
        self.old_token = os.environ.pop("LEGAL_GOOGLE_TOKEN", None)
        self.old_token_file = os.environ.pop("LEGAL_GOOGLE_TOKEN_FILE", None)
        commitments.STATE = Path(self.directory.name) / "state.json"

    def tearDown(self):
        commitments.STATE = self.old_state
        if self.old_token is not None:
            os.environ["LEGAL_GOOGLE_TOKEN"] = self.old_token
        os.environ.pop("LEGAL_GOOGLE_TOKEN_FILE", None)
        if self.old_token_file is not None:
            os.environ["LEGAL_GOOGLE_TOKEN_FILE"] = self.old_token_file
        self.directory.cleanup()

    def test_review_and_source_clause(self):
        review = commitments.execute("review_commitments", {})
        self.assertEqual(review["count"], 7)
        self.assertEqual(review["customer_count"], 3)
        self.assertEqual(review["commitments"][0]["id"], "APL-001")
        self.assertEqual(review["commitments"][-1]["id"], "APL-004")
        clause = commitments.execute("get_commitment", {"commitment_id": "APL-007"})
        self.assertEqual(clause["source_kind"], "local_copy_of_drive_document")
        self.assertIn("replaces the 30-day retention period", clause["clause"])

    def test_northstar_review_preserves_the_party_and_deliverables(self):
        review = commitments.execute("review_commitments", {})
        row = next(item for item in review["commitments"] if item["id"] == "APL-008")
        self.assertIn("A+ Active", row["obligation"])
        for deliverable in ("site schedule", "accessibility plan", "named escalation leads"):
            self.assertIn(deliverable, row["obligation"])
        self.assertNotIn("backup contacts", row["obligation"])
        clause = commitments.execute("get_commitment", {"commitment_id": "APL-008"})
        self.assertIn("A+ Active will provide", clause["clause"])
        self.assertIn("Northstar will confirm room availability and participating staff separately", clause["clause"])
        self.assertEqual(row["due_date"], "2026-10-01")

    def test_client_lookup_keeps_assigned_commitments_visible(self):
        commitments.execute("assign_owner", {"commitment_id": "APL-008", "owner": "Khizar", "expected_revision": 0})
        all_open = commitments.execute("review_commitments", {})
        self.assertFalse(all_open["unassigned_only"])
        row = next(item for item in all_open["commitments"] if item["id"] == "APL-008")
        self.assertEqual(row["owner"], "Khizar")
        unassigned = commitments.execute("review_commitments", {"unassigned_only": True})
        self.assertTrue(unassigned["unassigned_only"])
        self.assertNotIn("APL-008", [item["id"] for item in unassigned["commitments"]])

    def test_assignment_reports_mock_and_prevents_stale_write(self):
        result = commitments.execute("assign_owner", {
            "commitment_id": "APL-007", "owner": "Khizar", "expected_revision": 0})
        self.assertEqual(result["sheet_sync"], "mocked_local_only")
        self.assertEqual(result["commitment"]["revision"], 1)
        self.assertEqual(commitments.execute("get_commitment", {"commitment_id": "APL-007"})["owner"], "Khizar")
        self.assertEqual(commitments.execute("get_commitment", {"commitment_id": "APL-007"})["last_sheet_sync"], "mocked_local_only")
        with self.assertRaisesRegex(ValueError, "Record changed"):
            commitments.execute("assign_owner", {
                "commitment_id": "APL-007", "owner": "Anthony", "expected_revision": 0})
        self.assertEqual(json.loads(commitments.STATE.read_text())["commitments"][4]["owner"], "Khizar")


if __name__ == "__main__":
    unittest.main()
