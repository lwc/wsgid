Tutorials
=========


Here are some example tutorials about running WSGID with different frameworks.


.. _django:

Loading a Django Application
****************************


Suppose you have a django project (http://djangoproject.com) named *myproject*. So probably you have an folder named *myproject*, with your *settings.py*, *manage.py*, and other files.
To load this app with wsgid you need to copy your application code to the *app* folder. Make sure you copy **your django project folder**, not only its contents. Suppose your wsgid app will be at */var/wsgid/djangoapp*, so you must have inside this folder the correct structure for a wsgid app (see :doc:`appstructure`). 

In this example, we must copy the project folder (*myproject*) to the *app* folder: ::

    $ cp -a myproject/ /var/wsgid/djangoapp/app/

Now we have a *myproject* folder inside */var/wsgid/djangoapp/app*. As this last folder is added to *sys.path*, we are ready to go. Always remember that your django project should me importable with a simple *import myproject*.

Now just call wsgid as always: ::

    $ wsgid --app-path=/var/wsgid/djangoapp <other-options>

.. versionadded:: 0.4.0

Now you can have as many djangoproject as you like inside wsgid/app folder. Wsgid will load the first project it finds, ordered alphabetically.

.. _djangoconf:

Using an external config file to load additional django settings
----------------------------------------------------------------


.. versionadded:: 0.5.0


Optionally you can use an external file to load additional django settings to your application. The configuration file must be named ``django.json`` and resides inside your wsgidapp folder. It is a JSON file with any kind of setting you may need. All these will be added to your settings module and thus will be available to your django application, at runtime.

This is very useful, to deploy you app on production. Using this functionality you don't need leave any specific config value on your settings.py. As an example, think about your dabatase credentials. To do this you can have a ``django.json`` that looks like this: ::

     {
       "DATABASES": {
         "default": {
            "ENGINE": "mysql",
            "NAME": "mydb",
            "USER": "user",
            "PASSWORD": "passwd",
            "HOST": "localhost",
            "PORT": "3598"
         }
       }
     }

This setting will be joined with the ``DATABASES`` dict already present in your ``settings.py``. The key ``default`` will override any other ``default`` key that may exist in your ``settings.py``. You can define any additional dabatase if you want.

Some rules apply to how DjangoAppLoader will use these additional settings:

 * If a setting found is in django.json but is not found in settings module, it will be created;
 * If a setting exists in both locations and are of different types, the one from django.json will override the other;
 * Settings of type dict, list and tuple will be joined together, that is, all values from django.json will be appended to the original setting.

Loading a pyroutes Application
******************************

Loading a pyroutes (http://pyroutes.com) app is very easy and straightforward. First we create the new app. ::

    $ pyroutes-admin.py mynewproject

So now, inside this new folder we have the basic files for a pyroutes project. ::


    abc/
    templates/
    tests/
    handler.py
    pyroutes_settings.py

We should now copy **the contents** of this folder to the *app* folder of our wsgid app (see :doc:`appstructure`). Then we can load our app just passing */path/to/our/wsgid-app* to wsgid's *--app-path* option. Supposing we copied this to */var/wsgid/myproject/app* we call wsgid this way: ::

  wsgid --app-path=/var/wsgid/myproject <other-options>

And you are ready to go.


Loading a generic WSGI Application
**********************************

So you tried hard but wsgid was not able to load your app? OK, not everything is lost, yet! To load your app you first need to write a python module that declares the WSGI application object for your app, then you pass the complete name of this module to wsgid, like this.::

  wsgid --wsgi-app=myproject.frontends.wsgi.entry_point --send=SEND_SOCK --recv=RECV_SOCK --app-path=/path/to/the/wsgid-app

This means that the module *wsgi*, inside the module *frontends* of your project declares an object named *entry_point*. The *entry_point* object is just a callable that receives two parameters, just like PEP-333 says.

.. _asyncupload-tut:

Handling big requests using mongrel2's async upload mechanism
*************************************************************

.. versionadded:: 0.5.0

Mongrel2 has a very intereting way to handle big requests. Instead of trying to buffer all content in memory it creates a temporary file and dumps the request into it. This makes it possible to handle requests while keeping a very low memory usage. Wsgid makes all this transparent to your WSGI application.

But since mongrel2 creates all temporary files with a path relative to its chroot if you want to take advantage of this mechanism you must pass to wsgid the path where your mongrel2 server is chrooted. Each mongrel2 server instance can have its own chroot so you must know beforehand to which server your wsgid will be attached and responding requests.

Suppose we have a server chrooted at ``/var/mongrel2``. All wsgid instances that are attached to any handlers of this server must be called with ``--mongrel2-chroot=/var/mongrel2``. Note that you only need to pass different chroot values if you have more than one server and they are at different places. Normaly you will use the same chroot for all your servers.

You can also use this option from the ``wsgid.json`` configuration file. The name of the option is: ``mongrel2_chroot``.



