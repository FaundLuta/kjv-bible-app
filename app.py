import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# --- EXE PATH RESOLVER ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BibleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KJV Bible  Edition")
        self.root.geometry("1200x900")
        
        # --- PERSISTENCE SETUP ---
        self.save_file_path = os.path.join(os.path.expanduser("~"), "bible_study_data.json")
        
        # --- THEMES ---
        self.themes = {
            "Dark": {"bg": "#000000", "fg": "#ffffff", "header": "#0a0a0a", "accent": "#1a1a1a", "highlight": "#4d4d00", "btn_ot": "#7d6b60", "btn_nt": "#6b7b8b", "entry_bg": "#1a1a1a", "search_border": "#2980b9", "footer_fg": "#555555"},
            "Light": {"bg": "#ffffff", "fg": "#000000", "header": "#f0f0f0", "accent": "#e0e0e0", "highlight": "#ffffcc", "btn_ot": "#a69385", "btn_nt": "#92a1ad", "entry_bg": "#ffffff", "search_border": "#3498db", "footer_fg": "#999999"},
            "Sepia": {"bg": "#f4ecd8", "fg": "#5b4636", "header": "#e8dfc4", "accent": "#decba4", "highlight": "#d2b48c", "btn_ot": "#8b7355", "btn_nt": "#708090", "entry_bg": "#fdfaf1", "search_border": "#8b4513", "footer_fg": "#8b7e66"}
        }
        
        self.current_theme_name = "Dark"
        self.colors = self.themes[self.current_theme_name]
        self.settings = {"font_size": 14}
        
        self.bible_data = self.load_bible_data()
        self.saved_verses = self.load_saved_verses()
        
        self.current_book_idx = 0
        self.current_chap_idx = 0
        self.in_reader_mode = False
        self.search_highlight_verse = None

        # --- UI LAYOUT ---
        self.header = tk.Frame(self.root, bg=self.colors["header"], height=60)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)

        self.footer = tk.Frame(self.root, bg=self.colors["bg"], height=30)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.copyright_label = tk.Label(
            self.footer, 
            text="© 2026 faundln | All Rights Reserved", 
            font=("Segoe UI", 9), 
            bg=self.colors["bg"], 
            fg=self.colors["footer_fg"]
        )
        self.copyright_label.pack(pady=5)

        self.main_area = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_area.pack(expand=True, fill=tk.BOTH)

        self.setup_header_ui()
        self.show_book_selection()

    # ==========================================
    # DATA & PERSISTENCE
    # ==========================================
    def load_bible_data(self):
        try:
            path = resource_path('kjv.json')
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f).get("books", [])
        except Exception as e:
            messagebox.showerror("Error", f"Bible file missing: {e}")
            return []

    def load_saved_verses(self):
        if os.path.exists(self.save_file_path):
            try:
                with open(self.save_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_to_disk(self):
        try:
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.saved_verses, f, indent=4)
        except Exception as e: print(f"Error saving: {e}")

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        # Small temporary notification in the status bar/footer could go here
        # but for now, we'll use a simple messagebox or just silent copy
        messagebox.showinfo("Copied", "Verse copied to clipboard!")

    # ==========================================
    # UI CORE
    # ==========================================
    def setup_header_ui(self):
        for widget in self.header.winfo_children(): widget.destroy()
        self.header.configure(bg=self.colors["header"])
        menu_btn = tk.Menubutton(self.header, text="MENU ▾", bg=self.colors["accent"], 
                                 fg=self.colors["fg"], font=("Segoe UI", 10), relief=tk.FLAT, padx=25)
        self.app_menu = tk.Menu(menu_btn, tearoff=0, bg=self.colors["accent"], fg=self.colors["fg"], activebackground="#4a69bd")
        menu_btn["menu"] = self.app_menu
        self.app_menu.add_command(label="Home", command=self.show_book_selection)
        self.app_menu.add_command(label="Search Bible", command=self.show_search_screen)
        self.app_menu.add_command(label="Saved Verses", command=self.show_saved_screen)
        self.app_menu.add_separator()
        self.app_menu.add_command(label="Settings", command=self.open_settings_window)
        menu_btn.pack(side=tk.LEFT, padx=10, pady=10)

    def reset_view(self):
        self.main_area.configure(bg=self.colors["bg"])
        for widget in self.main_area.winfo_children(): widget.destroy()
        if hasattr(self, 'nav_prev'): 
            try: self.nav_prev.destroy() 
            except: pass
        if hasattr(self, 'nav_next'): 
            try: self.nav_next.destroy() 
            except: pass
        self.root.unbind_all("<MouseWheel>")

    def create_scroll_container(self, center=True):
        canvas = tk.Canvas(self.main_area, bg=self.colors["bg"], highlightthickness=0)
        scroll_y = ttk.Scrollbar(self.main_area, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        anchor_val = "n" if center else "nw"; x_pos = 600 if center else 20
        canvas.create_window((x_pos, 0), window=scroll_frame, anchor=anchor_val)
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.root.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return scroll_frame

    def toggle_save(self, b_name, c_num, v_num):
        c_str = str(c_num)
        if b_name not in self.saved_verses: self.saved_verses[b_name] = {}
        if c_str not in self.saved_verses[b_name]: self.saved_verses[b_name][c_str] = []
        existing = [e for e in self.saved_verses[b_name][c_str] if e['v'] == v_num]
        if existing: self.saved_verses[b_name][c_str].remove(existing[0])
        else:
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.saved_verses[b_name][c_str].append({"v": v_num, "t": time_now})
        self.save_to_disk(); self.render_reader_content()

    # ==========================================
    # SCREENS
    # ==========================================
    def show_book_selection(self):
        self.in_reader_mode = False; self.reset_view()
        sf = self.create_scroll_container(center=True)
        tk.Label(sf, text="Old Testament", font=("Segoe UI", 26, "bold"), fg=self.colors["fg"], bg=self.colors["bg"], pady=30).pack()
        ot_g = tk.Frame(sf, bg=self.colors["bg"]); ot_g.pack(pady=10)
        for i in range(39):
            tk.Button(ot_g, text=self.bible_data[i]['name'], bg=self.colors["btn_ot"], fg="white", relief=tk.FLAT, width=18, height=2, command=lambda b=i: self.show_chapter_selection(b)).grid(row=i//4, column=i%4, padx=8, pady=8)
        tk.Label(sf, text="New Testament", font=("Segoe UI", 26, "bold"), fg=self.colors["fg"], bg=self.colors["bg"], pady=30).pack()
        nt_g = tk.Frame(sf, bg=self.colors["bg"]); nt_g.pack(pady=10)
        for i in range(39, len(self.bible_data)):
            idx = i - 39
            tk.Button(nt_g, text=self.bible_data[i]['name'], bg=self.colors["btn_nt"], fg="white", relief=tk.FLAT, width=18, height=2, command=lambda b=i: self.show_chapter_selection(b)).grid(row=idx//4, column=idx%4, padx=8, pady=8)

    def show_chapter_selection(self, b_idx):
        self.in_reader_mode = False; self.current_book_idx = b_idx; self.reset_view()
        book = self.bible_data[b_idx]
        tk.Label(self.main_area, text=book['name'], font=("Segoe UI", 24, "bold"), bg=self.colors["bg"], fg=self.colors["fg"], pady=30).pack()
        grid = tk.Frame(self.main_area, bg=self.colors["bg"]); grid.pack()
        for i, chap in enumerate(book['chapters']):
            tk.Button(grid, text=str(chap['chapter']), width=6, height=2, bg=self.colors["accent"], fg=self.colors["fg"], relief=tk.FLAT, command=lambda c=i: self.show_reader(c)).grid(row=i//10, column=i%10, padx=6, pady=6)

    def render_reader_content(self):
        for widget in self.reader_scroll_frame.winfo_children(): widget.destroy()
        book = self.bible_data[self.current_book_idx]; chap = book['chapters'][self.current_chap_idx]
        for v in chap['verses']:
            v_num = v['verse']
            v_text_full = f"{v_num}   {v['text']}"
            is_saved = any(e['v'] == v_num for e in self.saved_verses.get(book['name'], {}).get(str(chap['chapter']), []))
            bg_col = self.colors["highlight"] if is_saved else self.colors["bg"]
            border_col = self.colors["search_border"] if self.search_highlight_verse == v_num else bg_col
            v_frame = tk.Frame(self.reader_scroll_frame, bg=border_col, pady=1); v_frame.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(v_frame, text=v_text_full, bg=bg_col, fg=self.colors["fg"], relief=tk.FLAT, 
                            font=("Georgia", self.settings["font_size"]), justify=tk.LEFT, wraplength=880, 
                            anchor="w", padx=20, pady=10, command=lambda n=v_num: self.toggle_save(book['name'], chap['chapter'], n))
            
            # Feature: Right Click to Copy
            btn.bind("<Button-3>", lambda e, t=v_text_full: self.copy_to_clipboard(t))
            btn.pack(fill=tk.X)
        self.search_highlight_verse = None

    def show_reader(self, chap_idx, b_idx=None):
        if b_idx is not None: self.current_book_idx = b_idx
        self.current_chap_idx = chap_idx; self.in_reader_mode = True; self.reset_view()
        book = self.bible_data[self.current_book_idx]; chap = book['chapters'][self.current_chap_idx]
        tk.Label(self.main_area, text=f"{book['name']} {chap['chapter']}", fg=self.colors["fg"], bg=self.colors["bg"], font=("Segoe UI", 18, "bold")).pack(pady=15)
        self.reader_scroll_frame = self.create_scroll_container(center=True)
        self.render_reader_content()
        self.nav_prev = tk.Button(self.root, text="<", font=("Arial", 26), bg=self.colors["header"], fg=self.colors["fg"], relief=tk.FLAT, command=self.prev_chap)
        self.nav_prev.place(relx=0.02, rely=0.5, anchor="w", width=50, height=100)
        self.nav_next = tk.Button(self.root, text=">", font=("Arial", 26), bg=self.colors["header"], fg=self.colors["fg"], relief=tk.FLAT, command=self.next_chap)
        self.nav_next.place(relx=0.98, rely=0.5, anchor="e", width=50, height=100)

    def show_search_screen(self):
        self.in_reader_mode = False; self.reset_view()
        h = tk.Frame(self.main_area, bg=self.colors["bg"]); h.pack(fill=tk.X, padx=100, pady=40)
        tk.Label(h, text="Search the Word", font=("Segoe UI", 20), fg=self.colors["fg"], bg=self.colors["bg"]).pack(pady=10)
        self.search_var = tk.StringVar()
        e = tk.Entry(h, textvariable=self.search_var, bg=self.colors["entry_bg"], fg=self.colors["fg"], font=("Segoe UI", 14), insertbackground=self.colors["fg"], relief=tk.FLAT, highlightthickness=1); e.pack(fill=tk.X, pady=10); e.focus_set(); e.bind("<Return>", lambda x: self.execute_search())
        self.search_results_area = tk.Frame(self.main_area, bg=self.colors["bg"]); self.search_results_area.pack(fill=tk.BOTH, expand=True)

    def execute_search(self):
        q = self.search_var.get().strip().lower()
        if not q: return
        for w in self.search_results_area.winfo_children(): w.destroy()
        c = tk.Canvas(self.search_results_area, bg=self.colors["bg"], highlightthickness=0)
        rf = tk.Frame(c, bg=self.colors["bg"]); sy = ttk.Scrollbar(self.search_results_area, orient="vertical", command=c.yview)
        rf.bind("<Configure>", lambda x: c.configure(scrollregion=c.bbox("all")))
        c.create_window((0, 0), window=rf, anchor="nw", width=1100)
        c.configure(yscrollcommand=sy.set); c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sy.pack(side=tk.RIGHT, fill=tk.Y)
        for b_idx, book in enumerate(self.bible_data):
            matches = []
            for c_idx, chap in enumerate(book['chapters']):
                for v in chap['verses']:
                    if q in v['text'].lower(): matches.append((chap['chapter'], v['verse'], v['text'], c_idx))
            if matches:
                header_col = self.colors["btn_ot"] if b_idx < 39 else self.colors["btn_nt"]
                tk.Label(rf, text=book['name'], bg=header_col, fg="white", font=("Segoe UI", 12, "bold"), padx=15, pady=5, anchor="w").pack(fill=tk.X, padx=40, pady=(20, 5))
                for cn, vn, vt, ci in matches:
                    box = tk.Frame(rf, bg=self.colors["bg"], highlightthickness=1, highlightbackground=self.colors["accent"]); box.pack(fill=tk.X, padx=60, pady=5)
                    full_txt = f"{cn}:{vn} {vt}"
                    s_btn = tk.Button(box, text=full_txt, bg=self.colors["bg"], fg=self.colors["fg"], relief=tk.FLAT, justify=tk.LEFT, wraplength=900, anchor="w", font=("Georgia", 11), command=lambda b=b_idx, cidx=ci, vnum=vn: self.jump_to_verse(b, cidx, vnum))
                    s_btn.bind("<Button-3>", lambda e, t=full_txt: self.copy_to_clipboard(t))
                    s_btn.pack(fill=tk.X, padx=10, pady=10)

    def jump_to_verse(self, b_idx, c_idx, v_num):
        self.search_highlight_verse = v_num; self.show_reader(c_idx, b_idx)

    def show_saved_screen(self):
        self.in_reader_mode = False; self.reset_view()
        sf = self.create_scroll_container(center=False)
        tk.Label(sf, text="Highlights", font=("Segoe UI", 24, "bold"), fg=self.colors["fg"], bg=self.colors["bg"], pady=30).pack(padx=40)
        if not self.saved_verses: tk.Label(sf, text="No saved verses.", fg="gray", bg=self.colors["bg"]).pack(pady=50); return
        for bn, chaps in self.saved_verses.items():
            for cn, verses in chaps.items():
                if not verses: continue
                tk.Label(sf, text=f"{bn} {cn}", bg=self.colors["highlight"], fg=self.colors["fg"], font=("Segoe UI", 11, "bold"), anchor="w", padx=20).pack(fill=tk.X, padx=40, pady=(15, 5))
                for e in verses:
                    v_num = e['v']; b_idx = next(i for i, b in enumerate(self.bible_data) if b['name'] == bn)
                    v_text = next(v['text'] for v in self.bible_data[b_idx]['chapters'][int(cn)-1]['verses'] if v['verse'] == v_num)
                    box = tk.Frame(sf, bg=self.colors["bg"], highlightthickness=1, highlightbackground=self.colors["accent"]); box.pack(fill=tk.X, padx=60, pady=5)
                    txt = f"{v_num}: {v_text}"
                    tk.Label(box, text=f"Saved: {e['t']}", font=("Arial", 8), fg="gray", bg=self.colors["bg"]).pack(anchor="e", padx=5)
                    sv_btn = tk.Button(box, text=txt, font=("Georgia", 11), fg=self.colors["fg"], bg=self.colors["bg"], relief=tk.FLAT, justify=tk.LEFT, wraplength=850, anchor="w", command=lambda b=b_idx, ci=int(cn)-1: self.show_reader(ci, b))
                    sv_btn.bind("<Button-3>", lambda e, t=txt: self.copy_to_clipboard(t))
                    sv_btn.pack(fill=tk.X, padx=10, pady=5)

    def open_settings_window(self):
        win = tk.Toplevel(self.root); win.title("Settings"); win.geometry("400x400"); win.configure(bg=self.colors["accent"])
        tk.Label(win, text="Settings", font=("Segoe UI", 18, "bold"), bg=self.colors["accent"], fg=self.colors["fg"]).pack(pady=20)
        theme_var = tk.StringVar(value=self.current_theme_name)
        ttk.Combobox(win, textvariable=theme_var, values=list(self.themes.keys()), state="readonly").pack(pady=10)
        tk.Button(win, text="Apply Theme", command=lambda: self.change_theme(theme_var.get())).pack()
        f_scale = tk.Scale(win, from_=10, to_=35, orient=tk.HORIZONTAL, bg=self.colors["accent"], fg=self.colors["fg"], command=self.apply_font_change)
        f_scale.set(self.settings["font_size"]); f_scale.pack(pady=20, fill=tk.X, padx=50)

    def change_theme(self, name):
        self.current_theme_name = name; self.colors = self.themes[name]
        self.root.configure(bg=self.colors["bg"]); self.header.configure(bg=self.colors["header"])
        self.footer.configure(bg=self.colors["bg"]); self.copyright_label.configure(bg=self.colors["bg"], fg=self.colors["footer_fg"])
        self.setup_header_ui(); self.show_book_selection()

    def apply_font_change(self, val):
        self.settings["font_size"] = int(val)
        if self.in_reader_mode: self.render_reader_content()

    def next_chap(self):
        if self.current_chap_idx < len(self.bible_data[self.current_book_idx]['chapters']) - 1: self.show_reader(self.current_chap_idx + 1)
        elif self.current_book_idx < len(self.bible_data) - 1: self.current_book_idx += 1; self.show_reader(0)

    def prev_chap(self):
        if self.current_chap_idx > 0: self.show_reader(self.current_chap_idx - 1)
        elif self.current_book_idx > 0: self.current_book_idx -= 1; self.show_reader(len(self.bible_data[self.current_book_idx]['chapters']) - 1)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(); style.theme_use('clam')
    app = BibleApp(root)
    root.mainloop()