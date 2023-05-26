call venv\Scripts\activate 

python TeleBot_Async.py

pause
timeout /t 10
python TeleBot_Async.py
timeout /t 20
python TeleBot_Async.py