from queue import Queue
from classes.ai import LlmManager
from classes.conversation import ConversationManager

if __name__ == "__main__":
    # Set up the queue that connects voice input/output and conversation flow
    speech_queue = Queue()

    # Instantiate the LLM and Conversation manager
    llm_manager = LlmManager()
    conversation_manager = ConversationManager(
        queue=speech_queue,
        llm_manager=llm_manager
    )

    # Start the threaded conversation loop
    conversation_manager.start()

