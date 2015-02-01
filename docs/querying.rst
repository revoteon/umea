Querying Data
=============

.filter(\*args, \*\*kwargs)
---------------------------

\*args, if present, must be F() object 

.. code-block:: python
    
    User.objects.filter(name="John")

Querysets are evaluted lazily. You can chain as much filter as you want. For example:

.. code-block:: python

    User.objects.filter(name="John").filter(sn="Smith")

is eqivalent to 

.. code-block:: python

    User.objects.filter(name="John", sn="Smith")






.all()
-------



