# from: https://pytorch.org/tutorials/intermediate/speech_recognition_pipeline_tutorial.html

import functools
import os
import re
import subprocess
from glob import glob

import torch

# Number of files to process in a batch.
# Experimentally, memory pressure was the largest concern
FILE_BATCH_SIZE = os.getenv("FILE_BATCH_SIZE", 5)


class UnsuportedLanguageError(Exception):
    pass


class ModelUtils:
    def __init__(self, model, decoder, utils):
        self.model = model
        self.decoder = decoder
        (
            self.read_batch,
            self.split_into_batches,
            self.read_audio,
            self.prepare_model_input,
        ) = utils


device = torch.device(
    "cpu"
)  # CPU is more portable than CUDA, so easier for running example code


language_map = {
    language: ModelUtils(
        *torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_stt",
            language=language,
            device=device,
        )
    )
    for language in ["en", "es", "de"]
}


def split_file(tmpdir):
    """
    Split the input file into 1 minute chunks to avoid consuming too much
    memory on large files.

    Returns list of files
    """
    input_path = os.path.join(tmpdir, "orig")
    output_path = os.path.join(tmpdir, r"output_%04d.MOV")

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-c",
        "copy",
        "-map",
        "0",
        "-segment_time",
        "00:01:00",
        "-f",
        "segment",
        "-reset_timestamps",
        "1",
        output_path,
    ]
    proc = subprocess.Popen(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    proc.wait()
    file_glob = os.path.join(tmpdir, "output_*.MOV")
    files = glob(file_glob)
    return files


def clean_text(text):
    """
    cleans text and removes unwanted duplicate spaces
    """
    return re.sub(r"\s+", " ", text.strip())


def run_model(input_files, language):
    """
    execute the model on the input files
    """
    utils = language_map[language]
    data = utils.read_batch(input_files)
    input = utils.prepare_model_input(data, device=device)
    output = utils.model(input)
    transcript = " ".join(language_map[language].decoder(example) for example in output)
    return transcript


def predict(tmpdir, language):
    """
    Given the language to retrieve the transcript for and the directory with
    the original video file (will look for a file called "orig"), run the model
    and return the predicted transcript to the caller
    """
    if language not in language_map:
        raise UnsuportedLanguageError(f"language: '{language}' not supported")

    utils = language_map[language]
    input_files = split_file(tmpdir)
    batches = utils.split_into_batches(input_files, batch_size=FILE_BATCH_SIZE)

    runner = functools.partial(run_model, language=language)
    transcript = " ".join(
        clean_text(text_chunk) for text_chunk in map(runner, batches)
    ).strip()
    return transcript
