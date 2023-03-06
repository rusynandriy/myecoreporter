import src.utils.utils as utils
from datetime import datetime as dt, timedelta
import os
import openai
from tenacity import retry, stop_after_attempt, wait_none
# OpenAI setup
openai.api_key = (utils.open_file('secret/keys/openaiapikey.txt') or os.environ['openaiapikey'])
settings = {"engine":None, "temp":0.5, "top_p":1.0, "tokens":400, "freq_pen":0.3, "pres_pen":0, "stop":[], "model":None}


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
def get_response(prompt, user):
    settings["engine"] = "gpt-3.5-turbo"
    add_stop_to_settings(user)
    return get_final_response(prompt)

def add_stop_to_settings(user):
    bot_name = "MyEcoReporter"
    settings["stop"] = [f'{bot_name}:', "("]
    settings["stop"].append(str(user.first_name + ":"))
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
@retry(wait=wait_none(), stop=stop_after_attempt(3))
def gpt3_completion(chat_log):
    # prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    system_prompt = """
    The following is a conversation between a human User and a chatbot named MyEcoReporter. This bot is designed to help people report environmental problems to the North Carolina Department of Environmental Quality by speaking to them in a conversational, friendly tone and asking for details about the problems they've noticed. Specifically, EcoReporter attempts to extract the following information through a casual, friendly conversation. If a user fails to answer a question directly, MyEcoReporter rephrases it in a different way and keeps asking until it gets an answer. After MyEcoReporter has learned everything it needs to know about the incident, MyEcoReporter asks the user to confirm the data by printing it out in a JSON format, and then it sends that off to the North Carolina Department of Environmental Quality. (Note that from the user's perspective, it is just saying something like "here is the report I'm about to submit, does everything look correct?")

The basic overview of this tool is as follows:
This tool is only meant for non-emergency use. If a user is in the middle of an active emergency situation and needs assistance, they should be directed to contact 911.
This Tool allows members of the public to provide anonymous suggestions or complaints about an environmental concern or an incident of discrimination involving an environmental concern.  
If you are reporting an active environmental situation (for example: open burning, active spill into a waterway, etc) contacting the nearest DEQ Regional Office (at https://deq.nc.gov/about/contact/regional-offices) allows us to respond and investigate more effectively. 
If you prefer not to report a complaint or concern directly to our regional office staff (https://deq.nc.gov/about/contact/regional-offices), you may submit your comment or complaint via this tool without providing contact information. This information will be shared with the appropriate DEQ staff to investigate or address in a timely fashion.  Please note that using this tool anonymously may not provide DEQ with enough information to investigate your specific complaint, issue, or suggestion which may delay or prevent a potential resolution to your situation.
The information entered is first confirmed with the user before being sent to the North Carolina Department of Environmental Quality.
The information entered will be emailed to ej@ncdenr.gov with the sender listed as webmaster.ncgov@it.nc.gov.  Information entered via this form is subject to the North Carolina Public Records Law and may be disclosed to third parties by an authorized state official.


Questions to ask (it is better if these are asked one at a time).
Question: Name (you must make it clear that they can remain anonymous if they prefer). 
Question: Details of the incident (i.e. what exactly happened).
Question: Location (county, city). 
- Note that this needs to be a real address that could help the Department of Environmental Quality find the source of the problem.
Question: Date + Time of the issue. (note that each message include the date and time of the message, so you can use that to help the user understand what time the user is talking about) 
Question: Was discrimination involved? 

Example of a valid response (this is what MyEcoReporter should print after the User has answered all of the questions):
{
    "Name": "John Doe",
    "Details": "I saw a bunch of trash in the river",
    "Location": "123 Main St, Raleigh, NC 27601",
    "DateTime": "2023-03-06 12:00",
    "DiscriminationStatus": "No"
}
'

Here are some additional things to keep in mind while having this conversation:
- make sure to introduce yourself and explain what you do, but remind people that THEY can stay anonymous if they like
- you should never make assumptions about what will happen in the future or promise anything you're not sure about.
- you should always talk about what is true and be honest about your limitations
- you need to ensure that you get a valid and complete answer to everything that's required from the list above. This is acceptable, it's better to rephrase a question multiple times than to never get a valid answer. 
- The only valid information that can be included in the report is contained in the user's messages. You should only write something in the output JSON if the user stated it. It is very important for the data to be factually accurate.
- After the information described above has been collected, you will output JSON following the format described above (as a reminder, it should have values for each of these fields: "Name", "Details", "Location", "DateTime", "DiscriminationStatus")
- you should never put the word "JSON" in your responses, it's a technical term that the user doesn't need to know about. In general, you should avoid revealing any technical details about how the tool works.
- you should ask each question separately instead of trying to ask them all at once. This will make it easier for the user to understand what you're asking and will make it easier for you to get a valid answer.
"""
    bot_name = "MyEcoReporter"
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
        messages=messages
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
    prompt = prompt + '\nMyEcoReporter:'

    return prompt
