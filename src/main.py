import socket
import paramiko
import threading
import time


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
        pass


def http_lure(log):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind(('0.0.0.0', 80))
        server_socket.listen(5)
        print("[*] HTTP Lure est en ligne sur le port 80")
    except Exception as e:
        print(f"[-] Erreur HTTP Lure : {e}")
        return

    while True:
        client, addr = server_socket.accept()
        data=client.recv(1024).decode(errors='ignore')

        request_line = data.splitlines()[0] if data else "Requête vide"
        log.log_attempt(addr[0],"HTTP","WebScanner",request_line, "Browser")

        #Fake Page de Log
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
        response += "<html><body><h1>Admin Panel</h1><form>User: <input><br>Pass: <input type='password'></form></body></html>"
        client.send(response.encode())
        client.close()
    
    



def ssh_listener():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 2222))
    server_socket.listen(100)

    print(f"[*] AttackMyLure est en ligne sur le port 2222")

    while True:
        client , addr = server_socket.accept()

        t = threading.Thread(target=handle_conn , args=(client , addr[0] , log , hostKey))
        t.start()

def start_server():
    log = AttackLogger()
    hostKey = paramiko.RSAKey.generate(2048)

            # On lance le thread SSH
    threading.Thread(target=ssh_listener, daemon=True).start()

            # On lance le thread HTTP
    threading.Thread(target=http_lure, args=(log,), daemon=True).start()

    print("[*] Système Multi-Leurre activé. Bonne chasse !")

            # Boucle infinie pour empêcher le script de s'arrêter
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Fermeture du Honeypot...")

if __name__ == '__main__':
    start_server()
