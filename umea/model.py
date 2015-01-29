import ldap
import db
from operator import itemgetter
from fields import LdapField
from queryset import QuerySet

# TODO: Restrict object creation without dn or pk
# If model pk is not rdn, then the only way to create model instance should be 
# through dn. Otherwise pk will suffice.  

# TODO: load function to reload attributes from db (tricky)

# TODO: Add function to rename RDN

# TODO: food for thought: make validate() more robust by requiring at least one 
# objectclass and cross checking mandatory attributes for given objectclasses with db schema
# (may need to write schema parser). Also checking unallowed attrbiutes for given schemas
 

class ModelManager:
    def __init__(self, model, db):
        self.model = model
        self.db = db

    def get_query_set(self):
        return QuerySet(model=self.model, db=self.db)

    def all(self):
        return self.get_query_set().all()

    def get(self, *args, **kwargs):
        return self.get_query_set().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        return self.get_query_set().filter(*args, **kwargs)

    def exists(self, dn):
        try:
            self.db.cursor().search_s(dn, 0)
        except ldap.NO_SUCH_OBJECT as e:
            return False
        else:
            return True

    def update(self, dn, modlist):
        self.db.cursor().modify_s(dn, modlist)

    def create(self, dn, addlist):
        self.db.cursor().add_s(dn, addlist)

    def delete(self, dn):
        self.db.cursor().delete_s(dn)


# TODO: Bit of mess, clean up
class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelMeta, cls).__new__

        # don't do anything for non inherited models 
        parents = [b for b in bases if isinstance(b, ModelMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        fields_dictionary = {}

        for field, val in attrs.items():
            if isinstance(val, LdapField):
                fields_dictionary[field] = val

        # name of fields that is different for DB (only when field has a db_name param)
        MODEL_TO_DB = dict()
        # mapping of DB name to model field name (only when field has a db_name param)
        DB_TO_MODEL = dict()

        attrs['_fields'] = []
        attrs['rdn'] = False 
        for attr, instance in fields_dictionary.iteritems():
            attrs['_fields'].append(attr)
            if instance.pk:
                attrs['pk'] = attr
            if instance.rdn:
                attrs['rdn'] = True
            if instance.db_name:
                MODEL_TO_DB[attr] = instance.db_name
                DB_TO_MODEL[instance.db_name] = attr
            del attrs[attr]

        attrs['MODEL_TO_DB'] = MODEL_TO_DB
        attrs['DB_TO_MODEL'] = DB_TO_MODEL

        db_class = getattr(db, attrs['db'].get('adaptor', 'Database'))
        db_instance = db_class(**attrs['db'])
        del attrs['db']

        instance = super_new(cls, name, bases, attrs)

        setattr(instance, 'objects', ModelManager(instance, db_instance))
        return instance


# TODO
# Make dn a property

# TODO
# Load field properties from meta

# TODO
# cleanup modlist, addlist, and ldif

class Model(object):
    __metaclass__ = ModelMeta

    def __init__(self, dn=None, fetched=False, **kwargs):
        if not self.rdn:
            assert dn
        self._dn = dn
        self._fetched = fetched
        for attr in self._fields:
            # while fetching only set of attributes( set attrbutes method in queryset)
            # do not instantiate field if it is not fetched this dramatically improves performance
            # while fetching lots of entries
            if attr not in kwargs and fetched is True:
                continue
            #default_properties = self._meta['fields'][attr]
            attr_instance = LdapField()
            # if value exists in kwargs, set attrs' value
            value = kwargs.get(attr, None)
            if value is not None:
                attr_instance.value = value
            setattr(self, attr, attr_instance)

        super(Model, self).__init__()

    def dn(self):
        if self._dn:
            return self._dn
        elif self.rdn and self._get_pk():
            return "%(rdn)s=%(pk)s,%(base)s" % {
                    'rdn': self.pk, 
                    'pk': self._get_pk(), 
                    'base': self.base
                    }    
        # raise exception - dn is not set and some advice about rdn
        return None


    def modlist(self):
        mods = list()
        for field in self._fields:
            field_object = getattr(self, field, None)
            field_db_name = self.MODEL_TO_DB.get(field, field)
            if field_object:
                for modification in field_object.modlist:
                    operation, value = modification
                    mods.append((operation, field_db_name, value))
        return mods

    def addlist(self):
        add_list = list()
        for field in self._fields:
            field_object = getattr(self, field, None)
            field_db_name = self.MODEL_TO_DB.get(field, field)
            if field_object:
                values = field_object.value
                if values:
                    add_attr = field_db_name, values
                    add_list.append(add_attr)
        return add_list

    def ldif(self):
        ldif_s = list()
        ldify = lambda attr, val: '%s: %s' % (attr, val)
        if self.dn():
            ldif_s.append(ldify('dn', self.dn()))
        for field in self._fields:
            field_object = getattr(self, field, None)
            field_db_name = self.MODEL_TO_DB.get(field, field)
            if field_object:
                vals = field_object.value
                for val in vals:
                    ldif_s.append(ldify(field_db_name, val))
        return '\n'.join(ldif_s)
   
    def save(self):
        if self._fetched:
            modlist = self.modlist()
            if modlist:
                self.objects.update(self.dn(), modlist)
        else:
            # check exists with dn
            # not create, else update
            self.objects.create(self.dn(), self.addlist())

    def exists(self):
        if self._fetched:
            return True
        if self.dn():
            return self.objects.exists(self.dn())
        else:
            raise ValueError('Object PK is not set')

    def delete(self):
        self.objects.delete(self.dn())

    # validation rules:
    #  must have one and only pk in fieldlist
    #  may have one and only pk in fieldlist
    #  must pass all validations of specific fields
    def validate(self):
        pass

    def _get_pk(self):
        pk = getattr(self, self.pk).value
        return pk[0] if pk else None

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._get_pk() == other._get_pk()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return self.ldif()
