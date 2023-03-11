
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

def run_gpt(query):
  
  response = openai.Completion.create(
    # The engine, or model, which will generate the completion. Some engines are suitable for natural language tasks, others specialize in code  
    engine="text-davinci-003",
    # the query to be completed in natural language. i.e. prompt="### Postgres SQL tables, with their properties:\n#\n# Employee(id, name, department_id)\n# Department(id, name, address)\n# Salary_Payments(id, employee_id, amount, date)\n#\n### A query to list the names of the departments which employed more than 10 employees in the last 3 months\nSELECT",
    prompt=query,
    # The temperature controls the randomness of the answer. 0.0 is the most deterministic and repetitive value
    temperature=0,
    # The maximum number of tokens to generate
    max_tokens=350,
    # Controls diversity via nucleus sampling. 0.5 means all of all likeliwood-weighted options are considered
    top_p=1.0,
    # Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
    frequency_penalty=0.0,
    # Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
    presence_penalty=0.0,
    # Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
    stop=["#", ";"]
  )

  return response.choices[0].text


detect_task_prompt = """
Detect task from this list: ["weather_temperature", "date_time", "other"]

Input: what is weather in Big Bear
Output: 'weather_temperature'
#
Input: how is weather in LA
Output:'weather_temperature'
#
Input: What time is in Tehran
Output:'date_time'
#
Input: time in los angeles
Output:'date_time'
#
Input: who is elon musk
Output:'other'
#
Input: tell me more about China wall
Output:'other'
#
Input: {user_input}
Output:
"""


answer_question = """
Answer the question, be very short and use simple words:

Question: {user_input}
Answer:
"""