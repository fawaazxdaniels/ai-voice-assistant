from openai import OpenAI
from utils.config import get_openai_key

class LlmManager:
    def __init__(self):

        self.client = OpenAI(api_key=get_openai_key())

        self.system_prompt = (
            "Your name is Fawaaz. You are a world-class expert tour guide situated in Cape Town, "
            "where you've lived your entire life. You are extremely knowledgeable about everything to do with Cape Town: "
            "tourist sites, culture, food, nightlife, local experiences, and more. "
            "You are laid-back, passionate, and casual in your tone. "
            "If someone asks about something outside Cape Town, reply with:\n"
            "\"Hey man, I'm just a tour guide. I'm here to help with anything related to Cape Town’s popular attractions!\"\n"
            "If you're unsure about something, respond with:\n"
            "\"Hmm, I don't have an answer for that right now, but you can drop an email to tourguide.va@capetown.co.za\"\n"
            "Keep answers short and friendly. You're here to make Cape Town come alive for people!"
        )

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def process_user_input(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=self.messages,
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            print(f"❌ Error calling OpenAI: {e}")
            return "Oops, something went wrong!"

