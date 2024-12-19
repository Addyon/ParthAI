import requests
import json
import speech_recognition as sr
import pyttsx3
import time
import tkinter as tk
from PIL import Image, ImageTk
import threading

class APIFetcher:
    def __init__(self, api_key, api_url, model=None):   
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Initialize pyttsx3 engine for TTS
        self.tts_engine = pyttsx3.init()

    def construct_request_data(self, messages, model=None):
        """Construct the data to be sent with the POST request."""
        if not model:
            model = self.model
        return json.dumps({"messages": messages, "model": model})

    def fetch(self, messages, model=None):
        """Make a POST request to the API endpoint."""
        data = self.construct_request_data(messages, model)
        response = requests.post(self.api_url, headers=self.headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None

    def text_to_speech(self, text):
        """Convert text to speech."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen_to_voice(self):
        """Listen to user voice and convert it to text."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for command...")
            audio = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            voice_text = recognizer.recognize_google(audio)
            print(f"Recognized: {voice_text}")
            return voice_text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

    def listen_for_wake_word(self, wake_word="hello parth"):
        """Continuously listen for the wake word to activate the assistant."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(f"Say '{wake_word}' to activate the assistant.")
            recognizer.adjust_for_ambient_noise(source)  # To handle background noise

            while True:
                try:
                    audio = recognizer.listen(source)
                    detected_speech = recognizer.recognize_google(audio)
                    print(f"Detected: {detected_speech}")

                    if wake_word.lower() in detected_speech.lower():
                        print(f"Wake word '{wake_word}' detected.")
                        self.text_to_speech("Good Morning Sir, How can I help you?")
                        return True  # Wake word detected, assistant is activated
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized audio
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                time.sleep(0.5)  # Slight delay before listening again

# Example usage for Groq with voice input/output and wake word
if __name__ == "__main__":
    groq_api_key = "Your_Groq_Api_here"
    groq_api_url = "Groq_API_url_here"
    model = "llama3-8b-8192"  # select your own AI model

    fetcher = APIFetcher(groq_api_key, groq_api_url, model)

    # Create a GUI window
    window = tk.Tk()
    window.title("AI Assistant")

    # Load a GIF to represent the AI
    image = Image.open("ai.gif")
    image.format = "GIF"
    gif_image = ImageTk.PhotoImage(image)
    gif_label = tk.Label(window, image=gif_image)
    gif_label.pack()

    # Continuously listen for the wake word to activate the assistant
    def listen_for_wake_word():
        if fetcher.listen_for_wake_word():
            # After activation, listen to the user's command
            user_voice_input = fetcher.listen_to_voice()

            if user_voice_input:
                # Prepare messages for the API
                messages = [{"role": "user", "content": user_voice_input}]
                
                # Fetch response from the API
                result = fetcher.fetch(messages)

                if result:
                    # Get the AI's response
                    ai_response = result["choices"][0]["message"]["content"]
                    print(f"AI Response: {'ai _response'}")

                    # Convert AI response to speech
                    fetcher.text_to_speech(ai_response)

    # Start listening for the wake word in a separate thread
    thread = threading.Thread(target=listen_for_wake_word)
    thread.start()

    # Start the GUI event loop
    window.mainloop()
