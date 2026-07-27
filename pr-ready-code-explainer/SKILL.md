---
name: pr-ready-code-explainer
description: Explain a final PR-ready code change for reviewers. Use only after implementation and review are complete.
---

# PR Ready Code Explainer

Use this skill only when:
- implementation is complete
- review loop is complete
- required checks have passed, or the caller says the change is PR-ready

Do not use this skill for:
- code changes
- bug fixing
- additional review rounds
- planning

Given the final diff and available context, produce:

1. Summary
What this change does and why.

2. What changed
Key implementation points only.

3. Reviewer focus points
What deserves careful review.

4. Risks / limitations
Remaining concerns or edge cases.

5. Validation
Tests, checks, and manual verification if available.

6. PR description draft
A compact markdown draft suitable for a pull request.

Constraints:
- Output must be in Japanese. (All sections from 1 to 6 must be written in natural Japanese)
- Do not modify code
- Do not invent intent, tests, or guarantees
- State uncertainty explicitly when context is missing
- Prefer explanation of why over file-by-file narration
