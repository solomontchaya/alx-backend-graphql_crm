import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

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
# Query with Filters
# -------------------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductNode, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderNode, filterset_class=OrderFilter)
