[toc]

## 前后端传输格式

比如说这个例子
```json
{
    "status": 0,
    "data": {
        "id": 1,
        "name": "Build shader",
        "file_size": "29101823",
        "sumbit_user": "John"
    },
    "message": "User details retrieved successfully."
}
```

* `status`: `int` 类型. 非 0 代表错误码
* `data`: `Dictionary` 类型. 具体返回类型与接口绑定
* `message`: `String` 类型. 返回的具体处理的内容
