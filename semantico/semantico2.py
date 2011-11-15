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

MAIN_UI_FILE = "semantico/data/main_window3.glade"

class SemanticoApp:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(MAIN_UI_FILE)
        self.builder.connect_signals(self)

        self.query_editor_buffer = self.builder.get_object('query_editor').get_buffer()   
        self.query_btn = self.builder.get_object('query_btn')  
        self.statusbar =  self.builder.get_object('statusbar')  
        self.outputscroll = self.builder.get_object('outputscroll')  
        #self.treeview = self.builder.get_object('treeview1')
        self.progress = self.builder.get_object('progressbar')
        self.box = self.builder.get_object('outputbox')
        
        self.notebook = MyNoteBook()
        self.notebook.set_scrollable(True)
        self.notebook.show_all()
        self.box.pack_start(self.notebook, True, True, 0)
                
        self.window = self.builder.get_object('window')
        self.window.show_all()
        
        
    def destroy(self, window):
        '''Close application'''
        Gtk.main_quit()
        
    def on_load_file_clicked(self, button):
        '''
        select a file with rdf data to read.
        Currently supports only nt rdf-encoded files
        '''
        dialog = MyFileChooserDialog(button.get_toplevel())
        
        if dialog.run() == 1:
            file_nt = dialog.get_filename()
            print 'File path %s' % file_nt
            self.load_file(file_nt, append=dialog.append_data())         
        else:
            print 'No file selected'
        dialog.destroy()
        
    def load_file(self, filename, format_type='nt', append=False):
        '''
        loads an rdf file, which is located in 'filename'
        Upon load, 'query' button becomes enabled
        and data are sent to the output
        '''
        if not append:
            self.graph = Graph()
        else:
            if not hasattr(self, 'graph'):
                self.graph = Graph()
        try:
            self.graph.parse(filename, format=format_type)
            self.query_btn.set_sensitive(True)
            self.populate_all_data()
        except IOError:
            self.status("Wrong URL of file path. Nothing loaded.")     
            
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
                    
    def on_load_url(self, button):
        dialog = URLDialog(button.get_toplevel())
        if dialog.run() == Gtk.ResponseType.OK:
            url = dialog.get_URL()
            dialog.destroy()
            (_, _, suffix) = url.rpartition('.')
            suffix = suffix.lower()
            if suffix == 'rdf':
                suffix = 'xml'
            print "URL:", url
            if url:
                self.load_file(url, format_type=suffix, append=dialog.append_data())
        else:
            dialog.destroy()
            print "The Cancel button was clicked"
        
        
    def status(self, text):
        self.statusbar.push(1, text) 
        
    def get_query_text(self):
        start_iter, end_iter = self.query_editor_buffer.get_bounds();
        query_text = self.query_editor_buffer.get_text(start_iter, end_iter, True)
        return query_text
    
    def populate_all_data(self):
        store = Gtk.ListStore(str, str,str)
        
        triples = 0;
        for row in self.graph:
            store.append(row)
            triples += 1
        plur = '' if triples == 1 else 's'
                
        self.status("%d triple%s inserted successfully" % (triples, plur))   
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
    
class URLDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Specify a valid URL", parent, 
                         flags=Gtk.DialogFlags.MODAL, 
                         buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_response(Gtk.ResponseType.OK)
        box = self.get_content_area()
        label = Gtk.Label("Give the URL of the RDF file:")
        label.set_halign(Gtk.Align.START)
        label.set_margin_bottom(6)
        label.set_margin_top(6)
        self.url_field = Gtk.Entry()
        self.url_field.set_width_chars(35)
        self.url_field.set_placeholder_text("Type a URL")
        self.url_field.set_margin_bottom(10)
        
        self.append_btn = Gtk.CheckButton("Append data")
        #box = Gtk.Box()
        box.pack_start(label, True, True, 0)
        box.pack_start(self.url_field, True, True, 0)
        box.pack_start(self.append_btn, True, True, 0)
        #box.set_spacing(1)
        box.set_margin_left(10)
        box.set_margin_right(10)
        self.show_all()
        
    def append_data(self):
        return self.append_btn.get_active()
        
    def get_URL(self):
        return self.url_field.get_text().strip()
            
class MyFileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, "Load RDF/XML file", parent, Gtk.FileChooserAction.OPEN)
        self.add_button(Gtk.STOCK_CANCEL, 0)
        self.add_button(Gtk.STOCK_OPEN, 1)
        self.append_btn = Gtk.CheckButton("Append data")
        self.append_btn.set_halign(Gtk.Align.END)
        self.set_extra_widget(self.append_btn)
        self.set_default_response(1)
        
        filefilter = Gtk.FileFilter()
        filefilter.set_name("RDF/nt files")
        filefilter.add_pattern("*.nt")
        self.set_filter(filefilter)
        
    def append_data(self):
        return self.append_btn.get_active()
        
def main():
    app = SemanticoApp()
    Gtk.main()
    
if __name__=='__main__':
    main()
        
        
