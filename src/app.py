#!/usr/bin/env python3


import os
import tempfile

from flask import Flask, request

import model

app = Flask(__name__)


@app.route("/version", methods=["GET"])
def version():
    return "v1"


def process_audio(tmpdir, language):
    filename = os.path.join(tmpdir, "orig")
    file = request.files["file"]
    file.save(filename)
    transcript = model.predict(tmpdir, language)
    return transcript


@app.route("/v1/predict/<language>", methods=["POST"])
def predict(language):
    """
    Example usage:
    $ curl -X POST -F file=@audio/epi.wav localhost:5001/v1/predict/en
    {
      "transcript": "hello this is ste fuller i'm a professor of social
    eppistemology at the university of warick and the question before us today is
    what is a pistetomology and why is it important a epistemology is the branch
    philosophy that is concerned with the nature of knowledge now why is no"
    }
    """

    if "file" not in request.files:
        return ("no audio file in POST request", 400)

    with tempfile.TemporaryDirectory() as tmpdir:
        transcript = process_audio(tmpdir, language)
        try:
            response = {
                "transcript": transcript,
            }
            return (response, 200)
        except model.UnsuportedLanguageError as e:
            return (str(e), 400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001")
