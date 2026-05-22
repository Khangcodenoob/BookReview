---
name: skill-tester
description: Validate and score skill quality (structure, scripts, scoring). Use when auditing Cursor/Codex skills, creating new skills, or reviewing SKILL.md quality gates.
---

# Skill Tester

## Purpose

This skill validates and scores quality of skills in a repository.
It is designed for:

- Structure validation
- Script testing
- Quality scoring

Use this skill when:

- A user asks to create or review skills
- A team needs quality gates for skills
- CI/CD needs automatic validation for `SKILL.md` and utility scripts

## Scope

This skill focuses on **skills QA**, not product feature QA.
It validates skill directories such as:

- `.cursor/skills/<skill-name>/`
- `~/.codex/skills/<skill-name>/`
- Any folder with `SKILL.md`

## Validation Dimensions

### 1) Structure Validation

Check:

- `SKILL.md` exists
- Optional files: `README.md`, `reference.md`, `examples.md`
- Optional folder: `scripts/`
- Markdown format and frontmatter validity

### 2) Script Testing

For Python scripts in `scripts/`:

- Syntax compiles
- Standard-library imports only (if policy requires)
- Script returns useful `--help`
- Runtime test with timeout
- Output can be parsed (JSON if declared)

### 3) Quality Scoring

Weighted dimensions:

- Documentation: 25%
- Code quality: 25%
- Completeness: 25%
- Usability: 25%

Grade mapping:

- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: below 60

## Tier Requirements

### BASIC

- `SKILL.md` >= 100 lines
- At least 1 script (100-300 LOC)
- Basic argparse and I/O

### STANDARD

- `SKILL.md` >= 200 lines
- 1-2 scripts (300-500 LOC)
- Advanced argparse
- JSON + text output
- Better edge-case handling

### POWERFUL

- `SKILL.md` >= 300 lines
- 2-3 scripts (500-800 LOC)
- Multiple modes/subcommands
- Robust validation and recovery
- CI/CD integration ready

## Execution Workflow

Use this checklist every time:

1. Discover target skill directories.
2. Validate structure and frontmatter.
3. Inspect and test scripts.
4. Compute weighted score and letter grade.
5. Emit human summary and machine JSON.
6. Provide actionable recommendations.

## Output Formats

### Human-readable

Provide:

- Skill path
- Tier detected/recommended
- Pass/fail by dimension
- Final score + grade
- Improvement actions

### JSON

Provide fields:

- `skill_path`
- `timestamp`
- `validation_results`
- `overall_score`
- `letter_grade`
- `improvement_suggestions`

## Safety Rules

- Do not execute untrusted scripts without timeout.
- Do not write outside workspace when running checks.
- Keep validation read-first, write only on explicit request.
- Never hide validation failures.

## Integration Notes

### Pre-commit

Block commit if:

- Missing `SKILL.md`
- Invalid frontmatter
- Score below threshold (example: 75)

### CI

Run validator + tester + scorer per changed skill.
Export artifacts as JSON reports.

## Project-specific Defaults (BookReview)

For this repository:

- Target skill location: `.cursor/skills/`
- Default threshold: `>= 75`
- Preferred report output:
  - concise human summary in chat
  - JSON file under `docs/quality-reports/` when requested

## Quick Commands

When scripts exist:

- `python scripts/skill_validator.py <skill_path> --json`
- `python scripts/script_tester.py <skill_path> --timeout 30`
- `python scripts/quality_scorer.py <skill_path> --detailed`

If scripts do not exist yet, start with static checks:

- frontmatter and sections
- minimum line count per tier
- references and examples completeness

## Recommendations Policy

Always prioritize:

1. Blocking issues (invalid structure, broken scripts)
2. Reliability issues (error handling, output consistency)
3. Usability issues (missing examples, weak help text)
4. Nice-to-have improvements

