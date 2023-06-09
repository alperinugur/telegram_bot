call venv\Scripts\activate 

:loopstart
python TeleBot_Async.py
timeout /t 5

goto loopstart
