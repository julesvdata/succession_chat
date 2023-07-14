from flask import Flask, render_template, request
import utils
import json
import yaml
import openai

## config
## path to openai key
PATH_TO_OPENAI_KEY = "./openai.yaml"

# get openai key
with open(PATH_TO_OPENAI_KEY, "r") as stream:
    OPENAI_KEY = yaml.safe_load(stream)["key"]

openai.api_key = OPENAI_KEY

app = Flask(__name__)


@app.route("/")
def index():
    """Render the index page"""
    return render_template("index.html")


@app.route("/chat")
def chat():
    """Render the chat page"""
    return render_template("chat.html")


@app.route("/getChatResponse", methods=["POST"])
def get_chat_response():
    """Get chat response"""
    request_json = request.json
    messages = request_json["messages"]
    roles = request_json["roles"]

    response = utils.get_chat_response(OPENAI_KEY, 5, messages, roles)

    return json.dumps({"response": response})


app.run(host="0.0.0.0",port=5050,debug=True)
