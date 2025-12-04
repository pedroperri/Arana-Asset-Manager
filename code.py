# ''CODIGO COM AUXILIO DO GEMINI, PARA INTERFACE E MICRO-CORREÇÃO
# ''CODIGO PROJETADO EM 5 HORAS. 

import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import sqlite3
import sys
import os
import hashlib
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (GITHUB DARK) ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Paleta de Cores
GH_BG_MAIN    = "#0d1117"       
GH_BG_SIDE    = "#161b22"       
GH_BG_CARD    = "#21262d"       
GH_BORDER     = "#30363d"       
GH_INPUT_BG   = "#0d1117"       
GH_ACCENT     = "#238636"       # Verde
GH_ACCENT_H   = "#2ea043"       
GH_BLUE       = "#58a6ff"       # Azul
GH_RED        = "#da3633"       
GH_ORANGE     = "#d29922"       # Laranja
GH_TEXT_PRI   = "#c9d1d9"       
GH_TEXT_SEC   = "#8b949e"       

def get_font(size, weight="normal"):
    font = "Segoe UI" if os.name == "nt" else "Sans Serif"
    return (font, size, weight)

# --- BANCO DE DADOS ---
class Database:
    def __init__(self):
        # Nome novo para garantir que crie o admin correto
        self.conn = sqlite3.connect("arana_github.db")
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY, codigo TEXT, conteudo TEXT, data TEXT, area TEXT, notas TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ti (
            id INTEGER PRIMARY KEY, tag TEXT, tipo TEXT, modelo TEXT, status TEXT, qtd INTEGER, usuario TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY, data TEXT, user TEXT, acao TEXT, detalhe TEXT)''')

        # --- ALTERAÇÃO AQUI: CRIAR USUÁRIO PADRÃO 'admin' ---
        self.cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
        if not self.cursor.fetchone():
            # Senha padrão para GitHub: admin / admin
            self.cursor.execute("INSERT INTO usuarios (username, password, role) VALUES (?,?,?)", 
                                ("admin", "admin", "admin"))
        self.conn.commit()

    def query(self, sql, params=(), fetch=False):
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            if fetch: return self.cursor.fetchall()
            return True
        except Exception as e:
            print(f"Erro SQL: {e}")
            return None

    def log(self, user, acao, detalhe):
        ts = datetime.now().strftime("%d/%m %H:%M")
        self.cursor.execute("INSERT INTO logs (data, user, acao, detalhe) VALUES (?,?,?,?)",
                            (ts, user, acao, detalhe))
        self.conn.commit()

# --- SISTEMA ARANA ---
class AranaSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arana • System")
        self.geometry("1280x800")
        self.configure(fg_color=GH_BG_MAIN)
        
        self.db = Database()
        self.user = None 
        
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"1280x800+{int((sw-1280)/2)}+{int((sh-800)/2)}")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_login()

    # ================= LOGIN =================
    def show_login(self):
        for w in self.container.winfo_children(): w.destroy()
        
        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center, text="🕷️", font=("Arial", 72)).pack(pady=(0, 10))
        ctk.CTkLabel(center, text="Arana System", font=get_font(24, "bold"), text_color=GH_TEXT_PRI).pack(pady=(0, 30))

        card = ctk.CTkFrame(center, fg_color=GH_BG_SIDE, border_width=1, border_color=GH_BORDER, corner_radius=6, width=320)
        card.pack(fill="both", pady=10)

        ctk.CTkLabel(card, text="Usuário", text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_u = ctk.CTkEntry(card, width=280, height=35, fg_color=GH_BG_MAIN, 
                                    border_width=1, border_color=GH_BORDER, corner_radius=6, text_color=GH_TEXT_PRI)
        self.entry_u.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(card, text="Senha", text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.entry_p = ctk.CTkEntry(card, width=280, height=35, fg_color=GH_BG_MAIN, show="•",
                                    border_width=1, border_color=GH_BORDER, corner_radius=6, text_color=GH_TEXT_PRI)
        self.entry_p.pack(padx=20, pady=(0, 20))

        ctk.CTkButton(card, text="Acessar", width=280, height=35, fg_color=GH_ACCENT, hover_color=GH_ACCENT_H,
                      font=get_font(13, "bold"), corner_radius=6, command=self.do_login).pack(padx=20, pady=(0, 25))
        
        # Dica visual para quem baixar no GitHub
        ctk.CTkLabel(center, text="Default: admin | admin", text_color=GH_TEXT_SEC, font=get_font(10)).pack(pady=5)

    def do_login(self):
        u = self.entry_u.get().upper().strip()
        p = self.entry_p.get().strip()
        
        # Verifica no banco (Admin deve ser 'admin' agora, mas convertemos input pra lower caso digite Admin)
        # Nota: O banco grava como 'admin' (minusculo) no init_tables
        res = self.db.query("SELECT role FROM usuarios WHERE lower(username)=? AND password=?", (u.lower(), p), fetch=True)
        
        if res:
            self.user = {"name": u, "role": res[0][0]}
            self.db.log(u, "LOGIN", "Sucesso")
            self.show_app()
        else:
            messagebox.showerror("Erro", "Login inválido")

    # ================= APP PRINCIPAL =================
    def show_app(self):
        for w in self.container.winfo_children(): w.destroy()
        
        self.container.grid_columnconfigure(0, weight=0, minsize=220) 
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self.container, fg_color=GH_BG_SIDE, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkFrame(self.container, width=1, fg_color=GH_BORDER).grid(row=0, column=0, sticky="nse")

        ctk.CTkLabel(sidebar, text=self.user['name'], font=get_font(14, "bold"), text_color=GH_TEXT_PRI).pack(anchor="w", padx=15, pady=(20, 2))
        ctk.CTkLabel(sidebar, text=self.user['role'].upper(), font=get_font(10), text_color=GH_TEXT_SEC).pack(anchor="w", padx=15)

        ctk.CTkFrame(sidebar, height=1, fg_color=GH_BORDER).pack(fill="x", pady=15)

        role = self.user['role']
        if role in ['admin', 'escritorio']: self.nav_btn(sidebar, "📦 Arquivos", lambda: self.load_view("CAIXA"))
        if role in ['admin', 'ti']: self.nav_btn(sidebar, "💻 Inventário T.I.", lambda: self.load_view("TI"))
        if role == 'admin':
            ctk.CTkFrame(sidebar, height=1, fg_color=GH_BORDER).pack(fill="x", pady=15, padx=10)
            self.nav_btn(sidebar, "⚙️ Admin", self.open_admin)

        ctk.CTkButton(sidebar, text="Sair", fg_color="transparent", text_color=GH_RED, hover_color=GH_BORDER, 
                      anchor="w", height=28, font=get_font(12), command=self.show_login).pack(side="bottom", fill="x", padx=10, pady=20)

        self.content = ctk.CTkFrame(self.container, fg_color=GH_BG_MAIN, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

        if role == 'ti': self.load_view("TI")
        elif role == 'escritorio': self.load_view("CAIXA")
        else: self.load_view("CAIXA")

    def nav_btn(self, parent, text, cmd):
        btn = ctk.CTkButton(parent, text=text, fg_color="transparent", hover_color=GH_BORDER, 
                            text_color=GH_TEXT_PRI, anchor="w", height=30, corner_radius=4, font=get_font(13), command=cmd)
        btn.pack(fill="x", padx=10, pady=2)

    # ================= VIEW & TABELA =================
    def load_view(self, mode):
        for w in self.content.winfo_children(): w.destroy()
        self.curr_mode = mode

        head = ctk.CTkFrame(self.content, fg_color="transparent", height=50)
        head.pack(fill="x", padx=20, pady=(20, 10))
        
        title = "Arquivo Geral" if mode == "CAIXA" else "Inventário T.I."
        ctk.CTkLabel(head, text=title, font=get_font(18, "bold"), text_color=GH_TEXT_PRI).pack(side="left")

        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", padx=20)

        self.search = ctk.CTkEntry(bar, width=250, height=30, placeholder_text="Filtrar...", 
                                   fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, corner_radius=4, text_color=GH_TEXT_PRI)
        self.search.pack(side="left")
        self.search.bind("<Return>", lambda event: self.refresh_table())

        ctk.CTkButton(bar, text="🔍 Pesquisar", width=90, height=30, fg_color=GH_BLUE, hover_color="#408cf0", 
                      border_width=1, border_color=GH_BORDER, text_color=GH_TEXT_PRI, command=self.refresh_table).pack(side="left", padx=5)

        btn_right = ctk.CTkFrame(bar, fg_color="transparent")
        btn_right.pack(side="right")

        ctk.CTkButton(btn_right, text="Excluir", fg_color="transparent", border_width=1, border_color=GH_BORDER, text_color=GH_RED,
                      width=70, height=30, corner_radius=4, hover_color=GH_BG_CARD, command=self.delete_sel).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_right, text="Novo Item", fg_color=GH_ACCENT, hover_color=GH_ACCENT_H,
                      width=90, height=30, corner_radius=4, font=get_font(12, "bold"), command=self.popup_add).pack(side="left", padx=5)

        t_frame = ctk.CTkFrame(self.content, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, corner_radius=6)
        t_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.build_tree(t_frame, mode)
        self.refresh_table()

    def build_tree(self, parent, mode):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Treeview", background=GH_BG_MAIN, foreground=GH_TEXT_PRI, fieldbackground=GH_BG_MAIN, 
                        rowheight=30, borderwidth=0, font=get_font(11))
        style.configure("Treeview.Heading", background=GH_BG_SIDE, foreground=GH_TEXT_PRI, relief="flat", font=get_font(11, "bold"))
        style.map("Treeview", background=[('selected', GH_BG_CARD)], foreground=[('selected', GH_BLUE)])

        if mode == "CAIXA":
            cols = ("id", "c1", "c2", "c3", "c4", "c5")
            self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="extended")
            self.tree.column("id", width=0, stretch=False)
            self.tree.heading("c1", text="CÓDIGO"); self.tree.column("c1", width=80, anchor="center")
            self.tree.heading("c2", text="CONTEÚDO"); self.tree.column("c2", width=300, anchor="center")
            self.tree.heading("c3", text="DATA"); self.tree.column("c3", width=100, anchor="center")
            self.tree.heading("c4", text="ÁREA"); self.tree.column("c4", width=120, anchor="center")
            self.tree.heading("c5", text="NOTAS"); self.tree.column("c5", width=250, anchor="center")
        else:
            cols = ("id", "c1", "c2", "c3", "c4", "c5", "c6")
            self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="extended")
            self.tree.column("id", width=0, stretch=False)
            self.tree.heading("c1", text="TAG"); self.tree.column("c1", width=100, anchor="center")
            self.tree.heading("c2", text="TIPO"); self.tree.column("c2", width=120, anchor="center")
            self.tree.heading("c3", text="MODELO"); self.tree.column("c3", width=250, anchor="center")
            self.tree.heading("c4", text="STATUS"); self.tree.column("c4", width=100, anchor="center")
            self.tree.heading("c5", text="QTD"); self.tree.column("c5", width=50, anchor="center")
            self.tree.heading("c6", text="USUÁRIO"); self.tree.column("c6", width=180, anchor="center")

        self.tree.tag_configure("ok", foreground="#3fb950")
        self.tree.tag_configure("warn", foreground="#d29922")
        self.tree.tag_configure("busy", foreground="#a371f7")

        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self.on_double_click)

    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = self.search.get().strip()
        sql = ""
        q = f"%{query}%"

        if self.curr_mode == "CAIXA":
            sql = "SELECT * FROM caixas WHERE CAST(id AS TEXT) LIKE ? OR codigo LIKE ? OR conteudo LIKE ? OR data LIKE ? OR area LIKE ? OR notas LIKE ?"
            params = (q, q, q, q, q, q)
        else:
            sql = "SELECT * FROM ti WHERE CAST(id AS TEXT) LIKE ? OR tag LIKE ? OR tipo LIKE ? OR modelo LIKE ? OR status LIKE ? OR CAST(qtd AS TEXT) LIKE ? OR usuario LIKE ?"
            params = (q, q, q, q, q, q, q)
            
        rows = self.db.query(sql, params, fetch=True)
        if rows:
            for r in rows:
                tag = ""
                if self.curr_mode == "TI":
                    st = str(r[4]).lower()
                    if "estoque" in st: tag="ok"
                    elif "uso" in st: tag="busy"
                    elif "manut" in st: tag="warn"
                vals = [str(x) if x is not None else "" for x in r]
                self.tree.insert("", "end", values=vals, tags=(tag,))

    def filter_list(self, event):
        pass

    def delete_sel(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "Deletar itens selecionados?"):
            ids = [self.tree.item(i, 'values')[0] for i in sel]
            tbl = "caixas" if self.curr_mode == "CAIXA" else "ti"
            for i in ids: self.db.query(f"DELETE FROM {tbl} WHERE id=?", (i,))
            self.db.log(self.user['name'], "DELETAR", f"{len(ids)} itens")
            self.refresh_table()

    # ================= POPUP =================
    def popup_add(self, item_id=None, data=None):
        pop = ctk.CTkToplevel(self)
        pop.title("Item")
        w, h = 450, 600
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        pop.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        pop.transient(self)
        pop.configure(fg_color=GH_BG_MAIN)

        head = ctk.CTkFrame(pop, fg_color=GH_BG_SIDE, height=50, corner_radius=0)
        head.pack(fill="x")
        ctk.CTkFrame(head, height=1, fg_color=GH_BORDER).pack(side="bottom", fill="x")
        ctk.CTkLabel(head, text="Editar Item" if item_id else "Novo Item", font=get_font(14, "bold"), text_color=GH_TEXT_PRI).pack(side="left", padx=20)

        f = ctk.CTkFrame(pop, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=20, pady=20)

        entries = {}
        
        def mk(lbl, k, v=""):
            ctk.CTkLabel(f, text=lbl, text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(anchor="w", pady=(5, 2))
            e = ctk.CTkEntry(f, height=32, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, corner_radius=6, text_color=GH_TEXT_PRI)
            e.insert(0, v); e.pack(fill="x", pady=(0, 8))
            entries[k] = e
            return e

        def fmt_date(e):
            t = e.widget.get().replace("/", "")
            if len(t) >= 2: t = t[:2] + "/" + t[2:]
            if len(t) >= 5: t = t[:5] + "/" + t[5:]
            if len(t) > 10: t = t[:10]
            e.widget.delete(0, "end"); e.widget.insert(0, t)

        if self.curr_mode == "CAIXA":
            vals = data if data else [""]*5
            mk("Etiqueta", "c1", vals[0])
            mk("Conteúdo", "c2", vals[1])
            d = mk("Data (00/00/0000)", "c3", vals[2]); d.bind("<KeyRelease>", fmt_date)
            mk("Área", "c4", vals[3])
            
            ctk.CTkLabel(f, text="Notas", text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(anchor="w", pady=(5, 2))
            note = ctk.CTkTextbox(f, height=100, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, text_color=GH_TEXT_PRI, corner_radius=6)
            note.insert("1.0", vals[4])
            note.pack(fill="x")
            entries["c5"] = note
        else:
            vals = data if data else ["", "", "", "Em Estoque", "1", ""]
            mk("Tag Patrimônio", "c1", vals[0])
            mk("Tipo", "c2", vals[1])
            mk("Modelo", "c3", vals[2])
            
            ctk.CTkLabel(f, text="Status", text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(anchor="w", pady=(5, 2))
            cb = ctk.CTkComboBox(f, values=["Em Estoque", "Em Uso", "Manutenção"], height=32, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, button_color=GH_BG_SIDE, text_color=GH_TEXT_PRI)
            cb.set(vals[3]); cb.pack(fill="x", pady=(0,8)); entries["c4"] = cb
            
            f2 = ctk.CTkFrame(f, fg_color="transparent"); f2.pack(fill="x")
            ctk.CTkLabel(f2, text="Qtd.", text_color=GH_TEXT_PRI, font=get_font(12, "bold")).pack(side="left")
            q = ctk.CTkEntry(f2, width=50, height=32, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, text_color=GH_TEXT_PRI)
            q.insert(0, vals[4]); q.pack(side="left", padx=5); entries["c5"] = q
            
            u = ctk.CTkEntry(f2, height=32, placeholder_text="Usuário Resp.", fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER, text_color=GH_TEXT_PRI)
            u.insert(0, vals[5]); u.pack(side="left", fill="x", expand=True, padx=5); entries["c6"] = u

        def save():
            vals = []
            for k in sorted(entries.keys()):
                widget = entries[k]
                if isinstance(widget, ctk.CTkTextbox): vals.append(widget.get("1.0", "end-1c"))
                else: vals.append(widget.get())

            if not vals[0]: return

            if self.curr_mode == "CAIXA":
                sql = "UPDATE caixas SET codigo=?, conteudo=?, data=?, area=?, notas=? WHERE id=?" if item_id else \
                      "INSERT INTO caixas (codigo, conteudo, data, area, notas) VALUES (?,?,?,?,?)"
            else:
                sql = "UPDATE ti SET tag=?, tipo=?, modelo=?, status=?, qtd=?, usuario=? WHERE id=?" if item_id else \
                      "INSERT INTO ti (tag, tipo, modelo, status, qtd, usuario) VALUES (?,?,?,?,?,?)"
            
            p = tuple(vals + [item_id]) if item_id else tuple(vals)
            self.db.query(sql, p)
            self.db.log(self.user['name'], "SALVAR", f"{self.curr_mode}: {vals[0]}")
            self.refresh_table()
            pop.destroy()

        foot = ctk.CTkFrame(pop, fg_color=GH_BG_SIDE, height=50, corner_radius=0)
        foot.pack(side="bottom", fill="x")
        ctk.CTkFrame(foot, height=1, fg_color=GH_BORDER).pack(side="top", fill="x")
        
        ctk.CTkButton(foot, text="Save changes", height=32, width=120, fg_color=GH_ACCENT, hover_color=GH_ACCENT_H, 
                      corner_radius=6, font=get_font(12, "bold"), command=save).pack(side="right", padx=20, pady=10)

    def on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            self.popup_add(item_id=vals[0], data=vals[1:])

    # ================= ADMIN =================
    def open_admin(self):
        adm = ctk.CTkToplevel(self)
        adm.title("Admin")
        w, h = 650, 500
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        adm.geometry(f"{w}x{h}+{int((sw-w)/2)}+{int((sh-h)/2)}")
        adm.configure(fg_color=GH_BG_MAIN)
        adm.transient(self)

        tabs = ctk.CTkTabview(adm, fg_color=GH_BG_SIDE, border_width=1, border_color=GH_BORDER, corner_radius=6)
        tabs.pack(fill="both", expand=True, padx=20, pady=20)
        t1 = tabs.add("Usuários")
        t2 = tabs.add("Logs")

        # USERS
        f_top = ctk.CTkFrame(t1, fg_color="transparent"); f_top.pack(pady=10)
        u = ctk.CTkEntry(f_top, placeholder_text="Login", width=120, height=30, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER); u.pack(side="left", padx=5)
        p = ctk.CTkEntry(f_top, placeholder_text="Pass", width=120, height=30, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER); p.pack(side="left", padx=5)
        r = ctk.CTkComboBox(f_top, values=["admin", "ti", "escritorio"], height=30, width=100, fg_color=GH_BG_MAIN, border_width=1, border_color=GH_BORDER); r.pack(side="left", padx=5)
        
        tree_u = ttk.Treeview(t1, columns=("User", "Role"), show="headings", height=8)
        tree_u.heading("User", text="Usuário"); tree_u.column("User", width=150)
        tree_u.heading("Role", text="Cargo"); tree_u.column("Role", width=100)
        tree_u.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        def list_u():
            for i in tree_u.get_children(): tree_u.delete(i)
            rs = self.db.query("SELECT username, role FROM usuarios", fetch=True)
            for x in rs: tree_u.insert("", "end", values=(x[0], x[1]))
        list_u()

        def add():
            if u.get() and p.get():
                self.db.query("INSERT INTO usuarios (username, password, role) VALUES (?,?,?)", (u.get().upper(), p.get(), r.get()))
                u.delete(0,'end'); p.delete(0,'end'); list_u()

        def delete_user():
            sel = tree_u.selection()
            if not sel: return
            user_to_del = tree_u.item(sel[0], "values")[0]
            if user_to_del == self.user['name']: messagebox.showerror("Erro", "Não pode se deletar!"); return
            if messagebox.askyesno("Confirmar", f"Apagar {user_to_del}?"):
                self.db.query("DELETE FROM usuarios WHERE username=?", (user_to_del,)); list_u()

        def reset_pass():
            sel = tree_u.selection()
            if not sel: return
            user_target = tree_u.item(sel[0], "values")[0]
            dialog = ctk.CTkInputDialog(text=f"Nova senha para {user_target}:", title="Redefinir Senha")
            new_p = dialog.get_input()
            if new_p:
                self.db.query("UPDATE usuarios SET password=? WHERE username=?", (new_p, user_target))
                messagebox.showinfo("Sucesso", "Senha alterada!")

        ctk.CTkButton(f_top, text="Adicionar", width=80, height=30, fg_color=GH_ACCENT, command=add).pack(side="left", padx=5)
        f_btns = ctk.CTkFrame(t1, fg_color="transparent")
        f_btns.pack(side="bottom", pady=10)
        ctk.CTkButton(f_btns, text="Redefinir Senha", width=120, height=30, fg_color="transparent", border_width=1, border_color=GH_ORANGE, text_color=GH_ORANGE, command=reset_pass).pack(side="left", padx=10)
        ctk.CTkButton(f_btns, text="Excluir Usuário", width=120, height=30, fg_color="transparent", border_width=1, border_color=GH_RED, text_color=GH_RED, command=delete_user).pack(side="left", padx=10)

        # LOGS
        tr = ttk.Treeview(t2, columns=("Data", "User", "Ação", "Detalhe"), show="headings")
        tr.heading("Data", text="Data"); tr.column("Data", width=100)
        tr.heading("User", text="User"); tr.column("User", width=80)
        tr.heading("Ação", text="Ação"); tr.column("Ação", width=80)
        tr.heading("Detalhe", text="Detalhe"); tr.column("Detalhe", width=250)
        tr.pack(fill="both", expand=True, padx=10, pady=10)

        logs = self.db.query("SELECT data, user, acao, detalhe FROM logs ORDER BY id DESC LIMIT 50", fetch=True)
        if logs:
            for l in logs: tr.insert("", "end", values=l)

if __name__ == "__main__":
    app = AranaSystem()
    app.mainloop()
