## 安装python3.8+
## 安装依赖
  ```shell
    pip install -r requirements
  ```
  若下载超时，修改pip源```%HOMEPATH%\pip\pip.ini```
  ```  
    [global]
    index-url = http://mirrors.aliyun.com/pypi/simple/
    [install]
    trusted-host = mirrors.aliyun.com
  ```
## 运行
```shell
  py index.py
```
显示 ```
Running on http://localhost:5000/ (Press CTRL+C to quit)```则说明运行成功

## 调用
```
  [POST]http://localhost:5000/details
```