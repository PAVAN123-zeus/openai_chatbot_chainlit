# OpenAI Chatbot using Chainlit

## How to run:

#### Step 1: 
* Create .env file with api_link, api_key, api_version, model
* Description : api_link: endpoint, api_key: azure api key, api_version: api version(example: "2024-02-15-preview"), model: deployment name
### Without Docker:
#### Step 2: 
* pip install -r requirements.txt (to install all the required packages)
* chainlit run app.py (to run the code)

### With Docker:
#### Step 2:
* docker build -t chatbot ./  (to build the docker image)
* docker run -d -p 8000:8000 -e .env chatbot (to run the docker container using image)

### Input File:
* "imdb.csv" is the sample file used for experimental purpose.

## Output:
### Data Analysis:
![alt text](image.png)

![alt text](image-1.png)

![alt text](image-4.png)

#### Executing Python code received from ChatGPT.
![alt text](image-5.png)


### Normal conversation:
![alt text](image-2.png)

![alt text](image-3.png)

## Future work:
* Handling large csv files.
* Ensuring the appropriate number of historical messages is maintained.
* Worked on handling larger csv files with the help of embedding models (final_code.py file in async branch has the relevant implementation).

