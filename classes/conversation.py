import json
import time
import pyttsx3
import threading
import speech_recognition as sr

class ConversationManager:
    def __init__(self, queue, llm_manager):
        self.stop_listening = False
        self.speech_queue = queue
        self.llm_manager = llm_manager
        self.energy_threshold = 50
        self.user_name = ""
        self.input_mode = "text"  # default is text
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def start(self):
        self.user_name = input("👋 Hey there! What's your name? ").strip().capitalize()
        self._ask_input_mode()

        print(f"\n🎙️ Hi {self.user_name}! I'm Fawaaz, your Cape Town tour guide.")
        print("Type `!switch` anytime to change between voice and text modes.")

        if self.input_mode == "voice":
            self._continuous_listen()
        else:
            threading.Thread(target=self._process_speech, daemon=True).start()

        try:
            while not self.stop_listening:
                if self.input_mode == "text":
                    user_input = input(f"\n💬 {self.user_name}, ask me something about Cape Town: ")
                    if user_input.lower() == "!switch":
                        self._ask_input_mode()
                        continue
                    self.process_input(user_input)
                else:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔄 Shutting down...")
            self.stop_listening = True
            print("✅ Application exited cleanly.")

    def _ask_input_mode(self):
        while True:
            mode = input("🤖 Would you like to use voice or text input? (v/t): ").lower().strip()
            if mode in ["v", "voice"]:
                self.input_mode = "voice"
                print("🎤 Voice mode enabled.")
                self._continuous_listen()
                break
            elif mode in ["t", "text"]:
                self.input_mode = "text"
                print("💬 Text mode enabled.")
                break
            else:
                print("❌ Invalid choice. Please enter 'v' or 't'.")

    def _continuous_listen(self):
        def listen_loop():
            print("\n🎧 Preparing mic for continuous listening...")

            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=5)
                print("🎤 Calibrating microphone for ambient noise...")
                print(f"\t--> Initial energy threshold: {self.recognizer.energy_threshold}\n")

                while not self.stop_listening and self.input_mode == "voice":
                    print("🎤 Listening...")
                    try:
                        audio = self.recognizer.listen(source, timeout=60, phrase_time_limit=90)
                        transcript = self.recognizer.recognize_google(audio)
                        print(f"\t--> 🗣️ You said: \"{transcript}\"")
                        self.speech_queue.put(transcript)
                    except Exception:
                        continue

        threading.Thread(target=listen_loop, daemon=True).start()
        threading.Thread(target=self._process_speech, daemon=True).start()

    def process_input(self, input_text):
        command = input_text.strip().lower()

        if command in ["!switch", "switch"]:
            self._ask_input_mode()
            return
        elif command in ["!exit", "exit"]:
            self.stop_listening = True
            print("👋 Exiting... Safe travels!")
            return

        # Otherwise, treat it as a regular user query
        response = self.llm_manager.process_user_input(input_text)
        print(f"\n🤖 Fawaaz: {response}")

        if self.input_mode == "voice":
            self._speak_response(response)

        self._save_state({"user_input": input_text, "response": response})



    def _process_speech(self):
        while not self.stop_listening:
            try:
                transcript = self.speech_queue.get(timeout=1)
                if transcript.strip().lower() == "!switch":
                    self._ask_input_mode()
                    continue

                response = self.llm_manager.process_user_input(transcript)
                print(f"\n🤖 Fawaaz: {response}")
                self._speak_response(response)
                self._save_state({"user_input": transcript, "response": response})

            except Exception:
                continue

    def _speak_response(self, response):
        if self.input_mode != "voice":
            return  # only speak in voice mode

        def speech_thread():
            try:
                engine = pyttsx3.init()
                engine.say(response)
                engine.runAndWait()
            except Exception as e:
                print(f"❌ Error playing speech: {e}")

        threading.Thread(target=speech_thread, daemon=True).start()

    def _save_state(self, state):
        with open("response.json", "w") as f:
            json.dump(state, f, indent=4)
