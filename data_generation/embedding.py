import openai
import pandas as pd
import tiktoken
import yaml

# config
## path to openai key
PATH_TO_OPENAI_KEY = "./openai.yaml"
# max tokens for an embedding
MAX_TOKENS = 500

# get openai key
with open(PATH_TO_OPENAI_KEY, "r") as stream:
    OPENAI_KEY = yaml.safe_load(stream)["key"]

openai.api_key = PATH_TO_OPENAI_KEY

# Load the tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")


def split_into_many(text, max_tokens=MAX_TOKENS):
    """Splits a text into chunks of max_tokens tokens

    Args:
        text (str): The text to split
        max_tokens (int): The maximum number of tokens per chunk

    Returns:
        list: A list of chunks of text
    """

    # Split the text into sentences
    sentences = text.split(". ")

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):
        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks


def get_shortened_text(df):
    """Shortens the text in a dataframe to a maximum number of tokens

    Args:
        df (pandas.DataFrame): The dataframe containing the text to shorten

    Returns:
        pandas.DataFrame: The dataframe with the shortened text
    """

    # Get current number of tokens per text
    df["n_tokens"] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():
        # If the text is None, go to the next row
        if row[1]["text"] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]["n_tokens"] > MAX_TOKENS:
            shortened += split_into_many(row[1]["text"])

        # Otherwise, add the text to the list of shortened texts
        else:
            shortened.append(row[1]["text"])

    df = pd.DataFrame(shortened, columns=["text"])

    return df


df = pd.read_csv("data/succession_wiki_text.csv")
df_shortened = get_shortened_text(df)
df_shortened["embeddings"] = df_shortened.text.apply(
    lambda x: openai.Embedding.create(input=x, engine="text-embedding-ada-002")["data"][
        0
    ]["embedding"]
)
df_shortened.to_csv("data/succession_wiki_embeddings.csv", index=False)
