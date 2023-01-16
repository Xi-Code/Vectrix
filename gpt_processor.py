import pandas_gbq, openai, json, re, configparser, os
from google.cloud import bigquery
from google.oauth2 import service_account

config = configparser.ConfigParser()
config.read('keys/config.ini')

# Set environment variables
# Google Cloud
key_path = 'keys/appgpt-374716-6184be28027d.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keys/appgpt_bigquery.json'

credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id,)
pandas_gbq.context.credentials = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
pandas_gbq.context.project = "appgpt-374716"

# OpenAI
openai.api_key = config['API_KEYS']['openai']

# Run a select query on the bigquery dataset
def run_query(query):
    query_job = client.query(query)
    results = query_job.result()
    return results

# Initialize a method to answer the question using GPT-3

def call_openai(question):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=question,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response


def ProcessQuestion(whatsapp_message):
    '''
    Based on the JSON-object WhatsApp Message, this function will return the answer to the question.
    We will also check Google BigQuery to see if there is a conversation history.
    This function returns the complete conversation as a String
    '''
    

    # Let's check BigQuery to see if we have a conversation with this user

    sender_phone_number = whatsapp_message['entry'][0]['changes'][0]['value']['messages'][0]['from']

    query = '''
    select WHATSAP_MESSAGE, GPT_RESPONSE, INSERT_TS
    from `conversations.chat_history`
    where (PHONE_NUMBER = %s) -- phone number
    AND (INSERT_TS > DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)) -- Only look at the last 24 hours
    ORDER BY INSERT_TS ASC
    '''
    results = pandas_gbq.read_gbq(query % sender_phone_number, credentials=credentials)

    print(f'We feteched {len(results)} rows from BigQuery')


    context = "Pretend you are a customer service chatbot working for a textile wholesale named Quality Textiles.\n\n"
    message_id = whatsapp_message['entry'][0]['changes'][0]['value']['messages'][0]['id']
    sender_phone_number = whatsapp_message['entry'][0]['changes'][0]['value']['messages'][0]['from']

    query = '''
    INSERT INTO conversations.chat_history (WHATSAPP_MESSAGE_ID, WHATSAP_MESSAGE, GPT_RESPONSE, PHONE_NUMBER, INSERT_TS)
    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP())
    '''    

    # If the result is 0 start a new conversation and set the context
    if len(results) == 0:
        #print('No conversation found, starting a new one\n')
        context += 'CUSTOMER: "' + whatsapp_message['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] + '"\n\n'
        #print(context)

        response = call_openai(context)
        answer = response['choices'][0]['text']
        context += response['choices'][0]['text'].replace('\n','')
        response = json.dumps(response)

        # escape all \n characters in the response
        response = re.sub(r'\\n', r'\\\\n', response)
        # escape all single quotes in the response
        response = re.sub(r"'", r"\'", response)

        #print(query % ("'" + message_id + "'", "JSON'" + json.dumps(whatsapp_message) + "'","JSON'" + (response) + "'",sender_phone_number))

        # Insert the prompt and response into BigQuery
        results = run_query(query % ("'" + message_id + "'", "JSON'" + json.dumps(whatsapp_message) + "'","JSON'" + (response) + "'",sender_phone_number))
        
        print('\n New conversation inserted into BigQuery')
        return answer, context 

    else :
        # Unpack the results
        conversation = context
        for index, row in results.iterrows():

            customer = str(json.loads(row['WHATSAP_MESSAGE'])['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'])
            bot = str(json.loads(row['GPT_RESPONSE'])['choices'][0]['text'])

            conversation += 'CUSTOMER: "' + customer + '"\n'
            conversation += bot + '\n\n"'
            
        print('adding to existing conversation\n')
        conversation += f"CUSTOMER: {whatsapp_message['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']}"
        response = call_openai(conversation)
        answer = str(response['choices'][0]['text'])
        conversation += answer
        response = json.dumps(response)
        
        # escape all \n characters in the response
        response = re.sub(r'\\n', r'\\\\n', response)
        response = re.sub(r"'", r"\'", response)
        response = re.sub(r'"', r'\"', response)
        print(response)
        results =  run_query(query % ("'" + message_id + "'", "JSON'" + json.dumps(whatsapp_message) + "'","JSON'" + (response) + "'",sender_phone_number))

        return answer, conversation

