from datetime import datetime
from taipy.gui import Gui, State, notify
import os
from openai import OpenAI
from logging.config import dictConfig
from dotenv import load_dotenv


client = None
context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "
conversation = {
    "Conversation": ["Who are you?", "Hi! I am GPT-3.5. How can I help you today?"]
}
current_user_message = ""
past_conversations = []
selected_conv = None
selected_row = [1]
content = None
json_output = None
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


def on_init(state: State) -> None:
    """
    Initialize the app.

    Args:
        - state: The current state of the app.
    """
    state.context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "
    state.conversation = {
        "Conversation": ["Who are you?", "Hi! I am GPT-3.5. How can I help you today?"]
    }
    state.current_user_message = ""
    state.past_conversations = []
    state.selected_conv = None
    state.selected_row = [1]
    state.client=OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # state.display = "empty-output"


def request(state: State, prompt: str) -> str:
    """
    Stub function to simulate an AI response.

    Args:
        - state: The current state of the app.
        - prompt: The prompt to send to the API.

    Returns:
        A fixed response string.
    """
    try:
        response = state.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            model="gpt-3.5-turbo",
        )
        return response.choices[0].message["content"]
    except Exception as e:
        raise RuntimeError(f"Error while requesting OpenAI API: {e}")


def update_context(state: State) -> str:
    """
    Update the context with the user's message and the AI's response.

    Args:
        - state: The current state of the app.
    """
    state.context += f"Human: \n {state.current_user_message}\n\n AI:"
    answer = request(state, state.context) #replace("\n", " ")
    state.context += answer
    state.selected_row = [len(state.conversation["Conversation"]) + 1]
    return answer


def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the context.

    Args:
        - state: The current state of the app.
    """
    notify(state, "info", "Sending message...")
    answer = update_context(state)
    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message, answer]
    state.current_user_message = ""
    state.conversation = conv
    notify(state, "success", "Response received!")


    # notify(state, "info", "Sending message...")
    # answer = update_context(state)
    # conv = state.conversation._dict.copy()
    # conv["Conversation"] += [state.current_user_message, answer]
    # state.conversation = conv
    # state.current_user_message = ""
    # # print(conv)
    # state.conversation = conv
    # notify(state, "success", "Response received!")


def style_conv(state: State, idx: int, row: int) -> str:
    """
    Apply a style to the conversation table depending on the message's author.

    Args:
        - state: The current state of the app.
        - idx: The index of the message in the table.
        - row: The row of the message in the table.

    Returns:
        The style to apply to the message.
    """
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_message"
    else:
        return "gpt_message"


def on_exception(state, function_name: str, ex: Exception) -> None:
    """
    Catches exceptions and notifies user in Taipy GUI

    Args:
        state (State): Taipy GUI state
        function_name (str): Name of function where exception occured
        ex (Exception): Exception
    """
    notify(state, "error", f"An error occured in {function_name}: {ex}")


# def reset_chat(state: State) -> None:
#     """
#     Reset the chat by clearing the conversation.

#     Args:
#         - state: The current state of the app.
#     """
#     state.past_conversations = state.past_conversations + [
#         [len(state.past_conversations), state.conversation]
#     ]
#     state.conversation = {
#         "Conversation": ["Who are you?", "Hi! I am Automation Automator. What type of automation you want to create?"]
#     }

def new_conv(state: State) -> None:
    """
    Starts new conversation.
    If the conversation is empty, show a message.

    Args:
        - state: The current state of the app.
    """
    if len(state.conversation["Conversation"]) <= 2:  # Check if the conversation is essentially empty
        notify(state, "warning",
               "This is an empty conversation. Please send a message before starting a new conversation.")
    else:
        timestamp = datetime.now().strftime("%H:%M")  # display chat start time
        state.past_conversations = state.past_conversations + [
            [len(state.past_conversations), state.conversation, timestamp]
        ]
    state.conversation = {
        "Conversation": ["Who are you?", "Hi! I am GPT-3.5. How can I help you today?"]
    }


def reset_chat(state: State) -> None:
    """
    Reset the chat by clearing the conversation.

    Args:
        - state: The current state of the app.
    """
    state.conversation = {
        "Conversation": ["Who are you?", "Hi! I am GPT-3.5. How can I help you today?"]
    }
    state.current_user_message = " "


def clear_history(state: State) -> None:
    """
    Clears the chat history.

    Args:
        - state: The current state of the app.
    """
    state.past_conversations = []


def tree_adapter(item: list) -> [str, str]:  # type: ignore
    """
    Converts element of past_conversations to id and displayed string

    Args:
        item: element of past_conversations

    Returns:
        id and displayed string
    """
    identifier = item[0]
    timestamp = item[2]
    if len(item[1]["Conversation"]) > 3:
        return (identifier, f"{timestamp} - {item[1]['Conversation'][2][:50]}...")
    return (identifier, f"{timestamp} - Empty conversation")
    #     return (identifier, item[1]["Conversation"][2][:50] + "...")
    # return (item[0], "Empty conversation")


def select_conv(state: State, var_name: str, value) -> None:
    """
    Selects conversation from past_conversations

    Args:
        state: The current state of the app.
        var_name: "selected_conv"
        value: [[id, conversation]]
    """
    state.conversation = state.past_conversations[value[0][0]][1]
    state.context = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today? "
    for i in range(2, len(state.conversation["Conversation"]), 2):
        state.context += f"Human: \n {state.conversation['Conversation'][i]}\n\n AI:"
        state.context += state.conversation["Conversation"][i + 1]
    state.selected_row = [len(state.conversation["Conversation"]) + 1]


past_prompts = []

page_1 = """
<|layout|columns=300px 1|

<|part|class_name=sidebar|
# Quantum **Oracle**{: .color-primary} # {: .logo-text}
<|New Conversation|button|class_name=fullwidth plain|id=reset_app_button|on_action=new_conv|>
### Previous activities ### {: .h5 .mt2 .mb-half}
<|{selected_conv}|tree|lov={past_conversations}|class_name=past_prompts_list|multiple|adapter=tree_adapter|on_change=select_conv|>
<|Reset|button|on_action=reset_chat|class_name=reset_chat|>
<|Clear History|button|on_action=clear_history|class_name=reset_chat|>
|>

<|part|class_name=p2 align-item-bottom table|
<|{conversation}|table|text|mode=pre|row_class_name=style_conv|show_all|selected={selected_row}|rebuild|>

<|part|class_name=card mt1|
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|change_delay=-1|>
|>
|>
|>


<style>
  body {
    overflow: hidden;
    transform: scale(0.96);
  }

  .gpt_message td {
    margin-left: 30px;
    margin-bottom: 20px;
    margin-top: 20px;
    position: relative;
    display: inline-block;
    padding: 20px;
    background-color: #f7634e;
    border-radius: 20px;
    max-width: 80%;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    font-size: medium;
    color: #ffffff;
    white-space: pre-wrap; /* Ensure line breaks are rendered */
  }

  .user_message td {
    margin-right: 30px;
    margin-bottom: 20px;
    margin-top: 20px;
    position: relative;
    display: inline-block;
    padding: 20px;
    background-color: #140a1e;
    border-radius: 20px;
    max-width: 80%;
    float: right;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    font-size: medium;
    color: #ffffff;
    white-space: pre-wrap; /* Ensure line breaks are rendered */
  }

  .past_prompts_list .MuiPaper-root {
    background-color: var(--color-background);
  }

  .past_prompts_list li + li {
    border-top: 1px solid var(--color-paper);
  }

  .past_prompts_list .MuiTreeItem-content {
    font-style: italic;
    padding: var(--spacing-half);
    user-select: text !important;
    cursor: pointer;
  }

  .past_prompts_list .MuiTreeItem-iconContainer {
    display: none;
  }

  .css-orq8zk {
    position: fixed;
    z-index: 5;
  }

  .css-y23wk4 {
    max-height: 55vh;
  }

  .reset_chat {
    border-width: 1.5px;
    margin-left: 8px;
    font-weight: bold;
  }

  /* Adjust padding to create space on the right side of the input box */
  .MuiInputBase-input {
    padding-right: 40px; 
  }

   /* Spinner container styles */
  .MuiCircularProgress-root {
    position: absolute;
    width: 30px !important; /* Adjust width */
    height: 30px !important; /* Adjust height */
    right: 80px;
    top: -92px;
    color: rgb(255, 96, 73);
  }

</style>
"""

if __name__ == "__main__":
    load_dotenv()
    Gui(page_1).run(debug=True, dark_mode=True, use_reloader=True, title="💬Chatbot", port="auto")