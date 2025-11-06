#!/bin/bash

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 서버 실행
echo "Starting backend server..."
python main.py


