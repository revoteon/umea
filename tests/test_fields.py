import unittest
import ldap3 as ldap
from umea.fields import LdapField

class LdapFieldTestCase(unittest.TestCase):
    def setUp(self):
        self.field = LdapField()

    def tearDown(self):
        self.field = LdapField()

    def test_default_values(self):
        self.assertEqual(self.field._value, list())
        self.assertEqual(self.field.value, list())
        self.assertEqual(self.field.modlist, list())
        self.assertEqual(self.field.pk, False)
        self.assertEqual(self.field.rdn, False)

    def test_add(self):
        self.field.add('apple')
        self.assertEqual(self.field.value, list(['apple']))
        self.assertEqual(self.field._value, list(['apple'])) 
        self.assertEqual(len(self.field.modlist), 1) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple')]) 

    def test_add_duplicate(self):
        self.field.add('apple')
        self.field.add('apple')
        self.assertEqual(self.field.value, list(['apple']))
        self.assertEqual(self.field._value, list(['apple'])) 
        self.assertEqual(len(self.field.modlist), 1) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple')]) 

    def test_replace_duplicate(self):
        self.field.add('apple')
        self.field.replace('apple')
        self.assertEqual(self.field.value, list(['apple']))
        self.assertEqual(self.field._value, list(['apple'])) 
        self.assertEqual(len(self.field.modlist), 1) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple')]) 

    def test_add_multiple(self):
        self.field.add('apple')
        self.field.add('pear')
        self.assertEqual(self.field.value, list(['apple', 'pear']))
        self.assertEqual(self.field._value, list(['apple', 'pear'])) 
        self.assertEqual(len(self.field.modlist), 2) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_ADD, 'pear')]) 

    def test_remove(self):
        self.field.add('apple')
        self.field.add('pear')
        self.field.remove('pear')
        self.assertEqual(self.field.value, list(['apple']))
        self.assertEqual(self.field._value, list(['apple'])) 
        self.assertEqual(len(self.field.modlist), 3) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_ADD, 'pear'), (ldap.MOD_DELETE, 'pear')]) 

    def test_remove_multiple(self):
        self.field.add('apple')
        self.field.add('pear')
        self.field.remove('apple')
        self.field.remove('pear')
        self.assertEqual(self.field.value, list())
        self.assertEqual(self.field._value, list()) 
        self.assertEqual(len(self.field.modlist), 4) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_ADD, 'pear'), (ldap.MOD_DELETE, 'apple'), (ldap.MOD_DELETE, 'pear')]) 

    def test_replace(self):
        self.field.add('apple')
        self.field.replace('pear')
        self.assertEqual(self.field.value, list(['pear']))
        self.assertEqual(self.field._value, list(['pear'])) 
        self.assertEqual(len(self.field.modlist), 2) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_REPLACE, ['pear'])]) 

    def test_replace_list(self):
        self.field.add('apple')
        self.field.replace(['apple', 'pear'])
        self.assertEqual(self.field.value, list(['apple', 'pear']))
        self.assertEqual(self.field._value, list(['apple', 'pear'])) 
        self.assertEqual(len(self.field.modlist), 2) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_REPLACE, ['apple', 'pear'])]) 

    def test_replace_list_duplicate(self):
        self.field.add('apple')
        self.field.add('pear')
        self.field.replace(['apple', 'pear'])
        self.assertEqual(self.field.value, list(['apple', 'pear']))
        self.assertEqual(self.field._value, list(['apple', 'pear'])) 
        self.assertEqual(len(self.field.modlist), 2) 
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_ADD, 'pear')]) 

    def test_delete(self):
        self.field.add('apple')
        self.field.add('pear')
        self.field.delete()
        self.assertEqual(self.field.value, list())
        self.assertEqual(self.field._value, list()) 
        self.assertEqual(len(self.field.modlist), 3)
        self.assertEqual(self.field.modlist, [(ldap.MOD_ADD, 'apple'), (ldap.MOD_ADD, 'pear'), (ldap.MOD_DELETE, None)]) 

    def test_set_value(self):
        self.field.value = 'apple'
        self.assertEqual(self.field.value, list(['apple']))
        self.assertEqual(len(self.field.modlist), 0)

    def test_set_value_multiple(self):
        self.field.value = ['apple', 'pear', 'grape']
        self.assertEqual(self.field.value, list(['apple', 'pear', 'grape']))
        self.assertEqual(len(self.field.modlist), 0)

    def test_repr(self):
        self.assertEqual(repr(self.field), str([]))
        self.field.add('apple')
        self.assertEqual(repr(self.field), str(['apple']))

    def test_cmp(self):
        field1 = LdapField()
        field2 = LdapField()
        self.assertTrue(field2 > field1)
        field3 = LdapField()
        self.assertTrue(field3 > field2)

