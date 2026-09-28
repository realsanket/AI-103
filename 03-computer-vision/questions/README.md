# Domain 3 question review

## Per-question lesson map

| Question | Lesson file(s) | Coverage note | Status |
|---:|---|---|---|
| Q11 | [`01_image_edit_fidelity_preflight.py`](01_image_edit_fidelity_preflight.py) | `questions/01_image_edit_fidelity_preflight.py` | New |
| Q20 | [`01_image_edit_fidelity_preflight.py`](01_image_edit_fidelity_preflight.py) | `questions/01_image_edit_fidelity_preflight.py` | New current image-edit equivalent |
| Q27 | [`06_image_masked_edit.py`](../06_image_masked_edit.py) | L06 mask-bounded editing | Existing |
| Q30 | [`06_image_masked_edit.py`](../06_image_masked_edit.py) | L06 sky replacement with a mask | Existing |
| Q32 | [`03_image_moderation.py`](../03_image_moderation.py) | L03 image moderation | Existing |
| Q37 | [`10_prompt_shields_user.py`](../../01-plan-and-manage/10_prompt_shields_user.py), [`11_prompt_shields_docs.py`](../../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../11_ocr_image_injection_safety.py) | D1 L10 user-prompt shields (No) versus L11 document shields, D3 L11 OCR | Existing |
| Q38 | [`11_prompt_shields_docs.py`](../../01-plan-and-manage/11_prompt_shields_docs.py), [`03_image_moderation.py`](../03_image_moderation.py), [`11_ocr_image_injection_safety.py`](../11_ocr_image_injection_safety.py) | D3 L03 image moderation (No) versus D1 L11 document shields, D3 L11 OCR | Existing |
| Q39 | [`11_prompt_shields_docs.py`](../../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../11_ocr_image_injection_safety.py) | L11 OCR injection plus D1 L11–12 | Existing |
| Q54 | [`06_image_masked_edit.py`](../06_image_masked_edit.py) | L06 remove a logo with a mask | Existing |
| Q60 | [`01_image_edit_fidelity_preflight.py`](01_image_edit_fidelity_preflight.py), [`05_image_prompt_edit.py`](../05_image_prompt_edit.py) | `questions/01_image_edit_fidelity_preflight.py` plus L05 source-image edit | Existing |
| Q72 | [`11_prompt_shields_docs.py`](../../01-plan-and-manage/11_prompt_shields_docs.py), [`11_ocr_image_injection_safety.py`](../11_ocr_image_injection_safety.py) | L11 OCR content is indirect injection | Existing |
| Q95 | [`06_image_masked_edit.py`](../06_image_masked_edit.py) | L06 selective object removal | Existing |
| Q105 | [`17_cu_custom_video_analyzer.py`](../17_cu_custom_video_analyzer.py), [`14_video_analysis.py`](../14_video_analysis.py) | L17 video field `colorScheme`: `string` + `generate` per segment; L14 prebuilt video segments | Existing |
| Q117 | Adjacent only: [`01_multimodal_understanding.py`](../01_multimodal_understanding.py) | L01 visual understanding | Compatibility: legacy Vision Brands result shape |
| Q124 | Adjacent only: [`09_video_remix.py`](../09_video_remix.py) | L09 video remix | Gap: video inpainting |
| Q126 | [`01_multimodal_understanding.py`](../01_multimodal_understanding.py) | L01 multimodal content input | Existing |
| Q135 | — | Custom Vision defect classifier | Compatibility: legacy Custom Vision |
| Q136 | [`16_image_model_deployment.py`](../16_image_model_deployment.py) | L16 deploys `gpt-image-2` with the Azure CLI (DALL-E 3 retired March 4, 2026) | Existing |
| Q143 | — | Custom Vision precision/recall | Compatibility: legacy Custom Vision |
| Q148 | — | Custom Vision classifier configuration | Compatibility: legacy Custom Vision |
| Q159 | — | Custom Vision defect detector | Compatibility: legacy Custom Vision |
| Q164 | — | Vision `imageType` API | Compatibility: legacy Vision API |
| Q165 | — | Custom Vision metrics | Compatibility: legacy Custom Vision |
| Q173 | [`07_video_generation.py`](../07_video_generation.py) | L07 `videos.create` → `videos.retrieve` → `download_content` | Existing |

Legacy Vision and Custom Vision questions are retained as compatibility review, not new labs. See [`../../docs/question-coverage.md`](../../docs/question-coverage.md#03---computer-vision).
