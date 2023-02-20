'''
This file implements client functionality of chat application.

Usage: python3 client.py IP_ADDRESS
'''
# Import relevant python packages
import grpc
from protos import chat_pb2, chat_pb2_grpc
import sys
from threading import Thread

# Constants/configurations
PORT = 1234 # fixed application port

def msgstream_thread(account_info, client):
    for message in client.MessageStream(account_info):
        print(message.msg)

def raise_exception(self):
    thread_id = self.get_id()
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
            ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        print('Exception raise failure')

# Main function for client functionality
def main():
    # Get IP address and port number of server socket
    if len(sys.argv) != 2:
        print('Usage: python3 client.py IP_ADDRESS')
        sys.exit('client.py exiting')
    ip_address = str(sys.argv[1])

    with grpc.insecure_channel('{}:{}'.format(ip_address, PORT)) as channel:
        client = chat_pb2_grpc.ChatAppStub(channel)
        print('Successfully connected to server @ {}:{}'.format(ip_address, PORT))

        # Account creation and login -- only exit loop if successful.
        while True:
            rpc_call = input("Please enter 1 or 2 :\n1. Create account.\n2. Login\n")
            account_info = chat_pb2.AccountInfo(username = input("Username: "), password = input('Password: '))
            if rpc_call == "1":
                account_response = client.CreateAccount(account_info)
            elif rpc_call == "2":
                account_response = client.LoginAccount(account_info)
            else:
                print('{} is not a valid option. Please enter either 1 or 2!'.format(rpc_call))
                continue
            print(account_response.msg)
            if account_response.status:
                break # account creation/login successful

        # create new listening thread for when new message streams come in
        Thread(target=msgstream_thread, args=(account_info, client), daemon=True).start()

        while True:
            rpc_call = input('Please enter 1, 2, or 3:\n1. Send message.\n2. List all users.\n3. Delete your account.\n')
            if rpc_call == "1":
                message = chat_pb2.Msg(src_username = account_info.username, dst_username = input("Target user: "), msg = input("Message: "))
                client.SendMessage(message)
            elif rpc_call == "2":
                message = chat_pb2.Empty()
                list_accounts_response = client.ListAccounts(message)
                print(list_accounts_response.msg)
            elif rpc_call == "3":
                message = chat_pb2.Empty()
                delete_account_response = client.DeleteAccount(account_info)
                if delete_account_response.status:
                    print('Account deletion successful. Server @ {}:{} disconnected!'.format(ip_address, PORT))
                    sys.exit('Closing application.')
            else:
                print('{} is not a valid option. Please enter either 1, 2, or 3!'.format(rpc_call))
                continue
    print('Server @ {}:{} disconnected!'.format(ip_address, PORT))
    sys.exit('Closing application.')

if __name__ == "__main__":
    main()