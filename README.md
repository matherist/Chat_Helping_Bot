### How to start
- `py -m venv venv`
- `source venv/bin/activate` or `.\venv\Scripts\activate.bat`
- `pip install -r requirements.txt`
#### For development
- `uvicorn app:app --reload` for DEVELOPMENT server
#### For server
- `pip install gunicorn`