from __future__ import print_function
import sys

from testtg2freeze.config.app_cfg import base_config
#from testtg2freeze.config.environment import load_environment
#base_config['sqlalchemy.url'] = 'mysql://user:pass@127.0.0.1:3306/db?charset=utf8'
base_config['sqlalchemy.url'] = 'sqlite:///devdata.db'
#base_config['templating.genshi.name_constant_patch'] = True  #PY3
#base_config['debug'] = True
base_config.auto_reload_templates = False 
base_config.use_toscawidgets = False
base_config.use_toscawidgets2 = True
#base_config['paths']['templates'] = 'testtg2freeze/templates'
if getattr(sys, 'frozen', False):
    base_config.custom_tw2_config = {'serve_resources':False, 'serve_controllers':False}#'res_prefix':'/../../',}
app = base_config.make_wsgi_app()

if getattr(sys, 'frozen', False):
    if '--patch' in sys.argv: 
        dotted_filename_finder = base_config['tg.app_globals']['dotted_filename_finder']
        dotted_filename_finder.get_dotted_filename(base_config.package_name+'.templates.master')

if __name__ == '__main__':
    if 'wsgiref' in sys.argv:  #for testing purposes
        from wsgiref.simple_server import make_server
        import webbrowser
        
        print("Simple server on port 8080...")
        httpd = make_server('', 8080, app)
        webbrowser.open_new_tab('http://127.0.0.1:8080')
        httpd.serve_forever()
    else:
        import cherrypy

        print("Cherrypy server on port 8080...")
    
        # Mount the application
        cherrypy.tree.graft(app, "/")
    
        # Unsubscribe the default server
        cherrypy.server.unsubscribe()
    
        # Instantiate a new server object
        server = cherrypy._cpserver.Server()
    
        # Configure the server object
        server.socket_host = "0.0.0.0"
        server.socket_port = 8080
        server.thread_pool = 30
    
        # For SSL Support
        # server.ssl_module            = 'pyopenssl'
        # server.ssl_certificate       = 'ssl/certificate.crt'
        # server.ssl_private_key       = 'ssl/private.key'
        # server.ssl_certificate_chain = 'ssl/bundle.crt'
    
        # Subscribe this server
        server.subscribe()
    
        # Example for a 2nd server (same steps as above):
        # Remember to use a different port
    
        # server2             = cherrypy._cpserver.Server()
    
        # server2.socket_host = "0.0.0.0"
        # server2.socket_port = 8002
        # server2.thread_pool = 30
        # server2.subscribe()
    
        # Start the server engine (Option 1 *and* 2)
    
        cherrypy.engine.start()
        cherrypy.engine.block()
