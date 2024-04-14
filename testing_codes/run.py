import os  
import pandas as pd
import tiktoken
from openai  import AzureOpenAI
import chainlit as cl  
from dotenv import load_dotenv  
load_dotenv()  

  
cl.instrument_openai()  

client = AzureOpenAI(
  azure_endpoint = os.getenv("api_link"), 
  api_key=os.getenv("api_key"),  
  api_version=os.getenv("api_version")
)

messages = [  
            {  
                "role": "system",  
                "content": "You are a Chat Code-Interpreter application! with advance data anlytical skills you are here to help people with code interpretation and general chit-chat. you will provide code snippets and you are designed to provide accurate and reusable code solutions." 
            }]


def process_csv_file(file_):
    print("processing csv file....")
    data = ""
    encoding = tiktoken.get_encoding("cl100k_base")
    df = pd.read_csv(file_, encoding="utf-8")
    dictionary = df.to_dict(orient="list")
    token_len = len(encoding.encode(str(dictionary)))
    if token_len<3000:
        data = str(dictionary)
    return data


def call_model(messages):
    response = client.chat.completions.create(
        temperature=0.7,
        max_tokens=600,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0, 
        model = os.getenv("model"),
        messages = messages 
    )
    return response.choices[0].message.content


@cl.on_chat_start
async def on_chat_start():
    files = None

    while files is None:
        files = await cl.AskFileMessage(
            content = "please upload the csv file to begin!",
            accept=["text/csv"],
            max_size_mb=10,
            timeout=90
        ).send()
    
    msg = cl.Message(content = "processing file.........")
    await msg.send()

    if files:
        content_ = process_csv_file(files[0].path)
        while len(content_)<=0:
            files = await cl.AskFileMessage(
                content = "Token limit exceeded please upload smaller csv file to proceed with..",
                accept = ["text/csv"],
                max_size_mb=10,
                timeout=90
            ).send()

            if files:
                content_ = process_csv_file(files[0].path)
        
    messages.append({"role":"user", "content": content_+ "this data is pandas dataframe. don't bring it up unless user specifies about this data."})
    cl.user_session.set('data', content_)
    msgs = cl.Message(content='file processing is done. now you can ask questions ..') 
    await msgs.send()


@cl.on_message  
async def main(message: cl.Message):
    messages.append({"role": "user","content": message.content}) 
    print(messages)
    response = call_model(messages)
    await cl.Message(content=response).send()  