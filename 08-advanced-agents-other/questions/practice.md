# Domain 08 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Advanced agents**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q22

A Microsoft Foundry agent helps engineers troubleshoot production systems.
The solution must meet the following requirements:
• Download diagnostic logs from an internal web application that does not expose APIs.
• Analyze the downloaded log files to identify performance bottlenecks.
Which combination of tools should you recommend?
A. Computer use and Code interpreter
B. File search and Microsoft Fabric
C. Grounding with Bing Search and Code interpreter
D. Computer use and File search

**Study mapping:** [Q22 in the coverage map](../../docs/question-coverage.md).

## Q106

You have a Microsoft Foundry project that contains an agent. The agent uses two tools to perform the
following actions:
• Use Azure AI Search to retrieve answers from a private product documentation index.
• Use the web search tool to retrieve public information on the internet.
You need to ensure that for a specific run, the agent deterministically retrieves information only from the
internet.
To what should you set tool_choice?
A. “type”: “bing_grouding”
B. “type”: “azure_ai-search”
C. “auto”
D. “required”

**Study mapping:** [Q106 in the coverage map](../../docs/question-coverage.md).

## Q149

You have a Microsoft Foundry project that contains an agent. The agent has a Model Context Protocol
(MCP) tool named kbsearch that queries a knowledge base stored in Azure AI Search.
Some agent runs return answers from the base model without invoking the knowledge base, which results in
responses without grounded citations.
You are provided with the following code snippet that runs the agent.
You need to deterministically force the agent to invoke kbsearch on each run. What should you do?
A. Add the response_format parameter to the create_and_process() method call.
B. Replace create_and_process() method with the create_thread_and_process_run() method.
C. Add the toolset parameter to the create_and_process() method call.
D. Add the tool_choice parameter to the create_and_process() method call.

**Study mapping:** [Q149 in the coverage map](../../docs/question-coverage.md).

