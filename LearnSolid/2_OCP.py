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
    def pay(self, order, security_code: str):
        pass

class DebitPaymentProcessor(PaymentProcessor):
    def pay(self, order: Order, security_code: str):
        print("Processing debit payment...")
        print("validating security code...")
        order.status = "paid"

class CreditPaymentProcessor(PaymentProcessor):
    def pay(self, order: Order, security_code: str):
        print("Processing credit payment...")
        print("validating security code...")
        order.status = "paid"

class PaypalPaymentProcessor(PaymentProcessor):
    def pay(self, order: Order, security_code: str):
        print("Processing PayPal payment...")
        print("validating security code...")
        order.status = "paid"

order = Order()
order.add_item("item1", 2, 10.0)
order.add_item("item2", 1, 20.0)
order.add_item("item3", 3, 5.0)

print(order.total_price())
payment_processor = DebitPaymentProcessor()
payment_processor.pay(order, "1234")
print(order.status)

payment_processor = PaypalPaymentProcessor()
payment_processor.pay(order, "5678")
print(order.status)