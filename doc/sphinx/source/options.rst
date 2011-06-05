WSGID Command line Options
==========================

Here we will document only the main options of wsgid. Other options you can read directly on the man page.

    $ man wsgid

app-path
********
  --app-path

Path to the WSGI application. This should be the path where the code of your application is located. If the app is installed system wide, you don't need this.
The directory that contains your application must obey some rules, please see :doc:`appstructure`.

wsgi-app
********
  --wsgi-app

Full qualified name for the WSGI application object. This options is used in two main ocasions. One: When wsgid cannot load your app automatically just by looking at **--app-path**. Two: When yout app is installed system wide. Supose you have inside your app an package name *web*, and in this package you have a module named *frontends*. Supose *frontends/wsgi.py* is the module that defines the WSGI application object, as specified by PEP-333. ::


    myapp/
      __init__.py
      module1.py
      module2.py
      web/
        __init__.py
        frontends/
          __init__.py
          wsgi.py


In this example you would call wsgid with **--wsgi-app=myapp.web.frontends.wsgi.application**

The WSGI application object does not necessarily have to be named *application*. So if your app defines an object named *wsgi_entry_point*, just pass **--wsgi-app=myapp.web.frontends.wsgi.wsgi_entry_point** to wsgid.

**Important**: if you pass *--wsgi-app* and not *--app-path*, wsgid will generate all logs inside */tmp/logs*, so be sure that this path exists before running wsgid in daemon mode.

loader-dir
**********
    --loader-dir=LOADER_DIR

If wsgid cannot auto-load your app, you can write your own loaders and point them to wsgid with this option. *LOADER_DIR* is just a folder with some .py files. wsgid will try to load all .py files searching for custom application loaders. The first loader that reports the ability to load the given application will be used

When this option is used at the same time as the --chroot option, the value passed will be relative to the --app-path folder. You can pass more than one *--loader-dir* options, all folders will be searched for custom loaders, in order.

chroot
******
  --chroot

When this option is used, wsgid does a chroot to the --app-path folder. Remember that you have to run wsgid as root for this options to take effect. Running a daemon as root is not a good idea, so wsgid will drop privileges to the user/group that owns the *--app-path* folder.

recv
****
  --recv=RECV_SOCKET

TCP socket used to receive data from mongrel2. This is the same value that is in the *send_spec* of *handler* table of mongrel2's config database. By passing this option to wsgid your application will respond to requests for any routes associated with this socket.

The format of *RECV_SOCKET* can be any format accepted by zeromq

send
****
  --send=SEND_SOCKET

TCP socket used to return data to mongrel2. This is the same value that is in the *recv_spec* of *handler* table of mongrel2's config database. This value must belong to the same registry from where you got your **--recv** socket.

The format of *SEND_SOCKET* can be any format accepted by zeromq

no-dameon
*********
  --no-daemon

Used mainly for debug purposes. When this option is passed wsgid will not fork to background and will write all logs to stderr.

workers
*******
  --workers=N

Set the number of wsgid workers processes. Each process has its own PID and is responsible for handling one request at a time.

keep-alive
**********
  --keep-alive

This option will make wsgid watch for its child processes. If any child process dies a new process is created immediately.


.. _json-config:

Using the command line options inside a config file
===================================================

.. versionadded:: 0.2

wsgid is able to load config options from a config file. This file must be at the root of your app-path. The file name is *wsgid.json*. The internal format is just plain JSON. The only option that you can't use in the JSON config file is *--app-path*. All other options are the same, just remember to remove the `--` part and replace the `-` with `_`. So *--wsgi-app* becomes *wsgi_app*. An example of a *wsgid.json* follows: ::

  {
    "recv": "tcp://127.0.0.1:5000",
    "send": "tcp://127.0.0.1:5001",
    "debug": "true",
    "workers": "1",
    "keep_alive": "true"
  }

Note that any options specified in the config file will overwrite the same options passed in the command line. It's now easier to start you app, as all you need is:

  $ wsgid --app-path=/path/to/wsgid-app-folder/

.. _env-vars:

Addindg Environment Variables to your App
*****************************************

.. versionadded:: 0.2.1

Now it is possible to create environ variables that will be available to your WSGI app. To do this you need to use one more options inside the config file. The new options is named `envs`. This is actually a JSON hash. Each key-value pair represents one Env Var that will be created by wsgid, when loading your app, eg: ::

  {
    "recv": "tcp://127.0.0.1:5000",
    "send": "tcp://127.0.0.1:5001",
    "debug": "true",
    "workers": "1",
    "keep_alive": "true",
    "envs": {
            "ENV1": "VALUE1",
            "ENV2": "VALUE2"
          }
  }


This will create two environ variables that your app will be able to read using `os.environ['ENV1']` and `os.environ['ENV2']`.

