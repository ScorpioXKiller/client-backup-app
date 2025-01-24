"""
@file main.py
@brief This file contains the main program that demonstrates the client simulation. It connects to the server and send the requests to perform operations with files.
       It reads the server information, connects to the server, loads backup files, requests list of files, saves and restores files, deletes files and finishes the work.
@author Dmitriy Gorodov
@id 342725405
@date 24/01/2025
"""

from Client import Client

def main():
    # Step 1: generate unique ID by default
    client = Client()
    try:
        # Step 2: read server info and connect
        client.read_server_info()
        client.connect()

        # Step 3: load backup files from file “backup.info”
        client.load_backup_files()

        # Step 4: request to display the list of files on the server
        client.request_list_files()

        # Step 5: read first file from the file “backup.info” and save it on the server
        if len(client.files_to_backup) > 0:
            client.request_backup_file(client.files_to_backup[0])

        # Step 6: read second file from the file “backup.info” and save it on the server
        if len(client.files_to_backup) > 1:
            client.request_backup_file(client.files_to_backup[1])

        # Step 7: request to display the list of files on the server
        client.request_list_files()

        # Step 8: retrieve the first file from the server and save it as "tmp" file on the client side
        if len(client.files_to_backup) > 0:
            client.request_restore_file(client.files_to_backup[0], "tmp")

        # Step 9: delete first file from the server
        if len(client.files_to_backup) > 0:
            client.request_delete_file(client.files_to_backup[0])

        # Step 10: retrieve first file from the server again
        if len(client.files_to_backup) > 0:
            client.request_restore_file(client.files_to_backup[0])

        # Step 11: end the work and close the connection
        print("Client work completed.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()