#!/usr/bin/env python3


from flask import Flask
import model

app = Flask(__name__)


languages = {
    "en",
    "es",
    "de",
}


@app.route("/")
def hello():
    return "Hello World!\n"


@app.route("/predict/<language>", methods=["POST"])
def predict(language):
    if language not in languages:
        return (f"language: '{language}' not supported", 400)
    else:
        predicted_text = model.predict(language)
        return (predicted_text, 200)


if __name__ == "__main__":
    app.run(port="5001")
