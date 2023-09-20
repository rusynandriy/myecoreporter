import src.utils.utils as utils
from datetime import datetime as dt, timedelta
import os
import openai
from tenacity import retry, stop_after_attempt, wait_none
# OpenAI setup
openai.api_key = (utils.open_file('secret/keys/openaiapikey.txt') or os.environ['openaiapikey'])
settings = {"engine":None, "temp":0.5, "top_p":1.0, "tokens":600, "freq_pen":0, "pres_pen":0, "stop":[], "model":None}

# OpenAI helper
# @retry(wait=wait_none(), stop=stop_after_attempt(3))
def chatgpt_completion(chat_log, prompt_filename, bot_name):
    # prompt = prompt.encode(encoding='ASCII',errors='ignore').decode() # this line can help prevent an entire class of rare unicode bugs, but it strips out any emojis so we aren't using it for now.
    system_prompt = utils.open_file(prompt_filename)
    system_prompt = system_prompt.replace("<<BOT_NAME>>", bot_name)
    messages = []
    system_message = {"role": "system", "content": system_prompt}
    messages.append(system_message)
    for message in chat_log:
        sender, content = message.split(": ", 1)
        if bot_name in sender:
            messages.append({"role": "assistant", "content": content})
        else:
            messages.append({"role": "user", "content": content})

    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=settings["temp"],
        top_p=settings["top_p"],
        frequency_penalty=settings["freq_pen"],
        presence_penalty=settings["pres_pen"],
        max_tokens=settings["tokens"]
        )
    except openai.error.InvalidRequestError as e:
        print("ERROR: " + str(e))
        return {"choices": [{"text": "Sorry, looks like our ongoing conversation got too long. Try sending 'reset' to restart the conversation."}]}

    return response['choices'][0]['message']['content']

# original prompt template logic (before migration from GPT-3's "Completion" endpoint to GPT-3.5-Turbo's "ChatCompletion" endpoint. Loads in a template, replaces some placeholders, and returns a "final prompt".
def build_myej_prompt(conversation, user):
    # load in starter prompt
    prompt = utils.open_file('assets/prompts/myejstarterprompt.txt')
    
    # add in date and weekday:
    today = dt.today()
    
    prompt = prompt.replace('<<TODAY>>', today.strftime("%m/%d/%y"))
    prompt = prompt.replace('<<TODAY-weekday>>', today.strftime("%A"))


    # add transcript so far
    text_block = '\n'.join(conversation.chat)
    prompt = prompt.replace('<<CONVERSATION>>', text_block) 
    
    # add bot name
    prompt = prompt + f'\nMyEcoReporter:'

    return prompt
