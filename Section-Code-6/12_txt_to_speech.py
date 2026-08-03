import azure.cognitiveservices.speech as speechsdk

endpoint="https://foundry-dev-eus-01.cognitiveservices.azure.com/"
api_key=""

speech_config=speechsdk.SpeechConfig(
    subscription=api_key,
    endpoint=endpoint
)

speech_config.speech_synthesis_voice_name="en-US-JennyNeural"

audio_output=speechsdk.audio.AudioOutputConfig(
    filename="cloudxeus_support_message.wav"
)

text = """
Hello, and thank you for contacting CloudXeus Technology Services.
Your support request has been received.
One of our cloud support specialists will review the issue and contact you shortly.
"""

speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_output
)

result=speech_synthesizer.speak_text_async(text).get()

# Check the result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesis completed successfully.")
    print("Audio file saved as cloudxeus_support_message.wav")
