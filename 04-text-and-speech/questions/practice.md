# Domain 04 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Text and speech**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q1

You are building a speech processing solution in Microsoft Foundry for a customer support platform.
The platform will transcribe live phone calls, so that supervisors at your company can view call transcripts
and detect issues while the calls are in progress. The call audio will arrive as a continuous stream from the
telephony system.
You need to ensure that the call transcripts appear within only a few seconds of the audio stream.
What should you do?
A. Use text to speech by using a custom neural voice.
B. Use speech translation to generate the transcripts into multiple languages.
C. Run a batch transcription job on recorded audio files.
D. Use real-time speech to text to process streaming audio input.

**Study mapping:** [Q1 in the coverage map](../../docs/question-coverage.md).

## Q50

You have a Microsoft Foundry project that contains an agent. The agent uses Azure Speech in Foundry
Tools. You fine-tune a baseline speech to text model for the en-us locale and publish the model.
The agent calls the Speech to text REST API and returns an error message indicating that the project ID is
invalid. You need to set the project property to the correct ID.
To what should you set the project property?
A. the project URL
B. the custom speech project ID
C. the project ID
D. the custom speech endpoint URL

**Study mapping:** [Q50 in the coverage map](../../docs/question-coverage.md).

## Q57

You have an application named App1 that uses Azure Speech in Foundry Tools to transcribe live calls.
Transcript segments often contain both English and Spanish.
App1 sends each segment to Azure Translator in Foundry Tools to translate to another language.
Sometimes, mixed-language segments result in incomplete or incorrect translations.
You need to reduce translation errors. The solution must ensure that the entire transcript is translated
successfully.
What should you do before sending the segments to Translator?
A. Use document translation to translate the entire transcript as a single document.
B. Split the mixed-language segments into single-language segments and translate each segment
separately.
C. Enable automatic language detection for the translation request.
D. Specify English as the source language in the translation request for all the segments.

**Study mapping:** [Q57 in the coverage map](../../docs/question-coverage.md).

## Q61

You have an Azure Speech in Foundry Tools resource that hosts a custom speech to text model
deployed to a custom endpoint. An agent uses the endpoint to perform real-time speech recognition.
You are approaching the expiration date of the custom speech to text model.
What is the expected behavior when the model expires?
A. Speech recognition requests will return a 4xx error until a new custom model is deployed.
B. Speech recognition requests will continue to use the expired custom model until the model is removed
manually.
C. Speech recognition requests will fall back to the most recent base model for the same locale.
D. The custom model will be deleted automatically when the model expires.

**Study mapping:** [Q61 in the coverage map](../../docs/question-coverage.md).

## Q91

You are creating an agent workflow in a Microsoft Foundry project to support natural voice interactions.
The agent must receive continuous audio input, convert the input into text for reasoning, and then return
spoken responses to a user.
The workflow must meet the following requirements:
• Support turn-taking dynamics, where the agent begins to generate the speech output before the user
finishes speaking.
• Operate with low latency to maintain conversational experience.
You need to enable both speech to text and text to speech in a real-time agent interaction.
What should you do?
A. Use batch transcription to convert the audio input and return text responses from the agent.
B. Use real-time speech to text for incoming audio and text to speech for agent responses.
C. Use an embeddings model to encode the audio, and then decode the audio into text and speech.
D. Use speech translation to convert the audio into another language and return the translated text.

**Study mapping:** [Q91 in the coverage map](../../docs/question-coverage.md).

## Q127

You have a Python application that redacts sensitive information before sending prompt text to a
language model. The application has the following code:
For each of the following statements, select Yes if the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q127 in the coverage map](../../docs/question-coverage.md).

## Q128

You are building a customer support web app named App1 in Microsoft Foundry that uses a GPT
realtime model.
App1 must support:
• Live, low-latency voice conversations that use Azure OpenAI
• Streaming audio input from users and playback audio responses
You need to configure a connection method that supports real-time audio streaming in client application and
targets approximately 100 ms latency.
Which connection method should you use?
A. RTMP
B. WebRTC
C. SIP
D. WebSocket

**Study mapping:** [Q128 in the coverage map](../../docs/question-coverage.md).

## Q137

You have a custom named entity recognition (NER) project in Azure Language in Foundry Tools for
support tickets. The schema for the project contains an entity type named ContactInfo.
In tagged training files, ContactInfo is used for phone numbers, email addresses, and social media handles.
Model evaluation shows low precision for ContactInfo, including false positives in which nearby text is
extracted as ContactInfo.
You need to improve the precision of the project.
What should you do before retraining the model?
A. Lower the confidence threshold for ContactInfo.
B. Trigger an auto-labeling job.
C. Add more support tickets as training data and label more ContactInfo entities.
D. Replace ContactInfo by using Phone, Email, and SocialMedia entities. Relabel every matching span.

**Study mapping:** [Q137 in the coverage map](../../docs/question-coverage.md).

## Q138

You are building a text-to-speech solution that uses Azure Speech in Foundry Tools to read
instructions from the script in a text file.
You discover that the solution often pronounces technical terms incorrectly.
You need to prevent the incorrect pronunciations. The solution must minimize development effort.
What should you do?
A. From Speech Studio, train a custom neural voice
B. Use Speech Synthesis Markup Language (SSML) to specify phonemes.
C. Use Speech Synthesis Markup Language (SSML) to apply say as rules.
D. Use Speech Synthesis Markup Language (SSML) to adjust the prosody of the voice.
E. From Azure OpenAI use the Whisper model.

**Study mapping:** [Q138 in the coverage map](../../docs/question-coverage.md).

## Q147

You are designing a content management system.
You need to ensure that the reading experience is optimized for users who have reduced comprehension and
learning differences, such as dyslexia. The solution must minimize development effort.
Which Azure service should you include in the solution?
A. Azure Document Intelligence in Foundry Tools
B. Azure Language in Foundry Tools
C. Azure AI Immersive Reader
D. Azure Translator in Foundry Tools

**Study mapping:** [Q147 in the coverage map](../../docs/question-coverage.md).

## Q150

You are developing a text processing solution. You have the following function.
You call the function and use the following string as the second argument. Our tour of London included a
visit to Buckingham Palace
What will be the output of the function?
A. London and Buckingham Palace only
B. Tour and visit only
C. Our tour of London included a visit to Buckingham Palace
D. London and Tour only

**Study mapping:** [Q150 in the coverage map](../../docs/question-coverage.md).

## Q151

You are building a solution that students will use to find references for essays. You use the following
code to start building the solution.
For each of the following statements, select Yes is the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q151 in the coverage map](../../docs/question-coverage.md).

## Q160

You run the following command.
For each of the following statements, select Yes if the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q160 in the coverage map](../../docs/question-coverage.md).

## Q161

You are developing an app that will use the Speech and Language APIs.
You need to provision resources for the app. The solution must ensure that each service is accessed by
using a single endpoint and credential.
Which type of resource should you create?
A. Azure Language in Foundry Tools
B. Microsoft Foundry service
C. Azure Speech in Foundry Tools
D. Content Safety in Foundry Control Plane

**Study mapping:** [Q161 in the coverage map](../../docs/question-coverage.md).

## Q163

You are building an app that will scan confidential documents and use the Azure Language in Foundry
Tools service to analyze the contents.
You provision a Microsoft Foundry Service resource.
You need to ensure that the app can make requests to the Azure Language in Foundry Tools service
endpoint. The solution must ensure that confidential documents remain on-premises.
Which three actions should you perform in sequence?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q163 in the coverage map](../../docs/question-coverage.md).

