import src.utils.utils as utils
from datetime import datetime as dt, timedelta
import os
import openai
from tenacity import retry, stop_after_attempt, wait_none
# OpenAI setup
openai.api_key = (utils.open_file('secret/keys/openaiapikey.txt') or os.environ['openaiapikey'])
settings = {"engine":None, "temp":0.5, "top_p":1.0, "tokens":600, "freq_pen":0, "pres_pen":0, "stop":[], "model":None}


def get_final_response(prompt):
    response = gpt3_completion(prompt, settings)
    text = response['choices'][0]['text'].strip()
    if text == "":
        response = gpt3_completion(prompt, settings)
        text = response['choices'][0]['text'].strip()
        return ""
    # simple double retry if we get an "unsafe" response
    if classify_safety(text) == "safe":
        return text
    else:
        response = gpt3_completion(prompt, settings)
        if classify_safety(text) == "safe":
            text = response['choices'][0]['text'].strip()
            return text
        else:
            return "UNSAFE"
    
# wrapper that tries to get a response + handles retrying if it's blank or unsafe
def get_response(prompt, user, bot_name):
    settings["engine"] = "gpt-3.5-turbo"
    add_stop_to_settings(user, bot_name)
    return get_final_response(prompt)

def add_stop_to_settings(user, bot_name):
    settings["stop"] = [f'{bot_name}:', "("]
    settings["stop"].append(f"{user.username}:")
    settings["stop"].append("\nConversation")


def get_datetime(input_value):
    print("getting datetime from GPT3")
    print("input value is: ", input_value)
    day_of_week = dt.today().strftime("%A")
    date = dt.today().strftime("%B %d, %Y")
    prompt = f"""The current date is {day_of_week} {date}.
I'm talking about {input_value}. What date is that in MM/DD/YYYY format?"""
    messages = []
    messages.append({'role': 'user', 'content': prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    returned_value = response['choices'][0]['message']['content']
    print("gpt got this date:", returned_value)
    return returned_value


# OpenAI helper
# @retry(wait=wait_none(), stop=stop_after_attempt(3))
def gpt3_completion(chat_log, prompt_filename, bot_name):
    # prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
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

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=settings["temp"],
        top_p=settings["top_p"],
        frequency_penalty=settings["freq_pen"],
        presence_penalty=settings["pres_pen"],
        max_tokens=settings["tokens"]
        )

    return response['choices'][0]['message']['content']

# this is a required filter from OpenAI for safety:
# see here: https://beta.openai.com/docs/models/content-filter
def classify_safety(content):
    result = "unsafe" #this is our default. 
    response = openai.ChatCompletion.create(
      model="content-filter-alpha",
      prompt = "<|endoftext|>"+content+"\n--\nLabel:",
      temperature=0,
      max_tokens=1,
      top_p=0,
      logprobs=10
    )
    # 0 - text is safe, 1 - text is sensitive, 2 - text is unsafe
    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    if output_label in ["0", "1"]:
        result = "safe"

    return result 

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
