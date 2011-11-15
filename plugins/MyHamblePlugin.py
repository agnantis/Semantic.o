'''
Created on Nov 14, 2011

@author: gs
'''
from semantico.PluginMount import PluginProvider

class MyHamblePlugin(PluginProvider):
    title = 'My Hamble Plugin'
    description = '''
        This is an attempt to create
        a simple plugin which removes the input window
        '''
    
    def __init__(self):
        pass
    
    def do_activate(self):
        print 'plugin activated'
    
    def do_deactivate(self):
        print 'plugin deactivated'
        
    def do_update_state(self):
        print 'plugin update'
        
        