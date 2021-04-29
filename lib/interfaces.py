import flask
import time

from lib.tools import conn_mysql, md5_passwd, op_redis
from flask import request, make_response  # 获取请求参数
from flask import send_from_directory, jsonify

server = flask.Flask(__name__)  # 把这个python文件当做一个web服务
server.config['JSON_AS_ASCII'] = False  # jsonify返回的中文正常显示


# 传json
# 传json
@server.route('/register1',methods=['get','post'])  # 第一个参数是接口的路径，第二个参数是请求方式
def reg():
    username = request.json.get("username").strip()  # 必填
    password = request.json.get("password").strip()  # 必填
    realname = request.json.get('realname', '').strip()  # 必填
    sex = request.json.get('sex', '0').strip()  # 非必填
    phone = request.json.get('phone', '').strip()  # 必填
    # u_type = request.json.get('type', '1')

    if username and password and realname and phone:
        res = conn_mysql('select username from users where username="%s";' % username)
        print(res)  # 如果数据库中没有请求的用户数据，返回None
        if res:
            if 'code' not in res:
                return '{"code":9310,"msg":"用户已经存在"}'
            else:
                return jsonify(res)
        elif len(password) < 6 or len(password) > 12:
            return '{"code":9320, "msg":"密码只能6-12位"}'
        elif not (sex == '0' or sex == '1'):
            return '{"code":9340, "msg":"性别只能是0（male）或者1(female)"}'
        elif not (phone.isdigit() and len(phone) == 11):
            return '{"code":9350, "msg":"手机号格式不正确"}'
        elif conn_mysql('select phone from users where phone="%s";' % phone):
            return '{"code":9360, "msg":"手机号已被注册"}'
        else:
            password = md5_passwd(password)  # 调用加密函数
            sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");' % (
            username, password, realname, sex, phone, '1', username)
            conn_mysql(sql)
            return '{"code":9370,"msg":"恭喜，注册成功！"}'
    else:
        return '{"code":9300,"msg":"必填参数（username，password，realname,phone）都不能为空"}'

        # 传k_v
@server.route('/register2',methods=['get','post'])
def reg2():
    print(request.values)
    username = request.values.get("username", '').strip()#必填
    password = request.values.get("password", '').strip()#必填
    realname = request.values.get('realname', '').strip()  # 必填
    sex = request.values.get('sex', '0').strip()  # 非必填
    phone = request.values.get('phone', '').strip()  # 必填
    # u_type = request.jsom.get('type','1')

    if username and password and realname and phone:
        if conn_mysql('select username from users where username ="%s";'% username):
            return jsonify ({"code":9310,"msg":"用户已经存在"})
        elif len(password)<6 or len(password)>12:
            return jsonify ({"code":9320, "msg":"密码只能6-12位"})
        elif not(sex=='0' or sex=='1'):
            return jsonify ({"code":9340, "msg":"性别只能是0（male）或者1(female)"})
        elif not (phone.isdigit() and len(phone)==11):
            return jsonify ({"code":9350, "msg":"手机号格式不正确"})
        elif conn_mysql('select phone from users where phone="%s";'%phone):
            return jsonify ({"code":9360, "msg":"手机号已被注册"})
        else:
            password = md5_passwd(password)  # 调用加密函数
            sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");'%(username,password,realname,sex,phone,'1',username)
            conn_mysql(sql)
            return  jsonify ({"code":9370,"msg":"恭喜，注册成功！"})
    else:
        return jsonify ({"code":9300,"msg":"必填参数（username，password，realname,phone）都不能为空"})


# 登录，可以get，也可以post
@server.route('/login', methods=['get', 'post'])
def login():
    username = request.values.get('username', '').strip()
    passwd = request.values.get('password', '').strip()
    if username and passwd:
        #passwd = md5_passwd(passwd)
        sql = 'select id,username from users where username="%s" and password="%s"' % (username, passwd)
        sql_res = conn_mysql(sql)  # 获取查询结果
        print('sql_res：', sql_res)
        if sql_res:
            token_str = username + str(int(time.time()))  # 用户名+时间戳
            token = md5_passwd(token_str)  # md5后的token
            op_redis(username,token)  # 放到redis中
            # 下面三行，真实开发代码会这样写，这样可以在客户端浏览器设置cookie（如果是postman发请求，会在postman中设置cookie）
            response = make_response('{"code":9420, "msg":"恭喜%s，登录成功","token":"%s"}' % (username, token))
            response.set_cookie(username,token)  # 设置cookie
            return response
            # return '{"code":9420, "msg":"恭喜%s，登录成功","token":"%s"}'%(username,token)
        else:
            # return '{"code":9410,"msg":"用户名或密码不正确"}'
            # return json.dumps({"code":9410,"msg":"用户名或密码不正确"},ensure_ascii=False)
            return jsonify({"code": 9410,
                            "msg": "用户名或密码不正确"})  # jmeter请求，中文响应乱码（需要加上server.config['JSON_AS_ASCII'] = False）；postman请求，中文正常显示

    else:
        return jsonify({"code":9400,"msg":"用户名和密码不能为空"})



    # 添加用户，data和token都在body中，body是k-v
@server.route('/add_user1', methods=['post'])
def add_user1():
        token = request.values.get('token', '').strip()  # 必填
        adduser = request.values.get('adduser', '').strip()  # 必填
        username = request.values.get("username").strip()  # 必填
        realname = request.values.get('realname', '').strip()  # 必填
        sex = request.values.get('sex', '0').strip()  # 非必填
        phone = request.values.get('phone', '').strip()  # 必填

        if token and adduser and username and realname and phone:
            if sex != '1' and sex != '0':
                return '{"code":9340, "msg":"性别只能是0（male）或者1(female)"}'
            elif not (phone.isdigit() and len(phone) == 11):
                return '{"code":9350, "msg":"手机号格式不正确"}'
            else:
                redis_sign = op_redis(adduser)  # 从redis里面取到token
                print('redis_sign：', redis_sign)
                if redis_sign:
                    if redis_sign.decode() == token:
                        select_sql = 'select utype from users where adduser="%s"' % adduser
                        print('select_sql：', select_sql)
                        res = conn_mysql(select_sql)['utype']
                        # print(res,type(res))
                        if res == 1:
                            return '{"code":9540,"msg":"你是普通用户，无权限添加用户"}'
                        else:
                            if conn_mysql('select username from users where username="%s";' % username):
                                return '{"code":9310,"msg":"用户已经存在"}'
                            else:
                                select_sql = 'select phone from users where phone="%s"' % phone
                                if conn_mysql(select_sql):
                                    return '{"code":9360, "msg":"手机号已被注册"}'
                                else:
                                    password = md5_passwd('123456')  # 默认密码123456
                                    sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");' % (
                                    username, password, realname, sex, phone, '1', adduser)
                                    conn_mysql(sql)
                                    return '{"code":9550,"msg":"添加用户成功。"}'
                    else:
                        return '{"code":9560,"msg":"token错误"}'
                else:
                    return '{"code":9510,"msg":"未登录"}'
        else:
            return '{"code":9500,"msg":"必填参数（token，username，realname，phone，adduser）不能为空"}'


    # 添加用户，cookie中传token，data传json
    # {"username":"test6","realname":"test6","sex":"1","phone":"13800000006","adduser":"qzcsbj1"}
@server.route('/add_user2', methods=['post'])
def add_stu2():
        token = request.cookies.get('token')  # 从cookie里面获取到token
        print('cookies:', request.cookies)
        print('传过来的headers是：', request.headers)
        print(request.json)
        adduser = request.json.get('adduser', '')  # 必填
        username = request.json.get('username', '')  # 必填
        realname = request.json.get('realname', '')  # 必填
        sex = request.json.get('sex', '0')  # 非必填
        phone = request.json.get('phone', '')  # 必填
        if token and adduser and username and realname and phone:
            if sex != '1' and sex != '0':
                return '{"code":9340, "msg":"性别只能是0（male）或者1(female)"}'
            elif not (phone.isdigit() and len(phone) == 11):
                return '{"code":9350, "msg":"手机号格式不正确"}'
            else:
                redis_sign = op_redis(adduser)
                if redis_sign:
                    if redis_sign.decode() == token:
                        select_sql = 'select utype from users where adduser="%s"' % adduser
                        res = conn_mysql(select_sql)['utype']
                        # print(res,type(res))
                        if res == 1:
                            return '{"code":9540,"msg":"你是普通用户，无权限添加用户"}'
                        else:
                            if conn_mysql('select username from users where username="%s";' % username):
                                return '{"code":9310,"msg":"用户已经存在"}'
                            else:
                                select_sql = 'select phone from users where phone="%s"' % phone
                                if conn_mysql(select_sql):
                                    return '{"code":9360, "msg":"手机号已被注册"}'
                                else:
                                    password = md5_passwd('123456')
                                    sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");' % (
                                    username, password, realname, sex, phone, '1', adduser)
                                    conn_mysql(sql)
                                    return '{"code":9550,"msg":"添加用户成功。"}'
                    else:
                        return '{"code":9560,"msg":"token错误"}'
                else:
                    return '{"code":9510,"msg":"未登录"}'
        else:
            return '{"code":9500,"msg":"必填参数（token，username，realname，phone，adduser）不能为空"}'

    # 添加用户，cookie中传token，data传json，添加的用户信息在嵌套字典中
    # {"adduser":"qzcsbj","data":{"username":"test9","realname":"test9","sex":"1","phone":"13800000009"}}
@server.route('/add_user3', methods=['post'])
def add_stu3():
        token = request.cookies.get('token')
        print('cookies:', request.cookies)
        print('传过来的headers是：', request.headers)
        print('传过来的json是：',request.json)
        adduser = request.json.get('adduser', '')# 必填
        print('传过来的adduser是：', adduser)
        data = request.json.get('data')
        print('传过来的data是：',data, type(data))
        username = request.json.get('data').get('username', '')  # 必填
        realname = request.json.get('data').get('realname', '')  # 必填
        sex = request.json.get('data').get('sex', '0')  # 非必填
        phone = request.json.get('data').get('phone', '')  # 必填
        print('传过来的数据是：',adduser, username, realname, sex, phone)
        if  adduser and username and realname and phone:
            if sex != '1' and sex != '0':
                return '{"code":9340, "msg":"性别只能是0（male）或者1(female)"}'
            elif not (phone.isdigit() and len(phone) == 11):
                return '{"code":9350, "msg":"手机号格式不正确"}'
            else:
                redis_sign = op_redis(adduser)
                if redis_sign:
                    if redis_sign.decode() == token:
                        select_sql = 'select utype from users where adduser="%s"' % adduser
                        print(select_sql, type(select_sql))
                        res = conn_mysql(select_sql)['utype']
                        print(res,type(res))
                        if res == 1:
                            return '{"code":9540,"msg":"你是普通用户，无权限添加用户"}'
                        else:
                            if conn_mysql('select username from users where username="%s";' % username):
                                return '{"code":9310,"msg":"用户已经存在"}'
                            else:
                                select_sql = 'select phone from users where phone="%s"' % phone
                                if conn_mysql(select_sql):
                                    return '{"code":9360, "msg":"手机号已被注册"}'
                                else:
                                    password = md5_passwd('123456')
                                    sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");' % (
                                    username, password, realname, sex, phone, '1', adduser)
                                    conn_mysql(sql)
                                    return '{"code":9550,"msg":"添加用户成功。"}'
                    else:
                        return '{"code":9560,"msg":"token错误"}'
                else:
                    return '{"code":9510,"msg":"未登录"}'
        else:
            return '{"code":9500,"msg":"必填参数（username，realname，phone，adduser）不能为空"}'

    # 添加用户，data和token都在body中，body是json
    # {"token":"dcf6455d20a8cb01b573e0838cb79e7a","username":"test6","realname":"test6","sex":"1","phone":"13800000006","adduser":"qzcsbj"}
@server.route('/add_user4', methods=['post'])
def add_stu4():
        token = request.json.get('token')  # 从cookie里面获取到token
        adduser = request.json.get('adduser', '')  # 必填
        username = request.json.get('username', '')  # 必填
        realname = request.json.get('realname', '')  # 必填
        sex = request.json.get('sex', '0')  # 非必填
        phone = request.json.get('phone', '')  # 必填
        if token and adduser and username and realname and phone:
            if sex != '1' and sex != '0':
                return '{"code":9340, "msg":"性别只能是0（male）或者1(female)"}'
            elif not (phone.isdigit() and len(phone) == 11):
                return '{"code":9350, "msg":"手机号格式不正确"}'
            else:
                redis_sign = op_redis(adduser)
                if redis_sign:
                    if redis_sign.decode() == token:
                        select_sql = 'select utype from users where adduser="%s"' % adduser
                        res = conn_mysql(select_sql)['utype']
                        # print(res,type(res))
                        if res == 1:
                            return '{"code":9540,"msg":"你是普通用户，无权限添加用户"}'
                        else:
                            if conn_mysql('select username from users where username="%s";' % username):
                                return '{"code":9310,"msg":"用户已经存在"}'
                            else:
                                select_sql = 'select phone from users where phone="%s"' % phone
                                if conn_mysql(select_sql):
                                    return '{"code":9360, "msg":"手机号已被注册"}'
                                else:
                                    password = md5_passwd('123456')
                                    sql = 'insert into users(username,password,realname,sex,phone,utype,addtime,adduser) values ("%s","%s","%s","%s","%s","%s",now(),"%s");' % (
                                    username, password, realname, sex, phone, '1', adduser)
                                    conn_mysql(sql)
                                    return '{"code":9550,"msg":"添加用户成功。"}'
                    else:
                        return '{"code":9560,"msg":"token错误"}'
                else:
                    return '{"code":9510,"msg":"未登录"}'
        else:
            return '{"code":9500,"msg":"必填参数（token，username，realname，phone，adduser）不能为空"}'

                            # 删除用户
                            # 略，自己完成了哈