WSGID Internals
===============


Plugin system
:::::::::::::

wsgid internal plugin system is implemented by plugnplay. This means that all plugins must inherit one same base class, in this case this class is *wsgid.core.Plugin*.

For now, wsgid only declares custom AppLoaders. But any other interface declared in the future will have to be implemented subclassing *wsgid.core.Plugin*.

App Loaders
:::::::::::

App loaders are classes that knows how to load an specific WSGI app. WSGID comes with some apploaders for some frameworks, for now django (http://djangoproject.com) and pyroutes (http://pyroutes.com).

As an app for each of this frameworks has a known structure, wsgid will try to discover the *best loader* for your app. The loaders are used in alphabetical order by the loader filename.

Writing your App Loader
************************

Writing your own AppLoader is very easy and simple. As said before every plugin must inherit *wsgid.core.Plugin* class, so it's not different with the AppLoaders.

To inform wsgid that your Plugin class implements the AppLoader interface (:py:class:`wsgid.loaders.IAppLoader`) you have to add one attribute to your class.::

  implements = [IAppLoader]

This is plugnplay specific, to know more about plugnplay go to: https://github.com/daltonmatos/plugnplay

Now, you need to fill the methods declared for the interface you are implementing, in this case are only two methods.

 * def can_load(self, app_path)
 * def load_app(self, app_path, app_full_name)

The first should return True/False if your loader, looking at the app_path directory, finds out that is can load this application. The second should return the WSGI application object for this app that is being loaded.

Now just save your loader into a .py file and pass --loader-dir=PATH_TO_LOADER to wsgid command line and your loader will be used to load your application. Feel free to write loader for other WSGI frameworks, see the :doc:`contributing` for more details.


.. _commands-implementation:

WSGID commands internal implementation
::::::::::::::::::::::::::::::::::::::

.. versionadded:: 0.3.0

Now wsgid ships with custom commands and you can implement new ones if you need. Again, this capability is implemented through plugnplay. 

To create a new command you just have to implement the :py:class:`wsgid.core.command.ICommand` interface. This interface have 4 methods:

 * `def command_name(self):`
   This method returns the name of your new command. This is the name showed on the help screen, if you command adds any extra option to wsgid CLI.

 * `def name_matches(self, name):`
   This method is used when wsgid is trying to find the right implementation for a command. The `name` parameter is the command name that wsgid is searching. Usually this is the first parameter that was just passed to wsgid CLI.
 
 * `def run(self, options):`
   This is your implementation's main method. The `options` parameter is a special object containing all options passed to wsgid CLI and you can access these options by the name, eg: `options.debug` or `options.app_path`. 
 
 * `def extra_options(sefl):`
   This is where you return the extra options that you want to add. You must return an array of :py:class:`wsgid.core.parser.CommandLineOption`.

Note that when wsgid finds an implementation for a command, it exits just after the run() method returns.
