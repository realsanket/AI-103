# Domain 05 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Information extraction**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q2

You have a Microsoft Foundry project that contains an agent.
The agent ingests scanned PDF vendor invoices that contain tables and embedded QR codes.
The agent must preserve the PDF layout in the extracted output to ensure that downstream processing can
reference sections and tables.
You plan to call Azure Content Understanding in Foundry Tools.
You need to extract content and layout elements and detect QR codes without requiring a language model
deployment.
Which built-in analyzer should you use?
A. prebuilt-documentFieldSchema
B. prebuilt-read
C. prebuilt-documentSearch
D. prebuilt-layout

**Study mapping:** [Q2 in the coverage map](../../docs/question-coverage.md).

## Q4

You are building a web app named App1 that generates responses by using a model deployed to a
Microsoft Foundry project named Project1. Before sending the prompts to the model, App1 must retrieve
documents by using Azure AI Search. You need to integrate Project1 and App1.
The solution must meet the following requirements:
• Multiple client applications must use the same search configuration.
• A security policy must prevent key-based authentication.
• Administrative effort must be minimized.
What should you do?
A. Create a custom HTTP connection in Foundry and manually configure Azure AI Search endpoints per
application.
B. Configure an Azure AI Search connection in Project1 and reference the connection in each application.
C. Call Azure AI Search directly from each application by using Microsoft Entra authentication.
D. Enable a managed identity for each application and call Azure AI Search directly.

**Study mapping:** [Q4 in the coverage map](../../docs/question-coverage.md).

## Q14

You have a chat app in a Microsoft Foundry project and an Azure AI Search vectorized index.
You need to connect to the index to meet the following requirements:
• Complex questions must retrieve information from multiple chunks.
• Multi-turn conversations must influence retrieval planning.
• Retrievals must run in parallel to reduce latency.
Which retrieval approach should you use?
A. iterative retrieval
B. agentic Retrieval Augmented Generation (RAG)
C. chain of thought
D. classic Retrieval Augmented Generation (RAG)

**Study mapping:** [Q14 in the coverage map](../../docs/question-coverage.md).

## Q15

You have a Microsoft Foundry project that contains an agent.
The agent processes scanned employee identification cards from multiple countries.
The solution must meet the following requirements:
• Extract structured fields such as employee ID, full name, and expiration date.
• Return the extracted values as a structured schema instead of raw text.
• Minimize custom post-processing.
You plan to call Azure Content Understanding in Foundry Tools.
Which built-in analyzer should you use?
A. prebuilt-layout
B. prebuilt-documentSearch
C. prebuilt-documentFieldSchema
D. prebuilt-read

**Study mapping:** [Q15 in the coverage map](../../docs/question-coverage.md).

## Q21

You have a Microsoft Foundry project that contains an agent.
The agent uses a knowledge source built from documents stored in Azure Blob Storage. The documents
include digitally scanned PDFs that contain multipage tables.
You have an ingestion job that extracts only plain text, causing loss of table structure, headings, and page-
number metadata.
Users frequently ask questions that require the retrieval of specific table rows across the pages.
You need to configure an ingestion job for a Retrieval Augmented Generation (RAG) pipeline that performs
optical character recognition (OCR) on scanned PDFs, preserves tables and headings as structure-aware
chunks, and stores page-number metadata with each chunk.
How should you configure the ingestion job?
A. Use advanced data parsing to reingest the documents.
B. Use OCR and page-level chunking.
C. Use page-level OCR extraction and store each page as a single chunk.
D. Use basic parsing and fixed-size chunking.

**Study mapping:** [Q21 in the coverage map](../../docs/question-coverage.md).

## Q28

You have a Microsoft Foundry project that contains an agent. The agent uses Azure AI Search in
Foundry Tools to retrieve documents from a search index.
The application returns an error indicating that the specified index cannot be found.
You verify that the Azure AI Search service is reachable and authentication succeeds.
You need to configure the request to reference the correct search index.
To what should you set the index property?
A. The Azure AI Search service name
B. The Azure AI Search endpoint URL
C. The Azure AI Search index name
D. The Microsoft Foundry project name

**Study mapping:** [Q28 in the coverage map](../../docs/question-coverage.md).

## Q31

You are planning a Microsoft Foundry project named Project1 that will contain multiple agents. Each
agent will access the same Azure AI Search resource.
You need to recommend a solution to centrally manage the Azure AI Search credentials within Project1. The
solution must be implemented across all the agents.
What should you recommend?
A. Enable role-based access control (RBAC) for the Azure AI Search resource.
B. Disable key-based access control on the Azure AI Search resource.
C. Add a connection to the Azure AI Search resource.
D. Create a managed private endpoint that connects to the Azure AI Search resource.

**Study mapping:** [Q31 in the coverage map](../../docs/question-coverage.md).

## Q35

You have a Microsoft Foundry project that contains an agent used by a legal department. The agent
generates answers by using documents retrieved from an Azure AI Search index.
Users report that some answers omit important clauses from lengthy legal documents.
You need to improve the completeness of responses. The solution must be implemented in the application
logic without changing the search index or replacing the deployed model.
What should you do?
A. Increase the number of retrieved document chunks before constructing the prompt.
B. Enable Prompt Shields for document attacks.
C. Configure Content Safety to annotate responses.
D. Use a lower temperature value.

**Study mapping:** [Q35 in the coverage map](../../docs/question-coverage.md).

## Q36

You have a Microsoft Foundry project that processes procurement documents submitted by suppliers.
You need to implement two pipelines by using Azure Content Understanding in Foundry Tools.
The solution must meet the following requirements:
• Include a pipeline named Pipeline1 that supports cost-effective, high-volume processing of
standalone PDF invoices.
• Include a pipeline named Pipeline2 that supports cross-document validation by using multi-step
reasoning and reference data.
How should you configure each pipeline?
To answer, drag the appropriate configurations to the correct pipelines. Each configuration may be used once,
more than once, of not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q36 in the coverage map](../../docs/question-coverage.md).

## Q41

You have a Microsoft Foundry project that ingests scanned PDF invoices stored in Azure Blob Storage.
Each invoice contains printed fine items and has a table-based layout.
Extracted results are stored as structured JSON and used as grounding data for an agent in a Retrieval
Augmented Generation (RAG) solution.
You need to create a single analyzer that meets the following requirements:
• Extracts the invoice number, invoice date, vendor name, and total amount across varying templates
• Returns confidence scores so that results with confidence below 0.80 can be routed for supervisor
review
What should you use?
A. a Foundry agent that has groundedness guardrails enabled to extract invoice fields and confidence scores
B. a custom Azure Content Understanding in Foundry Tools analyzer that defines the required fields as the
extracted fields and the returned confidence scores for routing
C. the Azure Content Understanding in Foundry Tools prebuilt-layout analyzer
D. the Azure Content Understanding in Foundry Tools prebuilt-documentSearch analyzer and search.score
from the Azure AI Search results for routing

**Study mapping:** [Q41 in the coverage map](../../docs/question-coverage.md).

## Q46

You have a Microsoft Foundry project that processes regulatory compliance documents submitted by
regional offices.
You need to implement two pipelines by using Content Understanding in Microsoft Foundry Tools.
The solution must meet the following requirements:
• Include a pipeline named Pipeline1 that extracts key compliance information from individual audit
reports while minimizing processing costs.
• Include a pipeline named Pipeline2 that analyzes multiple related audit reports together to identify
inconsistencies across reporting periods by using advanced reasoning.
How should you configure each pipeline?
To answer, drag the appropriate configurations to the correct pipelines. Each configuration may be used once,
more than once, or not at all.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q46 in the coverage map](../../docs/question-coverage.md).

## Q55

You have a Microsoft Foundry project that contains an agent.
The agent processes scanned maintenance reports that are uploaded by field technicians.
The solution must meet the following requirements:
• Extract all readable text from each document.
• Ignore the document layout, including tables and paragraph positions.
• Do not identify key-value pairs or structured business fields.
• Minimize processing costs and avoid using a language model deployment.
You plan to call Azure Content Understanding in Foundry Tools.
Which built-in analyzer should you use?
A. prebuilt-documentFieldSchema
B. prebuilt-layout
C. prebuilt-read
D. prebuilt-documentSearch

**Study mapping:** [Q55 in the coverage map](../../docs/question-coverage.md).

## Q75

You have a Microsoft Foundry project that contains an Azure AI Search resource used to ground
multiple agents.
Developers at your company use Microsoft Entra ID authentication to query the search index from a custom
application. They receive HTTP 403 (Forbidden) errors when executing search queries.
You need to grant the minimum permissions required for developers to query the search index.
Which role-based access control (RBAC) role should you assign?
A. Search Service Contributor
B. Search Index Data Reader
C. Contributor
D. Reader

**Study mapping:** [Q75 in the coverage map](../../docs/question-coverage.md).

## Q77

You have a Microsoft Foundry project that contains an agent. The agent has a Model Context Protocol
(MCP) tool that queries a knowledge base stored in Azure AI Search.
Some agent runs return answers from the base model without invoking the knowledge base, which results in
responses without grounded citations.
You are provided with the following code snippet that runs the agent.
run = project_client.agents.runs.create_and_process(
thread_id=thread.id,
agent_id=agent.id
)
You need to add the correct tool _choice parameter to the code to deterministically force the agent to invoke
the MCP tool on each run.
What should you add?
A. tool_choice= “required”
B. tool_choice= “auto”
C. tool_choice= “type”:“knowledge_base”
D. tool_choice = “type”:“mcp”

**Study mapping:** [Q77 in the coverage map](../../docs/question-coverage.md).

## Q84

You have a Microsoft Foundry project that contains an agent.
You need to process mixed-format documents that contain scanned text, tables, and multicolumn layouts.
The extracted content must preserve the document structure and be converted into the Markdown format for
downstream reasoning.
What should you configure first?
A. an Azure Language in Foundry Tools text analysis model deployment
B. a generative chat completion request
C. an Azure OpenAI Responses API call that uses a multimodal model
D. an Azure Content Understanding in Foundry Tools analyzer

**Study mapping:** [Q84 in the coverage map](../../docs/question-coverage.md).

## Q87

You have a Microsoft Foundry project that contains an agent.
The knowledge source for the agent is a set of scanned PDF troubleshooting guides stored in Azure Blob
Storage. The guide pages contain two-column layouts and tables.
You use Azure Content Understanding in Foundry Tools to process the PDFs.
You plan to ingest the processed content into an index for Retrieval Augmented Generation (RAG) and store
extracted fields for downstream automation.
Stakeholders must be able to verify where each extracted field value came from in the original PDF and route
low-reliability extractions for manual review.
You need to ensure that the Content Understanding document analyzer output includes a per-field confidence
score and source grounding to locations within the source document.
What should you do?
A. Set enableSegment to true.
B. Provide labeled samples.
C. Enable estimateFieldSourceAndConfidence.
D. Configure the analyzer to use generative extraction for all fields.

**Study mapping:** [Q87 in the coverage map](../../docs/question-coverage.md).

## Q88

A Microsoft Foundry agent answers questions from an Azure AI Search index.
Administrators observe the following:
• Average prompt size has doubled.
• Azure OpenAI costs have increased significantly.
• Response quality remains unchanged.
Which action should you recommend first?
A. Replace the model with GPT-4.1.
B. Retrieve fewer document chunks before constructing the prompt.
C. Increase the chunk overlap during indexing.
D. Increase the model context window.

**Study mapping:** [Q88 in the coverage map](../../docs/question-coverage.md).

## Q90

You have an application that processes scanned PDF invoices. The invoices have varied layouts and
include multipage tables.
You have a pipeline that uses optical character recognition (OCR) and extracts totals and invoice numbers.
The results are often incorrect because the document structure is ignored.
You need to implement a solution that provides OCR, layout analysis, and template-generalizing field
extraction. The solution must NOT require training a custom model. The solution must minimize
administrative effort.
What should you include in the solution?
A. Azure Language in Foundry Tools
B. Azure Content Understanding in Foundry Tools
C. an Azure Machine Learning model

**Study mapping:** [Q90 in the coverage map](../../docs/question-coverage.md).

## Q92

You have a Microsoft Foundry project that processes purchase orders stored in Azure Blob Storage.
Each purchase order has a different layout depending on the supplier.
The extracted information will be stored as structured JSON and used by a procurement agent.
You need to create a single analyzer that meets the following requirements:
• Extract the purchase order number, supplier name, requested delivery date, and total value from all
supported layouts.
• Return confidence scores for each extracted field.
• Minimize post-processing in the application.
What should you use?
A. A custom Azure Content Understanding analyzer in Foundry Tools that defines the required fields as
extracted fields.
B. The Azure Content Understanding prebuilt-read analyzer.
C. The Azure Content Understanding prebuilt-layout analyzer.
D. Azure AI Search with vector search enabled.

**Study mapping:** [Q92 in the coverage map](../../docs/question-coverage.md).

## Q94

You have a Microsoft Foundry project that contains an agent. The agent uses Azure AI Search as the
retriever.
You plan to ingest PDF into an Azure AI Search index to ensure that the agent can ground responses in texts
in both documents and embedded images.
Users require citations that link to the source files.
You need to ensure that during indexing, the images are extracted into a structure that can be used as input
for the built-in optical character recognition (OCR) skill.
Which indexing approach should you use?
A. an indexer to extract image data into a normalized_images collection
B. a Shaper skill to restructure the OCR input
C. a skillset to run the OCR skill directly against the content field of the index
D. the outputFieldMappings parameter to write image data to a searchable field

**Study mapping:** [Q94 in the coverage map](../../docs/question-coverage.md).

## Q114

You have a Microsoft Foundry project that contains an agent.
The agent uses Azure Content Understanding in Foundry Too to process vendor onboarding packets. The
packs include digital PDFs that contain tables and hyperlinks.
The extracted content is indexed for search and provided to a downstream agent in the Markdown format.
You need to generate a Markdown output that has a layout and a semantic structure optimized for Retrieval
Augmented Generation (RAG) workflows.
Which built-in analyzer should you use?
A. prebuilt-documentFieldSchema
B. prebuilt-documentSearch
C. prebuilt-read
D. prebuilt-layout

**Study mapping:** [Q114 in the coverage map](../../docs/question-coverage.md).

## Q116

You have a Microsoft Foundry project that contains an agent.
The agent uses Azure AI Search for Retrieval Augmented Generation (RAG). You plan to ingest and index PDF
product manuals.
You need to build a solution that supports semantic similarity matching. The solution must ensure that the
agent retrieves relevant data when user questions use different wording than the product manuals.
Which indexing approach should you use?
A. vector search
B. semantic ranking
C. suggesters
D. analyzers

**Study mapping:** [Q116 in the coverage map](../../docs/question-coverage.md).

## Q118

You have a Microsoft Foundry agent that grounds responses from an Azure Search index that contains
the following:
• Searchable text fields for product names and product codes
• A vector field that stores embeddings for product descriptions
You need to ensure that users can query the index by using the following:
• Exact product names or codes
• Natural language descriptions of the products
What should you configure?
A. vector search only
B. hybrid search
C. keyword search only
D. semantic search only

**Study mapping:** [Q118 in the coverage map](../../docs/question-coverage.md).

## Q120

You have an Azure AI Search indexer that ingests PDF policy manuals.
Client applications must display page-level citations that have bounding polygons for both text and images.
You need to add a single built-in multimodal content extraction skill to the Azure AI Search skillset.
The solution must meet the following requirements:
• Provide text and image location metadata.
• Extract tables that span multiple pages.
What should you add?
A. Document Extraction
B. Azure Content Understanding in Foundry Tools
C. GenAI Prompt
D. Document Layout

**Study mapping:** [Q120 in the coverage map](../../docs/question-coverage.md).

## Q121

You are building an Azure AI Search indexing pipeline named Pipeline1 that ingests invoices stored in
Azure Blob Storage. The invoices are stored as scanned images.
You need to enable users to search invoice data across the invoice fields. Which built-in skill should you add
to the skillset of Pipeline1?
A. Text Split
B. Text Translation
C. optical character recognition (OCR)
D. Image Analysis

**Study mapping:** [Q121 in the coverage map](../../docs/question-coverage.md).

## Q122

You have an invoice-processing application named App1 that uses Azure Constant Understanding in
Foundry Tools.
You are building a new Content Understanding pipeline named Pipeline1 that must meet the following
requirements:
• Compare an invoice to its related purchase order
• Validate the voice against static vendor contact documents
• Return a single structured output that includes discrepancy findings
You need to configure Pipeline1 and expose the pipeline as a single analyzer endpoint. What should you
configure?
A. a single-file task in standard mode that uses the vendor contract provided as an additional document
during analysis.
B. a single-file task in standard mode that uses confidence scores enabled for the extracted fields.
C. a multiple-file task in pro mode that uses the vendor contract files as reference data
D. a multi-file task in standard mode that uses the invoice and purchase order as input to the analyzer

**Study mapping:** [Q122 in the coverage map](../../docs/question-coverage.md).

## Q141

You are creating an enrichment pipeline that will use Azure AI Search. The knowledge store contains
unstructured JSON data and the text from scanned PDF documents.
Which projection type should you use for each data type?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q141 in the coverage map](../../docs/question-coverage.md).

## Q144

You are developing an application that will use Azure AI Search for internal documents. You need to
implement document-level filtering for Azure AI Search.
Which three actions should you include in the solution?
A. Add allowed groups to each index entry
B. Create one index per group.
C. Send access tokens from Microsoft Entra ID, with the search request.
D. Retrieve all the groups.
E. Retrieve the group memberships of the user
F. Supply the groups as a filter for the search requests

**Study mapping:** [Q144 in the coverage map](../../docs/question-coverage.md).

## Q145

You have a web app that uses Azure AI Search.
When reviewing activity you see greater than expected search query volumes. You suspect that the query
key is compromised.
You need to prevent unauthorized access to the search endpoint and ensure that users only have read only
access to the documents collection. The solution must minimize app downtime.
Which three actions should you perform in sequence?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q145 in the coverage map](../../docs/question-coverage.md).

## Q146

You have an Azure AI Search indexer that ingest PDF policy manuals.
Client applications must display page-level citations that have bounding polygons for both text and images.
You need to add a single built-in multimodal content extraction skill to the Azure AI Search skillset.
The solution must meet the following requirements:
• Provide text and image location metadata.
• Extract tables that span multiple pages.
What should you add?
A. Document Layout
B. Document Extraction
C. Azure Content Understanding
D. GenAI Prompt

**Study mapping:** [Q146 in the coverage map](../../docs/question-coverage.md).

## Q170

You need to recommend an invoice review solution that resolves the issue reported by the finance
department.
What should you include in the recommendation?
A. chat completions
B. Azure Document Intelligence in Foundry Tools
C. Azure Content Understanding in Foundry Tools
D. Image Analysis

**Study mapping:** [Q170 in the coverage map](../../docs/question-coverage.md).

## Q171

You need to configure an indexing pipeline for Agent1 to retrieve the relevant product information in
storage1. The solution must meet the technical requirement.
Which two built-in skills should you use?
A. Azure OpenAI Embedding
B. Entity Recognition
C. Text Split
D. Merge
E. Language Detection
F. key phrase extraction

**Study mapping:** [Q171 in the coverage map](../../docs/question-coverage.md).

## Q172

You need to recommend a solution to support the planned changes and technical requirements for
Agent1 to use the product information stored in storage1.
What should you include in the recommendation?
A. Azure Translator in Foundry Tools
B. Grounding with Bing Search
C. Azure AI Search
D. Azure Document intelligence in Foundry Tools

**Study mapping:** [Q172 in the coverage map](../../docs/question-coverage.md).

