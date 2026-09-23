# Domain 01 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Plan and manage Microsoft Foundry**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q3

You have a Microsoft Foundry project that contains an agent.
The agent accepts user-uploaded screenshots and uses a multimodal chat model. Some screenshots contain
potentially malicious embedded text.
You need to prevent a prompt injection attack and ensure that third-party content is treated as lower trust.
How should you configure prompt shields for document attacks?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q3 in the coverage map](../../docs/question-coverage.md).

## Q5

You have a Microsoft Foundry project that contains a customer support agent. The agent calls an internal
knowledge API tool before generating responses.
Users report the following issues:
• Some requests take more than 15 seconds to complete.
• Some responses are incorrect, even when the knowledge API returns the expected data.
You need to inspect individual agent runs to view the ordered sequence of large language model (LLM) calls,
tool invocations, and timing information.
Which observability capability should you use?
A. token usage
B. monitoring
C. safety metrics
D. tracing

**Study mapping:** [Q5 in the coverage map](../../docs/question-coverage.md).

## Q9

You have a Microsoft Foundry project that contains a customer support agent. The agent is deployed by
using a GitHub Actions workflow.
The organization has the following requirements:
• Every deployment to the production environment must use the latest approved evaluation baseline.
• Deployments must stop automatically if the current evaluation scores regress beyond the configured
tolerance.
How should you configure the workflow?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q9 in the coverage map](../../docs/question-coverage.md).

## Q10

Your company is piloting a customer support agent in a Microsoft Foundry project name Project1.
Project1 is connected to an existing Application Insights resource, and the company’s support team reviews
runs in the Traces tab.
The Foundry Agent Service is configured to perform the following actions:
Retrieve the Application Insights connection string by calling
project_client.telemetry.get_application_insights_connection_string().
Call configure_azure_monitor(connection_string=...) to enable telemetry.
A separate LangChain service is configured to use OpenTelemetry and has the following configurations:
Uses AzureAIOpenTelemetryTracer(connection_string=..., enable_content_recording=False)
Passes the tracer by using config= “callbacks”:[azure_tracer] Company policy has the following requirements:
• Telemetry from LangChain and OpenTelemetry must be distinguishable within the same Application
Insights resource.
• Secrets and credentials must NOT be stored in prompts, tool arguments, or span attributes.
For each of the following statements, select Yes if the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q10 in the coverage map](../../docs/question-coverage.md).

## Q17

You have a customer support agent built by using the Microsoft Foundry Agent Service. The agent calls
an Azure OpenAI model deployment.
During load testing, calls intermittently fail and return an HTTP 429 rate limit exceeded error.
You need to handle throttling to reduce call failures and improve reliability under load. The solution must
remain within the service and model limits.
What should you do?
A. Create a new thread and retry the calls immediately.
B. Reduce the number of registered tools.
C. Implement a retry policy that uses exponential backoff and jitter.
D. Spit uploaded content into smaller files.

**Study mapping:** [Q17 in the coverage map](../../docs/question-coverage.md).

## Q19

You have a Microsoft Foundry project that contains an agent that answers questions by using Retrieval-
Augmented Generation (RAG).
A GitHub Actions workflow automatically deploys updates whenever a pull request is approved.
The organization has the following requirements:
• Validate that responses remain grounded in the retrieved documents before deployment.
• Prevent pull requests from being merged if the evaluation does not satisfy the required quality
thresholds.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q19 in the coverage map](../../docs/question-coverage.md).

## Q23

You have a Microsoft Foundry project that contains an internal Q&A agent.
Users report the following issues when they ask the agent questions:
An increase in the following response: “No relevant information found”
Periodic HTTP 429 rate limit exceeded errors during peak hours
You need to identify whether each issue is caused by model unavailability, resource limits, or inference
failures.
What should you do?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q23 in the coverage map](../../docs/question-coverage.md).

## Q24

You have a Microsoft Foundry project that contains a prompt agent used by a customer support web
app. The agent is invoked from a Python service that does NOT run in the Foundry portal.
You need to implement end-to-end tracing to capture latency breakdowns and exceptions across agent runs.
Which two components can you use?
A. a Log Analytics workspace
B. Application Insights
C. OpenTelemetry
D. the Azure Monitor Agent
E. Microsoft Sentinel

**Study mapping:** [Q24 in the coverage map](../../docs/question-coverage.md).

## Q26

You have a Microsoft Foundry project that contains a customer support agent grounded in internal
documentation. After a recent update, users report the following issues:
• Some answers are unsupported by retrieved documents.
• A small number of responses are flagged for policy violations.
You need to evaluate each issue.
Which observability signals should you use for each issue?
To answer, drag the appropriate observability signals to the correct issues. Each observability signal may be
used once, more than once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q26 in the coverage map](../../docs/question-coverage.md).

## Q34

You have a Microsoft Foundry project that uses Azure AI Search to ground an agent in internal
documentation. After a recent content update, users report that the agent’s answers have become less
accurate.
You need to identify whether the retrieved content is negatively influencing the model’s generated responses.
Which observability signal should you review?
A. indexer status and failure history
B. latency breakdown traces
C. prediction drift metrics
D. groundedness evaluation metrics

**Study mapping:** [Q34 in the coverage map](../../docs/question-coverage.md).

## Q40

You have a multimodal AI generative model that accepts image uploads and uses extracted image text
to generate responses.
You discover that users can upload unsafe images and embed hidden instructions into images to manipulate
the model.
You need to implement controls to mitigate the risk.
Solution: You configure protected material detection.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q40 in the coverage map](../../docs/question-coverage.md).

## Q42

A Microsoft Foundry agent retrieves content from external websites by using Grounding with Bing
Search.
Security administrators want to:
• Detect indirect prompt injection attempts.
• Review detections before deciding whether to block requests.
Which configuration should you recommend?
A. Disable Prompt Shields.
B. Configure Prompt Shields to Block.
C. Configure Prompt Shields to Annotate and enable Spotlighting.
D. Configure Content Safety to Block Hate content.

**Study mapping:** [Q42 in the coverage map](../../docs/question-coverage.md).

## Q47

You have a Microsoft Foundry project that contains a high-traffic agent. After a recent update,
operational costs increase significantly.
Monitoring confirms that the volume of user traffic to the agent remains unchanged.
You suspect that changes to the request or response characteristics are causing the increase.
You need to identify whether the additional costs are driven by the model input size, the model output size, or
expanded tool usage.
Which observability capability should you use?
A. latency
B. evaluation metrics
C. run success rate
D. token usage

**Study mapping:** [Q47 in the coverage map](../../docs/question-coverage.md).

## Q48

You have a Microsoft Foundry project that contains an Azure Storage account used to store documents
for Retrieval-Augmented Generation (RAG).
The agents authenticate by using managed identities.
The agents must be able to read blob data but must not upload, modify, or delete files.
Which role-based access control (RBAC) role should you assign to the managed identities?
A. Storage Blob Data Owner
B. Storage Blob Data Contributor
C. Storage Blob Data Reader
D. Contributor

**Study mapping:** [Q48 in the coverage map](../../docs/question-coverage.md).

## Q49

You have a Microsoft Foundry project that contains an agent.
You use a GitHub Actions workflow for CI/CD.
You need to configure the workflow to automatically evaluate the agent when a pull request (PR) is created
and prevent branches from merging if the evaluation results do NOT meet the defined thresholds.
How should you configure the workflow?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q49 in the coverage map](../../docs/question-coverage.md).

## Q53

You have a Python application named App1 that integrates with a Microsoft Foundry project named
Project1.
You need to ensure that App1 meets the following requirements:
• Authenticates by using a Microsoft Entra managed identity
• Sends prompts to a deployed model by using the Azure OpenAI Responses API
How should you complete the Python code?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q53 in the coverage map](../../docs/question-coverage.md).

## Q56

You have a Microsoft Foundry project that contains a sales assistant agent. The agent retrieves product
information from an Azure AI Search index and generates responses by using a large language model.
After deploying a new version of the agent, users report the following issues:
• The average response time has increased significantly when users ask complex questions.
• Monthly model inference costs have increased even though the number of user requests has
remained unchanged.
You need to evaluate each issue.
Which observability signals should you use for each issue?
To answer, drag the appropriate observability signals to the correct issues. Each observability signal may be
used once, more than once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q56 in the coverage map](../../docs/question-coverage.md).

## Q58

You have a Microsoft Foundry project that contains an agent used by a customer service application.
Following a recent deployment, users report that responses take significantly longer to generate. Monitoring
shows that the number of requests per minute has remained constant.
You need to determine whether the increased response time is caused by document retrieval, tool execution,
or model inference.
Which observability capability should you use?
A. Evaluation metrics
B. Latency
C. Run success rate
D. Token usage

**Study mapping:** [Q58 in the coverage map](../../docs/question-coverage.md).

## Q59

You have a Microsoft Foundry project that processes engineering drawings stored in Azure Blob
Storage.
Azure AI Content Safety must retrieve images by using blob URLs to evaluate user-submitted images.
The solution must meet the following requirements:
• Follow the principle of least privilege.
• Avoid using storage account keys or shared access signatures (SAS).
• Allow Content Safety to read images stored in Azure Blob Storage.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q59 in the coverage map](../../docs/question-coverage.md).

## Q63

You have a Microsoft Foundry project that contains a customer support agent built by using the
Foundry Agent Service.
The agent uploads user-provided screenshots to Azure Storage through a ticketing tool and receives a blob
URL for additional reasoning.
You need to use image moderation during agent runs and prevent harmful content from being returned
during runs.
Azure AI Content Safety must access the images by using the blob URL. The solution must follow the
principle of least privilege.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q63 in the coverage map](../../docs/question-coverage.md).

## Q64

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
You need to improve response completeness. The solution must be implemented in the logic of the
application code before responses are returned.
What should you do?
A. Add a retry evaluation before the responses are returned.
B. Decrease the value of the max_tokens parameter.
C. Switch to Retrieval Augmented Generation (RAG).
D. Replace the model with a smaller deployment.

**Study mapping:** [Q64 in the coverage map](../../docs/question-coverage.md).

## Q65

You have an app named App1 that uses a Microsoft Foundry chat model deployment.
App1 accepts free-form text entered directly by users.
Some users intentionally submit prompts that attempt to bypass system instructions, reveal hidden prompts,
or manipulate tool execution.
You need to detect these direct prompt injection attempts before the model processes the user's input.
What should you use?
A. Image moderation
B. Prompt Shields for documents
C. Protected material text
D. Prompt Shields for user prompts

**Study mapping:** [Q65 in the coverage map](../../docs/question-coverage.md).

## Q66

You have a Microsoft Foundry project that contains an agent that answers employee questions by using
Retrieval-Augmented Generation (RAG).
After deployment, users report the following issues:
• The retrieved documents are relevant, but the generated answers do not address the user's question.
• Responses generated by the agent are significantly longer than expected, increasing inference costs.
You need to determine which diagnostic capability to use for each issue.
Which diagnostic capability should you use?
To answer, drag the appropriate diagnostic capabilities to the correct issues. Each diagnostic capability may
be used once, more than once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q66 in the coverage map](../../docs/question-coverage.md).

## Q68

You have a Microsoft Foundry project that contains a customer support agent.
After deploying a new prompt template, administrators observe that Azure OpenAI costs have increased
significantly, even though the number of user requests has remained constant.
You need to determine whether the prompt or generated responses are consuming more tokens than
expected.
Which observability signal should you review?
A. Groundedness evaluation metrics
B. Retrieval evaluation metrics
C. Token usage analytics
D. Agent execution timeline

**Study mapping:** [Q68 in the coverage map](../../docs/question-coverage.md).

## Q69

You have a Microsoft Foundry project that contains a customer support agent. The agent uses Azure AI
Search as a knowledge source to answer questions by using Retrieval-Augmented Generation (RAG).
After a recent deployment, users report the following issues:
• The agent occasionally generates responses that are not supported by the retrieved documents.
• Support engineers want the agent to return a fallback response instead of generating an answer
when insufficient grounding evidence is available.
You need to identify the evaluation metric and the recommended configuration to address the issues.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q69 in the coverage map](../../docs/question-coverage.md).

## Q71

You have a Microsoft Foundry project that contains a model deployment.
You have an application that calls the deployment by using the Azure OpenAI v1 API and
DefaultAzureCredential. The developers at your company receive HTTP 403 errors when they send inference
requests, even after running az login.
You need to ensure that the developers can perform model inference. The solution must follow the principle
of least privilege.
Which role-based access control (RBAC) role should you assign to the developers?
A. Cognitive Services User
B. Cognitive Services OpenAI User
C. Contributor
D. Cognitive Services Data Reader

**Study mapping:** [Q71 in the coverage map](../../docs/question-coverage.md).

## Q78

A Microsoft Foundry agent invokes three custom tools.
Administrators report that users occasionally experience response delays.
They need to determine which tool contributes the most to the total response time.
Which diagnostic capability should they review?
A. Token usage analytics
B. Tool execution traces
C. Groundedness evaluation
D. Conversation history

**Study mapping:** [Q78 in the coverage map](../../docs/question-coverage.md).

## Q80

You have a Microsoft Foundry project that contains an agent used by an internal HR application.
Following a prompt update, administrators notice that users are reporting more incomplete and unsupported
answers. The application continues to process requests successfully, and response times remain unchanged.
You need to determine whether the quality of the generated responses has degraded.
Which observability capability should you use?
A. Token usage
B. Latency
C. Evaluation metrics
D. Run success rate

**Study mapping:** [Q80 in the coverage map](../../docs/question-coverage.md).

## Q81

You have a Microsoft Foundry project that serves a high-volume chat app. Most requests are simple
FAQs, but some require advanced reasoning.
You need to reduce costs and latency for common queries, without degrading the quality of the responses to
complex questions.
What should you do?
A. Route all the requests to a smaller model.
B. Use a model cascade that routes the requests to different models.
C. Increase the value of the max_tokens parameter for all the requests.
D. Route all the requests to the most capable model.

**Study mapping:** [Q81 in the coverage map](../../docs/question-coverage.md).

## Q96

You have a Microsoft Foundry project that contains a customer support agent.
The agent invokes several tools to retrieve order information, customer profiles, and shipping status before
generating a response.
Users report that response times have increased significantly after a recent deployment.
You need to identify which stage of the agent execution is contributing most to the increased response time.
Which observability signal should you review?
A. Groundedness evaluation metrics
B. Latency breakdown traces
C. Content Safety metrics
D. Relevance evaluation metrics

**Study mapping:** [Q96 in the coverage map](../../docs/question-coverage.md).

## Q98

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
Users report that some responses omit required regulatory clauses, even when the clauses are present in
the retrieved content.
You need to improve response completeness.
Solution: You add a reflection pass that regenerates the response if the required clauses are missing.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q98 in the coverage map](../../docs/question-coverage.md).

## Q100

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
Users report that some responses omit required regulatory clauses, even when the clauses are present in
the retrieved content.
You need to improve response completeness.
Solution: You run an evaluation flow that scores responses for completeness and blocks responses that fall
below a defined threshold.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q100 in the coverage map](../../docs/question-coverage.md).

## Q101

You have a Microsoft Foundry project that contains a Retrieval Augmented Generation (RAG) chat
solution used by customer support agents.
You are adding an automated pre-production evaluation step to a CI/CD pipeline named Pipeline1. The
evaluation will run against a labeled test dataset that contains support questions and the expected grounding
context.
You need to ensure that Pipeline1 fails if unsupported content or a retrieval mismatch exceeds a defined
threshold:
• responses include claims not supported by the retrieved source content
• retrieved source content does not align with the labeled expected context
Which two built-in evaluators should you use in Pipeline1?
A. Retrieval
B. Fluency
C. Coherence
D. Groundedness
E. Response Completeness

**Study mapping:** [Q101 in the coverage map](../../docs/question-coverage.md).

## Q103

You have a Microsoft Founcy project that contains a Retrieval Augmented Generation (RAG) solution.
You need to run a pre-production evaluation by using labeled CSV dataset that contains the query, context,
response and ground truth.
The evaluation must measure the following:
• Whether responses address the user query
• Whether responses are supported by the provided context
• Whether responses contain sensitive or proprietary information
Which AI quality evaluation metrics should you use?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q103 in the coverage map](../../docs/question-coverage.md).

## Q104

You plan to configure an evaluation in Microsoft Foundry for a Retrieval Augmented Generation (RAG)
chat app. You need to provide scores for groundedness, relevance, and harmful content categories.
Which two evaluation categories can you use?
A. risk and safety metrics
B. fluency evaluator
C. similarity evaluators
D. AI quality (NLP) metrics
E. AI quality (AI assisted) metrics

**Study mapping:** [Q104 in the coverage map](../../docs/question-coverage.md).

## Q111

You have a web app named App1 that processes user prompts by integrating with a Microsoft Foundry
project named Project1.
App1 performs the following actions:
• Sends prompts directly to a model by using the Azure OpenAI Responses API
• Invokes the Azure AI Content Safety tool by using a Foundry connection within the same request
You need to configure end-to-end visibility into each step of the request workflow.
What should you do?
A. Enable logging by using the client SDK for Content Safety.
B. Enable logging by using Foundry Local.
C. Enable application tracing in Project1.
D. Route requests through the Azure OpenAI endpoint.

**Study mapping:** [Q111 in the coverage map](../../docs/question-coverage.md).

## Q112

You have a Microsoft Foundry project that contains an agent named Agent1.
Agent runs successful, but Foundry Control Plane does NOT display values for error rates, runs, and token
usage, and the Traces tab is empty.
You need to ensure that Found Control Plane displays the appropriate values for Agent1. What should you
do?
A. Update Agent1 to a new version.
B. Restart Agent from Foundry Control Plan
C. Assign to a Log Analytics workspace to Agent1.
D. Enable Application Insights for Agent1.

**Study mapping:** [Q112 in the coverage map](../../docs/question-coverage.md).

## Q113

You have a Microsoft Foundry project that contains an agent.
The agent uses a stored access key to retrieve secrets from an Azure key vault, which violates a keyless-
credentials requirement.
You need to ensure that the agent can retrieve the secrets. The solution must follow the principle of least
privilege. What should you configure?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q113 in the coverage map](../../docs/question-coverage.md).

## Q115

You have a Microsoft Foundry project that contains a multi-agent solution. The agents use tool calling
to query internal systems.
You need to implement responsible AI auditing to meet the following requirements:
• Capture all the nested operations across the entire agent run.
• Record tool invocation arguments and retuned results as metadata.
What should you use for each requirement?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q115 in the coverage map](../../docs/question-coverage.md).

## Q125

You have a Microsoft Foundry project that contains an agent. The agent uses threads and file uploads
and calls an Azure OpenAI model deployment.
During load testing, calls intermittently fall and return an HTTP 429 rate limit exceeded error. Some user
uploads fail and generate an HTTP 400 file size exceeded error.
You need to mitigate the errors and reduce call failures. The solution must remain within the service and
model limits.
What should you do to resolve each error?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q125 in the coverage map](../../docs/question-coverage.md).

## Q130

You have a Microsoft Foundry project that contains an agent and uses a GitHub repository. The
repository contains a YAM file named File1 that defines the evaluation settings of the agent.
You need to create a GitHub Actions workflow that runs the evaluation defined in File1 when a pull request
(PR) is opened.
How should you configure the workflow?
A. Set project-endpoint to the endpoint of the project.
B. Set evaluation-config to the path of the YAML file.
C. Set model-deployment-name to the deployed model.
D. Set tenant-id to the Microsoft Entra tenant ID

**Study mapping:** [Q130 in the coverage map](../../docs/question-coverage.md).

## Q133

You have a Python application collects customer comments before posting them to a public forum.
You need to send a text comment to Azure AI Content Safety and return the self-harm severity from the
response. How should you complete the code?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q133 in the coverage map](../../docs/question-coverage.md).

## Q134

You have a Microsoft Foundry project that contains an agent. The agent generates summaries from
retrieved policy documents.
You need to improve response completeness. The solution must be implemented in the logic of the
application code before responses are returned.
What should you do?
A. Add a retry evaluation before the responses are returned.
B. Decrease the value of the temperature parameter.
C. Increase the value of the presence_penalty parameter
D. Replace the model with a smaller deployment.

**Study mapping:** [Q134 in the coverage map](../../docs/question-coverage.md).

## Q139

You need to create a new resource that will be used to perform sentiment analysis and optical
character recognition (OCR).
The solution must meet the following requirements:
• Use a single key and endpoint to access multiple services.
• Consolidate billing for future services that you might use.
• Support the use of Azure Vision in Foundry Tools in the future.
How should you complete the HTTP request to create the new resource?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q139 in the coverage map](../../docs/question-coverage.md).

## Q140

You are developing a new sales system that will process user-generated video and text from a public-
facing website.
You plan to notify users that their data has been processed by the sales system. Which responsible AI
principle does this help meet?
A. fairness
B. transparency
C. inclusiveness
D. reliability and safety

**Study mapping:** [Q140 in the coverage map](../../docs/question-coverage.md).

## Q142

You have an Azure subscription that contains an Azure App Service app named App1. You provision a
Microsoft Foundry Service resource named CSAccount1.
You need to configure App1 to access CSAccount1. The solution must minimize administrative effort.
What should you use to configure App1?
A. the endpoint URI and subscription key
B. the endpoint URI and an OAuth token
C. the endpoint URI and a shared access signature (SAS) token
D. a system assigned managed identity and an X.509 certificate

**Study mapping:** [Q142 in the coverage map](../../docs/question-coverage.md).

## Q166

You need to configure the model deployment for Agent1 to meet the technical requirements. What
should you configure?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q166 in the coverage map](../../docs/question-coverage.md).

## Q167

You need to configure Agent1 to meet the security and compliance requirements.
What should you use?
A. self-harm content filtering
B. prompt shields
C. Personally identifiable information (PII) Detection
D. violence content filtering

**Study mapping:** [Q167 in the coverage map](../../docs/question-coverage.md).

## Q168

You need to recommend a solution to assess the responses generated by Agent1 when the agent uses
the product information stored in storage1. The solution must meet the technical requirements.
What should you include in the recommendation?
A. a Retrieval Augmented Generation (RAG) evaluator
B. a custom guardrail
C. model fine-tuning
D. a groundedness evaluator

**Study mapping:** [Q168 in the coverage map](../../docs/question-coverage.md).

## Q175

You need to ensure that Agent1Dev Team can access Agent1. The solution must meet the security and
compliance requirements.
How should you complete the Python code?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q175 in the coverage map](../../docs/question-coverage.md).

