from crm.models import Customer, Product

def run():
    customers = [
        {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"},
        {"name": "Jane Smith", "email": "jane@example.com", "phone": "123-456-7890"},
    ]
    products = [
        {"name": "Phone", "price": 500.00, "stock": 10},
        {"name": "Tablet", "price": 800.00, "stock": 5},
    ]

    for c in customers:
        Customer.objects.get_or_create(**c)
    for p in products:
        Product.objects.get_or_create(**p)

    print("Database seeded successfully.")
