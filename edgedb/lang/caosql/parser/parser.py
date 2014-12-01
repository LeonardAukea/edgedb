##
# Copyright (c) 2008-2010, 2014 Sprymix Inc.
# All rights reserved.
#
# See LICENSE for details.
##


from metamagic.utils import ast, parsing, debug

from metamagic.caos.caosql.parser.errors import CaosQLSyntaxError
from metamagic.caos.caosql import ast as qlast, CaosQLQueryError
from metamagic.caos import types as caos_types

from . import lexer


class CaosQLParserMeta(type(parsing.Parser)):
    _instances = {}

    @property
    def instance(cls):
        try:
            parser = cls.__class__._instances[cls]
        except KeyError:
            parser = cls.__class__._instances[cls] = cls()

        return parser


class CaosQLParser(parsing.Parser, metaclass=CaosQLParserMeta):
    def get_parser_spec_module(self):
        from . import caosql
        return caosql

    def get_debug(self):
        return 'caos.caosql.parser' in debug.channels

    def get_exception(self, native_err, context):
        return CaosQLQueryError(native_err.args[0], context=context)

    def get_lexer(self):
        return lexer.CaosQLLexer()

    def process_lex_token(self, mod, tok):
        tok_type = tok.attrs['type']
        if tok_type in ('WS', 'NL', 'COMMENT'):
            return None

        return super().process_lex_token(mod, tok)

    def normalize_select_query(self, query, filters=None, sort=None, limit=None,
                                     offset=None, anchors=None):
        nodetype = type(query)
        arg_types = {}

        qtree = query

        if nodetype != qlast.SelectQueryNode:
            selnode = qlast.SelectQueryNode()
            selnode.targets = [qlast.SelectExprNode(expr=qtree)]
            qtree = selnode

        if filters:
            targets = {t.alias: t.expr for t in qtree.targets}

            for name, value in filters.items():
                target = targets.get(name)
                if not target:
                    err = 'filters reference column %s which is not in query targets' % name
                    raise CaosQLQueryError(err)

                const = qlast.ConstantNode(value=None, index='__filter%s' % name)
                arg_types['__filter%s' % name] = value.__class__

                filter_expr = qlast.BinOpNode(left=target, right=const, op=ast.ops.EQ)
                if qtree.where:
                    qtree.where = qlast.BinOpNode(left=qtree.where, right=filter_expr, op=ast.ops.AND)
                else:
                    qtree.where = filter_expr

        if sort:
            targets = {t.alias: t.expr for t in qtree.targets}
            newsort = []

            for name, direction, *nones in sort:
                target = targets.get(name)
                if not target:
                    err = 'sort reference column %s which is not in query targets' % name
                    raise CaosQLQueryError(err)

                nones_order = qlast.NonesOrder(nones[0].lower()) if nones and nones[0] else None
                newsort.append(qlast.SortExprNode(path=target, direction=direction,
                                                  nones_order=nones_order))

            qtree.orderby = newsort

        if limit:
            qtree.limit = qlast.ConstantNode(value=None, index='__limit')
            arg_types['__limit'] = int

        if offset:
            qtree.offset = qlast.ConstantNode(value=None, index='__offset')
            arg_types['__offset'] = int

        return qtree, arg_types
