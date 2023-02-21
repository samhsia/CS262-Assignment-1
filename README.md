# CS262 Assignment 1
 
This repository is for **Assignment 1 -- Wire Protocols (Chat Application)**  of **CS 262: Introduction to Distributed Systems**.

Note that the chat application currently only works between sockets on the same Wi-Fi network.
We target a single server setup that can support multiple clients.
Clients can log on and off the chat application without deleting account.

## Setup

The implementations for both part 1 and part 2 are in Python (developed and tested using Python 3).

Relevant non-standard packages to install include:

- `grpcio`
- `grpcio-tools`

Install these packages using your preferred package management tool before proceeding.
Sample command using `pip`: `pip install grpcio grpcio-tools`.

## Running Code

To run the code,

1. `cd` into the corresponding directory (i.e., `cd part_1` or `cd part_2`).
2. Find out your IP address on the Wi-Fi network by using `ipconfig getifaddr en0`
3. Edit the `SERVER_IP` configuration variable within `server.py` to use the IP address found in step 2.
4. Launch server socket: `python3 server.py`.
5. Launch client socket(s); `python3 client.py SERVER_IP`. where `SERVER_IP` is the IP address found in step 2.
6. Enjoy (and follow instructions in prompt, of course)!
