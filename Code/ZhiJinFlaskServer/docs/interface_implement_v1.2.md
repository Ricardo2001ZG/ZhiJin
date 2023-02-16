# 接口实现形式
## 目录
---
- [接口实现形式](#接口实现形式)
  - [目录](#目录)
  - [返回资源](#返回资源)
    - [请求方式](#请求方式)
    - [功能描述](#功能描述)
    - [请求参数](#请求参数)
    - [返回参数](#返回参数)
  - [执行自动上传脚本](#执行自动上传脚本)
    - [请求方式](#请求方式-1)
    - [功能描述](#功能描述-1)
    - [请求参数](#请求参数-1)
    - [返回参数](#返回参数-1)
  - [接受任务](#接受任务)
    - [请求方式](#请求方式-2)
    - [功能描述](#功能描述-2)
    - [请求参数](#请求参数-2)
    - [返回参数](#返回参数-2)
  - [执行任务(分发任务)](#执行任务分发任务)
    - [功能描述](#功能描述-3)
    - [请求方式](#请求方式-3)
    - [请求参数](#请求参数-3)
    - [返回参数](#返回参数-3)
  - [监管进度(查看任务进度)](#监管进度查看任务进度)
    - [功能描述](#功能描述-4)
    - [请求方式](#请求方式-4)
    - [请求参数](#请求参数-4)
    - [返回参数](#返回参数-4)
  - [停止任务](#停止任务)
    - [功能描述](#功能描述-5)
    - [请求方式](#请求方式-5)
    - [请求参数](#请求参数-5)
    - [返回参数](#返回参数-5)
  - [删除任务](#删除任务)
    - [功能描述](#功能描述-6)
    - [请求方式](#请求方式-6)
    - [请求参数](#请求参数-6)
    - [返回参数](#返回参数-6)
  - [获取任务](#获取任务)
    - [功能描述](#功能描述-7)
    - [请求方式](#请求方式-7)
    - [请求参数](#请求参数-7)
    - [返回参数](#返回参数-7)


## 返回资源
---
### 请求方式

* URL: `/return`
* Method: [POST][Json]

### 功能描述 
返回某任务的产物列表

### 请求参数
```json
{
  "taskId":"f42ce86d-4279-47c0-99ff-ea020fece054"
}
```

> 参数说明
* `taskId`: 由`UUID` v4生成的唯一值

### 返回参数

```json
[ // 注意此处为List 类型，会返回0个或多个
  {
    "fileName":"文件名称",
    "fileSize":文件大小,
    "filePath":"文件下载地址，比如 https://xxx.com/fileStorage/[MD5]",
    "MD5":"文件MD5校验值",
    "timestamp":"文件上传日期,比如 2023-02-08-15-46-00"
  }
]
```

> 参数说明
* `fileName`: 文件名称
* `fileSize`: 文件大小
* `filePath`: 文件下载路径
* `MD5`: 文件的MD5校验值
* `timestamp`: 文件的生成时间


## 执行自动上传脚本
---
### 请求方式

URL: `/autoUpload`
Method: [POST][Json]

### 功能描述
将产物的文件上传到某目标地址

### 请求参数

```json
{
  "fileName":"上传文件的名称202302080102_shader.zip",
  "MD5":"43bc3bcab1610b1f3b62d418d7036c1a",
  "fileSize":114515,
  "uploadTarget":"https://xxx.com",
  "timestamp":"2023-02-08-16-11-31"
}
```

> 参数说明
* `uploadTarget`: 上传目标地址
* 其他同上

### 返回参数

```json
{}
```

> 参数
无参数
如果消息体 `status` 为0 则成功
其他数字请查看错误码


## 接受任务

---

### 请求方式

URL: `/submitTask`
Method: [POST][Json]


### 功能描述
创建任务

### 请求参数

```json
{
  "taskName":"Build shader",
  "taskDescription":"<Optional> Create a task for build shader",
  "timestamp":"2023-02-08-15-55-13",
  "repo":"github.com/XXX/",
  "branch":"master",
  "commitId":"<Optional> ed1d512d6521d7a275268ed5b007225429da47f1",
  "operate":"/bin/bash build.sh"
}
```

> 参数说明
* `taskName`: 任务名称
* `taskDescription`: [可选] 任务详情描述
* `taskstamp`: 任务提交时间
* `repo`: 拉取的仓库地址
* `branch`: 拉取仓库的分支。默认为 `master`
* `commitId`: [可选] 拉取特定的commit id
* `operate`: 具体执行的指令

### 返回参数
```json
{
  "taskId":"f42ce86d-4279-47c0-99ff-ea020fece054"
}
```

> 参数说明
* `taskId`: 任务的`UUID`值


## 执行任务(分发任务)

---

### 功能描述
开始执行某项任务，仅对状态为`close`的任务有效

### 请求方式
URL: `/run`
Method: [POST][Json]

### 请求参数
```json
{
  "taskId":2023020801,
  "runner":"windows-robot1",
}
```

> 参数说明
* `taskId`: 具体任务的ID。每个任务都有唯一的ID
* `runner`: 指定具体运行的实例机器

### 返回参数
```json
{
  "timestamp":"2023-02-01-11-22-33"
}
```

>参数说明
* `timestamp` 任务开始运行时间


## 监管进度(查看任务进度)
---
### 功能描述

查看某个任务进度并返回输出内容

### 请求方式
URL: `/job`
Method: [POST][Json]

### 请求参数

```json
{
  "taskId": "f42ce86d-4279-47c0-99ff-ea020fece054"
}
```

> 参数说明
* `taskId`: 任务的`UUID`值

### 返回参数

```json
{
  "taskId":2023020801,
  "startTime":"2023-02-08-15-55-12",
  "feedback": "Build xxx.shader\n Build www.shader\n",
  "status":"running",
}
```

参数说明
* `taskId`: 具体任务的ID。每个任务都有唯一的ID
* `startTime`: 任务开始时间
* `feedback`: 执行任务返回的消息。只捕捉`stdout` 和 `stderr`
* `tasks.task.status`: 执行任务的状态。有 `running`,`done`,`close` 三种状态(待定)


## 停止任务

### 功能描述
停止某个**正在运行**任务

### 请求方式

URL: `/stop`
Method: [POST][Json]

### 请求参数
```json
{
  "taskId":"f42ce86d-4279-47c0-99ff-ea020fece054"
}
```

> 参数说明
* `taskId`: 任务`UUID`值.

### 返回参数
```json
```

无参数
如果消息体的`status` 为0则成功
其他数字请参考错误码和`message`
注: 如果对已经是 `close` 或者 `done` 的任务无任何作用


## 删除任务
---
### 功能描述

删除具体任务

### 请求方式

URL: `/delete`
Method: [POST][Json]

### 请求参数
```json
{
  "taskId": "f42ce86d-4279-47c0-99ff-ea020fece054"
}
```

> 参数说明
* `taskId`: 任务`UUID`值


### 返回参数
```json
{}
```

无参数
如果消息体的`status` 为0则成功
其他数字请参考错误码和`message`
注: 对`running`的任务无效

## 获取任务

---

### 功能描述

获取全部的任务列表

### 请求方式

URL: `/getTasks`
Method: [POST][Json]

### 请求参数
```json
```
无参数

### 返回参数
```json
[
  {
    "taskId":"f42ce86d-4279-47c0-99ff-ea020fece054",
    "timestamp":"2023-02-13-11-22-33",
    "taskName":"Build shader",
    "timestamp":"2023-02-08-15-55-13",
  }
]
```

> 参数说明
* `taskId`: 任务`UUID`值
* `timestamp`: 任务创建时间
* `taskName`: 任务名称
