
import speech_recognition as sr

wake_up_word = "mazi"

DEVICE_INDEX = 1

microphone = sr.Microphone()
recognizer = sr.Recognizer()


def take_command(phrase_time_limit, wake_up=False):
    while True:
        print('listening .....')
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, phrase_time_limit=phrase_time_limit,timeout=8)

        try:
            # Use the speech recognition library to convert the voice input to text
            voice_input = recognizer.recognize_google(audio)
            print(f"Voice input: {voice_input}")
            if wake_up:
                # Check if the wake-up word is in the voice input
                if wake_up_word in voice_input.lower():
                    print("Wake-up word detected!")
                    return "wake_up_call"
            return voice_input

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")



    # with sr.Microphone(device_index=device_index) as source:
    #     query = ""
    #     try:
    #         audio = recognizer.listen(source, phrase_time_limit=phrase_time_limit,timeout=8)
    #         query = recognizer.recognize_google(audio, language="en-US")
    #     except:
    #         pass
    # return query.lower()