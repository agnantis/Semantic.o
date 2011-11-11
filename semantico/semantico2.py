#!/usr/bin/env python

from gi.repository import Gtk, GObject
import rdflib
from rdflib.graph import Graph
from rdflib import plugin
from semantico.MyNotebookPage import MyNotebookPage

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

UI_FILE = "data/main_window2.glade"

class SemanticoApp:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)

        self.query_editor_buffer = self.builder.get_object('query_editor').get_buffer()   
        self.query_btn = self.builder.get_object('query_btn')  
        self.statusbar =  self.builder.get_object('statusbar')  
        self.outputscroll = self.builder.get_object('outputscroll')  
        self.treeview = self.builder.get_object('treeview1')
        self.progress = self.builder.get_object('progressbar')
        self.tab_widget = self.builder.get_object('notebook')
        
        self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
        self.activity_mode = False
        
        window = self.builder.get_object('window')
        window.show_all()
        
        
    def destroy(self, window):
        Gtk.main_quit()
        
    def on_load_file_clicked(self, button):
        dialog = Gtk.FileChooserDialog("Load RDF/XML file", button.get_toplevel(), Gtk.FileChooserAction.OPEN)
        dialog.add_button(Gtk.STOCK_CANCEL, 0)
        dialog.add_button(Gtk.STOCK_OPEN, 1)
        dialog.set_default_response(1)
        
        filefilter = Gtk.FileFilter()
        filefilter.set_name("RDF/nt files")
        #filefilter.add_pattern("*.xml")
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
        self.graph = Graph()
        self.graph.parse(filename, format="nt")
        self.status("File loaded successfully")   
        self.query_btn.set_sensitive(True)
        
    def on_clear_btn_clicked(self, button):
        pass
    
    def on_new_tab_btn_clicked(self, button):
        myPage = MyNotebookPage(self.tab_widget)
        position = self.tab_widget.append_page(myPage.get_page(), myPage.get_title())
        myPage.set_position(position)
        
        
    def on_query_btn_clicked(self, button):
        if not self.graph:
            self.status("No graph loaded")   
        else:
            self.status("Querying...") 
            query_str = self.get_query_text() 
            if not len(query_str):
                for (s, p, o) in self.graph:
                    self.append('%s\t%s\t%s\n' % (s, p, o))
                self.status("Query answered")   
            else:
                try:
                    print "Query:", query_str
                    self.activity_mode = True
                    results = self.graph.query(query_str)
                    self.print_out_results(results)
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
        
        self.treeview.set_model(store)
        for col in self.treeview.get_columns():
            self.treeview.remove_column(col)
          
        for index, name in enumerate(result.selectionF):
            self.treeview.append_column(Gtk.TreeViewColumn(name, renderer, text=index))  
        
        
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
          
    def print_out_results(self, result):
        self.populate_output_treeview(result)
        
    def on_timeout(self, user_data):
        """
        Update value on the progress bar
        """
        if self.activity_mode:
            self.progress.pulse()
        #else:
        #    new_value = self.progress.get_fraction() + 0.01
        #    if new_value > 1:
        #        new_value = 0
        #    self.progress.set_fraction(new_value)

        # As this is a timeout function, return True so that it
        # continues to get called
        return True
        
        
def main():
    app = SemanticoApp()
    Gtk.main()
    
if __name__=='__main__':
    main()
        
        
