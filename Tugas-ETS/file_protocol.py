import json
import logging
# import shlex

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""



class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def process_string(self, string_datamasuk=''):
        tokens = string_datamasuk.strip().split()
        if not tokens:
            return json.dumps({"status": "ERROR", "data": "Empty command"})
        # logging.warning(f"string diproses: {string_datamasuk}")
        logging.info(f"Received command: {tokens[:3] if len(tokens) > 3 and len(tokens[3]) <= 100 else tokens[:2]}")
        
        command = tokens[0].strip().upper()
        if command == "LIST":
            return json.dumps(self.file.list())
        elif command == "GET":
            if len(tokens) < 2:
                return json.dumps({"status": "ERROR", "data": "filename required"})
            print(tokens[0], tokens[1])
            return json.dumps(self.file.get(tokens[1]))
        elif command == "UPLOAD":
            if len(tokens) < 3:
                return json.dumps({"status": "ERROR", "data": "filename and content required"})
            return json.dumps(self.file.upload(tokens[1:3]))
        elif command == "DELETE":
            if len(tokens) < 2:
                return json.dumps({"status": "ERROR", "data": "filename required"})
            return json.dumps(self.file.delete(tokens[1]))
        else:
            return json.dumps({"status": "ERROR", "data": "Unknown command"})

if __name__=='__main__':
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.process_string("LIST"))
    print(fp.process_string("GET kipli.jpg"))
    print(fp.process_string("UPLOAD kipli.jpg dGhpcyBpcyBhIHRlc3Q="))
    print(fp.process_string("DELETE kipli.jpg"))
