---
name: Rule Change
about: Propose an addition, update, or deprecation to a rule.
title: "[Rule]: Short description of the change"
labels: "type: rule-update, needs-triage"
assignees: ''
---

**Summary**
Briefly describe the rule change and its intent.

**Rule IDs affected**
List one or more rule IDs (e.g., `codeguard-0-...`). If new, propose an ID.

**Source files (unified rules)**
Point to the unified markdown source(s) to be edited (e.g., `rules/...` or `additional_rules/...`). Do not hand-edit `ide_rules/**`.

**Scope**
- Target IDE formats:
  - [ ] Cursor (.cursor)
  - [ ] Windsurf (.windsurf)
  - [ ] Copilot (.github/instructions)
- Application mode:
  - [ ] languages list
  - [ ] alwaysApply=true
- Languages (if applicable):

**Details of change**
Provide precise edits or content to add/remove, including rationale and references (links allowed).

**Acceptance criteria**
- Validation passes: `python src/validate_unified_rules.py <rules_dir>`
- Regeneration produces expected outputs for all formats: `python src/unified_to_all.py <rules_dir> .`
- Generated `ide_rules/**` show the intended changes only

**Impact/Risk**
Describe any compatibility or rollout considerations.

**Additional context**
Anything else reviewers should know.


