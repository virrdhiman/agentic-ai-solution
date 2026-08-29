# Architecture

> **Author:** Virender Dhiman

This document describes the internal architecture of the Universal Autonomous Agentic Engineering System.

## High-Level Overview

```
                    ┌──────────────────────┐
                    │      USER / API      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ UNIVERSAL PROBLEM    │
                    │      ROUTER          │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │    AGENT CORE        │
                    │  Orchestrator        │
                    │  State Machine       │
                    │  Evidence Engine     │
                    │  Quality Engine      │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │  DYNAMIC AGENT TEAM  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   PROVIDER LAYER     │
                    │  Mock / OpenSource   │
                    │  n8n                 │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │      TOOL LAYER      │
                    │  Git / Shell / Files  │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   TEST & QUALITY     │
                    │  Test → Repair Loop  │
                    │  Review → Verify     │
                    └──────────────────────┘
```

## Core Components

### 1. State Machine (`core/state.py`)

The state machine governs every state transition a task can make. It prevents invalid transitions and provides the backbone for the orchestrator lifecycle.

**States (20):**
`NEW → UNDERSTANDING → CLASSIFYING → INVESTIGATING → REPRODUCING → DIAGNOSING → PLANNING → IMPLEMENTING → TESTING → REGRESSION_TESTING → SECURITY_REVIEW → CODE_REVIEW → ADVERSARIAL_REVIEW → ACCEPTANCE_CHECK → DOCUMENTING → EVIDENCE_CHECK → RESOLVED`

**Error/recovery states:** `FAILED`, `REPAIRING`, `HUMAN_ACTION_REQUIRED`, `CANCELLED`

The transition table is defined in `VALID_TRANSITIONS` and is enforced by `can_transition()` and `transition()`.

### 2. Orchestrator (`core/orchestrator.py`)

The orchestrator is the central control loop. It:
- Drives the state machine through every lifecycle step
- Delegates to the AI provider for analysis, planning, generation, and review
- Collects evidence at every step
- Records agent runs for quality scoring
- Persists task state to disk for crash recovery
- Implements the repair loop with strategy escalation

**Key methods:**
- `run()` — Execute the full lifecycle
- `_classify()` → `_investigate()` → `_reproduce()` → `_diagnose()` → `_plan()` → `_implement()` → `_test_loop()` → `_regression_test()` → `_security_review()` → `_code_review()` → `_adversarial_review()` → `_acceptance_check()` → `_document()` → `_evidence_check()` → `_finalize()`
- `resume()` — Reload a persisted task and continue

### 3. Evidence Engine (`core/evidence.py`)

Collects and validates all evidence produced during a task lifecycle. Responsible for:
- Tracking test results, acceptance criteria, failures, and agent runs
- Calculating the 9-dimension quality score
- Checking for contradictions between claims and evidence
- Verifying all hard completion gates
- Generating the final evidence report

### 4. Universal Problem Router (`core/router.py`)

Classifies incoming problems and builds the minimal competent agent team. Uses:
- Keyword-based classification for speed
- Skill-to-agent mapping
- Problem-type-to-agent-team mapping
- Risk assessment
- Default acceptance criteria generation

### 5. Provider Layer (`providers/`)

Abstracts AI backends behind the `AIProvider` interface. Methods: `analyze`, `plan`, `generate`, `debug`, `review`, `summarize`.

| Provider | Description |
|----------|-------------|
| `MockProvider` | Deterministic responses for testing |
| `OpenSourceProvider` | Any OpenAI-compatible API (Ollama, vLLM, etc.) |
| `N8NProvider` | n8N workflow orchestration (requires credentials) |

The provider router (`providers/router.py`) creates the appropriate provider based on config, with automatic fallback to mock.

### 6. Tool Layer (`tools/`)

Every external capability goes through a tool interface with permission checking, timeout, and audit logging.

| Tool | Description | Permission |
|------|-------------|------------|
| `FileReadTool` | Read file contents | READ_ONLY |
| `FileWriteTool` | Write file contents | DEVELOPMENT_WRITE |
| `ListDirectoryTool` | List directory entries | READ_ONLY |
| `ShellTool` | Execute shell commands | DEVELOPMENT_WRITE |
| `GitTool` | Git operations | DEVELOPMENT_WRITE |

### 7. Quality Scoring

The quality score is a weighted average of 9 dimensions (0-100 scale):

| Dimension | Weight | How it's scored |
|-----------|--------|-----------------|
| Functional Correctness | 20% | % of tests that passed |
| Acceptance Criteria | 20% | % of criteria met |
| Testing | 15% | 100 if ≥3 tests all pass |
| Regression Safety | 10% | 100 if no unresolved failures |
| Code Quality | 10% | 100 if ≥5 evidence items |
| Security | 10% | 100 if no security failures |
| Architecture | 5% | 100 if ≥5 agent runs |
| Documentation | 5% | 100 if documentation agent ran |
| Maintainability | 5% | 100 if ≥3 evidence + ≥3 agent runs |

The display score is `total / 10` (e.g., 95.0 → "9.5/10").

### 8. Completion Gates

A task is only marked RESOLVED when ALL of these pass:
1. `problem_understood` — Classification exists
2. `acceptance_criteria_met` — All criteria PASS or N/A
3. `tests_passed` — All test results are PASSED
4. `evidence_exists` — At least one evidence item collected
5. `no_contradictions` — No contradictions between claims and evidence
6. `no_unresolved_failures` — All failures have a fix_result

## Data Flow

```
User submits problem
        ↓
Router classifies → ProblemClassification
        ↓
Orchestrator creates Task
        ↓
Lifecycle loop:
  understand → classify → investigate → reproduce → diagnose
  → plan → implement → test → regression → security
  → code review → adversarial → acceptance → document
  → evidence check → finalize
        ↓
EvidenceEngine collects evidence at every step
        ↓
QualityEngine scores the work (9 dimensions)
        ↓
Completion gates verified
        ↓
If all gates pass → RESOLVED (10/10)
If any gate fails → HUMAN_ACTION_REQUIRED or REPAIR loop
```

## Persistence

Every task persists to disk:
- `agent-work/tasks/{task-id}/task.json` — Task state
- `agent-work/tasks/{task-id}/evidence.json` — All evidence
- `agent-work/tasks/{task-id}/audit.json` — Audit log
- `agent-work/tasks/{task-id}/FINAL_REPORT.md` — Human-readable report

On crash/restart, the orchestrator can `resume()` from the last persisted state.

## Safety Controls

- Destructive shell commands are blocked by default
- Production environment requires explicit approval
- Every operation is audit-logged
- Evidence always outranks AI opinion
- No false success claims allowed
- The system never runs `git push` without explicit approval
