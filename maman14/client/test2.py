from backup_client import BackupClient

def run_tests():
    client = BackupClient()
    client.read_server_info()
    client.connect()
    client.test_simple_message()
    client.close()

if __name__ == "__main__":
    run_tests()