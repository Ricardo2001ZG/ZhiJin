set PATH=%PATH%;%cd%\env\python-3.11.2-embed-amd64;%cd%\env\python-3.11.2-embed-amd64\Scripts;
cmd /c "env\python-3.11.2-embed-amd64\python -m pip install -i https://mirrors.cloud.tencent.com/pypi/simple --upgrade pip"
cmd /c "pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple"
cmd /c "pip install virtualenv"
cmd /c "virtualenv venv_zhijin_flask_server"
cmd /c "venv_zhijin_flask_server\Scripts\activate.bat"
cmd /c "pip install -r requirements.txt"
pause
