# arq

pasos pa levantar el back pq se me olvida siempre:

- docker compose up -d
- cd backend
- python -m venv .venv
- .venv\Scripts\activate
- pip install -r requirements.txt
- uvicorn main:app --reload
