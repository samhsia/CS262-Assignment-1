'''
This file implements server functionality of chat application.

Usage: python3 server.py
'''
# Import relevant python packages
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import grpc
from protos import chat_pb2
from protos import chat_pb2_grpc

# Constants/configurations
MAX_CLIENTS = 100
PORT        = 1234 # fixed application port

SERVER_IP = '100.90.130.16' # REPLACE ME with output of ipconfig getifaddr en0

class ChatAppService(chat_pb2_grpc.ChatAppServicer):

    '''
    'users' is a hashmap to store all client data
        - key: username
        - values: 'password', 'socket', 'mailbox'
    '''
    def __init__(self) -> None:
        super().__init__()
        self.users = defaultdict(dict)
     
    # Handles user creation for new users
    def CreateAccount(self, request, context):
        # New username
        if request.username not in self.users:
            success = True
            self.users[request.username]['password'] = request.password
            print('Successfully created account with username: {}'.format(request.username))
            message = 'Successfully created account with username: {}\n'.format(request.username)
            self.users[request.username]['mailbox'] = []
        # Username has already been taken (re-enter)
        else:
            success = False
            message = '{} is already taken. Please enter a unique username!\n'.format(request.username)
        response = chat_pb2.Response(status=success, msg=message)
        return response
    
    def LoginAccount(self, request, context):
        success = False
        # Username exists
        if request.username in self.users:
            print(self.users)
            print('HERE')
            # Entered correct password
            if request.password == self.users[request.username]['password']:
                success = True
                print('{} successfully logged in'.format(request.username))
                message = 'Successfully logged in\n'

                # No mail to send
                if len(self.users[request.username]['mailbox']) == 0:
                    message += 'You do not have any queued messages.' # no mail to send
                # Send mail and clear mailbox
                else:
                    message += 'Welcome back, {}. Unread messages:\n'.format(request.username)
                    for mailbox_message in self.users[request.username]['mailbox']:
                        message += str(mailbox_message+'\n')
                    self.users[request.username]['mailbox'] = []
            # Entered incorrect password
            else:
                message = 'Incorrect password. Returning to the welcome page.'
        
        # Username does not exist
        else:
            message = '{} is not a valid username. Returning to the welcome page.'.format(request.username)

        response = chat_pb2.Response(status=success, msg=message)
        return response
    
    def ListAccounts(self, request, context):
        message = ''
        for index, username in enumerate(self.users):
            message += '{}. {}\n'.format(index, username)
        response = chat_pb2.Response(status=True, msg = message)
        return response
    
    def DeleteAccount(self, request, context):
        del self.users[request.username]
        # users.pop(request.username)
        print('{} deleted account.'. format(request.username))
        response = chat_pb2.Response(status=True, msg='')
        return response
    
    # Opens message (i.e., response) stream so server can keep sending messages to client(s)
    def MessageStream(self, request, context):
        # Let user know all other users available for messaging
        message = '\nWelcome to chatroom!\nAll users:'
        yield chat_pb2.Msg(src_username = '', dst_username = request.username, msg = message)
        for index, username in enumerate(self.users):
            message = '{}. {}'.format(index, username)
            yield chat_pb2.Msg(src_username = '', dst_username = request.username, msg = message)
        
        # Continuously listen to new messages
        while True:
            try:
                if len(self.users[request.username]['mailbox']) > 0:
                    for message in self.users[request.username]['mailbox']:
                        yield chat_pb2.Msg(src_username = '', dst_username = request.username, msg = message)
                    self.users[request.username]['mailbox'] = []
            except:
                # Only delete user information when DeleteAccount is called
                if not self.users[request.username]:
                    del self.users[request.username]
                break

    # Takes incoming message from client, adds it to destination mailbox, and then acknowledges success.
    def SendMessage(self, request, context):
        message = "<{}> {}".format(request.src_username, request.msg) # message formatting
        self.users[request.dst_username]['mailbox'].append(message) # append message to target user's mailbox
        response = chat_pb2.Response(status=True, msg='Message delivered to user')
        return response
    
def main():
    server = grpc.server(ThreadPoolExecutor(max_workers=MAX_CLIENTS))
    chat_pb2_grpc.add_ChatAppServicer_to_server(ChatAppService(), server)
    server.add_insecure_port('{}:{}'.format(SERVER_IP, PORT))
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    main()