import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.chdir('files/')

    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
    def put(self,params=[]):
        try:
            filename = params[0]
            data_file = params[1]
            if (filename == '' or data_file == ''):
                return dict(status='ERROR', data='Parameter filename atau data_file tidak lengkap')
            
            with open(f"{filename}", 'wb+') as fp:
                fp.write(base64.b64decode(data_file))
                
            return dict(status='OK', data=filename)
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
    def delete(self,params=[]):
        try:
            filename = params[0]
            if not filename:
                return dict(status='ERROR', data='Filename tidak boleh kosong')
            if os.path.exists(filename):
                os.remove(filename)
                return dict(status='OK',data=filename)
            else:
                return dict(status='ERROR', data='File tidak ditemukan')
        except IndexError:
            return dict(status='ERROR', data='Format DELETE: DELETE <filename>')
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
if __name__=='__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))
