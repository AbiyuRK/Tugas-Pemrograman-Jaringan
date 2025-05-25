import socket
import json
import base64
import logging
import os

server_address=('0.0.0.0',7777)

def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall((command_str + "\r\n\r\n").encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(4096)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received.split("\r\n\r\n")[0])
        logging.warning("data received from server:")
        return hasil
    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error: {e} | Raw data: {data_received}")
        print(f"Error: Invalid JSON response from server. Raw: {data_received}")
        return {"status": "ERROR", "data": "Invalid JSON response from server."}
    except Exception as e:
        logging.error(f"Error during data receiving/sending: {e}")
        print(f"Error client: {e}")
        return {"status": "ERROR", "data": f"Client error: {e}"}
    finally:
        sock.close()
    # except:
    #     logging.warning("error during data receiving")
    #     return False


def remote_list():
    command_str=f"LIST"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal")
        return False

def remote_get(filename=""):
    command_str=f"GET {filename}"
    hasil = send_command(command_str)
    if (hasil['status']=='OK'):
        #proses file dalam bentuk base64 ke bentuk bytes
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        fp = open(namafile,'wb+')
        fp.write(isifile)
        fp.close()
        return True
    else:
        print("Gagal")
        return False

def remote_upload(filepath="", filename=""):
    if not filepath or not filename:
        print("Format Upload : upload <local_filepath> <remote_filename>")
        return False
    
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} tidak dapat ditemukan.")
        return False
    
    try:
        fp = open(filepath, 'rb')
        content = base64.b64encode(fp.read()).decode()
        fp.close()
        
        hasil = send_command(f"UPLOAD {filename} {content}")
        if hasil['status'] == 'OK':
            print(f"{hasil['data']}")
            return True
        else:
            print(f"File {filename} gagal diupload: {hasil['data']}")
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

if __name__=='__main__':
    server_address=('172.16.16.101',7777)
    
    print("Selamat datang di Client CLI")
    print("Ketik 'help' untuk melihat daftar perintah yang tersedia.")
    while True:
        user_input = input(">>> ").strip()
        if not user_input:
            continue
        
        input_parts = user_input.split(" ", 1)
        req = input_parts[0].lower()
        args = input_parts[1] if len(input_parts) > 1 else ""
        
        if req == "list":
            remote_list()
        elif req == "get":
            remote_get(args)
        elif req == "upload":
            param = args.split(" ", 1)
            if len(param) != 2:
                print("Kesalahan input. Format Upload : upload <local_filepath> <remote_filename>")
                continue
            remote_upload(param[0], param[1])
        elif req == "delete":
            remote_delete(args)
        elif req == "exit":
            print("Keluar dari program.")
            break
        elif req == "help":
            print("Daftar perintah:")
            print("- list: Menampilkan daftar file di server.")
            print("- get <filename>: Mengunduh file dari server.")
            print("- upload <local_filepath> <remote_filename>: Mengunggah file ke server.")
            print("- delete <filename>: Menghapus file di server.")
            print("- exit: Keluar dari program.")
        else:
            print("Perintah tidak dikenali. Ketik 'help' untuk melihat daftar perintah yang tersedia.")

