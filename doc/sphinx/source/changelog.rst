Changelog
=========

Version 0.5.0
*************

 * Implemented the ``status`` command. More at :ref:`commands`;
 * New command line option: ``--stdout`` to redirect all logs to stdout;
 * Feature: Now it's possible to load external django configuration that will be added to your application's settings module. See moreat :ref:`djangoconf`; 
 * --no-daemon option is now also saved in wsgid.json (using ``wsgid config`` command). If you were using ``nodaemon`` in your wsgid.json files, remember to change all references of ``nodaemon`` to ``no_daemon``.
 * Support for mongrel2 async upload mechanism. This adds a new command line option, ``--mongrel2-chroot``. Read more at: :ref:`asyncupload`. A brief tutorial about how to use this options is here: :ref:`asyncupload-tut`
 * Implementation of a cached options at ``wsgid.conf.settings``. To use you just need: ``from wsgid.conf import settings``.
 * Minor bugfixes.

 * Commit log:  https://github.com/daltonmatos/wsgid/compare/v0.4.2...v0.5.0

Version 0.4.2
*************

 * Hotfix for default --workers value. Defaults to 1
 
 * Commit log:  https://github.com/daltonmatos/wsgid/compare/v0.4.1...v0.4.2

Version 0.4.1
*************

 * Hotfix for bug #6, that was actually not solved.
 
 * Commit log:  https://github.com/daltonmatos/wsgid/compare/v0.4.0...v0.4.1

Version 0.4.0
*************

 * Implemented a new command: ``restart``, ``stop`` with the ability to choose a custom signal to send. See more at :ref:`commands`;
 * Bugfix (github issue #6): Command line options are incorrectly parsed when using python 2.7.2;
 * Internal refactorings
 * Keep-alive is now the default behavior
 * Created WsgidApp abstraction around wsgid app folder. See more at :ref:`wsgidapp-object`
 * Better django application discovery

 * And as usual, here is the changelog for the nerds. =)  https://github.com/daltonmatos/wsgid/compare/v0.3.0...v0.4.0

 
Version 0.3.0
*************

 * Implementation of loadabe subcommands. For more see :ref:`commands` and :ref:`commands-implementation`
 * Internal refactoring to simplify the overall code.
 * First steps towards py3k compatibility.
 * Bug fixes.
 * Added simplejson as a dependency
 * Thanks to `yoshrote`_, `zhemao`_ and `Antoine Delaunay`_ for the contributions.

 * And as usual, here is the changelog for the nerds. =)  https://github.com/daltonmatos/wsgid/compare/v0.2.1...v0.3.0

.. _yoshrote: https://github.com/daltonmatos/wsgid/commit/524403b3
.. _zhemao: https://github.com/daltonmatos/wsgid/commit/e779e174
.. _Antoine Delaunay: https://github.com/daltonmatos/wsgid/commit/b3c9b73d

Version 0.2.1
*************

 * Now it's possible to declare custom environ variables wsgid will create before starting your instances. More at :ref:`env-vars`.
 * Bugfix: When wsgid did not start for any reason, it was not removing pid files.

 * Here is the changelog for the nerds. All commits since last version. https://github.com/daltonmatos/wsgid/compare/v0.2...v0.2.1


Version 0.2
***********

  * Wsgid now creates pidfiles for all started processes. Master and workers. See :ref:`pid-folder`;
  * Bugfix: DjangoAppLoader now disconsiders hiddend folders inside ${app-path}/app;
  * Bugfix: Create each request with a fresh environ. Wsgid was keeping values between different requests;
  * Support for REMOTE_ADDR;
  * Wsgid now licensed under New BSD License;
  * Removed pypi package, at least temporarily;
  * Fixed setup.py: Don't try to install man pages on every run;
  * Wsgid is now able to load options from a JSON config file. More on :ref:`json-config`;
  * bugfix: Fatal errors are now correctly logged;
  * Internal refactorings.

  
Version 0.1
***********

  * Initial release


