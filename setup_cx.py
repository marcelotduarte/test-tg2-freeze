#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function
from datetime import datetime
T1 = datetime.now()
import sys, os, shutil

from cx_Freeze import setup, Executable
import site

sys.argv.append('build')
dist_dir = 'build/exe.win32-2.7/'
project = os.path.basename(os.getcwd()).replace('-', '')
print('Project:', project)
 
# Remove the build folder
#shutil.rmtree(dist_dir, ignore_errors=True)

# The namespace packages must be installed all with 'pip install' or 'easy_install -Z'
# If necessary uninstall it and reinstall.
# Other packages not used, but in in the same namespace, must be reinstalled. 
# pip uninstall tgext.admin tgext.crud tgext.asyncjob tgext.wdb
# pip install tgext.admin tgext.asyncjob
# if you want install tgext.wdb, crud is auto installed by admin
# mysql: easy_install -Z mysql-python
# or use pymysql

namespace_packages = ['tg', 'tgext', 'tw2', ]
packages = [project, 'tgext.admin', 'genshi', 'backlash',
            'babel', 'sqlalchemy', 'alembic', 'repoze.who', 'tw2.forms',
            'tgext.asyncjob', 'setuptools', 'gearbox', 'paste.deploy', 'pymysql', 'MySQLdb',
            'cherrypy', 'encodings', 'email',]
includes = ['pygments.styles.default', 'zope.sqlalchemy', 'sqlalchemy.ext.declarative',
            'csv', 'tw2.core.templates',]
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl', 'Tkconstants', 'Tkinter']
dll_excludes = ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 
                'tcl85.dll', 'tk85.dll',
                'MSVCP90.dll', 'mswsock.dll', 'powrprof.dll', 'mpr.dll']
icon_resources = []
bitmap_resources = []
other_resources = []
data_files = []
def z_files(path_base, path_data):
    skip_count = len(path_base) 
    zip_includes = [(path_base, path_data)]
    for root, sub_folders, files in os.walk(path_base):
        print(root, sub_folders, files)
        for file_in_root in files:
            zip_includes.append(
                    (
                     os.path.join(root, file_in_root),
                     os.path.join(path_data, root[skip_count+1:], file_in_root).replace('\\', '/')
                    ) 
            )
    print(str(zip_includes).replace('),', '),\n'))      
    return zip_includes

include_files = [(site.getsitepackages()[1]+"\\tw2\\forms\\static\\calendar", "resources\\tw2.forms\\static\\calendar")]

zip_includes =  z_files(site.getsitepackages()[1]+"\\tw2\\core\\i18n", "tw2/resources/tw2/resources/tw2.core/i18n") +\
                z_files(site.getsitepackages()[1]+"\\tw2\\core\\templates", "tw2/core\\templates") +\
                z_files(site.getsitepackages()[1]+"\\tw2\\forms\\static", "tw2/resources/tw2/resources/tw2.forms/static") +\
                z_files(site.getsitepackages()[1]+"\\tw2\\forms\\templates", "tw2/forms\\templates") +\
                z_files(project+"\\templates", project+"/templates") +\
                z_files(project+"\\public", project+"/public")
                
                
# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": packages, "excludes": excludes, "includes": includes,
                     "namespace_packages": namespace_packages,
                     "include_files": include_files, "zip_includes": zip_includes}
base=None

setup(
    name=project,
    version='0.1',
    description=project,
    author='Marcelo Duarte',
    #author_email='',
    #url='',
    package_data={project: ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*/*/*/*/*']},

    options = {"build_exe": build_exe_options},
    executables = [Executable("serve.py", base=base, targetName='serve.exe')],
)
shutil.copy2('development.ini', dist_dir)
shutil.copy2('devdata.db', dist_dir)    #to access user table

print("Freeze completed!")
print("Time elapsed:", datetime.now() - T1)
