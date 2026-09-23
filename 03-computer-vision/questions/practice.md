# Domain 03 practice questions

These are the question stems and answer choices extracted from the supplied practice PDF for **Computer vision**. Answers and explanations are intentionally excluded so you can attempt each item first. Use the [coverage map](../../docs/question-coverage.md) and this directory's README after answering.

Text-only extraction cannot preserve a drag-and-drop surface, diagram, or code image. Where the source exposes no textual answer choices, that is called out without inventing options.

## Q11

You have a Microsoft Foundry project that contains an agent and an image generation model
deployment. The agent generates original images from user-supplied product photos.
You need to ensure that the generated images maintain the product identity and visual characteristics of the
provided photo.
What should you do?
A. Set the input_fidelity parameter to high.
B. Apply a groundedness detection filter.
C. Include a prompt and input image in the request.
D. Decrease the value of the temperature parameter.

**Study mapping:** [Q11 in the coverage map](../../docs/question-coverage.md).

## Q20

You are creating an image-processing workflow in a Microsoft Foundry project. The workflow must
meet the following requirements:
• Generate multiple alternative versions of an existing product image for marketing campaigns.
• Preserve the overall composition, lighting, and subject.
• Use the built-in image generation capabilities without training a custom model.
You need to configure the workflow to generate several stylistic alternatives from the original image.
How should you configure the workflow?
A. Enable image_variation mode and provide the original image as the input.
B. Enable mask_inpainting and provide a mask that covers the entire image.
C. Enable text_to_image mode and describe the original image in the prompt.
D. Enable image_to_image mode with the strength parameter set to 1.0.

**Study mapping:** [Q20 in the coverage map](../../docs/question-coverage.md).

## Q27

You are creating an image-editing workflow in a Microsoft Foundry project.
The workflow must meet the following requirements:
• Ensure that background objects can be removed by applying a mask-based inpainting edit.
• Preserve the original lighting and style of the edited images.
• Use the built-in image editing controls, NOT a custom model.
You need to ensure that image edits apply exclusively inside the masked area.
How should you configure the workflow?
A. Set generation mode to image_variation and provide the original image as a reference.
B. Enable text_to_image mode and a prompt describing the desired background removal.
C. Enable image_to_image mode and a high-strength value to regenerate the full image based on the
prompt.
D. Enable mask_inpainting and supply both the input image and a mask indicating which part of the image
to modify.

**Study mapping:** [Q27 in the coverage map](../../docs/question-coverage.md).

## Q30

You are developing an image-editing workflow in a Microsoft Foundry project.
The workflow must meet the following requirements:
• Replace the sky in landscape photographs with a sunset.
• Modify only the selected sky region.
• Preserve all foreground objects without regeneration.
• Use the built-in image editing capabilities.
You need to configure the workflow.
How should you configure the workflow?
A. Enable image_variation mode and provide the original image.
B. Enable mask_inpainting and provide the original image together with a mask covering the sky.
C. Enable text_to_image mode and describe the desired landscape.
D. Enable image_to_image mode with a high-strength value.

**Study mapping:** [Q30 in the coverage map](../../docs/question-coverage.md).

## Q32

You are deploying a support agent that enables users to upload photos.
You need to automatically classify uploaded images for harmful content. The solution must block content
based on severity levels.
What should you do?
A. Apply keyword scanning to optical character recognition (OCR) output by using Azure Vision in Foundry
Tools.
B. Enable prompt shields.
C. Use blocklists.
D. Implement image moderation.

**Study mapping:** [Q32 in the coverage map](../../docs/question-coverage.md).

## Q37

You have a multimodal AI generative model that accepts image uploads and uses extracted image text
to generate responses.
You discover that users can upload unsafe images and embed hidden instructions into images to manipulate
the model.
You need to implement controls to mitigate the risk.
Solution: You configure a prompt shield for user prompts.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q37 in the coverage map](../../docs/question-coverage.md).

## Q38

You have a multimodal AI generative model that accepts image uploads and uses extracted image text
to generate responses.
You discover that users can upload unsafe images and embed hidden instructions into images to manipulate
the model.
You need to implement controls to mitigate the risk.
Solution: You configure image moderation to block unsafe content before processing the images.
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q38 in the coverage map](../../docs/question-coverage.md).

## Q39

You have a multimodal AI generative model that accepts image uploads and uses extracted image text
to generate responses.
You discover that users can upload unsafe images and embed hidden instructions into images to manipulate
the model.
You need to implement controls to mitigate the risk.
Solution: You configure a prompt shield for documents. .
Does this meet the goal?
A. Yes
B. No

**Study mapping:** [Q39 in the coverage map](../../docs/question-coverage.md).

## Q54

You have a Microsoft Foundry project that generates product marketing images from text prompts.
After publishing several images, the legal team at your company identifies a competitor’s logo on a sign in
the background of an image.
You need to remove only the logo, while preserving the rest of the image.
What should you do?
A. Apply a mask-based inpainting edit to the part of the image that contains the logo.
B. Increase the prompt guidance strength.
C. Modify the original prompt to exclude brand names.
D. Rerun the prompt by using a different random seed.

**Study mapping:** [Q54 in the coverage map](../../docs/question-coverage.md).

## Q60

You have a Microsoft Foundry project that contains an agent and an image generation model
deployment.
The agent creates lifestyle marketing images for clothing products.
Users provide a photograph of a jacket and request new scenes in different environments.
The solution must ensure that the generated images continue to depict the same jacket while allowing the
background, lighting, and setting to change.
What should you do?
A. Include the original image as a reference image in the generation request.
B. Reduce the max_tokens parameter.
C. Enable groundedness detection.
D. Configure Content Safety to annotate the generated images.

**Study mapping:** [Q60 in the coverage map](../../docs/question-coverage.md).

## Q72

You have an app named App1 that uses a Microsoft Foundry multimodal model deployment.
App1 runs optical character recognition (OCR) on uploaded images and appends the OCR output to the
prompt as additional context.
Some uploaded images contain embedded text.
You need to prevent potentially malicious instructions from being processed by the model.
What should you use?
A. image moderation
B. prompt shields for documents
C. protected material text
D. prompt shields for user prompts

**Study mapping:** [Q72 in the coverage map](../../docs/question-coverage.md).

## Q95

You have a Microsoft Foundry project that generates real estate marketing images from text prompts.
After publishing several images, you discover that one image contains a vehicle parked in the driveway. The
property owner requests that only the vehicle be removed while preserving the house, landscaping, lighting,
and shadows.
You need to update the image.
What should you do?
A. Apply a mask-based inpainting edit to the area containing the vehicle.
B. Regenerate the image by using a lower temperature value.
C. Modify the original prompt to specify an empty driveway and generate a new image.
D. Create an image variation from the original image.

**Study mapping:** [Q95 in the coverage map](../../docs/question-coverage.md).

## Q105

You have a Microsoft Foundry project that uses Azure Content Understanding in Foundry Tools to
analyze marketing videos.
Video segmentation is enabled.
You need to configure an analyzer to output a generated JSON field that describes the color scheme of each
video segment.
How should you configure the analyzer?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q105 in the coverage map](../../docs/question-coverage.md).

## Q117

You develop a test method to verify the results retrieved from a call to the Azure Vision in Foundry
Tools API. The call is used to analyze the existence of company logos in images. The call returns a collection
of brands named brands.
You have the following code segment:
For each of the following statements, select Yes if the statement is true. Otherwise, select No.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q117 in the coverage map](../../docs/question-coverage.md).

## Q124

You have a Microsoft Foundry project that generates short promotional product videos.
After several clips are approved, reviewers notice a small watermark in the top-right corner of some videos.
You need to remove the watermark without regenerating the videos.
What should you do?
A. Modify the original prompt to exclude watermarks.
B. Crop the video by using the size parameter.
C. Increase the guidance scale.
D. Apply a mask-based inpainting edit to the affected part of the video.

**Study mapping:** [Q124 in the coverage map](../../docs/question-coverage.md).

## Q126

You have a web app named App1 that sends requests to a multimodal chat model deployment in a
Microsoft Foundry project.
User messages can contain both text and images.
Currently, App1 includes image URL: as plain text inside the message content so the model cannot recognize
them as images.
Traces show that the requests contain a single text message instead of a multimodal content array.
You need to send the message as a structured array that includes both the text portion and the image
reference to ensure that the model can process the image correctly.
What should you do?
A. Set the user message content array to include items that have type: text and type: image_url.
B. Encode the image to base64 and include the encoded data inside the content string of the user message.
C. Add the image URL to the request metadata section, so the model can resolve the processing issue
automatically.
D. Place the image URL inside the System Message and set type to image_url so the model loads the image
at initialization.

**Study mapping:** [Q126 in the coverage map](../../docs/question-coverage.md).

## Q135

You are developing an application that will detect faulty components produced on a factory production
line. The components are specific to your business.
You need to use the Azure Custom Vision API to help detect common faults.
Which three actions should you perform in sequence?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q135 in the coverage map](../../docs/question-coverage.md).

## Q136

You have an Azure subscription.
You plan to build an app that will use the Azure AI DALL-E model. You need to deploy the model.
What should you use?
A. the Azure SDK for Python and PowerShell cmdlets.
B. the Azure SDK for JavaScript and Azure Machine Learning Studio.
C. Microsoft Foundry and the Azure Command Line Interface (CLI)
D. the Azure portal and Microsoft Graph API

**Study mapping:** [Q136 in the coverage map](../../docs/question-coverage.md).

## Q143

You are building a model to detect objects in images.
The performance of the model based on training data is shown in the following exhibit.
Use the drop-down menus to select the answer choice that completes each statement based on the
information presented in the graphic.

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q143 in the coverage map](../../docs/question-coverage.md).

## Q148

You are building a custom vision model that will be deployed as part of an iOS app. You have images
of cats and dogs. Each image contains either a cat or a dog.
You need to use the Azure Custom Vision service to detect whether the image is of a cat or a dog.
How should you configure the project in the Azure Custom Vision portal?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q148 in the coverage map](../../docs/question-coverage.md).

## Q159

You are designing an Azure AI solution to identify defective products on a production line.
You have a real-time video feed and an image library of sample products that are approved or rejected
manually. You need to recommend a service that meets the following requirements:
• Monitors the video feed and identifies the defective products.
• Can train a new model by using the image library.
• Minimizes development effort.
What should you recommend?
A. Azure Vision in Foundry Tools
B. Azure AI Video Indexer
C. Azure AI Custom Vision
D. Azure Machine Learning

**Study mapping:** [Q159 in the coverage map](../../docs/question-coverage.md).

## Q164

You are developing an app that will use the Azure Vision in Foundry Tools API to analyze an image.
You need configure the request that will be used by the app to identify whether an image is clipart or a line
drawing.
How should you complete the request?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q164 in the coverage map](../../docs/question-coverage.md).

## Q165

You use the Azure Custom Vision service to build a classifier. After training is complete, you need to
evaluate the classifier.
Which two metrics are available for review?
A. F-score
B. area under the curve (AUC)
C. precision
D. weighted accuracy
E. recall

**Study mapping:** [Q165 in the coverage map](../../docs/question-coverage.md).

## Q173

You need to ensure that the marketing department can generate videos by using the model
deployed to Project2.
How should you complete the Python code?

> The answer interface or exhibit is visual in the source PDF; review the original PDF page before answering.

**Study mapping:** [Q173 in the coverage map](../../docs/question-coverage.md).

