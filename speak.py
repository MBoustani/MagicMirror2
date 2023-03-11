from gtts import gTTS
import playsound
from io import BytesIO
import pygame

def say(sentence):
    '''
    Function to generate voice from given sentence and play it.
    '''
    pygame.mixer.init(10000, -8, 1, 104)
    #pygame.mixer.init()
    mp3_fp = BytesIO()
    tts = gTTS(text=sentence, lang="en", slow=False)
    tts.write_to_fp(mp3_fp)
    pygame.mixer.music.load(mp3_fp, 'mp3')
    pygame.mixer.music.play()
    #audio.save("tmp.mp3")
    #playsound.playsound("tmp.mp3")
    # try:
    #     os.remove("tmp.mp3")
    # except:
    #     pass