# throughput will be audio time / real time processing
# simulate requests
# allow input parameter for total number of requests
# allow input parameter for number of parallel requests

# define latency to be time from sending request to time getting response

#!/usr/bin/env python3

import sys
import time
import wave
from multiprocessing import Pool

import numpy as np
import requests


def upload_file(filename, url):
    start = time.time()
    with open(filename, "rb") as fp:
        files = {"file": fp}
        response = requests.post(url, files=files)
        if response.status_code != 200:
            print(response.status_code, response.body)
            return False
            # raise Exception(f"got a bad error code for post request: {response.status_code}")
    finish = time.time()
    duration = finish - start
    return duration


def calculate_wav_total_time(filename):
    with wave.open(filename, "rb") as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration


def main():
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # this should be done with argparse, but I forgot the API for it.
    total_requests = int(sys.argv[1])
    concurrent_requests = int(sys.argv[2])
    filename = sys.argv[3]
    url = sys.argv[4]
    upload_file(filename, url)
    all_prediciton_runtimes = []
    num_iterations = total_requests // concurrent_requests
    print(f"will iterate: {num_iterations} times")
    duration = calculate_wav_total_time(filename)
    print(f"duration: {duration}")
    start = time.time()
    with Pool(concurrent_requests) as workers:
        iterator = total_requests * [(filename, url)]
        prediciton_runtime = workers.starmap(upload_file, iterator)
        all_prediciton_runtimes.extend(prediciton_runtime)

    all_prediciton_runtimes = np.array(all_prediciton_runtimes)
    finish = time.time()
    num_success = sum(
        1 for successful in all_prediciton_runtimes if successful
    )
    total_audio_time = duration * total_requests
    wall_clock_time = finish - start
    throughput = total_audio_time / wall_clock_time

    latency_mean = all_prediciton_runtimes.mean()
    median_latency = np.median(all_prediciton_runtimes)
    percentile_99 = np.percentile(all_prediciton_runtimes, 99)

    print(f"num successes: {num_success}")
    print(f"runtime (wall clock): {wall_clock_time}s")
    print(f"total audio time: {total_audio_time}s")
    print(f"throughput: {throughput} audio seconds per real time second")
    print(f"latency mean: {latency_mean}s")
    print(f"latency median: {median_latency}s")
    print(f"99th percentile: {percentile_99}s")


if __name__ == "__main__":
    main()
