from abc import ABC, abstractmethod

class Order:
    items = []
    quantities = []
    prices = []
    status = "open"

    def add_item(self, item, quantity, price):
        self.items.append(item)
        self.quantities.append(quantity)
        self.prices.append(price)
    
    def total_price(self):
        return sum(q * p for q, p in zip(self.quantities, self.prices))

class SMSAuth:
    authorized = False

    def verify_code(self, code):
        print(f"Verifying SMS code: {code}")
        self.authorized = True

    def is_authorized(self) -> bool:
        return self.authorized

class PaymentProcessor(ABC):

    @abstractmethod
    def pay(self, order: str):
        pass

class DebitPaymentProcessor(PaymentProcessor):

    def __init__(self, security_code: str, authorizer: SMSAuth = None):
        self.authorizer = authorizer
        self.security_code = security_code

    def pay(self, order: Order):
        if not self.authorizer or not self.authorizer.is_authorized():
            raise Exception("SMS authentication required for debit payments.")
        print("Processing debit payment...")
        print("validating security code...", {self.security_code})
        order.status = "paid"

class CreditPaymentProcessor(PaymentProcessor):

    def __init__(self, security_code: str):
        self.security_code = security_code
        self.verified = False

    def pay(self, order: Order):
        print("Processing credit payment...")
        print("validating security code...", {self.security_code})
        order.status = "paid"

class PaypalPaymentProcessor(PaymentProcessor):
    def __init__(self, email: str, authorizer: SMSAuth = None):
        self.authorizer = authorizer
        self.email = email

    def pay(self, order: Order):
        if not self.authorizer or not self.authorizer.is_authorized():
            raise Exception("SMS authentication required for PayPal payments.")
        print("Processing PayPal payment...")
        print("validating email...", {self.email})
        order.status = "paid"

order = Order()
order.add_item("item1", 2, 10.0)
order.add_item("item2", 1, 20.0)
order.add_item("item3", 3, 5.0)

authorizer = SMSAuth()
processor = DebitPaymentProcessor("1234", authorizer)
authorizer.verify_code("123456") 
processor.pay(order)
print(order.status)

