import ldap3 as ldap
from ldap3.utils.dn import dn2str, str2dn
from .fields import LdapField
from .search import Search, filterbuilder

# TODO: FIX BUG: Filtering is NOT possible with fields having different db name (db_name param) 
#       This is not a trivial problem to fix.
# TODO Streaming implementation

class QuerySet:
    def __init__(self, model=None, db=None):
        self.model = model
        self.db = db
        self.results = list()
        self._cached = False
        self._attrlist = set()
        self.search = Search()
        self.search.base = self.model.base

    def __iter__(self):
        if not self._cached:
            self._evaluate()
        return self._iter_cached()

    def __getitem__(self, i):
        len(self)
        if isinstance(i, slice):
            return [self._map_to_model(dn, entry) for dn, entry in self.results[i]]
        else:
            dn, entry = self.results[i]
            return self._map_to_model(dn, entry)

    def __len__(self):
        if not self._cached:
            self._evaluate()
        return len(self.results)

    def all(self):
        return self._get_all()

    def filter(self, *args, **kwargs):
        return self._filter(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._get_single_entry(*args, **kwargs)

    def exists(self, **kwargs):
        pass

    def attributes(self, *args, **kwargs):
        fetch_only = set(args)
        # pk should always be in attr list
        fetch_only.add(self.model.pk)
        # if you want to get all default attrs and specified extras
        if kwargs.get('include_defaults', False):
            fetch_only.add('*')
        self.search.attrlist = [self.model.MODEL_TO_DB.get(attr, attr) for attr in fetch_only]
        self._attrlist = fetch_only
        return self

    def raw(self):
        pass

    def _get_single_entry(self, *args, **kwargs):
        dn = kwargs.pop('dn', None)
        if dn:
            normalized_dn = lambda x: dn2str(str2dn(x))
            assert normalized_dn(dn).lower().endswith(normalized_dn(self.model.base).lower())
            self.search.scope = ldap.SCOPE_BASE
            self.search.base = dn
            if not args and not kwargs:
                self.search.filter = filterbuilder(objectclass__ne=None)
            else:
                self.search.filter = filterbuilder(*args, **kwargs)
        else:
            self.search.filter = filterbuilder(*args, **kwargs)

        self._evaluate()
        if not self.results:
            return None
        if len(self.results) > 1:
            raise ValueError("Multiple Results Found")
        else:
            dn, entry = self.results.pop()
            return self._map_to_model(dn, entry)

    def _get_all(self):
        opts = dict()
        opts['%s__ne' % self.model.pk] = None
        self.search.filter = filterbuilder(**opts)
        return self

    def _filter(self, *args, **kwargs):
        if self.search.filter:
            self.search.filter &= filterbuilder(*args, **kwargs)
        else:
            self.search.filter = filterbuilder(*args, **kwargs)
        return self

    # TODO: use deepcopy of the self.model
    def _map_to_model(self, dn, entry):
        # if .attrlist() is specified map only those attrs
        # otherwise map all fields
        if self._attrlist and '*' not in self._attrlist:
            fields = list(self._attrlist)
        else:
            fields = self.model._fields

        # dictionary to feed into model kwargs
        model_dict = dict.fromkeys(fields)
        for field, value in entry.items():
            field = field.lower()
            field = self.model.DB_TO_MODEL.get(field, field)
            if field in model_dict:
                model_dict[field] = value
        model = self.model(dn, fetched=True, **model_dict)
        return model

    def _evaluate(self):
        self.results = self.db.search(self.search.construct())
        self._cached = True

    def _iter_cached(self):
        for result in self.results:
            dn, entry = result
            yield self._map_to_model(dn, entry)
