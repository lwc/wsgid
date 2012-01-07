WSGID Command Line Interface
============================

.. _main-options:

Main Options
------------

Here we will document only the main options of wsgid. Other options you can read directly on the man page.

    $ man wsgid

app-path
********
  ``--app-path``

Path to the WSGI application. This should be the path where the code of your application is located. If the app is installed system wide, you don't need this.
The directory that contains your application must obey some rules, please see :doc:`appstructure`.

wsgi-app
********
  ``--wsgi-app``

Full qualified name for the WSGI application object. This options is used in two main ocasions. One: When wsgid cannot load your app automatically just by looking at ``--app-path``. Two: When yout app is installed system wide. Supose you have inside your app an package name *web*, and in this package you have a module named *frontends*. Supose *frontends/wsgi.py* is the module that defines the WSGI application object, as specified by PEP-333. ::


    myapp/
      __init__.py
      module1.py
      module2.py
      web/
        __init__.py
        frontends/
          __init__.py
          wsgi.py


In this example you would call wsgid with ``--wsgi-app=myapp.web.frontends.wsgi.application``

The WSGI application object does not necessarily have to be named *application*. So if your app defines an object named *wsgi_entry_point*, just pass ``--wsgi-app=myapp.web.frontends.wsgi.wsgi_entry_point`` to wsgid.

**Important**: if you pass ``--wsgi-app`` and not ``--app-path``, wsgid will generate all logs inside */tmp/logs*, so be sure that this path exists before running wsgid in daemon mode.

loader-dir
**********
    ``--loader-dir=LOADER_DIR``

If wsgid cannot auto-load your app, you can write your own loaders and point them to wsgid with this option. *LOADER_DIR* is just a folder with some .py files. wsgid will try to load all .py files searching for custom application loaders. The first loader that reports the ability to load the given application will be used

When this option is used at the same time as the --chroot option, the value passed will be relative to the --app-path folder. You can pass more than one *--loader-dir* options, all folders will be searched for custom loaders, in order.

chroot
******
  ``--chroot``

When this option is used, wsgid does a chroot to the ``--app-path`` folder. Remember that you have to run wsgid as root for this options to take effect. Running a daemon as root is not a good idea, so wsgid will drop privileges to the user/group that owns the ``--app-path`` folder.

recv
****
  ``--recv=RECV_SOCKET``

TCP socket used to receive data from mongrel2. This is the same value that is in the *send_spec* of *handler* table of mongrel2's config database. By passing this option to wsgid your application will respond to requests for any routes associated with this socket.

The format of *RECV_SOCKET* can be any format accepted by zeromq

send
****
  ``--send=SEND_SOCKET``

TCP socket used to return data to mongrel2. This is the same value that is in the *recv_spec* of *handler* table of mongrel2's config database. This value must belong to the same registry from where you got your ``--recv`` socket.

The format of *SEND_SOCKET* can be any format accepted by zeromq

no-dameon
*********
  ``--no-daemon``

Used mainly for debug purposes. When this option is passed wsgid will not fork to background and will write all logs to stderr.

stdout
******
.. versionadded:: 0.5.0

Redirect all log output to stdout. This is useful when you want to test things out. Use it with ``--no-daemon`` so you can see all log messages right on the you started wsgid.

workers
*******
  ``--workers=N``

Set the number of wsgid workers processes. Each process has its own PID and is responsible for handling one request at a time.

keep-alive
**********
  ``--keep-alive``

This option will make wsgid watch for its child processes. If any child process dies a new process is created immediately.

.. _asyncupload:

mongrel2-chroot
***************

.. versionadded:: 0.5.0

This option is used if you want to take advantage of mongrel2's async upload. You can still support big requests without it, but you will have to set ``limits.content_length`` to a big value.

Since mongrel2 creates all temporary files relative to it's chroot, each wsgid instance handling requests from any mongrel2 server instance must know where this server is chrooted. This is necessary because wsgid needs to prepend this chroot path to the path mongrel2 creates the files.

If this option is not set, wsgid will use the original path provided by mongrel2.

.. _json-config:

Using the command line options inside a config file
---------------------------------------------------

.. versionadded:: 0.2

wsgid is able to load config options from a config file. This file must be at the root of your app-path. The file name is *wsgid.json*. The internal format is just plain JSON. The only option that you can't use in the JSON config file is ``--app-path``. All other options are the same, just remember to remove the ``--`` part and replace the ``-`` with ``_``. So ``--wsgi-app`` becomes ``wsgi_app``. An example of a *wsgid.json* follows: ::

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


This will create two environ variables that your app will be able to read using ``os.environ['ENV1']`` and ``os.environ['ENV2']``.

.. _commands:


WSGID Commands
--------------

.. versionadded:: 0.3.0

Since version 0.3.0 wsgid has added support for loadable custom commands. A wsgid command is the first option passed on the command line to wsgid. This first options has a special meaning and wsgid will try to find and internal implementation for this command.

A simple example is the `init` command. To use it you can run:

   $ wsgid init --app-path=/some/path

This will initialize and wsgid application folder (See :doc:`appstructure`) by creating all necessary folders. Note that all options (See :ref:`main-options`) recognized by wsgid on the command line will be also passed to the command implementation.

Command cas also add extra options do wsgid. When you run wsgid with `--help`, at the bottom of the help screen you will see all options added by each custom command ::


    A complete WSGI environment for mongrel2 handlers
    
    Some text here...

    Options added by the init subcommand

    --no-init             Turns off debug option

    Options added by the config subcommand

    --no-debug            Turns off debug option
    --no-keep-alive       Turns off Keep alive option
    --no-chroot           Turns off Chroot option


For more information about how to implement more custom commands, please see :ref:`commands-implementation`.

init
****

This command will initialize a brand new appfolder for your new application. It will create all necessary folders automatically. It will also create the folder passed to `--app-path` if it does no already exist. ::

    $ wsgid init --app-path=/path/where/to/create

config
******


This command will create the config file using all command line arguments passed to it. eg. ::

    $ wsgid config --app-path=/path/to/app --send=tcp://127.0.0.1:8888 --recv=tcp:127.0.0.1:8889 --workers=8 --keep-alive

this  wil create a file named `wsgid.json` inside `/path/to/app`. So you will be able to start your application just running: ::

    $ wsgid --app-path=/path/to/app

The `wsgid.json` would be like this: ::

    {
      "keep_alive": "True",
      "workers": "8",
      "recv": "tcp://127.0.0.1:8889",
      "send": "tcp://127.0.0.1:8888"
    }

restart
*******

.. versionadded:: 0.4.0

This command sends a SIGTERM signal to all your worker processes. This, in addition to the keep-alive option can restart your entire application. ::

    $ wsgid restart --app-path=/path/to/your/app

stop
****

.. versionadded:: 0.4.0

This command sends a SIGTERM signal to all your master processes. This will completely turn off your entire application, unless you are using some kind of supervisor. ::

    $ wsgid stop --app-path=/path/to/your/app

status
******

.. versionadded:: 0.5.0

This command reports on stdout the current status of your wsgid instances. Note that it will report "Stopped" even if you have a master process but no worker processes. This is because the master process does not respond to requests. ::

    $ wsgid status --app-path=/path/to/your/app
    Status: Running
    Master pid(s): 17261
    Worker pid(s): 9847(dead), 17262

Any dead pid is reported as "(dead)".





