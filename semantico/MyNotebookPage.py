'''
Created on Nov 11, 2011

@author: konstantine
'''
from gi.repository import Gtk


class MyNoteBook(Gtk.Notebook):
    def __init__(self):
        Gtk.Notebook.__init__(self)
        self.tabs = list()
        
    def remove_output(self, outputTab):
        index = self.tabs.index(outputTab)
        self.remove_page(index)
        self.tabs.remove(outputTab)

    def add_output(self, outputTab, get_focus=True):
        index = self.append_page(outputTab.get_page(), outputTab.get_title())
        if get_focus:
            self.set_current_page(index)
        self.tabs.append(outputTab)

class OutputTab():
    '''
    '''
    counter = 1

    def __init__(self, parent, title=None, closable=True):
        '''
        Constructor
        parent: a Notebook
        '''
        self.parent = parent
        self.closable = closable
        self.btn = Gtk.Button('Dynamic button')
        self.box = Gtk.HBox()
        #self.box.add(self.btn)
        self.box.show_all()
        self.label_box = Gtk.HBox(spacing=5)
        if not title:
            label = Gtk.Label('Output %d' % OutputTab.counter)
            OutputTab.counter += 1
        else:            
            label = Gtk.Label(title)
        self.label_box.pack_start(label, False, False, 0)
        if closable:
            close_btn = Gtk.Button()
            close_btn.connect_after('clicked', self.on_close_clicked)
            img = Gtk.Image()
            img.set_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.MENU)
            close_btn.set_image(img)
            self.label_box.pack_start(close_btn, False, False, 0)
            
        self.label_box.show_all()
        
    def get_page(self):
        return self.box
    
    def get_title(self):
        return self.label_box
        
    def on_close_clicked(self, button):
        self.parent.remove_output(self)
        
    def add_context(self, context):
        context.show_all()
        self.box.pack_start(context, True, True, 0)
        
    
            
        