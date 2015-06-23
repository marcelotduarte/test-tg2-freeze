# test-tg2-freeze
A test and example on how to freeze a turbogears app

To use this example is easy.

It´s tested using python 2.7 (Python 2.7.10 on windows), and, to freeze I'm using cx-Freeze 4.3.4.

py2exe don't support namespaces and a ugly hack freeze it but don´t run.

The folowing must be observed:
- Install all the namespace packages with 'pip install' or 'easy_install -Z'.
- If necessary uninstall it and reinstall, including other packages not used, but in the same namespace.

Example:

`
pip uninstall tgext.admin tgext.crud tgext.asyncjob tgext.wdb
pip install tgext.admin tgext.asyncjob
`

if you want install tgext.wdb, tgext.crud is auto installed within tgext.admin

Example for mysql (use easy_install to install de binary package):
`
easy_install -Z mysql-python
`

If you use pymysql, install with pip.

The support to freeze is in the following patches:

https://github.com/TurboGears/tg2/pull/62

https://github.com/toscawidgets/tw2.core/pull/115

https://github.com/toscawidgets/tw2.forms/pull/43

Run:
`
python setup_cx.py
`

The windows executable will be in build\exe.win32-2.7

Run:
`
cd build\exe.win32-2.7
serve [wsgiref] [--patch]
`

option wsgiref - using library wsgiref ou otherwise cherrypy

option --patch - ativate the necessaries project patchs to run (the patches in tg and tw2 must be applied before)

without --patch you can see the errors like missing master.html, missing static files, etc.
