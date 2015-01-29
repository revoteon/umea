import re
import copy
import ldap
from ldap.filter import escape_filter_chars

EXTENDED_OPERATIONS_MAP = {
        'exact': '%s=%s',
        'startswith': '%s=%s*',
        'endswith': '%s=*%s',
        'contains': '%s=*%s*',
        'gte': '%s>=%s',
        'lte': '%s<=%s',
        'ne': '!(%s=%s)',
        }

NEGATE = "!(%s)"

FILTER_PATTERN_STRING = "^(?P<attribute>[0-9a-zA-Z]+)(?P<extended>(?P<separator>__)(?P<negate>not_)?(?P<operation>(startswith|endswith|contains|gte|lte|ne)))?$"
FILTER_PATTERN = re.compile(FILTER_PATTERN_STRING)

class F:
    def __init__(self, _raw_filter=None, **kwargs):
        if _raw_filter:
            self.filter = _raw_filter
        else:
            attribute, value = kwargs.popitem()
            self.filter = filter_factory(attribute, value)

    @classmethod
    def from_string(cls, filter_string):
        return cls(_raw_filter=filter_string)

    def __or__(self, other):
        new_obj = copy.deepcopy(self)
        new_obj.filter = "|(%s)(%s)" % (self.filter, other.filter)
        return new_obj

    def __and__(self, other):
        new_obj = copy.deepcopy(self)
        new_obj.filter = "&(%s)(%s)" % (self.filter, other.filter)
        return new_obj

    def __invert__(self):
        new_obj = copy.deepcopy(self)
        new_obj.filter = "!(%s)" % self.filter
        return new_obj

    def __str__(self):
        return self.filter


def filter_factory(attribute, value):
    filter_match = FILTER_PATTERN.match(attribute)
    ldap_filter = None
    existance_search = False
    if not filter_match:
        raise ValueError("Invalid filter pattern: %s" % attribute)
    attribute, extended, separator, negate, operation, _ = filter_match.groups()
    # escape value here
    if value is None:
        value = '*'
        existance_search = True
    else:
        value = escape_filter_chars(value)

    if not extended:
        operation = 'exact'

    if existance_search:
        if operation == 'ne':
            operation = 'exact'
        elif operation == 'exact':
            operation = 'ne'

    filter_string = EXTENDED_OPERATIONS_MAP[operation] % (attribute, value)
    if negate:
        filter_string = NEGATE % filter_string

    return filter_string


# TODO: make this classmethod of F
def filterbuilder(*args, **kwargs):
    """
    Accpets args where each of them is F() object
    and/or kwargs keypair
    """
    filter_string = None
    args = list(args)

    if args: 
        filter_string = args.pop(0)
    else:
        k,v = kwargs.popitem()
        initial_filter = dict()
        initial_filter[k] = v
        filter_string = F(**initial_filter)

    for arg in args:
        filter_string &= arg

    for k,v in kwargs.items():
        ldap_filter = dict()
        ldap_filter[k] = v
        filter_string &= F(**ldap_filter)

    return filter_string


class Search:
    def __init__(self, scope=ldap.SCOPE_SUBTREE, **kwargs):
        self.base = None
        self.scope = scope
        self.filter = None
        self.attrlist = list()

    def construct(self):
        return self.base, self.scope, "(%s)" % str(self.filter), self.attrlist
