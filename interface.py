# encoding: utf-8
import os, ttk, sys, tkFont, csv, re
import Tkinter as tk
import ScrolledText as tkst
from tkFileDialog import askdirectory, askopenfilename, asksaveasfilename

import regex_ops 

import radio_free_asia
import radio_free_asia.spiders.rfa_transcripts
import scrapy
from scrapy.crawler import CrawlerProcess


default_fieldnames = ['date','category','author_latin','text_latin','title_latin','keywords']
default_data = []
default_dir = os.getcwd()

class Window(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.master=master
        self.output_dir=default_dir
        self.input_csv=None

        self.all_fieldnames = default_fieldnames
        self.fieldnames = default_fieldnames
        self.data = default_data
        self.tree = None
        
        for row in range(50):
            tk.Frame.rowconfigure(self, row, weight=1)
            tk.Frame.columnconfigure(self, row, weight=1)

        self.init_window()


    def init_window(self):
        self.master.title("rfa webscraper")
        self.pack(fill=tk.BOTH, expand=1)

        #INITIALIZE NOTEBOOK STRUCTURE
        tabs = ttk.Notebook(self)
        tabs.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')

        pages = []
            
        page1 = ttk.Frame(tabs)
        #tabs.add(page1,text='Spider')
        #pages.append(page1)
        
        page2 = ttk.Frame(tabs)
        tabs.add(page2,text='CSV')
        pages.append(page2)

        for page in pages:
          for row in range(50):
            ttk.Frame.rowconfigure(page, row, weight=1)            
            ttk.Frame.columnconfigure(page, row, weight=1)            

        #PAGE1 ELEMENTS
        outdir_button = tk.Button(page1, text="Select output dir", command=self.sel_outdir)
        outdir_button.grid(row=9, column=1, sticky='W')

        self.outdir_text = tk.StringVar()
        self.outdir_text.set("  current dir: "+ self.output_dir)
        self.outdir_label = tk.Label(page1, textvariable=self.outdir_text)
        self.outdir_label.grid(row=9,column=2,sticky='W')

        crawl_button = tk.Button(page1, text="Crawl spider", command=self.run_spider)
        crawl_button.grid(row=8, column=1, sticky='W')

        #CASCADING MENU
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)
        file_menu = tk.Menu(menu)
        
        file_menu.add_command(label="Exit", command=self.client_exit)
        file_menu.add_command(label="Export Data", command=self.export_data)
        menu.add_cascade(label="File", menu=file_menu)
        
        #PAGE2 ELEMENTS

        #treeview with dual scrollbars
        self.tree = ttk.Treeview(page2, columns=self.fieldnames, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.tree.xview)
        self.tree.bind('<Double-Button-1>', self.row_detail_view)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=1, columnspan=20, rowspan=20, padx=20, pady=20, sticky='nsew', in_=page2)
        vsb.grid(column=19, row=2, rowspan=18, sticky='ns', in_=page2)
        hsb.grid(column=0, row=20, columnspan=20, padx=20, sticky='ew', in_=page2)

        self.build_tree()
        #\\\
        
        tk.Label(page2, text="Select a .csv: ").grid(row=21, column=0, padx=20, sticky='W')
        selfile_button = tk.Button(page2, text="File", width=5, command=self.sel_csv)
        selfile_button.grid(row=21, column=1, sticky='W')

        tk.Label(page2, text="Input csv:").grid(row=21, column=2, sticky="W")
        self.selfile_text = tk.StringVar()
        self.selfile_text.set("")
        self.selfile_label = tk.Label(page2, textvariable=self.selfile_text)
        self.selfile_label.grid(row=21,column=3,sticky='W')

        selfile_button = tk.Button(page2, text="Reload selection", width=12, command=self.reload_csv)
        selfile_button.grid(row=21, column=6, sticky='W')

        self.regex = None

        tk.Label(page2, text="Input RegExp: ").grid(row=22, column=0, padx=20, sticky='W')
        self.regex_entry = tk.Entry(page2, width=60)
        self.regex_entry.grid(row=22,column=1, columnspan=4, sticky='W')
        regexcomp_button = tk.Button(page2, text='Compile RegExp', command=self.compile_regex_handler)
        regexcomp_button.grid(row=22,column=6,sticky='W')

        self.regexmsg_text = tk.StringVar()
        self.regexmsg_text.set("")
        self.regexmsg_label = tk.Label(page2, textvariable=self.regexmsg_text)
        self.regexmsg_label.grid(row=23,column=1,columnspan=5, sticky='W')

        self.regexop_text = tk.StringVar()
        self.regexop_text.set('')
        tk.Label(page2, textvariable=self.regexop_text, fg='red').grid(row=24,column=4,columnspan=3,sticky='W')
        tk.Label(page2, text="RegExp operations: ").grid(row=23, column=0, padx=20, sticky='W')
        tk.Label(page2, text="Field: ").grid(row=24, column=0, padx=20, sticky='W')

        self.field_entry = tk.Entry(page2, width=15)
        self.field_entry.grid(row=24,column=1,sticky='W')

        tk.Label(page2, text="select operation: ").grid(row=24, column=3, columnspan=3, sticky='E')
        
        regex_options = ['Sift', 'Find all']
        regex_sel = tk.StringVar()
        regex_sel.set('Sift (default)')
        regex_drop = tk.OptionMenu(page2, regex_sel, *regex_options)
        regex_drop.grid(row=24,column=6, columnspan=1, sticky='W')
        regex_drop.config(width=len(max(regex_options +
                                        ['Sift (default)'], key=len)))
        
        self.regexfilter_button = tk.Button(page2, text='Filter',
                                            command=lambda: self.regex_filter_handler
                                            (self.field_entry.get(), regex_sel.get()))
        self.regexfilter_button.grid(row=25,column=6, padx=20, sticky='W')
        self.regexfilter_button.configure(width=10)

        self.export_button = tk.Button(page2, text='Export .csv',
                                       command=self.export_csv_handler)
        self.export_button.grid(row=26, column=6, sticky='W')
        self.regexfilter_button.configure(width=10)
        
    #===================#
    #  CASCADE METHODS  #
    #===================#

    def client_exit(self):
        exit()

    def export_data(self):
        return


    #===================#
    #   PAGE1 METHODS   #
    #===================#
     
    # opens new window to select directory; updates text in root.
    def sel_outdir(self):
        #check for cancelled command
        tmp = askdirectory()
        if (tmp != ''):
            self.output_dir = tmp
        self.outdir_text.set("  current dir: " + self.output_dir)

    def run_spider(self):
        radio_free_asia.spiders.rfa_transcripts.foo()


    #===================#
    #   PAGE2 METHODS   #
    #===================#

    def sel_csv(self):
        #check for cancelled command
        tmp = askopenfilename(filetypes=[('csv files', '*.csv')])
        if (tmp != ''):
            self.input_csv = tmp
        parts = tmp.split('/')
        self.selfile_text.set("  input .csv: " + '...'+(parts[-2]+'/'+parts[-1])[-16:])
        self.update_table()

    def reload_csv(self):
        try:
            self.update_table()
        except TypeError:
            return
        
    def build_tree(self):
        self.tree.delete(*self.tree.get_children())
        for col in self.fieldnames:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: self.sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))
        for item in self.data:
            self.tree.insert('', 'end', \
                             values=reduce(lambda x,y : x+(item[y],), \
                             default_fieldnames, ()))
            # adjust column's width if necessary to fit each value
            for name, val in enumerate(filter(lambda x : x in default_fieldnames, item)):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.fieldnames[name],width=None)<col_w:
                    self.tree.column(self.fieldnames[name], width=col_w)

    # This method does not behave properly if the new CSV has different 
    # fieldnames than the previous file.  This shouldn't be an issue,
    # since any new CSV should be a product of a previous one.
    #
    # As of this version, the method is well-behaved if default_fieldnames
    # is a subset of the csv's fieldnames
    def update_table(self):
        with open(self.input_csv) as csvfile:
            dr = csv.DictReader(csvfile)
            self.all_fieldnames = dr.fieldnames
            self.data = []
            for row in dr:
                tmp = {}
                for key in row:
                    tmp[regex_ops.ensure_unicode(key)] = regex_ops.ensure_unicode(row[key])
                self.data.append(tmp)
            self.build_tree()
    
    def sortby(self, tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, \
            int(not descending)))    

    #TODO:  get this function to access the original csv-dict line
    #       note that at present, this method relies on the values
    #       of default_fieldnames for formatting.
    #
    def row_detail_view(self, event):
        cur =  self.tree.item(self.tree.focus())['values']
        if not cur: return
        # the items at ['values'] are already in the right order.
        # just zip them up with their key.
        vals = dict(zip(default_fieldnames, cur))

        # Frames 1 through 3 are pretty self-explanatory.
        # print keys/vals
        popup = tk.Toplevel()
        frame1 = tk.Frame(popup)
        frame1.pack(fill='x')
        tk.Label(frame1, text="Title:", width=6).pack(side='left', padx=5, pady=5)
        tk.Message(frame1, text=vals["title_latin"], width=400).pack(side='left', padx=5)
        frame2 = tk.Frame(popup)
        frame2.pack(fill='x')
        tk.Label(frame2, text="Author:", width=7).pack(side='left', padx=5, pady=5)
        tk.Label(frame2, text=vals["author_latin"]).pack(side='left', padx=5)
        frame3 = tk.Frame(popup)
        frame3.pack(fill='x')
        tk.Label(frame3, text="Date:", width=5).pack(side='left', padx=5, pady=5)
        tk.Label(frame3, text=vals["date"]).pack(side='left', padx=5)

        # frame4 creates a Message; this is used to help the
        # ScrolledText obj. look like a Message obj..  
        #
        frame4 = tk.Frame(popup)
        frame4.pack(fill='x', expand=True)
        m = tk.Message(frame4)
        txt = tkst.ScrolledText(frame4,background=m.cget("background"),
                      relief="flat", borderwidth=0, wrap='word',
                      font=m.cget("font"), width = 75, height=25)
        m.destroy()
        txt.insert('end', vals["text_latin"])
        txt.pack(side='left', padx=5, pady=5, fill='x',expand=True)
        
        return
    
    def compile_regex_handler(self):
        try:
            # the parens are to set the whole regexp to a 'group'
            # this allows the regexp to have parens internally
            # without changing the return type of findall().
            #
            s_u = u'(' + unicode(self.regex_entry.get()) + u')'
            tmp = re.compile(s_u, re.UNICODE)
            self.regex = tmp
            self.regexmsg_text.set('compilation success')
            self.regexmsg_label.configure(fg='blue')
        except re.error:
            self.regexmsg_text.set('compilation failure')   
            self.regexmsg_label.configure(fg='red')
            
    def regex_filter_handler(self, field, op):
        if self.regex == None:
            self.regexop_text.set('RegExp not found.')
            return
        elif field not in default_fieldnames:
            self.regexop_text.set('Field not in fieldnames.')
            return
        self.regexop_text.set('')

        if op == 'Sift (default)' or op == 'Sift':
            self.data = regex_ops.sift(self.data, field.lower(), self.regex)
        elif op == 'Find all':
            self.data = regex_ops.find_all(self.data, field.lower(), self.regex)
        self.build_tree()

    def export_csv_handler(self):
        f = asksaveasfilename(filetypes=[('csv files', '*.csv')])
        if (f != ''):
            try:
                with open(f, 'wb') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.all_fieldnames)
                    writer.writeheader()
                    for row in self.data:
                        writer.writerow(dict((k, v.encode('utf-8')) for k, v in row.iteritems()))
            except IOError as (errno, strerror):
                print("I/O error({0}): {1}".format(errno, strerror))    
        return      

        
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("680x500")

    main_iface = Window(root)
    root.mainloop()
