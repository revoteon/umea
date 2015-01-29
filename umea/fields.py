import ldap


class LdapField(object):
    # tracks order of fields in model
    order = 0

    def __init__(self, **kwargs):
        self.pk = kwargs.get('pk', False)
        self.rdn = kwargs.get('rdn', False)
        self.db_name = kwargs.get('db_name')
        self._value = list()
        self.modlist = list()
        self.order = LdapField.order
        LdapField.order += 1

    @property
    def value(self):
        return list(self._value)

    @value.setter
    def value(self, value):
        #if value is not iterable, make it one 
        if not hasattr(value, '__iter__'):
            value = list([value])
        self._value = value
        self._clear_modlist()

    def add(self, value):
        if value not in self._value:
            self._value.append(value)
            self.modlist.append((ldap.MOD_ADD, value))

    def remove(self, value):
        if value in self._value:
            self._value.remove(value)
            self.modlist.append((ldap.MOD_DELETE, value))

    def replace(self, value):
        if not hasattr(value, '__iter__'):
            value = list([value])
        if set(value) != set(self._value):
            self._value = value
            self.modlist.append((ldap.MOD_REPLACE, value))

    def delete(self):
        if self._value:
            self._value = list()
            self.modlist.append((ldap.MOD_DELETE, None))

    def _clear_modlist(self):
        self.modlist = list()

    def __repr__(self):
        return str(self._value)

    def __cmp__(self, other):
        return cmp(self.order, other.order)
