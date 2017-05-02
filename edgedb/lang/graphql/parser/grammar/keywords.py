##
# Copyright (c) 2016-present MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import typing

keyword_types = range(1, 3)
UNRESERVED_KEYWORD, RESERVED_KEYWORD = keyword_types

graphql_keywords = {
    "false": ("FALSE", UNRESERVED_KEYWORD),
    "fragment": ("FRAGMENT", UNRESERVED_KEYWORD),
    "mutation": ("MUTATION", UNRESERVED_KEYWORD),
    "on": ("ON", UNRESERVED_KEYWORD),
    "query": ("QUERY", UNRESERVED_KEYWORD),
    "subscription": ("SUBSCRIPTION", UNRESERVED_KEYWORD),
    "true": ("TRUE", UNRESERVED_KEYWORD),
}


by_type: typing.Dict[int, dict] = {typ: {} for typ in keyword_types}

for val, spec in graphql_keywords.items():
    by_type[spec[1]][val] = spec[0]
