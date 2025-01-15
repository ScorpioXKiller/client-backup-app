from backup_client import BackupClient

def main():
    client = BackupClient()
    try:
        # 1) user_id is generated in the constructor
        # 2) Read the server IP/port
        client.read_server_info()
        # 3) Read filenames from backup.info
        client.read_backup_info()

        # Connect to the server
        client.connect()

        # 4) Request list of files
        #client.request_list_files()

        # 5) Save the first file (if any)
        if len(client.backup_files) > 0:
            client.request_save_file(client.backup_files[0])

        # 6) Save the second file (if any)
        if len(client.backup_files) > 1:
            client.request_save_file(client.backup_files[1])

        # 7) Request list again
        client.request_list_files()

        # 8) Retrieve the first file
        if len(client.backup_files) > 0:
            client.request_retrieve_file(client.backup_files[0])

        # 9) Delete the first file
        if len(client.backup_files) > 0:
            client.request_delete_file(client.backup_files[0])

        # 10) Try to retrieve the first file again (likely error if deleted)
        if len(client.backup_files) > 0:
            client.request_retrieve_file(client.backup_files[0])

        # 11) End/exit
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Always close the connection
        client.close()

if __name__ == "__main__":
    main()