Users
====================
This page seeks to explain the methods and classes involved in the Users sub-application of the *propertea* Application.

.. danger::
    Please note that the uses of these classes and functions are heavily dependent on the provision of the database that stores the user data and other related information.

models.py Methods
---------------------

.. automodule:: users.models
    :members:


forms.py Methods
----------------------

.. automodule:: users.forms
    :members:

.. important::
    Please note that we have separated view logic into controller and views in order to comply with the MVC framework.

controller.py Methods
---------------------------

.. automodule:: users.controller
    :members:
    :undoc-members:


tokens.py Methods
-------------------------

.. automodule:: users.tokens
    :members: _make_hash_value

.. autoclass:: users.tokens.AccountActivationTokenGenerator
    :members: _make_hash_value

urls.py Methods
---------------------

.. autoclass:: users.urls.urlpatterns
    :members:
    :undoc-members:

views.py Methods
----------------------

.. automodule:: users.views
    :members:
    :undoc-members:
