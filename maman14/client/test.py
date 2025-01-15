from backup_client import BackupClient

def run_tests():
    client = BackupClient()
    try:
        # Initialize client
        client.read_server_info()
        client.read_backup_info()
        client.connect()

        # 1. List files (should be empty initially)
        print("Test 1: Listing files before any operation:")
        client.request_list_files()

        # 2. Save files
        print("\nTest 2: Saving files:")
        for file in client.backup_files:
            client.request_save_file(file)

        # 3. List files after save
        print("\nTest 3: Listing files after saving:")
        client.request_list_files()

        # 4. Retrieve the first file
        if client.backup_files:
            print("\nTest 4: Retrieving the first file:")
            client.request_retrieve_file(client.backup_files[0])

        # 5. Delete the first file
        if client.backup_files:
            print("\nTest 5: Deleting the first file:")
            client.request_delete_file(client.backup_files[0])

        # 6. Attempt to retrieve the deleted file
        if client.backup_files:
            print("\nTest 6: Attempting to retrieve the deleted file:")
            client.request_retrieve_file(client.backup_files[0])

        # 7. List files after deletion
        print("\nTest 7: Listing files after deletion:")
        client.request_list_files()

    except Exception as e:
        print("An error occurred during testing:", e)
    finally:
        client.close()

if __name__ == "__main__":
    run_tests()
