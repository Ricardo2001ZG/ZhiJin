#!/bin/bash

pip install pyenv 
pyenv virtualenv flask_api
pyenv activate flask_api
pip install -r requirements.txt

echo "Import finshed..."

