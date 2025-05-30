import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import argparse
from file_protocol import  FileProtocol
fp = FileProtocol()


class ProcessClient(threading.Thread):
    DELIMITER = b"\r\n\r\n"
    
    def __init__(self, connection, address, pool):
        super().__init__()
        self.connection = connection
        self.address = address
        self.pool = pool

    def run(self):
        try:
            buffer = b""
        
            while True:
                chunk = self.connection.recv(2**20)
                if not chunk:
                    break
                buffer += chunk
                if self.DELIMITER in buffer:
                    break
                
            if buffer:
                data = buffer.decode()
                tokens = data.strip().split("\r\n\r\n")[0]
                command = tokens.strip()
                future = self.pool.submit(fp.process_string, command)
                hasil = future.result() + "\r\n\r\n"
                self.connection.sendall(hasil.encode())
                    
        except Exception as e:
            logging.exception(f"Error: {str(e)}")
        finally:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6667)
    parser.add_argument("--mode", choices=["thread", "process"], default="thread")
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    
    logging.warning(f"Server mode: {args.mode} pool, workers={args.workers}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.ip, args.port))
    sock.listen(100)
        
    if args.mode == "thread":
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            while True:
                try:
                    conn, addr = sock.accept()
                    logging.warning(f"Connection from {addr}")
                    handleClient = ProcessClient(conn, addr, pool)
                    handleClient.start()
                except KeyboardInterrupt:
                    logging.warning("Shutting down server...")
                    break
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            while True:
                try:
                    conn, addr = sock.accept()
                    logging.warning(f"Connection from {addr}")
                    handleClient = ProcessClient(conn, addr, pool)
                    handleClient.start()
                except KeyboardInterrupt:
                    logging.warning("Shutting down server...")
                    break
    
    

if __name__ == "__main__":
    main()

