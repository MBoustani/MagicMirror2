import os
import cv2
import pickle
import numpy as np

import face_recognition
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont

import speak


def get_last_user_id(face_name_hash_table):
    '''
    Function to get the last user id.
    '''
    return max(user['user_id'] for user in face_name_hash_table) if face_name_hash_table else 0


def recognize_speech_from_mic(recognizer, microphone):
    '''
    Function to detect voice and convert it to string.
    '''
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("recognizer must be Recognizer instance")
    if not isinstance(microphone, sr.Microphone):
        raise TypeError("microphone must be Microphone instance")
    if not isinstance(microphone, sr.Microphone):
        raise TypeError("microphone must be Microphone instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        speak.say("Can you spell your name please?")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("time passed")
            audio = None

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        if audio:
            response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"
    
    return response


def get_user_name(recognizer, microphone):
    '''
    Function to get user name.
    '''
    response = recognize_speech_from_mic(recognizer, microphone)
    if response["transcription"] and "cancel" in response["transcription"].lower():
        return None
    if response["transcription"] and "reset" in response["transcription"].lower():
        response = recognize_speech_from_mic(recognizer, microphone)
    return response["transcription"]


def detect_face():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # list of users:
    # schema as follow: {"user_id":0, "user_name": "mazi", "user_face_encoding": [.....]}
    face_name_hash_table = []
 
    if os.path.exists('faces_and_names.pickle'):
        with open('faces_and_names.pickle', 'rb') as handle:
            face_name_hash_table = pickle.load(handle)

    # Initialize some variables
    
    known_face_encodings = [user['user_face_encoding'] for user in face_name_hash_table]
    known_face_names = [user['user_name'] for user in face_name_hash_table]
    known_user_ids = [user['user_id'] for user in face_name_hash_table]
    face_encodings = []
    face_names = []
    process_this_frame = True

    # live face recognition
    video_capture = cv2.VideoCapture(0)

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find all the faces and face encodings in the current frame of video
            face_encodings = face_recognition.face_encodings(rgb_small_frame)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "unknown_person_face"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if face_distances.any():
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                # If face detected but the person face is not in database ask user the name and save it.
                if name == "unknown_person_face":
                    speak.say("Unknown face")
                    user_name = get_user_name(recognizer, microphone)
                    if user_name:
                        known_face_encodings.append(face_encoding)
                        known_face_names.append(user_name)
                        last_user_id = get_last_user_id(face_name_hash_table)
                        face_name_hash_table.append({"user_id": last_user_id+1, "user_name": user_name, "user_face_encoding": face_encoding})
                        with open('faces_and_names.pickle', 'wb') as handle:
                            pickle.dump(face_name_hash_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    print(name)


        # Display the resulting image
        cv2.imshow('Video', frame)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        process_this_frame = not process_this_frame

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()