# pip install azure.cognitiveservices.speech
import azure.cognitiveservices.speech as speechsdk
import time

endpoint="https://foundry-dev-eus-01.cognitiveservices.azure.com/"
api_key=""

speech_config=speechsdk.SpeechConfig(
    subscription=api_key,
    endpoint=endpoint
)

audio_config=speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer=speechsdk.SpeechRecognizer(speech_config=speech_config,audio_config=audio_config)

done = False

def stop_cb(evt):
    speech_recognizer.stop_continuous_recognition()
    global done
    done = True

speech_recognizer.recognized.connect(lambda evt: print(evt.result.text))
speech_recognizer.session_stopped.connect(stop_cb)
speech_recognizer.canceled.connect(stop_cb)

speech_recognizer.start_continuous_recognition()
while not done:
    time.sleep(0.5)