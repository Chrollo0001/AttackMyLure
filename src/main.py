import socket
import paramiko
import threading
from logger import AttackLogger
from ssh_module import LureServer
ip_test = "126.253.0.1"
def handle_conn(client , ip_source , log , hostKey):
    transport =  paramiko.Transport(client)
    transport.add_server_key(hostKey)
    server = LureServer(ip_source, log)
    try:
        transport.start_server(server=server)
    except Exception as e:
        print(f"Erreur transport {e}")

def start_server():
    log = AttackLogger()
    hostKey = paramiko.RSAKey.generate(2048)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(100)

    print(f"[*] AttackMyLure est en ligne sur le port 2222")

    while True:
        client , addr = server_socket.accept()

        t = threading.Thread(target=handle_conn , args=(client , addr[0] , log , hostKey))
        t.start()

if __name__ == '__main__':
    start_server()
