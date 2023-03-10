import os

from pocketsphinx import LiveSpeech, get_model_path

import speech_recognition as sr


for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(i, name)

DEVICE_INDEX = 0

microphone = sr.Microphone(device_index=DEVICE_INDEX)
recognizer = sr.Recognizer()


def wake_up_call(wake_up=False, timeout=5):
    while True:
        # set up the pocketsphinx decoder
        model_path = get_model_path()
        speech = LiveSpeech(
            verbose=False,
            sampling_rate=16000,
            buffer_size=248,
            no_search=False,
            full_utt=False
        )

        print("Listening...")

        # listen for the wake-up phrase
        for phrase in speech:
            text = str(phrase).lower()
            print("Detected phrase:", text)
            
            # check if the wake-up phrase is present in the detected text
            if "okay" in text:
                return "wake_up_call"
            # exit the loop if timeout is reached
            if phrase.segments(detailed=True)[-1][2] >= timeout:
                print("Timeout reached. Exiting...")
                break

def take_command(wake_up=False):
    while True:
        print('listening .....')
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source,timeout=8)
        try:
            
            # Use the speech recognition library to convert the voice input to text
            voice_input = recognizer.recognize_google(audio)
            print(f"Voice input: {voice_input}")
            return voice_input

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

