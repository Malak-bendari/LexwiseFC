from app import create_app
from app.database.db import db
from app.models.user import User
from app.models.transaction import Transaction

app = create_app()

with app.app_context():
    user = User.query.first()
    if not user:
        print("No user")
    else:
        print(f"Transactions for user {user.name}:")
        txs = Transaction.query.filter_by(user_id=user.id).all()
        for t in txs:
            print(f"- {t.amount} {t.category} ({t.transaction_type})")
        if not txs:
            print("0 transactions found in DB.")
