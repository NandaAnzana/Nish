import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as tkf
from tkinter.ttk import *
import sqlite3
import pandas as pd

class NISH(tk.Tk):

	def __init__(self):
		tk.Tk.__init__(self)
		self.title("NISH")
		self.geometry('800x600')
		self.iconbitmap('my_icon.ico')
		container = tk.Frame(self)
		container.pack(side="top", fill="both", expand = True)
		container.grid_rowconfigure(2, weight=1)
		container.grid_columnconfigure(3, weight=1)
		self.frames = {}
		for F in (PageAwal,PageSatu,PageDua,PageTiga):
			frame = F(container, self)
			self.frames[F] = frame
			frame.grid(row=1, column=3, sticky="nsew")
		self.show_frame(PageAwal)

	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()	

	def ambil_page(self, page_class):
		return self.frames[page_class]


class PageAwal(tk.Frame):
	
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller=controller
		label = tk.Label(self, text="\n\n\n\n\nHello! Welcome to NISH!", font=("Verdana",24,"bold"), fg="red")
		label.pack(pady=10,padx=10)
		label_1 = tk.Label(self, text="NISH dibuat untuk memenuhi penilaian UAS mata kuliah Komputasi Terstruktur", font=("arial",16), fg="black")
		label_1.pack(pady=10,padx=10)
		button = tk.Button(self, text="Start",command=lambda:controller.show_frame(PageSatu),fg="white",bg="green",font=("arial",16,"bold"))
		button.pack(pady=25,padx=10)

class PageSatu(tk.Frame):
	
	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller=controller
		self.fileopenname=tk.StringVar()
		self.path_name = None
		label = tk.Label(self, text="\n\n\n\n\nPilih Database Anda", font=("Verdana",24,"bold"), fg="red")
		label.pack(pady=10,padx=10)
		label = tk.Entry(self, textvariable=self.fileopenname, state='disabled')
		label.pack(pady=10,padx=10)
		button = tk.Button(self, text="Pilih Yuk!",command=lambda: self.pilih_database(self),fg="white",bg="blue",font=("arial",16,"bold"))
		button.pack(pady=10,padx=10)
		self.button_1 = tk.Button(self, text="Next",command=lambda:controller.show_frame(PageDua),fg="white",bg="blue",font=("arial",16,"bold"),state="disabled")
		self.button_1.pack(side="right")

	def pilih_database(self,root):
		f = tkf.askopenfilename(parent=root, initialdir='C:\\users\\',
                title='Choose file', filetypes=[('db database', '.db')])
		if len(f)==0 and self.path_name==None:
			messagebox.showerror('Gagal', 'Database belum diinput')
			self.button_1["state"]='disabled'
		else:
			if len(f)==0:
				pass
			else:
				kontroler_page_dua = self.controller.ambil_page(PageDua)
				self.path_name = f
				self.conn, self.koneksi_database = koneksi(self.path_name)
				self.koneksi_biasa = DB(self.koneksi_database)
				kontroler_page_dua.combo["values"] = self.koneksi_biasa.list_nama_tabel
				kontroler_page_dua.combo["state"] = "readonly"
				f = f.split("/")
				f = f[-1] 	
				self.fileopenname.set(f)
				messagebox.showinfo('Berhasil', 'Database berhasil diinput')
			self.button_1["state"]='normal'


class PageDua(tk.Frame):

	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller=controller
		self.df = None
		self.list_dataframe = []
		label = tk.Label(self, text="\n\n\n\n\nPilih Tabel Anda", font=("Verdana",24,"bold"), fg="red")
		label.pack(pady=10,padx=10)
		self.combo = Combobox(self)
		self.combo.bind("<<ComboboxSelected>>", self.bikin_treeview)
		self.combo.pack()
		self.button_1 = tk.Button(self, text="Lihat Tabelnya!",command=lambda:controller.show_frame(PageTiga),fg="white",bg="blue",font=("arial",16,"bold"),state="disabled")
		self.button_1.pack(side="right")
		

	def bikin_treeview(self,event):
		kontroler_page_satu = self.controller.ambil_page(PageSatu)
		kontroler_page_dua = self.controller.ambil_page(PageDua)
		kontroler_page_tiga = self.controller.ambil_page(PageTiga)
		self.list_nama_tabel = kontroler_page_satu.koneksi_biasa.list_nama_tabel
		self.path_database = kontroler_page_satu.path_name
		self.conn, self.koneksi_database = koneksi(self.path_database)
		if not isinstance(self.df, pd.DataFrame):
			for i in self.list_nama_tabel:
				query_table = "SELECT * FROM "+ i
				self.df = pd.read_sql(query_table, self.conn)
				self.list_dataframe.append(self.df)
		self.nama_tabel = kontroler_page_dua.combo.get()
		self.index = self.list_nama_tabel.index(self.nama_tabel)
		self.df = self.list_dataframe[self.index]
		self.df_col = self.df.columns.values
		tree_di_PageTiga = kontroler_page_tiga
		for i in tree_di_PageTiga.tree.get_children():
			tree_di_PageTiga.tree.delete(i)
		tree_di_PageTiga.tree["columns"] = list(self.df_col)
		tree_di_PageTiga.tree.column("#0", width=50, minwidth=50, stretch=tk.NO)
		tree_di_PageTiga.tree.heading("#0", text='Index')
		for x in range(len(self.df_col)):
			tree_di_PageTiga.tree.column(self.df_col[x], minwidth=50)
			if self.df[self.df_col[x]].map(str).map(len).max()<9:
				tree_di_PageTiga.tree.column(self.df_col[x], width=50, minwidth=50)
			tree_di_PageTiga.tree.heading(self.df_col[x], text=self.df_col[x])
			counter = len(self.df.loc[:,self.df_col[x]])
		for i in range(counter):
			rowLabels = self.df.index.tolist()
			tree_di_PageTiga.tree.insert('', i, text=i, values=list(self.df.iloc[i,:]))
		tree_di_PageTiga.tree.configure(yscrollcommand=tree_di_PageTiga.scrollbar.set)
		self.button_1["state"]='normal'

class PageTiga(tk.Frame):

	def __init__(self,parent,controller):
		tk.Frame.__init__(self,parent)
		self.controller=controller
		self.tree = Treeview(self)
		self.scrollbar = Scrollbar(self, orient="vertical", command=self.tree.yview)
		self.scrollbar.pack(side="right", fill='y')
		label = tk.Label(self, text="\n\n\n\n\nBerikut tabel anda", font=("Verdana",24,"bold"), fg="red")
		label.pack(pady=10,padx=10)
		self.tree = Treeview(self)
		self.tree.pack()
		button_1 = tk.Button(self, text="Back",command=lambda:controller.show_frame(PageDua),fg="white",bg="blue",font=("arial",16,"bold"))
		button_1.pack(side="left")
		button_2 = tk.Button(self, text="Insert",command=self.Insert,fg="white",bg="red",font=("arial",16,"bold"))
		button_2.pack(side="right")
		button_3 = tk.Button(self, text="Search",command=self.Search,fg="white",bg="red",font=("arial",16,"bold"))
		button_3.pack(side="right")
		button_4 = tk.Button(self, text="Delete",command=self.delet,fg="white",bg="red",font=("arial",16,"bold"))
		button_4.pack(side="right")

	def Insert(self):

		def Submit():
			self.insert_baru = []
			for i in self.list_entry:
				self.insert_baru.append(i.get())
			if "" not in self.insert_baru:
				kontroler_page_dua = self.controller.ambil_page(PageDua)
				self.insert_baru = [self.insert_baru]
				self.data_tambahan = pd.DataFrame(self.insert_baru,columns=list(self.data.columns))
				self.data = self.data.append(self.data_tambahan, ignore_index=True)
				self.data.to_sql(kontroler_page_dua.nama_tabel,kontroler_page_dua.conn,if_exists='replace', index=False)
			else:
				messagebox.showerror('Gagal', 'Isi lengkap!')

		def update():
			if isinstance(self.data, pd.DataFrame):
				for i in self.tree.get_children():
					self.tree.delete(i)
				self.df_col = self.data.columns.values
				self.tree["columns"] = list(self.df_col)
				self.tree.column("#0", width=50, minwidth=50, stretch=tk.NO)
				self.tree.heading("#0", text='Index')
				for x in range(len(self.df_col)):
					self.tree.column(self.df_col[x], minwidth=50)
					if self.data[self.df_col[x]].map(str).map(len).max()<9:
						self.tree.column(self.df_col[x], width=50, minwidth=50)
					self.tree.heading(self.df_col[x], text=self.df_col[x])
					counter = len(self.data.loc[:,self.df_col[x]])
				for i in range(counter):
					rowLabels = self.data.index.tolist()
					self.tree.insert('', i, text=i, values=list(self.data.iloc[i,:]))
				self.tree.configure(yscrollcommand=self.scrollbar.set)
				self.index = self.controller.ambil_page(PageDua).index
				self.controller.ambil_page(PageDua).list_dataframe[self.index] = self.data
			else:
				pass
		k=0
		self.insert_baru = []
		self.nama_kolom = self.controller.ambil_page(PageDua)
		self.data = self.nama_kolom.df
		self.nama_kolom = list(self.nama_kolom.df_col)
		self.window = tk.Toplevel(self)
		self.window.title("Insert")
		self.window.geometry("700x400")
		self.window.iconbitmap('my_icon.ico')
		self.list_entry = []
		for i in self.nama_kolom:
			label = tk.Label(self.window, text=i, font=("Verdana",10,"bold"), fg="blue")
			label.grid(row=k,column=0)
			entry = tk.Entry(self.window)
			entry.grid(row=k,column=1)
			self.list_entry.append(entry)
			k = k+1
		button_1 = tk.Button(self.window, text="Submit",command=Submit,fg="white",bg="blue",font=("arial",16,"bold"))
		button_1.grid(row=k+2)
		button_2 = tk.Button(self.window, text="Update",command=update,fg="white",bg="blue",font=("arial",16,"bold"))
		button_2.grid(row=k+3)
		self.window.grab_set()

	def Search(self):

		def banyak_kondisi(event):
			
			if self.search_baru_combo != [] or self.search_baru_combo !=[]:
				for i in self.search_baru_combo:
					i.destroy()
				for i in self.search_baru_entry:
					i.destroy()
			self.search_baru_entry = []
			self.search_baru_combo = []
			k=4
			for i in range(0, int(self.combo.get())):
				combo = Combobox(self.window, values=self.nama_kolom, state="readonly")
				combo.bind("<<ComboboxSelected>>")
				combo.grid(row=k,column=0)
				entry = tk.Entry(self.window)
				entry.grid(row=k,column=1)
				self.search_baru_entry.append(entry)
				self.search_baru_combo.append(combo)
				k = k+1
			self.button_5["state"]="normal"
		
		def lihat():
			kontroler_page_dua = self.controller.ambil_page(PageDua)
			index = kontroler_page_dua.index
			self.data = kontroler_page_dua.list_dataframe[index]
			self.list_search_combo = []
			self.list_search_entry = []
			for i in self.search_baru_combo:
				self.list_search_combo.append(i.get())
			for i in self.search_baru_entry:
				self.list_search_entry.append(i.get())
			if ("" not in self.list_search_entry):
				if ("" not in self.list_search_combo):
					for i in range (0,len(self.list_search_combo)):
						if self.data[self.list_search_combo[i]].dtype == "int64" or self.data[self.list_search_combo[i]].dtype == "int32":
							for i in range (0,len(self.list_search_entry)):
								self.list_search_entry[i]=int(self.list_search_entry[i])
						self.data = self.data[self.data.loc[:,self.list_search_combo[i]]==self.list_search_entry[i]]
					for i in self.tree.get_children():
						self.tree.delete(i)
					self.df_col = self.data.columns.values
					self.tree["columns"] = list(self.df_col)
					self.tree.column("#0", width=50, minwidth=50, stretch=tk.NO)
					self.tree.heading("#0", text='Index')
					for x in range(len(self.df_col)):
						self.tree.column(self.df_col[x], minwidth=50)
						if self.data[self.df_col[x]].map(str).map(len).max()<9:
							self.tree.column(self.df_col[x], width=50, minwidth=50)
						self.tree.heading(self.df_col[x], text=self.df_col[x])
						counter = len(self.data.loc[:,self.df_col[x]])
					for i in range(counter):
						rowLabels = self.data.index.tolist()
						self.tree.insert('', i, text=i, values=list(self.data.iloc[i,:]))
					self.tree.configure(yscrollcommand=self.scrollbar.set)
				else:
					pass
			else:
				pass
		def on_closing():
		    kontroler_page_dua = self.controller.ambil_page(PageDua)
		    for i in self.tree.get_children():
		    	self.tree.delete(i)
		    kontroler_page_dua.bikin_treeview(self)
		    self.window.destroy()

		self.search_baru_entry = []
		self.search_baru_combo = []
		self.list_search_entry = []
		self.list_search_combo = []
		self.window = tk.Toplevel(self)
		self.window.title("Search")
		self.window.geometry("700x300")
		self.window.iconbitmap('my_icon.ico')
		self.nama_kolom = self.controller.ambil_page(PageDua)
		self.nama_kolom = list(self.nama_kolom.df_col)
		panjang_kondisi = []
		for i in range (len(self.nama_kolom)):
			panjang_kondisi.append(str(i+1))
		label = tk.Label(self.window, text="Berapa banyak kondisi pencarian yang anda inginkan", font=("Verdana",10,"bold"), fg="blue")
		label.grid(row=0, column=0)
		self.combo = Combobox(self.window, values=panjang_kondisi, state="readonly")
		self.combo.bind("<<ComboboxSelected>>",banyak_kondisi)
		self.combo.grid(row=0, column=1)
		self.button_5 = tk.Button(self.window, text="Lihat",command=lihat,fg="white",bg="blue",font=("arial",16,"bold"),state='disabled')
		self.button_5.grid(row=0, column=2)
		self.window.grab_set()
		self.window.protocol("WM_DELETE_WINDOW", on_closing)

	def delet(self):

		def Submit():
			self.delete_entry = self.entry.get()
			if self.delete_entry != "":
				kontroler_page_dua = self.controller.ambil_page(PageDua)
				index = kontroler_page_dua.index
				self.data = kontroler_page_dua.list_dataframe[index]
				if self.data[self.combo.get()].dtype == "int64" or self.data[self.combo.get()].dtype == "int32":
					self.delete_entry=int(self.delete_entry)
				self.data = self.data[~(self.data.loc[:,self.combo.get()]==self.delete_entry)]
				self.controller.ambil_page(PageDua).list_dataframe[index] = self.data
				self.data.to_sql(kontroler_page_dua.nama_tabel,kontroler_page_dua.conn,if_exists='replace', index=False)
			else:
				messagebox.showerror('Gagal', 'Isi lengkap!')

		def update():
			if isinstance(self.data, pd.DataFrame):
				for i in self.tree.get_children():
					self.tree.delete(i)
				self.df_col = self.data.columns.values
				self.tree["columns"] = list(self.df_col)
				self.tree.column("#0", width=50, minwidth=50, stretch=tk.NO)
				self.tree.heading("#0", text='Index')
				for x in range(len(self.df_col)):
					self.tree.column(self.df_col[x], minwidth=50)
					if self.data[self.df_col[x]].map(str).map(len).max()<9:
						self.tree.column(self.df_col[x], width=50, minwidth=50)
					self.tree.heading(self.df_col[x], text=self.df_col[x])
					counter = len(self.data.loc[:,self.df_col[x]])
				for i in range(counter):
					rowLabels = self.data.index.tolist()
					self.tree.insert('', i, text=i, values=list(self.data.iloc[i,:]))
				self.tree.configure(yscrollcommand=self.scrollbar.set)
				self.index = self.controller.ambil_page(PageDua).index
				self.controller.ambil_page(PageDua).list_dataframe[self.index] = self.data
			else:
				pass


		self.window = tk.Toplevel(self)
		self.window.title("Search")
		self.window.geometry("700x300")
		self.window.iconbitmap('my_icon.ico')
		self.nama_kolom = self.controller.ambil_page(PageDua)
		self.nama_kolom = list(self.nama_kolom.df_col)
		label = tk.Label(self.window, text="Hapus berdasarkan:", font=("Verdana",10,"bold"), fg="blue")
		label.grid(row=0, column=0)
		self.combo = Combobox(self.window, values=self.nama_kolom, state="readonly")
		self.combo.grid(row=1, column=0)
		self.button_6 = tk.Button(self.window, text="Submit",command=Submit,fg="white",bg="blue",font=("arial",16,"bold"))
		self.button_6.grid(row=2, column=0)
		self.button_7 = tk.Button(self.window, text="Update",command=update,fg="white",bg="blue",font=("arial",16,"bold"))
		self.button_7.grid(row=2, column=1)
		self.entry = tk.Entry(self.window)
		self.entry.grid(row=1,column=1)
		self.window.grab_set()



		

def koneksi(nama):
	if nama != None:
		conn = sqlite3.connect(nama)
		c = conn.cursor()
		return  conn, c
	else:
		return 1

class DB:

	def __init__(self,konek):

		if konek!=1:
			self.c = konek
			self.list_nama_tabel = []
			res = self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
			for name in res:
				self.list_nama_tabel.append(name[0])
		else:
			self.list_nama_tabel=['1']

app = NISH()
app.mainloop()