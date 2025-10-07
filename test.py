import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *

my_w = ttk.Window()
my_w.geometry("400x300")  # width and height
colors = my_w.style.colors
l1 = [
    {"text": "id", "stretch": False, "width": 50, "anchor": "center"},
    {"text": "Name", "stretch": True, "minwidth": 100},
    {"text": "Class", "anchor": "w"},  # Left-aligned text
    {"text": "Mark", "width": 80, "anchor": "e"},  # Right-aligned, fixed width
    {"text": "Gender"}
]  # Columns with Names and style 
# # Data rows as list 
r_set = [(1, "Alex", 'Four',90,'Female'), (2, "Ron", "Five",80,'Male'), 
            (3, "Geek", 'Four',70,'Male'),(4,'King','Five',78,'Female'),
            (5,'Queen','Four',60,'Female'),(6,'Jack','Five',70,'Female')]
marks=[r[3] for r in r_set] # List of all marks column
print(sum(marks)) # sum of the marks column 
dv = ttk.tableview.Tableview(
    master=my_w,
    paginated=True,
    coldata=l1,
    rowdata=r_set,
    searchable=False,
    bootstyle=SUCCESS,
    pagesize=5,
    height=5,
    stripecolor=(colors.light, None),
)
dv.grid(row=0, column=0, padx=10, pady=5)
dv.autofit_columns() # Fit in current view 
dv.insert_row("end", values=['-', "---", "All", sum(marks), "All"])
dv.load_table_data() # Load all data rows 
my_w.mainloop()



class InfiniteTable(ttk.Frame):
    """
    Treeview-based table that loads data in pages when user scrolls near bottom.
    Usage:
      tbl = InfiniteTable(parent, columns=col_defs, data=rows, pagesize=100)
      tbl.pack(fill='both', expand=True)
    columns: list of dict or strings. If dict, can include 'text', 'width', 'anchor'.
    data: iterable of row tuples/lists (will be converted to list internally).
    """
    def __init__(self, master, columns, data, pagesize=50, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columns = columns
        self._data = list(data)
        self.pagesize = max(1, pagesize)
        self._idx = 0
        self._loading = False

        # Column ids for Treeview
        self._col_ids = [f"c{i}" for i in range(len(columns))]
        self.tree = ttk.Treeview(self, columns=self._col_ids, show='headings', height=15)
        for cid, col in zip(self._col_ids, columns):
            if isinstance(col, dict):
                text = col.get('text', '')
                width = col.get('width', None)
                anchor = col.get('anchor', 'w')
            else:
                text, width, anchor = str(col), None, 'w'
            self.tree.heading(cid, text=text)
            if width is not None:
                self.tree.column(cid, width=width, anchor=anchor)
            else:
                self.tree.column(cid, anchor=anchor)

        # Scrollbar
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self._on_vscroll)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bind scrolling events (cross-platform)
        self._bind_scroll_events()

        # initial load
        self._load_next_page()

    def _bind_scroll_events(self):
        # Windows: <MouseWheel>; Mac: also <MouseWheel>; Linux: <Button-4/5> may be needed.
        self.tree.bind('<MouseWheel>', lambda e: self.after(5, self._check_load_more))
        self.tree.bind('<Button-4>', lambda e: self.after(5, self._check_load_more))
        self.tree.bind('<Button-5>', lambda e: self.after(5, self._check_load_more))
        # Also check after scrollbar drag / key navigation:
        self.vsb.bind('<ButtonRelease-1>', lambda e: self.after(10, self._check_load_more))
        self.tree.bind('<KeyRelease>', lambda e: self.after(10, self._check_load_more))

    def _on_vscroll(self, *args):
        # Forward to treeview and then schedule check
        self.tree.yview(*args)
        self.after(10, self._check_load_more)

    def _load_next_page(self):
        if self._idx >= len(self._data):
            return
        self._loading = True
        end = min(self._idx + self.pagesize, len(self._data))
        for row in self._data[self._idx:end]:
            # If row is shorter/longer than columns, Treeview will pad/truncate automatically
            self.tree.insert('', 'end', values=row)
        self._idx = end
        self._loading = False

    def _check_load_more(self):
        if self._loading:
            return
        # tree.yview() returns (first_fraction, last_fraction)
        first, last = self.tree.yview()
        # When last is near 1.0, load more
        if last >= 0.98 and self._idx < len(self._data):
            self._load_next_page()

    # Optional helper: reset data (for filtering/search)
    def set_data(self, data_iterable):
        self._data = list(data_iterable)
        self._idx = 0
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._load_next_page()