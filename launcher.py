import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, shutil, subprocess, json

# --- CONFIGURAÇÕES ---
APP_VERSION = "1.0.4"
CONFIG_FILE = "launcher_config.json"
ENGINES = ["Psych Engine", "V-Slice (Base Game)", "Codename Engine"]

LANG = {
    "pt": {
        "tab_launcher": "Launcher", "tab_settings": "Configurações",
        "play": "INICIAR JOGO", "add_mod": "Adicionar Mod", "del_mod": "Deletar Mod",
        "save_btn": "Salvar", "save_success": "Configurações salvas!", "no_version": "Sem versões",
        "error_exe": "Executável não encontrado.", "lang_label": "Idioma:",
        "theme_label": "Tema:", "dark_mode": "Escuro", "light_mode": "Claro",
        "default_ver": "Padrão (Launcher)", "confirm_del": "Deletar este mod?"
    },
    "en": {
        "tab_launcher": "Launcher", "tab_settings": "Settings",
        "play": "START GAME", "add_mod": "Add Mod", "del_mod": "Delete Mod",
        "save_btn": "Save", "save_success": "Settings saved!", "no_version": "No versions",
        "error_exe": "Executable not found.", "lang_label": "Language:",
        "theme_label": "Theme:", "dark_mode": "Dark", "light_mode": "Light",
        "default_ver": "Default (Launcher)", "confirm_del": "Delete mod?"
    }
}

class Launcher:
    def __init__(self, root):
        self.root = root
        self.load_config()
        self.root.geometry("850x700")
        self.root.title(f"FNF Launcher Pro - v{APP_VERSION}")
        
        self.engine_var = tk.StringVar(value=self.config.get("engine", ENGINES[0]))
        self.version_var = tk.StringVar()
        self.lang = self.config.get("lang", "pt")
        self.dark = self.config.get("dark", True)

        # FUNÇÕES CORRIGIDAS (Não dão mais AttributeError)
        self.setup_styles()
        self.create_ui()
        self.update_versions_list()
        self.apply_theme()
        self.apply_lang()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: self.config = json.load(f)
            except: self.config = {"dark": True, "lang": "pt"}
        else: self.config = {"dark": True, "lang": "pt"}

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def create_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.launcher_tab = tk.Frame(self.tabs)
        self.settings_tab = tk.Frame(self.tabs)
        self.tabs.add(self.launcher_tab, text="Launcher")
        self.tabs.add(self.settings_tab, text="Settings")
        self.tabs.pack(fill="both", expand=True)

        top = tk.LabelFrame(self.launcher_tab, padx=10, pady=10)
        top.pack(fill="x", padx=10, pady=5)

        tk.Label(top, text="Engine:").pack(side="left")
        self.engine_menu = ttk.Combobox(top, values=ENGINES, textvariable=self.engine_var, state="readonly")
        self.engine_menu.pack(side="left", padx=5)
        self.engine_menu.bind("<<ComboboxSelected>>", lambda e: self.update_versions_list())

        self.version_menu = ttk.Combobox(top, textvariable=self.version_var, state="readonly")
        self.version_menu.pack(side="left", padx=5)
        self.version_menu.bind("<<ComboboxSelected>>", lambda e: self.load_mods())

        self.mods_list = tk.Listbox(self.launcher_tab, font=("Segoe UI", 10), borderwidth=0)
        self.mods_list.pack(fill="both", expand=True, padx=10, pady=5)

        m_btns = tk.Frame(self.launcher_tab)
        m_btns.pack(fill="x", padx=10)
        self.add_mod_btn = tk.Button(m_btns, command=self.add_mod, bg="#2196F3", fg="white")
        self.add_mod_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.del_mod_btn = tk.Button(m_btns, command=self.delete_mod, bg="#f44336", fg="white")
        self.del_mod_btn.pack(side="right", fill="x", expand=True)

        self.play_btn = tk.Button(self.launcher_tab, command=self.play, font=("bold"), bg="#4CAF50", fg="white")
        self.play_btn.pack(fill="x", padx=10, pady=10)

        # ABA CONFIGS
        s_cnt = tk.Frame(self.settings_tab, padx=30, pady=30)
        s_cnt.pack(fill="both")
        self.lbl_lang = tk.Label(s_cnt, text="Idioma:")
        self.lbl_lang.pack(anchor="w")
        self.lang_menu = ttk.Combobox(s_cnt, values=["Português (Brasil)", "Inglês (USA)"], state="readonly")
        self.lang_menu.pack(fill="x", pady=(5, 20))
        self.lang_menu.bind("<<ComboboxSelected>>", self.change_lang_from_menu)

        self.lbl_theme = tk.Label(s_cnt, text="Tema:")
        self.lbl_theme.pack(anchor="w")
        self.theme_btn = tk.Button(s_cnt, command=self.toggle_theme)
        self.theme_btn.pack(fill="x", pady=(5, 30))
        self.save_btn = tk.Button(s_cnt, command=self.save_config_manual, bg="#2196F3", fg="white")
        self.save_btn.pack(fill="x")

    def get_paths(self):
        engine = self.engine_var.get().split(" ")[0].lower()
        ver = self.version_var.get()
        g_path = os.path.abspath(os.path.join("engines", engine, "mods"))
        if ver == LANG[self.lang].get("default_ver"):
            v_path = os.path.abspath(os.path.join("engines", engine, "launcher"))
        else:
            v_path = os.path.abspath(os.path.join("engines", engine, "versions", ver))
        return g_path, os.path.join(v_path, "mods"), v_path

    def update_versions_list(self):
        engine = self.engine_var.get().split(" ")[0].lower()
        v_dir, l_dir = os.path.join("engines", engine, "versions"), os.path.join("engines", engine, "launcher")
        vers = []
        if os.path.exists(l_dir): vers.append(LANG[self.lang]["default_ver"])
        if os.path.exists(v_dir):
            vers.extend([d for d in os.listdir(v_dir) if os.path.isdir(os.path.join(v_dir, d))])
        self.version_menu['values'] = vers
        if vers: self.version_menu.current(0); self.load_mods()
        else: self.version_var.set(LANG[self.lang]["no_version"]); self.mods_list.delete(0, tk.END)

    def load_mods(self):
        self.mods_list.delete(0, tk.END)
        g, l, _ = self.get_paths()
        found = set()
        for p in [g, l]:
            if os.path.exists(p):
                for m in os.listdir(p):
                    if os.path.isdir(os.path.join(p, m)): found.add(m)
        for mod in sorted(list(found)): self.mods_list.insert(tk.END, mod)

    def add_mod(self):
        src = filedialog.askdirectory()
        if src:
            _, l, _ = self.get_paths()
            if not os.path.exists(l): os.makedirs(l)
            shutil.copytree(src, os.path.join(l, os.path.basename(src)))
            self.load_mods()

    def delete_mod(self):
        if not self.mods_list.curselection(): return
        mod = self.mods_list.get(self.mods_list.curselection())
        if messagebox.askyesno("Confirm", LANG[self.lang]["confirm_del"]):
            g, l, _ = self.get_paths()
            for p in [l, g]:
                t = os.path.join(p, mod)
                if os.path.exists(t): shutil.rmtree(t, ignore_errors=True)
            self.load_mods()

    def play(self):
        if not self.mods_list.curselection(): return
        mod = self.mods_list.get(self.mods_list.curselection())
        _, _, v = self.get_paths()
        exe = next((os.path.join(v, f) for f in os.listdir(v) if f.endswith(".exe")), None)
        if exe: subprocess.Popen([exe, f"--mod={mod}"], cwd=v)
        else: messagebox.showerror("Erro", LANG[self.lang]["error_exe"])

    def change_lang_from_menu(self, e=None):
        self.lang = "pt" if "Português" in self.lang_menu.get() else "en"
        self.apply_lang(); self.update_versions_list()

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme(); self.apply_lang()

    def save_config_manual(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"dark": self.dark, "lang": self.lang, "engine": self.engine_var.get()}, f)
        messagebox.showinfo("OK", LANG[self.lang]["save_success"])

    def apply_theme(self):
        bg, fg = ("#1e1e1e", "#fff") if self.dark else ("#f0f0f0", "#000")
        self.root.configure(bg=bg)
        for tab in [self.launcher_tab, self.settings_tab]:
            tab.configure(bg=bg)
            for w in tab.winfo_children():
                try: w.configure(bg=bg, fg=fg)
                except: pass
        self.mods_list.configure(bg="#2d2d2d" if self.dark else "white", fg=fg)

    def apply_lang(self):
        t = LANG[self.lang]
        self.play_btn.config(text=t["play"]); self.add_mod_btn.config(text=t["add_mod"])
        self.del_mod_btn.config(text=t["del_mod"]); self.save_btn.config(text=t["save_btn"])
        self.tabs.tab(0, text=t["tab_launcher"]); self.tabs.tab(1, text=t["tab_settings"])
        self.theme_btn.config(text=t["dark_mode"] if self.dark else t["light_mode"])
        self.lang_menu.set("Português (Brasil)" if self.lang == "pt" else "Inglês (USA)")

if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()