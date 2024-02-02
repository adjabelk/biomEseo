import speech_recognition as sr
import os
import threading

from Levenshtein import distance

LANGUAGE_CODES = ["en-US", "fr-FR", "de-DE"]

class VoiceProcessing:
    def __init__(self, enrollment_path):
        self.enrollment_path = enrollment_path
        self.recognizer = sr.Recognizer()

    # def voice_enrollment(self, filename, language_code):
    #     # Capture voice input in selected language
    #     with sr.Microphone() as source:
    #         self.recognizer.adjust_for_ambient_noise(source)
    #         print("Speak now in {} language:".format(language_code))
    #         audio = self.recognizer.listen(source)

    #     try:
    #         # Save audio to given path
    #         with open(os.path.join(self.enrollment_path, filename + "_" + language_code + ".wav"), "wb") as f:
    #             f.write(audio.get_wav_data())
    #             print("Voice enrollment successful for {} in {} language.".format(filename, language_code))
    #             recognized_text = self.recognizer.recognize_google(audio, language=language_code)
    #             print("Recognized text in {} language: {}".format(language_code, recognized_text))
    #     except sr.UnknownValueError:
    #         print("Google Speech Recognition could not understand audio.")
    #     except sr.RequestError as e:
    #         print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def enroll_voice(self, filename, language_code):
        while True:
            # Capture voice input in selected language
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Speak now in {} language:".format(language_code))
                audio = self.recognizer.listen(source)

            try:
                # Save audio to given path
                with open(os.path.join(self.enrollment_path, filename + "_" + language_code + ".wav"), "wb") as f:
                    f.write(audio.get_wav_data())
                    print("Voice enrollment successful for {} in {} language.".format(filename, language_code))

                # Transcribe audio data and print the recognized text
                recognized_text = self.recognizer.recognize_google(audio, language=language_code)
                print("You said:", recognized_text)

                # Prompt user for confirmation
                confirmation = input("Is this what you said? (y/n): ")

                if confirmation.lower() == "y":
                    print("Voice enrollment completed successfully.")
                    break
                else:
                    continue
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def voice_recognition(self):
        while True:
            # Capture voice input from the user
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Speak now:")
                audio = self.recognizer.listen(source)

            # Get the language of the captured audio
            audio_file = sr.AudioFile(audio)
            language = audio_file.get_language()

            # If the language is supported, proceed with recognition
            if language in LANGUAGE_CODES:
                # Try to recognize captured audio using Google Speech Recognition
                try:
                    recognized_text = self.recognizer.recognize_google(audio, language=language)
                    print("Recognized text in {} language: {}".format(language, recognized_text))

                    # Calculate similarity score using Levenshtein distance
                    similarity_score = distance(recognized_text, "welcome to my page")
                    if similarity_score <= 3:
                        print("Voice recognized as iofile")
                        return
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

            # If no match found, indicate that the voice is not recognized
            print("Voice not recognized.")


# # Example usage:
voice_processor = VoiceProcessing(enrollment_path=r"C:\Users\HP\OneDrive - ESEO\Bureau\Data Processing Project\biometries_data\voices")
voice_processor.enroll_voice("test", "en-EN")  # Call this to enroll voices
# # voice_processor.voice_recognition()  # Call this to recognize voices

