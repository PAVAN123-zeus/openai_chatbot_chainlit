import os  
import pandas as pd
import numpy as np
import tiktoken
import time
from openai  import AzureOpenAI
import chainlit as cl  
from dotenv import load_dotenv  
load_dotenv()  

# numpy == 1.26.4
# embedding_model = "text-embedding-002"

cl.instrument_openai()  

client = AzureOpenAI(
  azure_endpoint = os.getenv("api_link"), 
  api_key=os.getenv("api_key"),  
  api_version=os.getenv("api_version")
)

messages = [  
            {  
                "role": "system",  
                "content": "You are a Chat Code-Interpreter application! you are here to help people with code interpretation and general chit-chat. you will provide code snippets for analysis and you are designed to provide accurate and reusable code solutions." 
            }]


def generate_embeddings(client, text, embeddingmodel):
    result = ''
    sleepTime,i = 10, 1
    while type(result)!=list:
        try:
            result = client.embeddings.create(model = embeddingmodel, input = text).data[0].embedding
        except Exception as e:
            print(f'Retries: {i}\nError: {e}')
            time.sleep(sleepTime*i)
        i+=1
    return result


def process_big_csv_file(df):
    dictionary = df.to_dict(orient='records')
    df['document_embeddings'] = [generate_embeddings(client, val, os.getenv('embedding_model')) for val in dictionary]
    return df


def perform_vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


def process_csv_file(file_):
    data = ""
    encoding = tiktoken.get_encoding("cl100k_base")
    df = pd.read_csv(file_, encoding="utf-8")
    dictionary = df.to_dict(orient='list')
    token_len = len(encoding.encode(str(dictionary)))
    if token_len<3000:
        data = str(dictionary)
    else:
        data = process_big_csv_file(df)
    return data


def call_model(messages):
    response = client.chat.completions.create(
        temperature=0.7,
        max_tokens=600,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0, 
        model = "ChatGPT-35-16K",
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
            max_size_mb=100,
            timeout=100
        ).send()
    
    msg = cl.Message(content = "processing file.........")
    await msg.send()

    if files:
        print("files loaded....")
        file_ = files[0].path
        content_ = process_csv_file(file_)
    cl.user_session.set('data', content_)
    print("this is on chat start.....")
    msgs = cl.Message(content='file processing is done. now you can ask questions ..') 
    await msgs.send()


@cl.on_message  
async def main(message: cl.Message):
    df = cl.user_session.get('data')
    if type(df) != str:
        dff = df
        user_input = {"role": "user","content": message.content}
        query_embeddings = generate_embeddings(client, user_input['content'], os.getenv('embedding_model'))
        dff['similarity'] = dff['document_embeddings'].apply(lambda x: perform_vector_similarity(x, query_embeddings))
        dff = dff.sort_values(by='similarity', ascending = False).drop(columns = ['document_embeddings'])
        encoding = tiktoken.get_encoding("cl100k_base")
        i = 1
        limit = 0
        while limit < 3000:
            dff_ = dff[:i]
            limit = len(encoding.encode(str(dff_.to_dict(orient='list'))))
            i+=1
        final_df = dff[:i]
    else:
        final_df = df

    messages.append({"role":"user", "content": final_df+ "this data is pandas dataframe. don't bring it up unless user specifies about it."})
    messages.append({"role": "user","content": message.content})
    
    print(messages) 

    response = call_model(messages)
    await cl.Message(content=response).send()  