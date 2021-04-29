from conf.settings import *


# 加盐加密
def md5_passwd(str):
    str = str + SALT  # 加盐
    import hashlib
    md = hashlib.md5()  # 构造一个md5对象
    md.update(str.encode())
    res = md.hexdigest()
    return res


# 操作数据库
def conn_mysql(sql):
    import pymysql
    try:
        conn = pymysql.connect(host=MYSQL_HOST,user=USER,password=PASSWORD,db=DB,charset='utf8',port=MYSQL_PORT)
    except Exception as e:
        print('mysql连接出错,错误信息为%s'%e)
        res = {"code":9901,"msg":'mysql连接出错,错误信息为%s'%e}
    else:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    try:
        cur.execute(sql)
    except Exception as e:
        msg = "sql执行出错，请检查sql,错误信息为：%s"%e
        res = {"code":9902,"msg":msg}
    else:
        res = cur.fetchone()
        conn.commit()
    finally:
        cur.close()
        conn.close()
        print("res:",res)
        return res


# 操作redis
def op_redis(k, v=None):
    import redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    if v:  # v是真，表明是set，否则是get
        r.setex(k, EX_TIME,v)  # 时间是秒，等同于set name jack ex 10
    else:
        return r.get(k)