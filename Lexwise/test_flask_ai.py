from app import create_app
from app.services.ai_service import AIService
from app.database.db import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Force a dummy user id
    user = User.query.first()
    if user:
        print(f"Testing with user: {user.name} (ID: {user.id})")
        result = AIService.answer_user_question(user.id, "Bilan du mois ?")
        print("Result:", result)
    else:
        print("No user found in DB.")
