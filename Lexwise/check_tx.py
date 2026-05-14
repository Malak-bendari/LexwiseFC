from app import create_app
from app.models.transaction import Transaction

app = create_app()

with app.app_context():
    txs = Transaction.query.all()
    print("All TXs in DB:", len(txs))
    for t in txs:
        print(t.id, t.amount, t.category, "User:", t.user_id)
