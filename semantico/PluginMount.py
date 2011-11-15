'''
Created on Nov 14, 2011

@author: gs
'''

class PluginMount(type):

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            #list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)
            
            
class PluginProvider:
    """
    Mount point for plugins which refer to actions that can be performed.

    Plugins implementing this reference should provide the following attributes:

    ===========  ========================================================
    title         The text to be displayed, describing the action
    description   The URL to the view where the action will be carried out
    ===========  ========================================================
    """
    __metaclass__=PluginMount
    
    def __init__(self):
        pass
    
    def do_activate(self):
        pass
    
    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass
    