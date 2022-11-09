import graphene

import swiftmovers.swift.schema as swift


class Query(swift.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
