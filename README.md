# test-tg2-freeze
A test and example on how to freeze a turbogears app

To use this example is easy.
It´s tested using python 2.7 (Python 2.7.10 on windows)
To freeze I'm using cx_Freeze.
py2exe don't support namespaces and a ugly hack freeze it but don´t run.

See the comments in setup_cx.py, especially:
# The namespace packages must be installed all with 'pip install' or 'easy_install -Z'
# If necessary uninstall it and reinstall.
# Other packages not used, but in in the same namespace, must be reinstalled. 
# pip uninstall tgext.admin tgext.crud tgext.asyncjob tgext.wdb
# pip install tgext.admin tgext.asyncjob
# if you want install tgext.wdb, crud is auto installed by admin
# mysql: easy_install -Z mysql-python
# or use pymysql

Tg2 patch is https://github.com/TurboGears/tg2/pull/62
To support tw2, the patch is https://github.com/toscawidgets/tw2.core/pull/115

Run:
python setup_cx.py

The windows executable will be in build\exe.win32-2.7

Run:
cd build\exe.win32-2.7
serve [wsgiref] [--patch]

option wsgiref - using library wsgiref ou otherwise cherrypy
option --patch - ativate the necessaries project patchs to run
(the patches in tg and tw2 must be applied before)
without --patch you can see the errors like missing master.html, missing static files, etc.