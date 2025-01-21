from client_test import BackupClient

def main():
    client = BackupClient()
    try:
        client.read_server_info()
        client.connect()
        client.request_save_file("maman14/modules.txt")
        #client.backup_file("maman14/demofile.txt")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    main()