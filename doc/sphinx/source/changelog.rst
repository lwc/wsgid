Changelog
=========

Version 0.2.1
***********

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


