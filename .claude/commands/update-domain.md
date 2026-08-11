---
description: Restructure a domain README and Python lessons to match AI-103 style — beginner-to-advanced stages, per-lesson references from local foundry docs, code details from docstrings.
---

You are restructuring domain $ARGUMENTS (e.g. `01-plan-and-manage`, `02-generative-ai-and-agents`) to match the AI-103 doc and code style established in domains 01 and 02.

Work in this order. Do not skip phases.

---

## Phase 1 — Audit

Read every Python file in the domain folder:
- Collect the docstring (module-level `"""..."""` and key inline comments)
- Note the `# Run:` line at the top
- Note which env vars / flags the file uses
- Note what Azure API / endpoint the file calls
- Flag any file whose name or position in the sequence is pedagogically wrong

Read the current README. List:
- Which lessons have good walkthroughs vs stubs
- Which sections are duplicated
- What is missing compared to domain 01 style

Read the local foundry docs at `.context/azure-ai-docs/articles/foundry/` to find reference docs for each lesson topic. URL pattern: local path `foundry/<sub>/<name>.md` → `https://learn.microsoft.com/azure/foundry/<sub>/<name>`

---

## Phase 2 — Reorder (if needed)

Pedagogically sound lesson order for any domain:
1. Core concept lessons first (local, no cloud calls)
2. Progressively more advanced / cloud-connected lessons
3. Group related lessons together (e.g. all evaluation lessons adjacent, all observability adjacent)
4. Hard dependencies: a lesson that requires understanding lesson N must come after N

If reorder is needed:
- Use `git mv` to rename files
- If source and target numbers clash (e.g. moving 20→19 when 19→21), use a temp name first: `git mv 19_foo.py _temp_foo.py` then cascade
- Update `# Run:` comments in ALL Python files after renaming: `sed -i '' 's/old_name.py/new_name.py/g' *.py`
- Confirm no orphaned old names remain

---

## Phase 3 — Python file quality

For each Python file, ensure the module docstring follows this template:

```python
# Run: uv run python <domain-folder>/<filename>.py
"""<One-line summary of what this lesson demonstrates.>

<2-4 sentence background: what problem this solves, why it exists, what it is NOT.>

<When applicable: mention the prerequisite lesson or concept this builds on.>

<Flows / code paths: label each flow (Flow A, Flow B) with what it does and why.>

<What to watch in the output: what key things the learner should look for.>

Prerequisites / env vars:
  VAR_NAME  — what it controls
  FLAG_NAME — what --flag does
"""
```

Rules:
- Beginner-friendly: explain WHY before HOW
- Distinguish what the code proves vs what it does NOT prove
- No wall of text; use short paragraphs or bullet lists
- If the file is a preflight/guide (no cloud calls by default), say so explicitly
- If the file requires `--apply` or `--run` for cloud writes, say so

---

## Phase 4 — README structure

The README must follow this exact structure:

```
# Domain N: <Title>

> <tagline: what the domain covers, how to run>
> <scope warning: evidence is narrow>

## What this domain teaches
[lifecycle flow diagram showing progression]
[1-paragraph context]

## <Domain-specific mental model>
[tables, endpoint maps, planes diagram — varies by domain]

## Glossary
[table of key terms]

## Setup
### Environment variables
[.env block + DefaultAzureCredential note]

### Safe run order
[numbered list: what to run first, what gates what]

### Costs and side effects
[table: lesson → what it writes/costs]

## Decision tables
[domain-specific decision flows and comparison tables]

## Lesson map
[full table: # | Lesson | Runnable objective | Status/limitation]

---

## Stage 1 — <Topic> (lessons NN–NN)
[1-para intro explaining what this stage teaches and why these lessons are grouped]

### NN — <Lesson title>
**Question answered:** <single question this lesson answers>

**Background.** <Why this capability exists. What problem it solves. What it is NOT.>

[if relevant: **Before code.** <prerequisites>]

```bash
uv run python <domain>/<file>.py [flags]
```

**Code path.**
1. <key statement → what it does in Azure>
2. <key statement → what it does in Azure>
...

**What to watch in the output.** <what the learner should look for>

**<Topic-specific section>** (study points / exam cues / what this proves / what it does not)

**References:** [Title](url) · [Title](url)

[repeat for each lesson in stage]

---

## Stage 2 — <Topic> (lessons NN–NN)
...

[Continue for all stages]

---

## Feature status and hard limits
[table: feature | status | practical boundary]

## Troubleshooting
[table: symptom | likely cause | resolution]

## CI/CD and operational release
[pipeline flow + what to version + release gates table]

## Security, networking, and IaC
[table: decision | recommendation | common pitfall]

## Common exam traps
[table: claim | correct interpretation]

## Objective coverage and limits
[paragraph: what is covered, what is NOT]

## References
[grouped by topic, all links from local foundry docs]
```

---

## Phase 5 — Per-lesson reference links

For each lesson section, add `**References:**` at the end with links sourced from local docs.

Find relevant docs:
```bash
find .context/azure-ai-docs/articles/foundry -name "*.md" | grep -i "<topic keyword>"
```

URL construction: strip `.md`, replace `.context/azure-ai-docs/articles/foundry/` with `https://learn.microsoft.com/azure/foundry/`

Example: `.context/azure-ai-docs/articles/foundry/observability/how-to/trace-agent-setup.md`
→ `https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-setup`

Format: `**References:** [Title one](url) · [Title two](url)`

It is fine for the same doc to appear in multiple lessons.

---

## Phase 6 — Global References section

At the bottom of the README, reorganize all references into topic groups:

```markdown
## References

### <Topic group 1>
- [Title](url)

### <Topic group 2>
- [Title](url)
```

Groups should match the stage structure of the README. Include all links referenced per-lesson plus any additional foundry docs relevant to the domain.

---

## Quality checklist before finishing

- [ ] Every Python file has a `# Run:` comment at line 1
- [ ] Every Python file has a module docstring with Background + Code path + What to watch
- [ ] No lesson appears twice in the README
- [ ] No section is a stub (less than 3 bullet points or 2 sentences of substance)
- [ ] Every lesson section has `**References:**`
- [ ] Lesson numbers in README match actual filenames
- [ ] `# Run:` paths in Python files match actual filenames
- [ ] All referenced local doc files actually exist: `ls .context/azure-ai-docs/articles/foundry/<path>.md`
- [ ] README stages are in beginner-to-advanced order (local/concept lessons before cloud/advanced)
- [ ] Syntax check all Python files: `python3 -m py_compile <domain>/*.py`
- [ ] Verify all README run commands point to existing files

---

## Style rules

**Tone:** Direct. No "In this lesson you will learn..." — instead "Lesson 07 proves keyless project access."

**Technical precision:**
- Always name the specific Azure API called (e.g. `client.deployments.list()`, not "lists deployments")
- Always name the specific result field checked (e.g. `protectedMaterialAnalysis.detected`, not "checks if protected")
- Always distinguish what code proves vs what it does NOT prove

**What NOT to add:**
- Don't add features the lesson doesn't implement
- Don't add error handling for impossible cases
- Don't add abstractions not in the code

**Reference docs to always check for new domains:**
```
.context/azure-ai-docs/articles/foundry/concepts/
.context/azure-ai-docs/articles/foundry/observability/
.context/azure-ai-docs/articles/foundry/guardrails/
.context/azure-ai-docs/articles/foundry/openai/concepts/
.context/azure-ai-docs/articles/foundry/foundry-models/
.context/azure-ai-docs/articles/foundry/how-to/
```
