=========
Models
=========
Model declarations

.. code-block:: python

    from umea.models import Model
    from umea.fields import Field

    class Users(Model):
        db = db_settings
        base = "ou=users, o=company, c=us"
        uid = Field(pk=True, rdn=True)
        cn = Field()
        sn = Field()
        givenname = Field()
        objectclass = Field()

Getting all objects under tree

.. code-block:: python

    users = User.objects.all()


Filters
_______

There are several filtering methods available. 

.. code-block:: python

    # All users with name John
    User.objects.filter(givenname="John")

    # All users with name starting with J
    User.objects.filter(givenname__startswith="J")

    # All users with name John and objectclass 'staff'
    User.objects.filter(givenname="John", objectclass="Apple")


Complex Lookups

.. code-block:: python

    # Users with name Arnold or surname Smith
    from umea.search import F
    User.objects.filter(F(givenname="Arnold") | F(sn="Smith"))

