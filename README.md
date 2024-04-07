# OpenAI Chatbot using Chainlit

## How to run:

#### Step 1: 
* Create .env file with api_link, api_key, api_version, model
### Without Docker:
#### Step 2: 
* pip install -r requirements.txt
* chainlit run run.py 

### With Docker:
#### Step 2:
* docker build -t chatbot ./
* docker run -d -p 8000:8000 -e .env chatbot

## Output:
### Data Analysis:
![alt text](image.png)

![alt text](image-1.png)

### Normal conversation:
![alt text](image-2.png)

## Future work:
* Handling large csv files.
* Maintaining higher number of chain of thoughts.
* Worked on handling larger csv files with the help of embedding models (final_code.py file in async branch has the relevant implementation).

