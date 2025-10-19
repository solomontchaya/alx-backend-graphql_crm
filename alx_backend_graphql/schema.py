import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

# Combine queries from CRM
class Query(CRMQuery, graphene.ObjectType):
    pass

# Combine mutations from CRM
class Mutation(CRMMutation, graphene.ObjectType):
    pass

# Define the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
