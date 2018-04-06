import unittest
import ldap3 as ldap
from umea.fields import LdapField
from umea.model import Model, ModelManager


class SampleModel(Model):
    db = {}
    base = "ou=sample, o=sc, c=au"


class SampleModel2(Model):
    db = {}
    base = "ou=sample, o=sc, c=au"
    name = LdapField(pk=True, rdn=True)
    surname = LdapField()
    orgunit = LdapField(db_name='organizational-unit')


class ModelMetaTests(unittest.TestCase):

    def setUp(self):
        self.cls = SampleModel

    def test_attributes(self):
        self.assertEqual(self.cls.base, 'ou=sample, o=sc, c=au')
        self.assertEqual(self.cls._fields, list())
        self.assertTrue(type(self.cls.objects), ModelManager)
        self.assertTrue(isinstance(self.cls.objects, ModelManager))


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model = SampleModel2()

    def tearDown(self):
        self.model = SampleModel2()

    def test_fields(self):
        self.assertEqual(set(self.model._fields), set(['name', 'surname', 'orgunit']))

    def test_attr_mapping(self):
        self.assertEqual(self.model.DB_TO_MODEL, {'organizational-unit': 'orgunit'})
        self.assertEqual(self.model.MODEL_TO_DB, {'orgunit': 'organizational-unit'})

    def test_extra_attrs(self):
        self.assertTrue(self.model.rdn)
        self.assertEqual(self.model.pk, 'name')
        self.assertFalse(self.model._fetched)

    def test_pk(self):
        self.assertEqual(self.model._get_pk(), None)
        self.model.name.value = 'john'
        self.assertEqual(self.model._get_pk(), 'john')
    
    def test_dn(self):
        self.assertIsNone(self.model.dn())
        self.model.name.value = 'john'
        self.assertEqual(self.model.dn(), 'name=john,ou=sample, o=sc, c=au')

    def test_modlist(self):
        self.assertEqual(self.model.modlist(), list())
        self.model.name.add('apple')
        self.assertEqual(self.model.modlist(), [(ldap.MOD_ADD, 'name', 'apple')])
        self.model.name.add('apple')
        self.assertEqual(self.model.modlist(), [(ldap.MOD_ADD, 'name', 'apple')])
        self.model.surname.add('pear')
        self.assertEqual(set(self.model.modlist()), set([(ldap.MOD_ADD, 'name', 'apple'), (ldap.MOD_ADD, 'surname', 'pear')]))
        self.model.surname.remove('pear')
        self.assertEqual(set(self.model.modlist()), set([(ldap.MOD_ADD, 'name', 'apple'), (ldap.MOD_ADD, 'surname', 'pear'), (ldap.MOD_DELETE, 'surname', 'pear')]))

    def test_modlist_for_different_model_to_db_name(self):
        self.assertEqual(self.model.modlist(), list())
        self.model.orgunit.add('some organization')
        self.assertEqual(self.model.modlist(), [(ldap.MOD_ADD, 'organizational-unit', 'some organization')])


    def test_addlist(self):
        self.assertEqual(self.model.addlist(), list())
        self.model.name.add('apple')
        self.assertEqual(self.model.addlist(), [('name', ['apple'])])
        self.model.name.add('pear')
        self.assertEqual(self.model.addlist(), [('name', ['apple', 'pear'])])
        self.model.name.remove('apple')
        self.assertEqual(self.model.addlist(), [('name', ['pear'])])

    def test_addlist_for_different_model_to_db_name(self):
        self.assertEqual(self.model.addlist(), list())
        self.model.orgunit.add('some organization')
        self.assertEqual(self.model.addlist(), [('organizational-unit', ['some organization'])])

    def test_ldif(self):
        pass

    def test_save(self):
        pass

    def test_validate(self):
        pass

