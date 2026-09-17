import traceback
from app.db.session import SessionLocal
from app.api.v1.routes_auth import login
from fastapi.security import OAuth2PasswordRequestForm

db = SessionLocal()
form_data = OAuth2PasswordRequestForm(
    grant_type="password",
    username="admin@college.edu",
    password="admin123",
    scope="",
    client_id=None,
    client_secret=None
)

try:
    res = login(form_data=form_data, db=db)
    print("Success:", res)
except Exception as e:
    traceback.print_exc()
finally:
    db.close()
