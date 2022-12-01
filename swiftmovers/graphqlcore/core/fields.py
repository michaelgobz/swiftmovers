
from json import JSONDecodeError

import graphene
from graphql import GraphQLError


class JSONString(graphene.JSONString):
    @staticmethod
    def parse_literal(node):
        try:
            return graphene.JSONString.parse_literal(node)
        except JSONDecodeError:
            raise GraphQLError(f"{str(node.value)[:20]}... is not a valid JSONString")
