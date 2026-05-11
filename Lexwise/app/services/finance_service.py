class FinanceService:
    def __init__(self):
        pass

    def calculate_expenses(self, transactions):
        return sum(transaction.amount for transaction in transactions)
