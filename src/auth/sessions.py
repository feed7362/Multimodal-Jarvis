import json
from fastapi import Request, Response
import uuid
from src.auth.models import GradioSession
from src.database import AsyncSession

def save_session(user_id: str, session_id: str, state: dict):
    db = AsyncSession()
    session = db.query(GradioSession).filter_by(session_id=session_id).first()

    if session:
        session.state = json.dumps(state)
    else:
        session = GradioSession(session_id=session_id, user_id=user_id, state=json.dumps(state))
        db.add(session)

    db.commit()
    db.close()

def load_session(session_id: str) -> dict:
    db = AsyncSession()
    session = db.query(GradioSession).filter_by(session_id=session_id).first()
    db.close()

    return json.loads(session.state) if session else {}



def get_or_create_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    return session_id
