import os  
import pandas as pd
import tiktoken
from openai  import AzureOpenAI
import chainlit as cl  
from dotenv import load_dotenv  
load_dotenv()
import executor  
import re

cl.instrument_openai()  

client = AzureOpenAI(
  azure_endpoint = os.getenv("api_link"), 
  api_key=os.getenv("api_key"),  
  api_version=os.getenv("api_version")
)


# processing csv file
def process_csv_file(file_):
    data = ""
    encoding = tiktoken.get_encoding("cl100k_base")
    df = pd.read_csv(file_, encoding="utf-8")
    dictionary = df.to_dict(orient="list")
    token_len = len(encoding.encode(str(dictionary)))
    if token_len<3000:
        data = str(dictionary)
    else:
        print("token limit exceeded please upload smaller file..")
    return data,df

# calling model
def call_model(messages):
    response = client.chat.completions.create(
        temperature=0.5,
        max_tokens=600,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0, 
        model = os.getenv("model"),
        messages = messages 
    )
    return response.choices[0].message.content


# calling python interpreter
def python_exec(code: str, variables: dict, language: str = "python"):
    myexcutor = executor.PythonExecutor()
    code_output = myexcutor.execute(code, variables)
    response = {"result": code_output}
    return response['result']


@cl.on_chat_start
async def on_chat_start():
    messages = [{"role": "system","content":"You are a Code Assistant equipped with advanced data analytical skills. You are here to help people by providing accurate, reusable and executable code solutions, and engage in general chit-chat."}]
    cl.user_session.set("message history", messages)


@cl.on_message
async def main(message: cl.Message):
    messages = cl.user_session.get('message history')
    # Send empty message for loading
    msg = cl.Message(
        content=""
    )
    await msg.send()

    csv_file = [file for file in message.elements if "text/csv" in file.mime]
    if csv_file:
        messages[:] = [messages.pop(0)]
        msg = cl.Message(content = "processing file.........")
        await msg.send()
        content_ = process_csv_file(csv_file[0].path)
        while len(content_[0])<=0:
            files = await cl.AskFileMessage(
                content = "Token limit exceeded please upload smaller csv file to proceed with..",
                accept = ["text/csv"],
                max_size_mb=10,
                timeout=90
            ).send()
            if files:
                content_ = process_csv_file(files[0].path)
        cl.user_session.set("df", content_[1])
        messages.append({"role":"user", "content": str(content_[0])+ "this data is pandas dataframe. don't bring it up unless user specifies about this data."})
        msgs = cl.Message(content='file processing is done.') 
        await msgs.send()
    
    messages.append({"role": "user","content": message.content})
    if "code" in str(messages[-1]['content']).lower() or "python" in str(messages[-1]['content']).lower():
        messages[-1]['content'] = messages[-1]['content']+ " and if you want to use dataframe in your code assume you have a dataframe stored in the variable 'df', you can directly reference it as 'df' without the need to create or load the dataframe."

    print(messages)

    response = call_model(messages)
    pattern = r"(`{3})(?:python)?(.*?)\1"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        await cl.Message(content=response).send() 
        for i in range(len(matches)):
            python_code = str(matches[i][1])
            output = await cl.make_async(python_exec)(code=python_code, variables={"df":cl.user_session.get("df")})
            msgs = cl.Message(content=f"```OUTPUT\n {output}")
            await msgs.send()

    if not matches:
        await cl.Message(content=response).send()  