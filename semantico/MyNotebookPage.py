'''
Created on Nov 11, 2011

@author: konstantine
'''
from gi.repository import Gtk


class MyNoteBook(Gtk.Notebook):
    def __init__(self):
        Gtk.Notebook.__init__(self)
        self.tabs = list()
        self.connect_after("switch-page", self._on_switch_page_after)
        self.last_page = 0
        
    def remove_output(self, outputTab):
        if len(self.tabs) == 2:
            return
        index = self.tabs.index(outputTab)
        self.prev_page()
        self.remove_page(index)
        self.tabs.remove(outputTab)

    def add_output(self, outputTab, get_focus=True, set_last=False):
        if set_last:
            index = self.append_page(outputTab.get_page(), outputTab.get_title())
        else:
            index = self.insert_page(outputTab.get_page(), outputTab.get_title(), len(self.tabs)-1)        
        
        if get_focus:
            self.set_current_page(index)
        self.tabs.insert(index, outputTab)
        
    def get_current_output(self):
        return self.tabs[self.get_current_page()]
    
    def change_current_content(self, content):
        _output = self.get_current_output()
        _output.change_content(content)
        
        
    def _on_switch_page_before(self, notebook, page, page_no):
        self.current = self.get_current_page()
         
    def _on_switch_page(self, notebook, page, page_no):
        #check if is the "+" tab
        print 'inside'
        if len(self.tabs) == 0 or self.get_current_page() == len(self.tabs)-1:
            return
        self.current = page_no;
    
    def _on_switch_page_after(self, notebook, page, page_no):
        #check if is the "+" tab
        #and change back to the previous tab
        if page_no == self.get_n_pages() -1:
            self.set_current_page(self.last_page)
        else:
            self.last_page = page_no
        

class OutputTab():
    '''
    This is the class to create a new tab
    '''
    counter = 1

    def __init__(self, parent, title=None, closable=True, no_title=False, persistant=False):
        '''
        Constructor
        parent: a Notebook
        '''
        self.parent = parent
        self.closable = closable
        self.scroll = Gtk.ScrolledWindow()
        self.box = Gtk.HBox()
        self.label_box = Gtk.HBox(spacing=5)
        self.scroll.add_with_viewport(self.box)
        self.scroll.show_all()
        #default title: Tab 1,2,3...
        if no_title:
            pass
        else:
            if title is None:
                label = Gtk.Label('Output %d' % OutputTab.counter)
                OutputTab.counter += 1
            else:            
                label = Gtk.Label(title)
                
            self.label_box.pack_start(label, False, False, 0)
        
        _btn = Gtk.Button()
        _btn.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image()
        if closable:
            _btn.connect_after('clicked', self.on_close_clicked)
            img.set_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.MENU)
        else:
            _btn.connect_after('clicked', self.on_add_clicked)
            img.set_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU)
        
        _btn.set_image(img)
        if not persistant:
            self.label_box.pack_start(_btn, False, False, 0)
        self.label_box.show_all()
        
    def get_page(self):
        return self.scroll
    
    def get_title(self):
        return self.label_box
        
    def on_close_clicked(self, button):
        self.parent.remove_output(self)
        
    def on_add_clicked(self, button):
        add_tab = OutputTab(self.parent)
        self.parent.add_output(add_tab)
        
    def add_content(self, content):
        content.show_all()
        self.box.pack_start(content, True, True, 0)
    
    def change_content(self, content):
        for child in self.box.get_children():
            self.box.remove(child)
        self.add_content(content)
        
    
            
        