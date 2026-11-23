---
name: garden-auto-capture
description: Capture low-threshold, source-backed traces from the current conversation, including casual chat, or work context into Terrarium's machine Inbox when a concrete decision, comparison, observation, failure, unresolved question, or user-voiced idea, preference, or unease is worth later rediscovery. Use at a natural boundary such as a topic change or the end of a discussion. This skill may run implicitly; it is not a global conversation event hook.
metadata:
  short-description: Capture searchable traces in the machine Inbox
---

# Capture to the machine Inbox

Use this skill at a natural boundary in the current conversation or work session, in whichever agent is running, when the available context contains a useful trace. It sees only the conversation and work context available in the current invocation. It is not an event hook, background watcher, or guarantee that every conversation will be captured.

When selected implicitly, perform the bounded capture pass without asking the user to predict whether the item will matter later. Keep the capture local and brief so it does not interrupt the main task.

## Capture threshold

Capture a candidate when the current context contains at least one of these:

- a concrete decision and the reason or trade-off behind it;
- a comparison that selected, rejected, or constrained an option;
- a measurement, observed result, reproducible command outcome, or other concrete evidence;
- a failed approach, correction, surprising behavior, or discovered constraint;
- an unresolved question that could guide a later investigation;
- a reusable design hypothesis or cross-project lesson grounded in the current work;
- from casual chat, something the user expressed: an idea, a metaphor or framing, a preference with its context, a sense that something is off, or a question that changed shape.

Use a low threshold. The capture does not need to be canonical or likely to matter in the future. For casual chat, record what the user said and the context that prompted it; do not infer personality or motives, and do not attribute the assistant's own suggestions to the user. Do not capture greetings, generic encouragement, unsupported restatements, or sensitive material. If there is no candidate, do nothing and report an empty capture when appropriate.

## Destination and hard boundaries

- Write only new Markdown files under `~/workspace/terrarium/machine-inbox/`. Resolve and verify the directory before writing; stop if it is missing or ambiguous.
- Never modify, overwrite, delete, move, or rename an existing file, including `machine-inbox/index.md`.
- Do not write to `inbox/`, `machine-notes/`, `decisions/`, `principles/`, `projects/`, or any other Garden directory. Organizing, deduplicating, summarizing existing notes, and canonical promotion belong to another workflow.
- Read existing filenames or note text only for the metadata rules, related-note links, and duplicate and filename collision checks. Do not rewrite the existing note when a duplicate is found.
- Capture at most three new notes per invocation. Combine closely related claims into one note.
- Exclude secrets, credentials, access tokens, private keys, and unnecessary personal or sensitive information. A conversation ID or turn locator may be recorded only when the runtime exposes it and it is useful for finding the source; never invent one.
- If the current user explicitly asks not to save or capture, skip the write.

## Workflow

1. Review only the available current conversation and work context. Extract up to three independent candidates and preserve the wording and scope supported by that context.
2. For each candidate, collect exact provenance that is available: conversation title, conversation ID, turn number, repository path and line, command or test, commit, and date. If a locator is unavailable, say so instead of guessing.
3. Read the `type` and `description` rules in `~/workspace/terrarium/index.md`, then read the existing `machine-inbox/` filenames and search narrowly for an obvious match by source and claim. Skip a candidate that adds nothing. If it develops, corrects, or contradicts an earlier note, capture only what is new and link to that note under `関連`. A previous machine summary is not evidence by itself; retain or cite the original source when it is available.
4. Choose a new filename in `YYYY-MM-DD-short-slug.md` form. If the name exists, use a more specific slug or a numeric suffix; never overwrite the existing file.
5. Write a compact, self-contained note. Separate facts and observations from interpretations, hypotheses, and unresolved questions. Keep claims proportional to the evidence and preserve failed or inconclusive outcomes.
6. Re-read each created file and verify that only new files were added under `machine-inbox/`, with no existing file changed, no more than three files created, every `[[link]]` target existing, and `description` claiming nothing the body does not.
7. Report the created paths, the captured topics, and any skipped duplicate or empty capture. Do not imply that this invocation covered other conversations or that the note is canonical.

## Note shape

Use the existing Garden frontmatter conventions where possible. Omit provenance fields that are unavailable rather than filling them with placeholders.

```markdown
---
title: "<concise title>"
date: YYYY-MM-DD
type: note
description: "<1-2 sentences: the claim or open question, and what is unverified>"
tags:
  - <grounded tag>
status: machine-captured
source: "<agent or app, and conversation title, work session, or repository source>"
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

## 関連

- [[<root-relative path without .md>|<note title>]]：<how it relates>
```

Keep `type: note` even for a captured decision, so unreviewed captures do not appear in searches for confirmed decisions or principles. Link by root-relative path with the title as the label, never by title alone. Omit empty sections.

The note is a machine-captured candidate. It is not a verified canonical decision, principle, or project specification. Keep the original source locator so a later organizer or human can check it before promotion.
