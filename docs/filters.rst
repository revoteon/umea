=============
Filters
=============

There are several filtering methods available. 

.. code-block:: python

    # All users with name John
    User.objects.filter(givenname="John")

    # All users with name starting with J
    User.objects.filter(givenname__startswith="J")

    # All users with name John and objectclass 'staff'
    User.objects.filter(givenname__endswith="John")

    User.objects.filter(givenname__contains="John")

    # All users with name John and objectclass 'staff'
    User.objects.filter(givenname="John", objectclass="Apple")


Inverse lookups
----------------

You can use __ne and __not in front of filter to invert the search:

.. code-block:: python

    User.objects.filter(givenname__ne="John")
    User.objects.filter(givenname__not_startswith="John")
    User.objects.filter(givenname__not_endswith="John")
    User.objects.filter(givenname__not_contains="John")
    

Existance search
-----------------

.. code-block:: python

    # All users with empty givenname
    User.objects.filter(givenname=None)

    # All users with non-empty givenname
    User.objects.filter(givenname__ne=None)



Complex Lookups
----------------

.. code-block:: python

    # Users with name Arnold or surname Smith
    from umea.search import F
    User.objects.filter(F(givenname="Arnold") | F(sn="Smith"))

    # grouping together conditions
    User.objects.filter(F(givenname="Arnold") | (F(sn="Smith") & F(objectclass="people")))

