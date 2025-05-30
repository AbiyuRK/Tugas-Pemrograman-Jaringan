import socket
import json
import base64
import logging
import os
import argparse

server_address=('127.0.0.1', 6667)

DELIMITER = "\r\n\r\n"

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    # logging.warning(f"connecting to {server_address}")
    
    try:
        # logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n\r\n").encode())
        
        data_received = ""
        while True:
            data = sock.recv(2**20)
            if data:
                data_received += data.decode()
                if DELIMITER in data_received:
                    break
            else:
                break
            
        hasil = json.loads(data_received.split(DELIMITER)[0])
        # logging.warning("data received from server:")
        return hasil

    except Exception as e:
        logging.error(f"Error during data receiving/sending: {e}")
        print(f"Error client: {e}")
        # traceback.print_exc()
        return {"status": "ERROR", "data": f"Client error: {e}"}
    finally:
        sock.close()

def remote_list():
    command_str=f"LIST{DELIMITER}"
    hasil = send_command(command_str)
    if hasil['status']=='OK':
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}{DELIMITER}"
    hasil = send_command(command_str)
    fileName = hasil['data_namafile']
    encoded_data = hasil['data_file']
    if hasil and hasil['status'] == 'OK':
        try:
            missing_padding = len(hasil['data_file']) % 4
            if missing_padding: 
                encoded_data += '=' * (4 - missing_padding)
            isifile = base64.b64decode(encoded_data)
            with open(fileName, 'wb+') as fp:
                fp.write(isifile)
            return True
        except Exception as e:
            logging.error(f"Error decoding base64 or writing file: {str(e)}")
            print(f"Error: {e}")
            # traceback.print_exc()
            return False
    
    return False

def remote_upload(filepath=""):
    if not filepath:
        print("Format Upload : upload <filepath>")
        return False
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} tidak dapat ditemukan.")
        return False
    
    try:
        fp = open(filepath, 'rb')
        content = base64.b64encode(fp.read()).decode()
        fp.close()
        
        hasil = send_command(f"UPLOAD {filepath} {content}{DELIMITER}")
        if hasil['status'] == 'OK':
            print(f"{hasil['data']}")
            return True
        else:
            print(f"File {filepath} gagal diupload: {hasil['data']}")
            return False
    except Exception as e:
        print(f"Error saat upload file: {str(e)}")
        return False

def remote_delete(filename=""):
    command_str=f"DELETE {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print(f"{hasil['data']}")
        return True
    else:
        print(f"Gagal menghapus file: {hasil['data']}")
        return False

def main():
    global server_address
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=6667)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list")
    getp = sub.add_parser("get")
    getp.add_argument("filename")
    upp = sub.add_parser("upload")
    upp.add_argument("filepath")
    delp = sub.add_parser("delete")
    delp.add_argument("filename")

    args = parser.parse_args()
    server_address = (args.server, args.port)

    if args.command == "list":
        result = remote_list()
        print("Berhasil list" if result else "Gagal list")
    elif args.command == "get":
        result = remote_get(args.filename)
        print("Sukses download" if result else "Gagal download")
    elif args.command == "upload":
        result = remote_upload(args.filepath)
        print("Sukses upload" if result else "Gagal upload")
    elif args.command == "delete":
        result = remote_delete(args.filename)
        print("Sukses delete" if result else "Gagal delete")
    else:
        parser.print_help()
    

if __name__=='__main__':
    main()
    