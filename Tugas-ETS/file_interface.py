import os
import base64
from glob import glob
import logging

class FileInterface:
    def __init__(self, basePath="./files"):
        if not os.path.exists(basePath):
            os.makedirs(basePath)
            
        self.basePath = basePath
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def list(self,params=[]):
        try:
            fileList = glob("*.*", root_dir=self.basePath)
            return dict(status='OK',data=fileList)
        except Exception as e:
            logging.error(f"Error listing files: {str(e)}")
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            fileName = params
            logging.info(f"GET request for file: {fileName}")
            
            if not fileName:
                logging.error("GET called with no filename parameter")
                return dict(status='ERROR', data='Missing parameter: fileName is required')
            
            filePath = os.path.join(self.basePath, fileName)
            if not os.path.exists(filePath):
                logging.error(f"File {fileName} not found")
                return dict(status='ERROR', data=f"File {fileName} not found")
            
            logging.info(f"Reading file {fileName} for GET request")
            
            with open(filePath, 'rb') as fp:
                content = fp.read()
            
            logging.info(f"File {fileName} found, start encoding content...")
            encodedContent = base64.b64encode(content).decode()
            encodedContentSize = len(encodedContent)
            logging.info(f"Successfully encoded content, encoded size: {encodedContentSize} bytes")
            
            return dict(status='OK',data_namafile=fileName,data_file=encodedContent)
        except Exception as e:
            return dict(status='ERROR',data=f"Unexpected error on GET method: {str(e)}")
        
    def upload(self,params=[]):
        try:
            fileName = params[0]
            fileData = params[1]
            if not fileName or not fileData:
                return dict(status='ERROR', data='Missing parameters: fileName and fileData are required')
            
            logging.info(f"Received upload request for file: {fileName}")
            logging.info(f"Encoded content size: {len(fileData)} bytes")
            
            missingPadding = len(fileData) % 4
            if missingPadding:
                fileData += '=' * (4 - missingPadding)
                
            filePath = os.path.join(self.basePath, fileName)
            
            logging.info(f"Writing file {fileName}: {len(fileData)} bytes")
            
            with open(f"{filePath}", 'wb') as fp:
                fp.write(base64.b64decode(fileData))
                
            
            if os.path.exists(filePath):
                logging.info(f"File {fileName} uploaded successfully")
                return dict(status="OK", data=f"{fileName} uploaded successfully")
            else:
                logging.error(f"File {fileName} upload failed")
                return dict(status="ERROR", data=f"Failed to upload file {fileName}")
        except Exception as e:
            return dict(status='ERROR',data=f"Unexpected error on UPLOAD method {fileName}: {str(e)}")
        
    def delete(self,params=[]):
        try:
            fileName = params
            if not fileName:
                logging.error("Missing fileName parameter for delete operation")
                return dict(status='ERROR', data='Missing parameter: fileName is requiered')
            
            logging.info(f"DELETE request for file: {fileName}")
            filePath = os.path.join(self.basePath, fileName)
            
            if not os.path.exists(filePath):
                logging.error(f"File {fileName} not found")
                return dict(status="ERROR", data= f"File {fileName} not found")
            
            logging.info(f"Attempting to delete file {fileName}")
            os.remove(filePath)
            
            if os.path.exists(filePath):
                logging.error(f"Failed to delete file {fileName}")
                return dict(status="ERROR", data=f"Failed to delete file {fileName}")
            
            logging.info(f"File {fileName} deleted successfully")
            return dict(status="OK", data=f"{fileName} delete successfully")
            
        except IndexError:
            return dict(status='ERROR', data='Format Delete: delete <filename>')
        except Exception as e:
            logging.error(f"Unexpected error on DELETE method {fileName}: {str(e)}")
            return dict(status='ERROR',data=f"Unexpected error on DELETE method {fileName}: {str(e)}")
        
if __name__=='__main__':
    f = FileInterface()
    # print(f.list())
    # print(f.get(['pokijan.jpg']))
    # print(f.get(['10MB.txt']))
    print(f.delete(['10MB.txt']))
    