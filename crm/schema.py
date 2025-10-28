import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.core.validators import RegexValidator
from graphql import GraphQLError
from django.db import transaction
from crm.models import Product
from crm.models import Customer, Order

# -------------------------------
# Graphene Types
# -------------------------------

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

# Define the Mutation
class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # No input needed for this mutation

    success = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_list = []

        for product in low_stock_products:
            product.stock += 10  # simulate restocking
            product.save()
            updated_list.append(product)

        return UpdateLowStockProducts(
            success=f"{len(updated_list)} products restocked successfully.",
            updated_products=updated_list
        )
    
class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# -------------------------------
# Mutations
# -------------------------------

# --- Create Single Customer ---
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists")
        if phone:
            validator = RegexValidator(
                regex=r'^(\+?\d{1,3})?[- ]?\d{3}[- ]?\d{3}[- ]?\d{4}$',
                message="Phone number must be valid"
            )
            validator(phone)
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


# --- Bulk Create Customers ---
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        customers = []
        errors = []
        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Email {data.email} already exists")
                    continue
                if data.phone:
                    validator = RegexValidator(
                        regex=r'^(\+?\d{1,3})?[- ]?\d{3}[- ]?\d{3}[- ]?\d{4}$',
                        message=f"Phone number {data.phone} is invalid"
                    )
                    validator(data.phone)
                customer = Customer(name=data.name, email=data.email, phone=data.phone)
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(str(e))
        return BulkCreateCustomers(customers=customers, errors=errors)


# --- Create Product ---
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise GraphQLError("Price must be positive")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative")
        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


# --- Create Order ---
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        products = []
        for pid in product_ids:
            try:
                products.append(Product.objects.get(pk=pid))
            except Product.DoesNotExist:
                raise GraphQLError(f"Invalid product ID: {pid}")

        if not products:
            raise GraphQLError("At least one product must be selected")

        order = Order(customer=customer)
        order.save()
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()
        return CreateOrder(order=order)

# -------------------------------
# Graphene Types
# -------------------------------
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")
        interfaces = (graphene.relay.Node,)

# -------------------------------
# Mutation Class
# -------------------------------

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -------------------------------
# Query Class
# -------------------------------

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderNode, filterset_class=OrderFilter)
