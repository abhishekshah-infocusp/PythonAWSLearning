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

class PaymentProcessor(ABC):

    @abstractmethod
    def pay(self, order: str):
        pass

class DebitPaymentProcessor(PaymentProcessor):

    def __init__(self, security_code: str):
        self.security_code = security_code

    def pay(self, order: Order):
        print("Processing debit payment...")
        print("validating security code...", {self.security_code})
        order.status = "paid"

class CreditPaymentProcessor(PaymentProcessor):

    def __init__(self, security_code: str):
        self.security_code = security_code


    def pay(self, order: Order):
        print("Processing credit payment...")
        print("validating security code...", {self.security_code})
        order.status = "paid"

class PaypalPaymentProcessor(PaymentProcessor):
    def __init__(self, email: str):
        self.email = email

    def pay(self, order: Order):
        print("Processing PayPal payment...")
        print("validating email...", {self.email})
        order.status = "paid"

order = Order()
order.add_item("item1", 2, 10.0)
order.add_item("item2", 1, 20.0)
order.add_item("item3", 3, 5.0)

print(order.total_price())
payment_processor = DebitPaymentProcessor("1234")
payment_processor.pay(order)
print(order.status)

payment_processor = PaypalPaymentProcessor("abhishek@gmail.com")
payment_processor.pay(order)
print(order.status)