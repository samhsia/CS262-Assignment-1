# Design Notebook (Wire Protocols -- Chat Application)

We document the design decisions and thought processes behind the server and client implementations for both parts 1 and 2 in this design notebook.
This notebook is organized around key questions that we answer and implement as Python-based functions.

## How can users create accounts?

- **(Part 1)** Users can create accounts by following the on-screen prompts. 
Users will be asked for both username and password. 
These information will be exchanged with server and subsequently stored in the `users` data structure (more on that below).

- **(Part 2)** Users can create accounts by following the on-screen prompts.
In this case, users, will call the gRPC service `CreateAccount` with message `AccountInfo` that contains both username and password obtained via on-screen prompts.
These information will be exchanged with server and subsequently stored in the `users` data structure (more on that below).

## How is user data stored and organized? How can we access user data (e.g., list all users)?

- We use a dictionary called `users` to store account information. 
A unique `username` is the key of each entry. 
In each entry, a last active socket *(only for part 1)*, password, and list of mailbox messages are recorded as shown below.

        users[username]['socket']   = sock
        users[username]['password'] = password
        users[username]['mailbox']  = []


## How are messages formatted and sent?

- **(Part 1)** The user can specify a username as the target recipient and the message itself is formatted as a string variable that is then encoded as bytes before being sent to server.

- **(Part 2)** Messages use the following gRPC message format (variable names are self-descriptive):

        message Msg {
            string src_username = 1;
            string dst_username = 2;
            string msg = 3;
        }
        
## How do we handle undelivered messages?

- The undelivered messages are recorded in the user’s mailbox, `users[username]['mailbox']`, and the messages will be sent to the user at login time.

## How is account deletion handled?

- For this chat application, we define logging out (closing client application) and account deletion separately.
Account deletion is handled via a separate prompt option.
To delete an account, on the server side, the whole entry in `users` dictionary (i.e., `users[username_to_delete]` is deleted -- this includes all the messages in the mailbox.

## What is the implemented wire protocol?

- In part 1, we devise our own *"call-and-response"* style wire protocol. 
Combined with messages of fixed sizes (i.e., `BUFFER_SIZE = 2048 # fixed 2KB buffer size`), a *"call-and-response"* style protocol allows both server and client to understand how to interpret the message.
For example, during a successful account creation, messages on the *"wire"* are interpreted as follows:

    1. (Server to Client) Welcome message -- interpreted as string
    2. (Client to Server) 1, 2, or 3 -- interpreted as choice (e.g., 1 for account creation)
    3. (Server to Client) Username solicitation -- interpreted as string
    4. (Client to Server) Username -- interpreted as string
    5. (Server to Client) Password solicitation -- interpreted as string
    6. (Client to Server) Password -- interpreted as string
    7. (Server to Client) Success message -- interpreted as string

- Part 2 utilizes gRPC, which has its own set of system of requests and responses

## How are multiple clients handled?

- The server keeps on listening to `PORT = 1234`. 
If any client tries to connect, a new thread and socket are created to handle the communication. 
The thread and the corresponding socket are killed when a user logs out or deletes their account -- or when the server is not able to send messages to the user. 

## How does the custom wire protocol in Part 1 compare with gRPC?

- **(Code Complexity)** 
Server implementation (i.e., `server.py`) required less lines of code using gRPC than our custom protocol (128 LOC vs 252 LOC).
This is because the complexities behind managing socket communication is handled by the files generated from our `protos` file.
In contrast, client implementation (i.e., `client.py`) was slightly more complicated since the client is now in charge of calling different gRPC services (75 LOC vs 57 LOC).
In part 1, the client was not in charge of determining functionality of its messages -- parsing of functionalities was done exclusively on server side.

- **(System Performance)**
To compare the system performance of part1&2, we measured the message round-trip time from client to server back to the client. The gRPC protocol is more than 100x slower than part 1 as shown in the below table.

  |      | Runtime(ms) |
  | ----------- | ----------- |
  | part1      | 0.23   |
  | part2   | 29.65        |

- **(Size of Buffers)**
For part 1, we use 2KB for buffer size. For part 2, the default buffer size for incoming messages is 4MB and no limit for outgoing messages. 
Comparing part1 and 2, gRPC can support much larger buffer size.
