# Domain 02 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Generative AI and agents**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q6

You have a Microsoft Foundry project that contains an agent used by the financial analysts at your
company. You need to optimize the agent workflow by providing additional data access and processing
capabilities. The solution must meet the following requirements:
• Ensure that the agent can perform calculations during conversations.
• Ensure that the agent can access up-to-date information from public websites.
• Ensure that the agent can retrieve information from documents uploaded directly to the agent.
What should you use for each requirement? To answer, drag the appropriate tools to the correct
requirements. Each tool may be used once, more than once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q6 in the coverage map](../../docs/question-coverage.md).

## Q7

You have a Microsoft Foundry project named Project1 that contains an agent. The agent uses an
OpenAPI 3.0 specification to call an external weather service.
The weather service requires a key to be passed in an HTTP header. The key value is stored as a connection
in Project1.
You need to ensure that the key value from the connection is included automatically whenever the OpenAPI
tool is invoked.
What should you configure in the OpenAPI specification?
A. a header parameter defined for each operation
B. an Azure Key Vault connection
C. an API key security scheme
D. a Bearer token security scheme

**Study mapping:** [Q7 in the coverage map](../../docs/question-coverage.md).

## Q8

You have a Microsoft Foundry project that contains three agents as shown in the following table.
You need to orchestrate the agents to ensure that the customer requests meet the following requirements:
• Support a deterministic, step-based process that uses conditional branching and shared state across
the agents.
• Optionally trigger a ticket action based on the triage result.
• The solution must minimize development effort.
What should you include in the solution?
A. a workflow
B. threads and runs without a workflow
C. a multi-agent group chat session
D. separate agent runs coordinated in the application code

**Study mapping:** [Q8 in the coverage map](../../docs/question-coverage.md).

## Q12

You are developing a travel planning agent by using Microsoft Foundry Agent Service.
The solution must meet the following requirements:
• Remember each user's preferred airline and hotel chain across future conversations.
• Ensure that payment card details are discarded after the conversation ends.
• Minimize custom development.
Which implementation should you recommend?
A. Store both preferences and payment information in persistent agent memory.
B. Store preferences in persistent agent memory and retain payment information only in orchestration-
managed session context.
C. Store both preferences and payment information in conversation history.
D. Store payment information in Azure AI Search and preferences in session context.

**Study mapping:** [Q12 in the coverage map](../../docs/question-coverage.md).

## Q13

You have a Microsoft Foundry project that contains an agent. The agent uses tools to retrieve internal
content and call external APIs. The agent is configured to let the model decide when to call the tools.
You need to publish the agent for a compliance workflow.
The solution must meet the following requirements:
• Each workflow run must include a retrieval step before generating a response.
• Tool calls must authenticate by using the published agent’s own identity.
• Tool access must use an identity isolated from other project resources.
• Tool access must use support audit tracing.
What should you do?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q13 in the coverage map](../../docs/question-coverage.md).

## Q16

You have a Microsoft Foundry project that contains a deployed ticket-triage agent.
You discover that sometimes the agent responds without calling any tools, even when a tool is required. You
need to ensure that the agent calls a tool during execution.
How should you complete the Python code?
To answer, drag the appropriate values to the correct targets. Each value may be used once, more than once,
or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q16 in the coverage map](../../docs/question-coverage.md).

## Q18

You are planning a Microsoft Foundry project named Project1 that will contain several prompt flow
applications and agents.
Each application must use the same Azure AI Foundry Model deployment hosted in another Azure resource.
You need to recommend a solution that enables all applications in Project1 to reuse the model configuration
without duplicating connection settings.
What should you recommend?
A. Create a connection to the model resource.
B. Configure a managed private endpoint.
C. Enable role-based access control (RBAC) on the model deployment.
D. Configure diagnostic settings for the model deployment.

**Study mapping:** [Q18 in the coverage map](../../docs/question-coverage.md).

## Q25

You have a Microsoft Foundry project that contains a customer support agent.
The agent uses multiple tools during execution. Users report that responses are delayed because the agent
waits for several independent tool calls to complete.
You need to reduce the overall response time. The solution must be implemented in the application logic.
What should you do?
A. Execute independent tool calls in parallel before generating the response.
B. Increase the maximum completion tokens.
C. Replace the language model with a larger deployment.
D. Enable persistent agent memory.

**Study mapping:** [Q25 in the coverage map](../../docs/question-coverage.md).

## Q29

You need to recommend a plan to create a customer support agent by using the Microsoft Foundry
Agent Service.
The agent must meet the following requirements:
• Retain user preferences across multiple conversations.
• Enable users to provide contextual grounding by directly uploading documents during a chat.
Which Foundry capability should you recommend for each requirement?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q29 in the coverage map](../../docs/question-coverage.md).

## Q33

You have a Microsoft Foundry project that contains an agent named PaymentAgent.
PaymentAgent includes a function tool that issues customer refunds by using an external API.
You are creating a workflow in YAML.
You need to ensure that the workflow pauses for human approval and continues with the refund step only
after approval is granted.
How should you complete the workflow definition?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q33 in the coverage map](../../docs/question-coverage.md).

## Q43

You have a Microsoft Foundry project that contains a workflow for a customer support triage process.
You have an Ask a question node that stores user responses in a local variable named Var01.
You need to create the following Power Fx expressions:
• An if/else condition expression that ensures that Var01 contains a value
• A Send message expression that returns the stored user response in uppercase
How should you configure the expressions?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q43 in the coverage map](../../docs/question-coverage.md).

## Q44

You have a customer support agent that uses the Microsoft Foundry Agent Service.
Sometimes, customers return to a session days later to continue the same support case, and the agent must
resume with the full historical context.
The agent must provide the following:
• Multi-turn continuity within the session Cross-session continuity for the same case
• Access to the full interaction history, including user messages, agent messages, tool calls, and tool
outputs
You need to ensure that the agent automatically reloads the complete history on each new turn.
What should you do?
A. Create and reuse a conversation by storing the conversation’s ID and supplying the ID on subsequent
requests.
B. Persist only the final model response stored in the client application and prepend the response to future
prompts.
C. Enable memory summarization on the agent definition to persist the context automatically.

**Study mapping:** [Q44 in the coverage map](../../docs/question-coverage.md).

## Q45

You have a Microsoft Foundry Agent Service project that contains an HR onboarding agent.
Employees frequently pause conversations and continue them several days later.
The solution must meet the following requirements:
• Resume the conversation exactly where it ended.
• Ensure the agent can reference previous tool invocations and uploaded documents.
• Avoid manually reconstructing conversation history.
What should you do?
A. Create a new thread for each user request and copy previous responses into the prompt.
B. Persist the thread ID and continue subsequent requests by using the existing thread.
C. Store conversation summaries in persistent memory and start a new thread for every session.
D. Save only the final assistant response and include it as context in future requests.

**Study mapping:** [Q45 in the coverage map](../../docs/question-coverage.md).

## Q52

A legal research agent must satisfy the following requirements:
• Search contracts uploaded by users during an active conversation.
• Search millions of historical court decisions stored in a centralized enterprise index.
Which combination should you recommend?
A. File Search for both requirements
B. Azure AI Search for both requirements
C. File Search for uploaded contracts and Azure AI Search for historical court decisions
D. Microsoft Fabric for uploaded contracts and File Search for historical court decisions

**Study mapping:** [Q52 in the coverage map](../../docs/question-coverage.md).

## Q62

You have a technical support agent that uses the Microsoft Foundry Agent Service.
Customers often upload log files while troubleshooting issues. A support case can remain open for several
weeks, and different support engineers may continue the conversation during that time.
The solution must meet the following requirements:
• Maintain the complete conversation history across multiple sessions.
• Preserve uploaded files, tool calls, tool outputs, and agent responses.
• Minimize application code.
What should you do?
A. Store the thread ID after the initial conversation and provide the same thread ID when continuing the
support case.
B. Store the generated responses in Azure AI Search and prepend them to every new prompt.
C. Enable persistent agent memory and allow the agent to reconstruct previous conversations automatically.
D. Store conversation summaries in a database and include the summaries in each new request.

**Study mapping:** [Q62 in the coverage map](../../docs/question-coverage.md).

## Q67

You have a Microsoft Foundry project named Project1 that contains the following: An OpenAPI tool that
calls an external API
A project connection named Connection1 that stores the API key of the external API
When an agent calls the OpenAPI tool, the API returns a 401 unauthorized error, and traces show that the API
key header is NOT being sent.
You need to ensure that the OpenAPI tool automatically includes the API key from Connection1 on all
requests.
What should you do?
A. Enable identity passthrough so that the tool uses the Microsoft Entra token of the caller.
B. Add the API key header manually to the OpenAPI specification.
C. Configure the tool to use the default connection of Project1.
D. Connect the tool to Connection1.

**Study mapping:** [Q67 in the coverage map](../../docs/question-coverage.md).

## Q73

You need to recommend a solution for a legal research agent by using the Microsoft Foundry Agent
Service.
The solution must meet the following requirements:
• Retain attorney preferences across multiple conversations.
• Enable the agent to retrieve reference material from documents uploaded during a conversation.
Which Foundry capability should you recommend for each requirement?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q73 in the coverage map](../../docs/question-coverage.md).

## Q76

You have a Microsoft Foundry project that contains an agent used by an insurance company.
You need to enhance the agent by using built-in tools. The solution must meet the following requirements:
• Allow the agent to analyze claim spreadsheets uploaded during conversations and generate charts.
• Allow the agent to interact with a legacy claims management website that does not expose APIs.
• Allow the agent to answer questions by using policy documents uploaded directly to the current
conversation.
What should you use for each requirement?
To answer, drag the appropriate tools to the correct requirements. Each tool may be used once, more than
once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q76 in the coverage map](../../docs/question-coverage.md).

## Q79

You need to recommend a solution for a customer service agent by using the Microsoft Foundry Agent
Service.
The agent must meet the following requirements:
• Execute Python code to analyze spreadsheets uploaded by users during conversations.
• Access current weather conditions from public websites without requiring users to upload
documents.
Which Foundry capability should you recommend for each requirement?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q79 in the coverage map](../../docs/question-coverage.md).

## Q82

A financial reporting application generates JSON that is consumed by downstream automation.
Occasionally, responses contain unexpected fields that cause processing failures.
Which approach should you recommend?
A. Lower the model temperature.
B. Use structured outputs with a JSON schema.
C. Increase the maximum completion tokens.
D. Fine-tune the model.

**Study mapping:** [Q82 in the coverage map](../../docs/question-coverage.md).

## Q83

You need to recommend a solution for a procurement agent by using the Microsoft Foundry Agent
Service.
The solution must meet the following requirements:
• Answer questions by using supplier contracts uploaded by users during conversations.
• Generate charts that summarize purchasing trends from uploaded Excel workbooks.
Which Foundry capability should you recommend for each requirement?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q83 in the coverage map](../../docs/question-coverage.md).

## Q86

You have a Microsoft Foundry project that contains a legal research agent.
The solution must meet the following requirements:
• Research recently published court decisions available on public websites.
• Search contracts that attorneys upload during a conversation.
• Log in to a third-party compliance portal and download supporting evidence for the current case.
What should you use for each requirement?
To answer, drag the appropriate tools to the correct requirements. Each tool may be used once, more than
once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q86 in the coverage map](../../docs/question-coverage.md).

## Q93

You have a Microsoft Foundry project that contains a deployed chat model.
You have a Python service that sends API requests to the model. The service is integrated with an automated
validation system that compares generated outputs against approved response patterns.
Stakeholders report that small wording differences are causing validation mismatches.
You need to update the request parameters to improve output stability. The solution must maximize
reasoning quality.
How should you complete the Python code?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q93 in the coverage map](../../docs/question-coverage.md).

## Q97

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
Users report that some responses omit required regulatory clauses, even when the clauses are present in
the retrieved content.
You need to improve response completeness.
Solution: You increase the value of the max_tokens parameter.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q97 in the coverage map](../../docs/question-coverage.md).

## Q99

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
Users report that some responses omit required regulatory clauses, even when the clauses are present in
the retrieved content.
You need to improve response completeness.
Solution: You increase the value of the temperature parameter.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q99 in the coverage map](../../docs/question-coverage.md).

## Q102

You have a Microsoft Foundry project that contains a support-ticket triage agent built by using the
Foundry Agent Service.
The agent uses tool to classify the ticket type and sot the ticket priority.
Sometimes, the same support case continues across multiple sessions over several days.
You need to persist state by using a durable ID to ensure that the agent can automatically reuse the full
interaction history. The solution must preserve previous user messages, tool calls and tool outputs across
turns and sessions.
Which runtime component should you use?
A. output item
B. agent
C. conversation
D. response

**Study mapping:** [Q102 in the coverage map](../../docs/question-coverage.md).

## Q108

You have a Microsoft Foundry project that contains a customer support agent built on a deployed chat
model. The agent responses are validated by using an automated testing system that compares generated
answers to stored expected outputs. Identical prompts must return consistent response to prevent
automated test failures.
You need to reduce response variability, without modifying the prompt or reducing factual accuracy.
What should you do for the model?
A. Increase the max_tokens parameter.
B. Remove stop sequences from the requests.
C. Decrease the temperature parameter.
D. Increase the temperature parameter.

**Study mapping:** [Q108 in the coverage map](../../docs/question-coverage.md).

## Q109

You have a Microsoft Foundry project that contains two agents named PolicyWriter and RskReviewer.
PolicyWriter generates daft updates for customer polices, and RiskReviewer reviews the drafts.
In the visual builder, you need to create a workflow that meets the following requirements:
• Finalizes low-risk updates without manual intervention
• Ensures predictable execution across the agents
• Requires user approval for highs updates
What should you configure?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q109 in the coverage map](../../docs/question-coverage.md).

## Q110

You are developing prompts for a Micosoft Foundry project that classifies incoming support tickets by
category. You need to improve accuracy by showing the model how correct classifications look, without
retaining the model or storing knowledge permanently.
Which prompt engineering approach should you use?
A. Retrieval Augmented Generation (RAG)
B. zero-shot learning
C. chain of thought
D. few-shot learning

**Study mapping:** [Q110 in the coverage map](../../docs/question-coverage.md).

## Q123

You have a Microsoft Foundry project.
You need to create a customer support agent that meets the following requirements:
• Grounds responses only in company policy documents stored in curated repositories
• Retains customer preferences across separate chat sessions
How should you configure the agent?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q123 in the coverage map](../../docs/question-coverage.md).

## Q131

You have a Microsoft Foundry project.
You need to deploy a model from the model catalog to support a search solution for internal policy
documents. The model must generate vector representations of the text in the documents and of user
queries.
Which type of model should you use?
A. an embedding model
B. an image generation model
C. a large language model (LLM)
D. a small language model (SLM)

**Study mapping:** [Q131 in the coverage map](../../docs/question-coverage.md).

## Q153

You have an Azure subscription.
You need to build an app that will compare documents for semantic similarity. The solution must meet the
following requirements:
• Return numeric vectors that represent the tokens of each document.
• Minimize development effort.
Which Azure OpenAI model should you use?
A. GPT-3.5
B. embeddings
C. GPT-4
D. DALL-E

**Study mapping:** [Q153 in the coverage map](../../docs/question-coverage.md).

## Q154

You are building an app that will provide users with definitions of common AI terms. You create the
following Python code.
For each of the following statements, select Yes if the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q154 in the coverage map](../../docs/question-coverage.md).

## Q155

You have an Azure OpenAI model named AI1.
You are building a web app named App1 by using the Azure OpenAI SDK. You need to configure App1 to
connect to AI1.
What information must you provide?
A. the deployment name, key, and model name
B. the endpoint, key, and model type
C. the deployment name, endpoint, and key
D. the endpoint, key, and model name

**Study mapping:** [Q155 in the coverage map](../../docs/question-coverage.md).

## Q169

You need to configure Agent1 to answer customer questions about only the Contoso products. The
solution must meet the business requirements.
What should you do?
A. Modify the system message instructions.
B. Add few-shot examples.
C. Apply top-p sampling.
D. Increase the value of the temperature parameter.

**Study mapping:** [Q169 in the coverage map](../../docs/question-coverage.md).

## Q174

You need to configure personalized user interactions for Agent1. The solution must meet the business
requirements.
What should you include in the solution?
A. knowledge
B. memory
C. guardrails
D. tools

**Study mapping:** [Q174 in the coverage map](../../docs/question-coverage.md).

