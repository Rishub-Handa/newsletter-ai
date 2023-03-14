import mailparser
from bs4 import BeautifulSoup
from pprint import pprint
import os
from dotenv import load_dotenv
import re
import time

from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

from my_email import MyEmail
from gmail import gmail_send_message, get_recent_messages


if __name__ == "__main__":

    print("Running newsletter summary generator")

    load_dotenv()

    openapi_key = os.environ['OPENAI_KEY']
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['SENDER_PASSWORD']
    environment = os.environ['ENVIRONMENT']

    # Get recent newsletters from newsletters folder
    emails = get_recent_messages()

    # Summarize newsletters
    davinci = OpenAI(model_name='text-davinci-003',
                     openai_api_key=openapi_key, temperature=0.6)
    template = """Question: Retrieve the 5 most important and intriguing article headlines from the following newsletter snippets. Avoid headlines for ads or promotions. Ignore headlines that are very vague and uninformative. If no valid headlines are present, truthfully answer no valid headlines found.

    {newsletter_headings}

    Answer: """
    prompt = PromptTemplate(
        template=template,
        input_variables=['newsletter_headings']
    )

    llm_chain = LLMChain(
        prompt=prompt,
        llm=davinci
    )

    execution_time = int(time.time())
    os.makedirs(f'./outputs/v2_headings/{execution_time}', exist_ok=True)
    for e in emails:
        print(f"Generating headlines for {e.sender}...")
        headlines = llm_chain.run(e.headings_text)
        print(headlines)
        with open(f'./outputs/v2_headings/{execution_time}/{e.sender}.txt', 'w') as f:
            f.write(headlines)
        e.set_headlines(headlines)

        time.sleep(0.5)

    # Construct response email (might need to individualize this per user if anyone else ever decides they want something like this)
    response_body = ""
    for e in emails:
        if "No valid" in e.headlines:
            continue
        response_body += os.path.splitext(e.sender)[0] + " - " +  \
            e.email.subject + "\n" + \
            e.headlines.strip() + "\n\n"

    os.makedirs(f'./summary/{execution_time}', exist_ok=True)
    with open(f'./summary/{execution_time}/response.txt', 'w') as f:
        f.write(response_body)

    print("Response body: ")
    pprint(response_body)

    gmail_send_message("Newsletter Digest :)", "handarishub@gmail.com", response_body)
