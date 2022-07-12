# Transcriptor

Transcriptor is a web service that receives audio and video files and returns a
transcript from those files.

Please note that these instructions were tested on Linux, but are likely to work
on MacOS as well. Windows would likely require some tweaks.

## Contents
- [Dependencies](#dependencies)
- [Start the server with Docker](#start-the-server-with-docker)
- [Start the server without Docker](#start-the-server-without-docker)
- [Usage](#usage)
- [Design goals](#design-goals)
- [TODOs](#todos)

## Dependencies

Transcriptor requires the following dependencies:
- [Python 3](https://www.python.org/downloads/release/python-3105/) (tested on Python 3.10)
- [ffmpeg](https://ffmpeg.org/)
- [docker](https://www.docker.com/) (optional)

## Start the server with Docker

The following command will both build the docker container and run it on port
5001

```bash
make docker-run
```

## Start the server without Docker

Install the `requirements.txt` in whichever way you prefer. Since this is Python
there are many many ways of doing this. I'll demonstrate an example using the
classic `virtualenv`.

```bash
virtualenv venv -p `which python3`
source venv/bin/activate
pip install -r requirements.txt
```

Run the next command to start a Flask development server and serve the app on
port 5001:

```bash
make run
```

## Usage

Run this command to upload an example audio file to the service (after starting
the server).

```bash
$ curl -X POST -F file=@audio/speech-and-music.wav localhost:5001/v1/predict/en
{
  "transcript": "and that was the end of the veryaring brothers and company bankage he've now made it legend markets"
}
```

> Notice that the file is taken as a form field with the name `file`.

## Design goals

This project was designed and tested to handle files of the size of a typical
movie. It was tested on several movie files.

Transcriptor achieves this by splitting audio and video files up into one minute
chunks, and processing those chunks in batches. Without this batching and
splitting, Transcriptor would quickly exhaust all memory for large input files.

Transcriptor uses the program [ffmpeg](https://ffmpeg.org/) to split audio/video
files into chunks of one minute each.

## TODOs
- Currently the language models are downloaded at startup, but for a proper
production deployment, the model used should be deterministic as per the
container. A way to solve this would be to download the models as a part of
the build

- Logging. There are SO many ways to do logging, and different organizations
have different setups. An approach I've used in the past would be to use a log
aggregator such as Sumo Logic or DataDog to capture stdout and stderr from an
application. There are other systems that use OpenTelemetry such as Lightstep
that take a slightly different approach to log aggregators, but require some
logic within application code to use. Needless to say. Rotating log files on a
server is yet another way to handle logs, but one needs additional tooling to
scale this in prod.

- Testing. I'm a firm believer in integration and end-to-end testing, but unit
testing is also important to verify program correctness.

- Use a production webserver. The built-in Flask development server is not
intended for production. One should deploy this with a WSGI HTTP Server such as
gunicorn or mod_wsgi instead.
