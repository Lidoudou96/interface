import  os,sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#print(BASE_PATH)
sys.path.insert(0,BASE_PATH)#将项目根路径加入环境变量
from lib.interfaces import server
from conf.settings import SERVER_PORT

if __name__=='__main__':
    server.run(host='127.0.0.2',port=SERVER_PORT,debug=True)#启动服务