# Compounding Quest (FastAPI)

A gamified explainer of compound interest for four age profiles, with myth-busting, investor benefits, a quiz, and an XP system.

Run
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

Open http://127.0.0.1:8000 (API docs: http://127.0.0.1:8000/docs)

Structure
main.py FastAPI app: content (profiles, myths, quiz) + compound-interest engine
templates/index.html Jinja2 page with the games (vanilla JS, no external libraries)

Educational use only. Rates shown are assumptions, not guaranteed returns.
