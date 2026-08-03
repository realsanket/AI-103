# AI-103 Prep Codebase

Runnable code + notes for **Microsoft Certified: Azure AI Engineer — AI-103: Developing AI Apps and Agents on Azure**.

## Layout

```
_shared/                    reusable clients + sample data (all lessons import this)
01-plan-and-manage/         Domain 1 (25-30%)
02-generative-ai-and-agents/Domain 2 (30-35%)
03-computer-vision/         Domain 3 (10-15%)
04-text-and-speech/         Domain 4 (10-15%)
05-information-extraction/  Domain 5 (10-15%)
docs/coverage.md            syllabus bullet → file matrix
```

Study material (unchanged):

- `AI-103.md` — official exam objectives.
- `Slides.md` — full slide notes (extracted from `Slides.pdf`).
- `other-notes-link.md` — external resources.
- `.context/azure-ai-docs/` — cloned official Azure docs, linked from every domain README.

## First-time setup

```bash
cp .env.example .env               # fill in your Foundry / Search / Speech / Language / CU endpoints
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
az login                           # DefaultAzureCredential picks this up
```

Every lesson runs with:

```bash
python 02-generative-ai-and-agents/01_first_api_call.py
```

No API keys live in any Python file. Auth is Entra bearer tokens via `DefaultAzureCredential`.

## Syllabus map

| Domain | Weight | Folder |
|---|---|---|
| Plan and manage an Azure AI solution | 25-30% | [`01-plan-and-manage/`](01-plan-and-manage/README.md) |
| Implement generative AI and agentic solutions | 30-35% | [`02-generative-ai-and-agents/`](02-generative-ai-and-agents/README.md) |
| Implement computer vision solutions | 10-15% | [`03-computer-vision/`](03-computer-vision/README.md) |
| Implement text analysis solutions | 10-15% | [`04-text-and-speech/`](04-text-and-speech/README.md) |
| Implement information extraction solutions | 10-15% | [`05-information-extraction/`](05-information-extraction/README.md) |

Each domain README maps every AI-103 syllabus bullet to a concrete file, links the relevant doc in `.context/azure-ai-docs/`, and shows the expected output.

## Conventions

- Folder names: `NN-kebab-case/`.
- File names: `NN_snake_case.py` — always zero-padded prefix.
- No hardcoded endpoints/keys in Python files. All config through `_shared/config.py` reading `.env`.
- Every lesson file has a runnable `if __name__ == "__main__":` block.
- Every non-trivial lesson prints something you can eyeball — a decision, a citation, a JSON blob, a moderation verdict.
