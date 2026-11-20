---
name: garden-auto-capture
description: Capture low-threshold, source-backed traces from the current conversation or work context into Terrarium's machine Inbox when a concrete decision, comparison, observation, failure, or unresolved question is worth later rediscovery. This skill may run implicitly; it is not a global conversation event hook.
metadata:
  short-description: Capture searchable traces in the machine Inbox
---

# Capture to the machine Inbox

Use this skill at a natural boundary in the current Codex conversation or work session when the available context contains a useful trace. It sees only the conversation and work context available in the current invocation. It is not an event hook, background watcher, or guarantee that every conversation will be captured.

When selected implicitly, perform the bounded capture pass without asking the user to predict whether the item will matter later. Keep the capture local and brief so it does not interrupt the main task.

## Capture threshold

Capture a candidate when the current context contains at least one of these:

- a concrete decision and the reason or trade-off behind it;
- a comparison that selected, rejected, or constrained an option;
- a measurement, observed result, reproducible command outcome, or other concrete evidence;
- a failed approach, correction, surprising behavior, or discovered constraint;
- an unresolved question that could guide a later investigation;
- a reusable design hypothesis or cross-project lesson grounded in the current work.

Use a low threshold. The capture does not need to be canonical or likely to matter in the future. Do not capture greetings, generic encouragement, unsupported restatements, or sensitive material. If there is no candidate, do nothing and report an empty capture when appropriate.

## Destination and hard boundaries

- Write only new Markdown files under `~/workspace/terrarium/machine-inbox/`. Resolve and verify the directory before writing; stop if it is missing or ambiguous.
- Never modify, overwrite, delete, move, or rename an existing file, including `machine-inbox/index.md`.
- Do not write to `inbox/`, `machine-notes/`, `decisions/`, `principles/`, `projects/`, or any other Garden directory. Organizing, deduplicating, summarizing existing notes, and canonical promotion belong to another workflow.
- Read existing filenames or note text only for an obvious duplicate check and filename collision check. Do not rewrite the existing note when a duplicate is found.
- Capture at most three new notes per invocation. Combine closely related claims into one note.
- Exclude secrets, credentials, access tokens, private keys, and unnecessary personal or sensitive information. A conversation ID or turn locator may be recorded only when the runtime exposes it and it is useful for finding the source; never invent one.
- If the current user explicitly asks not to save or capture, skip the write.

## Workflow

1. Review only the available current conversation and work context. Extract up to three independent candidates and preserve the wording and scope supported by that context.
2. For each candidate, collect exact provenance that is available: conversation title, conversation ID, turn number, repository path and line, command or test, commit, and date. If a locator is unavailable, say so instead of guessing.
3. Read the existing `machine-inbox/` filenames and search narrowly for an obvious match by source and claim. Skip an obvious duplicate. A previous machine summary is not evidence by itself; retain or cite the original source when it is available.
4. Choose a new filename in `YYYY-MM-DD-short-slug.md` form. If the name exists, use a more specific slug or a numeric suffix; never overwrite the existing file.
5. Write a compact, self-contained note. Separate facts and observations from interpretations, hypotheses, and unresolved questions. Keep claims proportional to the evidence and preserve failed or inconclusive outcomes.
6. Re-read each created file and verify that only new files were added under `machine-inbox/`, with no existing file changed and no more than three files created.
7. Report the created paths, the captured topics, and any skipped duplicate or empty capture. Do not imply that this invocation covered other conversations or that the note is canonical.

## Note shape

Use the existing Garden frontmatter conventions where possible. Omit provenance fields that are unavailable rather than filling them with placeholders.

```markdown
---
title: <concise title>
date: YYYY-MM-DD
type: note
tags:
  - <grounded tag>
status: machine-captured
source: <conversation title, work session, or repository source>
source_id: <conversation ID or other locator when available>
source_turn: <turn locator when available>
---

# <title>

## 要点

<the searchable claim or question>

## 事実・観察

<measurements, outputs, decisions, constraints, or failures supported by the source>

## 推論・未検証

<interpretations and hypotheses, clearly marked>

## 未決事項

<questions or follow-up checks>

## 出典

<exact conversation, file, command, test, commit, or other available locator>
```

The note is a machine-captured candidate. It is not a verified canonical decision, principle, or project specification. Keep the original source locator so a later organizer or human can check it before promotion.
