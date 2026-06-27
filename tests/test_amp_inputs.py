from __future__ import annotations

import unittest

from veloserve_ai_amp.inputs import normalize_inputs


class AmpInputsTests(unittest.TestCase):
    def test_draft_issue_contract_adds_strict_headings_and_scope_lock(self) -> None:
        normalized = normalize_inputs(
            {
                "task_type": "draft_issue",
                "repo_scope": "platform",
                "segment": "webhooks",
                "target": "platform.veloserve.io",
                "goal": (
                    "Draft a GitHub-ready issue for webhook hardening with signature verification, "
                    "replay protection, idempotency, logging, failure handling, and rollout scope."
                ),
                "artifacts_required": [
                    "issue_title",
                    "github_issue_body",
                    "acceptance_criteria",
                    "risk_summary",
                    "approval_gates",
                ],
            }
        )

        contract = normalized["artifact_output_contract"]
        self.assertIn("## github_issue_body", contract)
        self.assertIn("fenced `md` code block", contract)
        self.assertIn("180-220 words", contract)

        scope_lock = normalized["scope_lock_rules"]
        self.assertIn("Do not silently narrow or replace the requested scope", scope_lock)
        self.assertIn("do not drop replay protection, idempotency, DB, or rollout concerns", scope_lock)

    def test_list_fields_are_rendered_as_clean_text_helpers(self) -> None:
        normalized = normalize_inputs(
            {
                "artifacts_required": ["issue_title", "github_issue_body"],
                "context_urls": ["https://platform.veloserve.io", "https://example.test/spec"],
            }
        )

        self.assertEqual(normalized["artifacts_required_text"], "issue_title, github_issue_body")
        self.assertEqual(
            normalized["context_urls_text"],
            "- https://platform.veloserve.io\n- https://example.test/spec",
        )

    def test_repo_profile_exposes_real_repo_stack_details(self) -> None:
        normalized = normalize_inputs({"repo_scope": "velopanel"})

        repo_profile = normalized["repo_profile"]
        self.assertIn("Repo profile for `velopanel`", repo_profile)
        self.assertIn("Rust", repo_profile)
        self.assertIn("Svelte SPA at panel-ui/package.json", repo_profile)
        self.assertIn("panel-ui/src/pages/CreateAccount.svelte", repo_profile)


if __name__ == "__main__":
    unittest.main()
