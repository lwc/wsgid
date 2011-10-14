Tutorials
=========


Here are some example tutorials about running WSGID with different frameworks.


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
