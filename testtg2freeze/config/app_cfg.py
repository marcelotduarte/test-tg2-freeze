# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in test-tg2-freeze.

This file complements development/deployment.ini.

"""
from tg.configuration import AppConfig

import testtg2freeze
from testtg2freeze import model, lib

import sys
if getattr(sys, 'frozen', False) and '--patch' in sys.argv:
    from tg.support.statics import StaticsMiddleware, FileServeApp, HTTPForbidden, time, _FileIter, _BLOCK_SIZE
    import mimetypes
    from pkg_resources import resource_exists, resource_stream, ResolutionError, ExtractionError
    
    class FrozenFileServeApp(FileServeApp):
        def __init__(self, package, path, cache_max_age):
            self.package = package
            self.path = path
            self.last_modified = 0#getmtime(path)
            self.content_length = 0#getsize(path)
            self.cache_expires = cache_max_age
            content_type, content_encoding = mimetypes.guess_type(path, strict=False)
            if content_type is None:
                content_type = 'application/octet-stream'
    
            self.content_type = content_type
            self.content_encoding = content_encoding
            
        def __call__(self, environ, start_response):
            try:
                fp = resource_stream(self.package, self.path)
            except (ResolutionError, ExtractionError) as e:
                return HTTPForbidden('You are not permitted to view this file (%s)' % e)(environ, start_response)
            except Exception as e:
                return HTTPForbidden('Unknown exception (%s)' % e)(environ, start_response)
    
            headers = []
            timeout = self.cache_expires
            etag = self.generate_etag()
            headers += [('Etag', '%s' % etag),
                ('Cache-Control', 'max-age=%d, public' % timeout)]
    
            if not self.has_been_modified(environ, etag, self.last_modified):
                fp.close()
                start_response('304 Not Modified', headers)
                return []
    
            headers.extend((
                ('Expires', self.make_date(time() + timeout)),
                ('Content-Type', self.content_type),
                #('Content-Length', str(self.content_length)),
                ('Last-Modified', self.make_date(self.last_modified))
                ))
            print(headers)
            start_response('200 OK', headers)
            #return environ.get('wsgi.file_wrapper', _FileIter)(fp, _BLOCK_SIZE)
            return iter(lambda: fp.read(_BLOCK_SIZE), '')
    
    class FrozenStaticsMiddleware(StaticsMiddleware):
        def __init__(self, app, package, root_dir, cache_max_age=3600):
            super(FrozenStaticsMiddleware, self).__init__(app, root_dir, cache_max_age)
            self.package = package
            
        def __call__(self, environ, start_response):
            full_path = environ['PATH_INFO']
            print('full_path', full_path)
            if full_path is not None and full_path != '/': 
                filepath = self.doc_root + full_path
                print('procurando', self.package, filepath)
                if resource_exists(self.package, filepath):
                    print('encontrado', self.package, filepath)
                    return FrozenFileServeApp(self.package, filepath, self.cache_max_age)(environ, start_response)
    
            return self.app(environ, start_response)

    class FrozenAppConfig(AppConfig):
        def add_static_file_middleware(self, app):
            app = FrozenStaticsMiddleware(app, 'tw2', 'resources')
            app = FrozenStaticsMiddleware(app, self.package_name, 'public')
            return app
    
    base_config = FrozenAppConfig()
else:
    base_config = AppConfig()
base_config.renderers = []

# True to prevent dispatcher from striping extensions
# For example /socket.io would be served by "socket_io"
# method instead of "socket".
base_config.disable_request_extensions = False

# Set None to disable escaping punctuation characters to "_"
# when dispatching methods.
# Set to a function to provide custom escaping.
base_config.dispatch_path_translator = True

base_config.prefer_toscawidgets2 = True

base_config.package = testtg2freeze

# Enable json in expose
base_config.renderers.append('json')
# Enable genshi in expose to have a lingua franca
# for extensions and pluggable apps.
# You can remove this if you don't plan to use it.
base_config.renderers.append('genshi')

# Set the default renderer
base_config.default_renderer = 'genshi'
# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = testtg2freeze.model
base_config.DBSession = testtg2freeze.model.DBSession
# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "6e2aea2a-5913-4464-b9af-e35d24c352f4"
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User

from tg.configuration.auth import TGAuthMetadata


# This tells to TurboGears how to retrieve the data for your user
class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        login = identity['login']
        user = self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=login
        ).first()

        if not user:
            login = None
        elif not user.validate_password(identity['password']):
            login = None

        if login is None:
            try:
                from urllib.parse import parse_qs, urlencode
            except ImportError:
                from urlparse import parse_qs
                from urllib import urlencode
            from tg.exceptions import HTTPFound

            params = parse_qs(environ['QUERY_STRING'])
            params.pop('password', None)  # Remove password in case it was there
            if user is None:
                params['failure'] = 'user-not-found'
            else:
                params['login'] = identity['login']
                params['failure'] = 'invalid-password'

            # When authentication fails send user to login page.
            environ['repoze.who.application'] = HTTPFound(
                location='?'.join(('/login', urlencode(params, True)))
            )

        return login

    def get_user(self, identity, userid):
        return self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=userid
        ).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]

base_config.sa_auth.dbsession = model.DBSession

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)

# You can use a different repoze.who Authenticator if you want to
# change the way users can login
# base_config.sa_auth.authenticators = [('myauth', SomeAuthenticator()]

# You can add more repoze.who metadata providers to fetch
# user metadata.
# Remember to set base_config.sa_auth.authmetadata to None
# to disable authmetadata and use only your own metadata providers
# base_config.sa_auth.mdproviders = [('myprovider', SomeMDProvider()]

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'
try:
    # Enable DebugBar if available, install tgext.debugbar to turn it on
    from tgext.debugbar import enable_debugbar
    enable_debugbar(base_config)
except ImportError:
    pass
