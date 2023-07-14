import openai
from openai.embeddings_utils import distances_from_embeddings
import pandas as pd
import numpy as np


def openai_query(max_tries,
                 messages,
                 stop=None,
                 max_tokens=None,
                 temperature=None):
  """Query OpenAI API for a response.
    Args:
        max_tries (int): Maximum number of tries to get a response from OpenAI.
        messages (list): List of messages to send to OpenAI.
        stop (str): String to stop the response.
        max_tokens (int): Maximum number of tokens to return.
        temperature (float): Temperature of the response.
    Returns:
        response (dict): Response from OpenAI.
    """
  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages,
    stop=stop,
    max_tokens=max_tokens,
    temperature=temperature,
  )

  return response


def get_chat_response(openai_key, max_tries, messages, roles):
  openai.api_key = openai_key

  question = messages[-1]


  max_len = 1800
  size = "ada"

  df = pd.read_csv('data/succession_embeddings.csv')
  df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)

  context = create_context(
    question,
    df,
    max_len=max_len,
    size=size,
  )

  print("Context:\n" + context)
  print("\n\n")

  initial_prompt = f"""Answer the following question based on the context below, and if the question can't be answered based on the context, say \"I don't know\". Please refrain from referring to the fact that you've been given a context.\n\nContext: {context}"""

  message_prompt = [{
    "role":
    "system",
    "content":
    "You are Succession Chat. An expert about all things related to the HBO show Succession."
  }]
  for i in range(0, len(messages) - 1):
    role_string = roles[i]
    if "response-message" in role_string:
      role = "assistant"
    elif "user-message" in role_string:
      role = "user"
    d = {"role": role, "content": messages[i]}
    message_prompt.append(d)

  message_prompt.append({"role": "user", "content": initial_prompt})
  message_prompt.append({"role": "assistant", "content": "Yes, I understand."})
  message_prompt.append({"role": "user", "content": question})

  print("message prompt")
  print(message_prompt)
  response = openai_query(max_tries, message_prompt)
  response_text = response["choices"][0]["message"]["content"]

  print(response_text)

  return response_text


def create_context(question, df, max_len=1800, size="ada"):
  
  """Creates a context for the question based on the embeddings of the text
  
  Args:
      question (str): Question to answer
      df (pd.DataFrame): DataFrame with the text and embeddings
      max_len (int): Maximum length of the context
      size (str): Size of the embeddings
      
    Returns:
        context (str): Context for the question
    """

  # Get the embeddings for the question
  q_embeddings = openai.Embedding.create(
    input=[question], engine='text-embedding-ada-002')['data'][0]['embedding']

  # Get the distances from the embeddings
  df['distances'] = distances_from_embeddings(q_embeddings,
                                              df['embeddings'].values,
                                              distance_metric='cosine')
  returns = []
  cur_len = 0

  # Sort by distance and add the text to the context until the context is too long
  for i, row in df.sort_values('distances', ascending=True).iterrows():

    # Add the length of the text to the current length
    cur_len += row['n_tokens'] + 4

    # If the context is too long, break
    if cur_len > max_len:
      break

    # Else add it to the text that is being returned
    returns.append(row["text"])

  # Return the context
  return "\n\n###\n\n".join(returns)
