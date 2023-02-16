'''
消息格式
'''


from flask import jsonify


# 生成的信息结构体
def generate_req_body(status:int , data:dict|list|None, message: str|None):
    if data == None:
        data = {}
    if message == None:
        message = ''
    return jsonify(
            {
                'status':status,
                'data':data,
                'message':message
                }
            )

# 生成错误信息
def generate_error_message(err_code:int, message:str):
    return generate_req_body(status=err_code, data=None, message=message)
