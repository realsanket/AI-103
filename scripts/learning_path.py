# Run: uv run python scripts/learning_path.py [--check]
"""Build docs/learning-path.md: every numbered lesson once, in Foundry learning order.

Lesson folders follow the AI-103 exam domains, which is not a teaching order.
PARTS below is the teaching order: parts hold modules, and each module lists
lessons as "D<domain> <number>". Titles and anchors come from the domain README
headings, so a retitled lesson only needs a rerun.

After adding a numbered lesson, put it in the module where a learner first
needs it, then run this script. --check writes nothing and exits 1 when
docs/learning-path.md is out of date; tests/test_repo_docs.py runs that check.
"""
import argparse
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "learning-path.md"
HEADING = re.compile(r"^#{1,6}\s+(.*?)(?:\s+#+)?\s*$")
LESSON_HEADING = re.compile(r"^(?:L|Lesson\s+)?(\d{2}[a-z]?)\b")
TITLE_PREFIX = re.compile(r"^(?:L|Lesson\s+)?\d{2}[a-z]?\s*[—–:-]\s*")

# (part, [(module, intro, needs, [lesson or (lesson, note)])])
PARTS = [
    ("Part 1 — Foundations", [
        ("How Foundry is organized",
         "A Foundry resource (Azure kind `AIServices`) holds projects, model deployments, and connections. "
         "Apps call a deployment by name. Start by choosing what to build on, deploying one model, and "
         "proving keyless access with least privilege.",
         "`az login`; a Foundry resource and project; `FOUNDRY_ENDPOINT`, `PROJECT_ENDPOINT`, "
         "`AZURE_OPENAI_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`.",
         ["D1 36", "D1 02", "D6 14", "D1 03", "D1 01", "D1 07", "D1 08", "D1 05"]),
        ("Call a model with the Responses API",
         "One API covers text, multi-turn state, structured output, reasoning, caching, and embeddings. "
         "Learn the request shape and the settings that change behavior before adding tools.",
         "`AZURE_OPENAI_ENDPOINT` and a chat deployment in `DEFAULT_MODEL`; `REASONING_MODEL` and "
         "`EMBEDDING_MODEL` deployments for the later steps.",
         ["D2 01", "D2 02", "D1 16", "D2 07", "D2 32", "D2 38", "D2 03", "D2 36", "D2 33", "D2 31", "D1 06"]),
        ("Choose among models",
         "Route requests between models, then look beyond OpenAI models: partner models such as Claude "
         "and DeepSeek have their own APIs, and catalog and industry models have their own deployment rules.",
         "`PROJECT_ENDPOINT` and a `model-router` deployment (`MODEL_ROUTER_DEPLOYMENT`). Partner and "
         "industry model steps are optional (`CLAUDE_DEPLOYMENT`, `DEEPSEEK_MODEL`, `HEALTHCARE_AI_ENDPOINT`).",
         ["D1 04", "D1 04b", ("D6 16", "same idea as D1 04"), "D6 15", "D6 17", "D6 18", "D6 19", "D9 07"]),
        ("Guardrails and content safety",
         "Every deployment already has a guardrail. Learn what it blocks, when to call the Content Safety "
         "APIs yourself, and how prompt attacks arrive through users and documents, before you build apps "
         "that act.",
         "The Responses setup from Module 2, `CONTENT_SAFETY_ENDPOINT`, and Blob read access for "
         "provenance detection.",
         ["D1 09", "D1 10", "D1 11", "D1 12", "D1 13", "D1 15", "D1 18", "D1 19", "D1 20"]),
    ]),
    ("Part 2 — Build apps and agents", [
        ("Give models tools",
         "A tool call is a proposal from the model; your code decides whether to run it. Start with the "
         "raw function-calling loop, then the built-in tools the service runs for you.",
         "The Responses setup from Module 2, plus `PROJECT_ENDPOINT` for file search.",
         ["D2 35", "D2 51", "D2 04", ("D2 37", "same tool as D2 04, on the Azure OpenAI endpoint"),
          "D2 05", "D2 06", "D2 39"]),
        ("Build agents with Foundry Agent Service",
         "A prompt agent is a versioned definition (instructions, model, tools) stored in the project. "
         "Create and invoke one, add tools, keep conversation state and memory, then check an agent's tool "
         "plans with Task Adherence and guardrail intervention points.",
         "`PROJECT_ENDPOINT` with the Foundry User role; `ORDERS_FN_ENDPOINT` for the OpenAPI step; "
         "`CONTENT_SAFETY_ENDPOINT` for Task Adherence; subscription and resource group for the guardrail step.",
         ["D2 08", "D2 09", "D2 10", "D2 11", "D2 12", "D2 13", "D2 14", "D8 11", "D1 14", "D1 28"]),
        ("MCP, Toolbox, and governed tool catalogs",
         "MCP connects agents to external tool servers; a Toolbox publishes a reviewed, versioned set of "
         "tools that many agents share. Treat every server as a trust boundary: approval, least privilege, "
         "and allow-lists.",
         "`PROJECT_ENDPOINT`, an MCP server you trust (`MCP_SERVER_URL`), and project connections.",
         ["D8 09", "D2 25", "D8 10", "D2 47", "D8 15", "D2 26", "D8 02", "D8 20", "D8 21", "D8 18", "D8 19"]),
    ]),
    ("Part 3 — Ground agents in your data", [
        ("Azure AI Search and manual RAG",
         "Build the retrieval corpus yourself: index, skillset, and indexer; compare keyword, vector, and "
         "hybrid search; then let your app own retrieval and pass the sources to an agent.",
         "`SEARCH_ENDPOINT`, a Storage account and container with the sample PDFs, `EMBEDDING_MODEL`, and "
         "the Search managed-identity roles in the Domain 5 README.",
         ["D5 19", "D5 00", "D5 05", "D5 04", "D5 01", "D5 02", "D5 03", "D5 18", "D5 07", "D5 08"]),
        ("Extract content from documents",
         "Content Understanding turns documents into Markdown and fields with confidence and source "
         "grounding; Document Intelligence gives deterministic OCR, layout, and prebuilt models. Learn "
         "both, then choose.",
         "`CU_ENDPOINT` (with its default model deployments), `DOCUMENT_INTELLIGENCE_ENDPOINT`, and "
         "runtime-only document URLs.",
         ["D5 09", "D5 10", "D5 11", "D5 12", "D5 13", "D5 14", "D5 15", "D5 16",
          "D9 01", "D9 02", "D9 03", "D9 04", "D9 06", "D9 05"]),
        ("Enrich what you index",
         "Skills add structure while indexing: custom Web API skills, OCR for images, the Content "
         "Understanding skill for layout and page citations, and permission metadata from SharePoint.",
         "The Search pipeline from Module 8; `FOUNDRY_ENDPOINT` for skill billing; `STORAGE_ACCOUNT`, "
         "`AZURE_SUBSCRIPTION_ID`, and `AZURE_RESOURCE_GROUP` for identity-based storage connections.",
         ["D5 06", "D5 17", "D5 29", "D5 30", "D5 28"]),
        ("Search in agents and agentic retrieval",
         "Let agents query Search directly, then move to knowledge bases: several knowledge sources, "
         "model-planned queries, and cited answers. This is the retrieval layer behind Foundry IQ.",
         "The index from Module 8; `PROJECT_ENDPOINT` for the agent steps; preview Search REST API access.",
         ["D5 20", "D2 27", "D5 21", "D5 22", "D5 23", "D5 24", "D5 25", "D5 26", "D5 27",
          "D8 01", ("D8 16", "checks the connection from D8 01")]),
        ("More agent tools",
         "Web grounding, enterprise data, reminders, and browser or computer use. Most are preview. Each "
         "one widens what an agent can reach, so review identity, data boundaries, and approval before "
         "enabling it.",
         "The matching project connection for each tool; check each lesson's region and preview notes.",
         ["D8 22", "D8 23", "D8 26", "D8 24", "D8 14", "D8 25"]),
    ]),
    ("Part 4 — Beyond text", [
        ("Vision",
         "Multimodal input, image and video generation, visual safety, and Content Understanding for "
         "images and video.",
         "`IMAGE_MODEL` and `VIDEO_MODEL` deployments, `CONTENT_SAFETY_ENDPOINT`, `CU_ENDPOINT`, and "
         "runtime-only Blob SAS URLs for media.",
         ["D3 01", "D3 02", "D3 03", "D3 16", "D3 04", "D3 05", "D3 06", "D8 27", "D3 07", "D3 08", "D3 09",
          "D3 10", "D3 11", "D3 12", "D3 13", "D3 14", "D3 17", "D3 15"]),
        ("Language",
         "Compare prompt-based extraction with Azure Language's deterministic APIs, then translation, then "
         "the Language MCP server for agents.",
         "The Module 2 setup for the prompt-based steps; `LANGUAGE_ENDPOINT`; Translator with "
         "`TRANSLATOR_RESOURCE_ID`; `PROJECT_ENDPOINT` for the MCP agent.",
         ["D4 01", "D4 02", "D4 03", "D4 06", "D4 07", "D4 05", "D4 20", "D4 10",
          "D4 04", "D4 22", "D4 23", "D4 08", "D4 09"]),
        ("Speech and real-time voice",
         "Speech to text and text to speech first, then speech translation, audio models, and real-time "
         "voice sessions for agents.",
         "`SPEECH_ENDPOINT` and `SPEECH_REGION`, audio samples, and real-time model deployments for the "
         "later steps.",
         ["D4 11", "D4 12", "D4 13", "D4 17", "D4 19", "D4 14", "D4 15", "D4 16", "D4 21",
          "D4 27", "D4 26", "D4 18", "D4 24", "D4 28", "D4 29", "D4 30", "D4 25"]),
    ]),
    ("Part 5 — Orchestrate agents", [
        ("Frameworks and multi-agent systems",
         "Run agents in your own process with Microsoft Agent Framework, LangChain, or LangGraph; "
         "coordinate several agents; describe workflows in YAML with checkpoints and human approval.",
         "`PROJECT_ENDPOINT` or `AZURE_OPENAI_ENDPOINT`; a .NET 8+ runtime for declarative workflows.",
         ["D2 17", "D2 18", "D2 19", "D2 34", "D2 20", "D2 43", "D2 44", "D2 50", "D2 45",
          ("D2 15", "optional: Foundry workflows retire on 1 December 2026"),
          ("D2 16", "optional: Foundry workflows retire on 1 December 2026")]),
    ]),
    ("Part 6 — Measure and harden", [
        ("Tracing and observability",
         "See what happened: server-side tracing in the project, client-side spans in your code, framework "
         "tracing, and telemetry queries.",
         "Application Insights connected to the project (`APPLICATIONINSIGHTS_CONNECTION_STRING`) and "
         "Log Analytics Reader.",
         ["D1 25", "D1 26", "D2 23", "D2 24", "D1 29", "D8 28"]),
        ("Evaluation",
         "Measure quality with evaluators: locally first, then cloud runs against models and agents, "
         "continuous evaluation in production, and a CI/CD gate that blocks a bad change.",
         "A judge model deployment; agents from earlier modules as targets; `AZURE_AI_PROJECT_ENDPOINT` "
         "for cloud runs.",
         ["D1 17", "D2 21", "D1 35", "D2 22", "D1 21", "D1 32", "D1 33", "D1 34", "D1 22", "D1 23", "D1 30"]),
        ("Red teaming",
         "Attack your own system on purpose: a safe synthetic target first, then a bounded probe of a real "
         "deployment.",
         "A nonproduction project and an approved test plan.",
         ["D1 24", "D1 31"]),
    ]),
    ("Part 7 — Ship agents", [
        ("Hosted agents",
         "Package your own agent code as a container that Foundry hosts, configures, isolates per session, "
         "guards with a policy, improves with the optimizer, and ships through CI/CD.",
         "`azd`, a container registry, `HOSTED_AGENT_NAME`, `HOSTED_AGENT_IMAGE`, and an RAI policy ID.",
         ["D2 28", "D8 07", "D8 08", "D2 49", "D2 48", "D2 30", ("D8 06", "runs the optimizer locally"),
          ("D8 17", "submits a cloud optimization job")]),
        ("Agent-to-agent, publishing, and Microsoft 365",
         "Connect agents across systems with A2A, register agents that run elsewhere, publish a stable "
         "endpoint, schedule runs, and reach Microsoft 365 data and users.",
         "A2A targets and connections; Microsoft 365 tenant consent for the Work IQ and Agent 365 steps.",
         ["D2 29", "D2 40", "D2 41", ("D8 03", "overlaps D2 41"), "D2 42", "D8 05", "D8 04",
          ("D8 12", "overlaps D8 04"), "D8 13", "D2 46"]),
    ]),
    ("Part 8 — Run in production", [
        ("Platform infrastructure and governance",
         "Everything so far used a lab resource. Production uses infrastructure as code: private "
         "networking, customer-managed keys, policy, connections, diagnostics, CI/CD, and disaster recovery.",
         "Permission to deploy to a nonproduction subscription; Bicep or Terraform.",
         ["D1 27", "D7 01", "D7 02", "D7 03", "D7 11", "D7 07", "D7 08", "D7 05", "D7 04", "D7 06", "D7 09"]),
        ("Capacity and cost",
         "Choose how you pay for throughput (Standard, Priority, provisioned with spillover, Batch, "
         "routing), then estimate cost.",
         "Management-plane read access; deployments for the priority and batch steps.",
         ["D6 10", "D7 10", "D6 11", "D6 12", "D6 09", "D6 13"]),
    ]),
    ("Part 9 — Customize models", [
        ("Fine-tuning lifecycle",
         "Fine-tune only after prompting, RAG, and evaluation fall short: prepare SFT, DPO, or RFT data, "
         "train, monitor, deploy a checkpoint, and compare it with the baseline.",
         "A region and model that support fine-tuning, reviewed training data, and a quota plan.",
         ["D6 00", "D6 01", "D6 02", "D6 03", "D6 04", "D6 05", "D6 06", "D6 07", "D6 08"]),
    ]),
]

HEADER = """# Learning path: Microsoft Foundry from first call to production

<!-- Generated by scripts/learning_path.py. Change the order there, then run it. -->

The numbered folders follow the AI-103 exam domains, so reading them 01 → 09
jumps between levels: evaluation lessons come before the agents they evaluate,
and core API skills sit after hosted agents. This path puts all {total}
lessons in learning order instead, and each module builds on the ones before
it. Folder and file numbers don't change; only the reading order does.

How to use it:

- Work top to bottom. Read the lesson's README section, then run its code.
- Check that section before each run. Some lessons call Azure as soon as they
  start; others run a local preflight until you add `--apply` or `--run`. The
  section lists the roles, cost, and cleanup.
- **Needs** lists what a module adds; set those values in `.env` first.
- Studying for AI-103 as well? The same path covers every exam domain. To
  practice, look up a lesson in [the question map](question-coverage.md).

## At a glance

| Part | Modules | Steps |
|---|---|---:|
{glance}
"""


def slug(text: str) -> str:
    """GitHub heading anchor: lowercase, punctuation removed, spaces to hyphens."""
    text = text.strip().lower().replace("`", "")
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def heading_anchors(markdown: str) -> list[tuple[str, str]]:
    """(heading text, anchor) for each heading outside code fences; repeats get -1, -2, ..."""
    seen: Counter[str] = Counter()
    headings = []
    in_fence = False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        match = None if in_fence else HEADING.match(line)
        if match:
            base = slug(match.group(1))
            headings.append((match.group(1), f"{base}-{seen[base]}" if seen[base] else base))
            seen[base] += 1
    return headings


def lessons() -> dict[str, tuple[str, str, str, str]]:
    """'D2 32' -> (domain folder, file name, README title, README anchor) for every numbered lesson."""
    found = {}
    for folder in sorted(ROOT.glob("0[1-9]-*")):
        headings = heading_anchors((folder / "README.md").read_text(encoding="utf-8"))
        for path in sorted(folder.glob("[0-9]*_*.py")):
            number = path.name.split("_")[0]
            section = next(
                ((text, anchor) for text, anchor in headings
                 if (match := LESSON_HEADING.match(text)) and match.group(1) == number),
                None,
            )
            if section is None:
                raise ValueError(f"{folder.name}/README.md has no section heading for lesson {number}")
            found[f"D{folder.name[1]} {number}"] = (folder.name, path.name, TITLE_PREFIX.sub("", section[0]), section[1])
    return found


def render() -> str:
    catalog = lessons()
    placed: Counter[str] = Counter()
    body: list[str] = []
    glance: list[str] = []
    step = module = 0
    for part, modules in PARTS:
        body.append(f"## {part}\n")
        first_step = step + 1
        names = []
        for name, intro, needs, entries in modules:
            module += 1
            names.append(f"{module}. {name}")
            body += [f"### Module {module} — {name}\n", f"{intro}\n", f"**Needs:** {needs}\n",
                     "| Step | Lesson | Read | Code |", "|---:|---|---|---|"]
            for entry in entries:
                code, note = (entry, "") if isinstance(entry, str) else entry
                if code not in catalog:
                    raise ValueError(f"{code} is in PARTS but has no numbered lesson file")
                folder, file_name, title, anchor = catalog[code]
                step += 1
                placed[code] += 1
                suffix = f" _({note})_" if note else ""
                body.append(
                    f"| {step} | {code} | [{title}](../{folder}/README.md#{anchor}){suffix} "
                    f"| [`{file_name}`](../{folder}/{file_name}) |"
                )
            body.append("")
        glance.append(f"| [{part}](#{slug(part)}) | {'; '.join(names)} | {first_step}–{step} |")
    repeated = sorted(code for code, count in placed.items() if count > 1)
    missing = sorted(set(catalog) - set(placed))
    if repeated or missing:
        raise ValueError(f"Place every lesson exactly once. Repeated: {repeated}; missing: {missing}")
    text = HEADER.format(total=len(catalog), glance="\n".join(glance)) + "\n" + "\n".join(body)
    return text.rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build docs/learning-path.md from the module order in this file.")
    parser.add_argument("--check", action="store_true", help="Write nothing; exit 1 if the file is out of date.")
    args = parser.parse_args(argv)
    text = render()
    target = OUTPUT.relative_to(ROOT)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != text:
            print(f"{target} is out of date. Run: uv run python scripts/learning_path.py")
            return 1
        print(f"{target} is up to date.")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    modules = [entries for _, part_modules in PARTS for *_, entries in part_modules]
    print(f"Wrote {target}: {sum(map(len, modules))} steps in {len(modules)} modules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
