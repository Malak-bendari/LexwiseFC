from app import create_app
from app.database.db import db
from app.models.user import User
from app.models.transaction import Transaction

app = create_app()

with app.app_context():
    user = User.query.first()
    print("User:", user)
    
    t = Transaction(
        user_id=user.id,
        amount=150.0,
        category="Groceries",
        description="Test script",
        transaction_type="expense"
    )
    db.session.add(t)
    db.session.commit()
    print("Transaction added manually! ID:", t.id)
    
    txs = Transaction.query.filter_by(user_id=user.id).all()
    for tx in txs:
        print(tx.id, tx.amount, tx.category)
