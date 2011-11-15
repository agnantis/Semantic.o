#!/usr/bin/env python

import os, sys
from gi.repository import Gtk
import rdflib
from rdflib.graph import Graph
from rdflib import plugin
from semantico.MyNotebookPage import MyNoteBook, OutputTab
from semantico.PluginMount import PluginProvider

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

UI_FILE = "semantico/data/main_window2.glade"

class SemanticoApp:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)

        self.query_editor_buffer = self.builder.get_object('query_editor').get_buffer()   
        self.query_btn = self.builder.get_object('query_btn')  
        self.statusbar =  self.builder.get_object('statusbar')  
        self.outputscroll = self.builder.get_object('outputscroll')  
        #self.treeview = self.builder.get_object('treeview1')
        self.progress = self.builder.get_object('progressbar')
        self.box = self.builder.get_object('outputbox')
        
        self.notebook = MyNoteBook()
        self.notebook.show_all()
        self.box.pack_start(self.notebook, True, True, 0)
                
        window = self.builder.get_object('window')
        window.show_all()
        
        
    def destroy(self, window):
        '''Close application'''
        Gtk.main_quit()
        
    def on_load_file_clicked(self, button):
        '''
        select a file with rdf data to read.
        Currently supports only nt rdf-encoded files
        '''
        dialog = Gtk.FileChooserDialog("Load RDF/XML file", button.get_toplevel(), Gtk.FileChooserAction.OPEN)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OPEN, 1)
        dialog.set_default_response(1)
        
        filefilter = Gtk.FileFilter()
        filefilter.set_name("RDF/nt files")
        filefilter.add_pattern("*.nt")
        dialog.set_filter(filefilter)
        
        if dialog.run() == 1:
            file_nt = dialog.get_filename()
            print 'File path %s' % file_nt
            self.load_nt_file(file_nt)         
        else:
            print 'No file selected'
        dialog.destroy()
        
    def load_nt_file(self, filename):
        '''
        loads an nt file, which is located in 'filename'
        Upon load, 'query' button becomes enabled
        and data are sent to the output
        '''
        self.graph = Graph()
        self.graph.parse(filename, format="nt")
        self.status("File loaded successfully")   
        self.query_btn.set_sensitive(True)
        self.populate_all_data()
        
    def on_clear_btn_clicked(self, button):
        self._load_plugins()
          
    def on_query_btn_clicked(self, button):
        if not self.graph:
            self.status("No graph loaded")   
        else:
            self.status("Querying...") 
            query_str = self.get_query_text() 
            if not len(query_str):
                pass  
            else:
                try:
                    print "Query:", query_str
                    self.activity_mode = True
                    results = self.graph.query(query_str)
                    self.populate_output_treeview(results)
                    self.status("Results: %d" % len(results))
                    self.activity_mode = False 
                except SyntaxError as er:
                    self.status(str(er))    
        
    def status(self, text):
        self.statusbar.push(1, text) 
        
    def get_query_text(self):
        start_iter, end_iter = self.query_editor_buffer.get_bounds();
        query_text = self.query_editor_buffer.get_text(start_iter, end_iter, True)
        return query_text
    
    def populate_all_data(self):
        store = Gtk.ListStore(str, str,str)
        
        for row in self.graph:
            store.append(row)
            
        self.status("Query answered")   
        #create renderer
        renderer = Gtk.CellRendererText()
        
        treeview = Gtk.TreeView(store)
        for col in treeview.get_columns():
            treeview.remove_column(col)
          
        treeview.append_column(Gtk.TreeViewColumn("Subject", renderer, text=0))
        treeview.append_column(Gtk.TreeViewColumn("Predicate", renderer, text=1))
        treeview.append_column(Gtk.TreeViewColumn("Object", renderer, text=2))  
        
        if not self._main_tab_exists():
            self.all_data_tab = OutputTab(self.notebook, "All Data", persistant=True)
            self.all_data_tab.add_content(treeview)
            self.notebook.add_output(self.all_data_tab)
            #add a + tab
            tab = OutputTab(self.notebook, no_title=True, closable=False)
            self.notebook.add_output(tab, get_focus=False, set_last=True)
        else:
            #populate existing tab
            self.all_data_tab.change_content(treeview)
        
        
    def populate_output_treeview(self, result):
        #create list store
        col_no = len(result.selectionF)
        store = Gtk.ListStore(*[str for _ in range(col_no)])
        #populate list store
        for rs in result:
            #if col = 1, rs won't be a list but a single value
            if col_no == 1:
                rs = [rs]
            store.append(rs)
        #create renderer
        renderer = Gtk.CellRendererText()
        treeview = Gtk.TreeView(store)
        for col in treeview.get_columns():
            treeview.remove_column(col)
          
        for index, name in enumerate(result.selectionF):
            treeview.append_column(Gtk.TreeViewColumn(name, renderer, text=index))  
        
        #check if it is the 'All data' tab, 
        #and create a new one if this is the case
        if self._main_tab_exists() and self.all_data_tab == self.notebook.get_current_output():
            tab = OutputTab(self.notebook)
            tab.add_content(treeview)
            self.notebook.add_output(tab)
        else:
            self.notebook.change_current_content(treeview) 
        
        
    def get_test_output_treeview(self):
        #create list store
        store = Gtk.ListStore(*[str for i in range(3)])
        #populate list store
        treeiter = store.append(["element 1", "element 2", "element 3"])
        treeiter = store.append(["element 2", "element 3", "element 1"])
        treeiter = store.append(["element 3", "element 1", "element 2"])
        #attach store to the treeView
        treeView = Gtk.TreeView(store)
        #create renderer
        renderer = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn("Subject", renderer, text=0)
        column3 = Gtk.TreeViewColumn("Predicate", renderer, text=1)
        column2 = Gtk.TreeViewColumn("Object", renderer, text=2)
        treeView.append_column(column1)       
        treeView.append_column(column2)       
        treeView.append_column(column3)       
        
        return treeView
          
    
    def _load_plugins(self):
        sys.path.append('/home/gs/workspace/python/semantic.o/plugins')
        plugin_path = os.path.join(os.path.expanduser('~'), 'workspace/python/semantic.o/plugins')
        contents = os.listdir(plugin_path)
        for f in contents:
            if os.path.isfile(os.path.join(plugin_path, f)) and f.endswith('.py'):
                (name, _, _) = f.rpartition('.')
                __import__(name)
        print "Activate plugins"
        for plugin in PluginProvider.plugins: #@UndefinedVariable 
            plugin().do_activate()
        
    def _main_tab_exists(self):
        return hasattr(self, 'all_data_tab')
        
def main():
    app = SemanticoApp()
    Gtk.main()
    
if __name__=='__main__':
    main()
        
        
