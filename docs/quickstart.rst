.. _ref-quickstart:

Quickstart
===========


Define database settings in settings.py

.. code-block:: python

        my_database = {
            'host': 'directory.mycompany.com',
            'port': '389',
            'user': 'cn=myusername, o=compay',
            'password': 'xxxxxxxx'
        }
    

Now declare a model using this database in models.py 

.. code-block:: python

    import settings
    from umea.models import Model
    from umea.fields import Field

    class Users(Model):
        db = settings.my_database
        base = "ou=users, o=company, c=us"
        uid = Field(pk=True, rdn=True)
        cn = Field()
        sn = Field()
        givenname = Field()
        objectclass = Field()


Now you can start querying database 

.. code-block:: python

    from models import User
    users = User.objects.all()


