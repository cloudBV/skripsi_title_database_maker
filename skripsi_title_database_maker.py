#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import tkinter.font as tkfont
import json
import os
import sys
import csv
import hashlib

# ---------------------------------------------------------------------------
# FILE PATHS — always resolved relative to where this script lives
# This prevents "file not found" errors when launching from different locations
# (taskbar, terminal, file manager — doesn't matter, paths always work)
# os.path.abspath(sys.argv[0]) = full path to this script file
# os.path.dirname(...)         = folder containing this script
# ---------------------------------------------------------------------------
BASE_DIR         = os.path.dirname(os.path.abspath(sys.argv[0]))
STUDENTS_FILE    = os.path.join(BASE_DIR, "students.json")      # one JSON object per line (JSONL format)
INSPIRATION_FILE = os.path.join(BASE_DIR, "inspiration.txt")    # one title per line

# ---------------------------------------------------------------------------
# ADMIN PASSWORD — stored as a SHA-256 hash, never as plaintext
# To change the password: replace the string "awawa" with your new password
# The hash will be computed automatically on startup
# ---------------------------------------------------------------------------
ADMIN_PASSWORD_HASH = hashlib.sha256("awawa".encode()).hexdigest()


# ---------------------------------------------------------------------------
# PLACEHOLDER ENTRY — a text entry that shows grey hint text when empty
# Clears on focus, restores hint if left empty
# ---------------------------------------------------------------------------
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder       = placeholder
        self.placeholder_color = color
        self.default_fg_color  = self['fg']   # save original text color

        self.bind("<FocusIn>",  self.foc_in)   # when user clicks in
        self.bind("<FocusOut>", self.foc_out)  # when user clicks away
        self.put_placeholder()                 # show hint text on startup

    def put_placeholder(self):
        """Insert placeholder text in grey."""
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, _event=None):
        """Clear placeholder when user clicks into the box."""
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, _event=None):
        """Restore placeholder if user leaves the box empty."""
        if not self.get():
            self.put_placeholder()


# ---------------------------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------------------------
class SkripsiProV4:
    def __init__(self, app_root):
        self.root = app_root
        self.root.title("Skripsi Title Manager By : Yosef Setiawan")
        self.root.geometry("1100x850")   # default window size — change if needed

        # --- Treeview (table) styling ---
        self.style = ttk.Style()
        self.style.theme_use('clam')   # 'clam' supports custom colors; alternatives: 'default', 'alt'
        self.style.configure("Treeview",
                             background="#2b2b2b",      # table row background
                             foreground="white",         # table row text color
                             fieldbackground="#2b2b2b",  # area behind rows
                             rowheight=28)               # row height in pixels — increase for bigger text
        self.style.configure("Treeview.Heading",
                             background="#333",          # column header background
                             foreground="white",
                             font=("Arial", 10, "bold"))
        self.style.map("Treeview",
                       background=[('selected', '#4a90e2')])   # selected row highlight color

        # --- App colors — change these to restyle ---
        self.bg_color     = "#1e1e1e"   # main background (dark grey)
        self.accent_color = "#00b894"   # buttons and highlights (green)
        self.root.configure(bg=self.bg_color)

        # Outer container — all screens are built inside this frame
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_main_menu()   # start on the main menu screen

    def clear_screen(self):
        """Destroy all widgets inside self.container to prepare for a new screen."""
        for widget in self.container.winfo_children():
            widget.destroy()

    # =========================================================================
    # PASSWORD GATE — wraps any function behind an admin password prompt
    # =========================================================================
    def check_password(self, target_command):
        """
        Open a small popup asking for the admin password.
        If correct: close popup and run target_command().
        If wrong: show error and close popup.
        Password is compared as SHA-256 hashes (never plaintext).
        """
        win = tk.Toplevel(self.root)   # Toplevel = a new window on top of the main one
        win.title("Awawawawa?")
        win.geometry("300x150")
        win.configure(bg="#2b2b2b")

        tk.Label(win, text="Awawawawa!!", bg="#2b2b2b", fg="white").pack(pady=10)
        pw_entry = tk.Entry(win, show="*")   # show="*" hides typed characters
        pw_entry.pack(pady=5)
        pw_entry.focus_set()   # auto-focus so user can type immediately

        def validate():
            # Hash what was typed and compare to stored hash — never compare plaintext
            entered_hash = hashlib.sha256(pw_entry.get().encode()).hexdigest()
            if entered_hash == ADMIN_PASSWORD_HASH:
                win.destroy()
                target_command()   # run the protected function
            else:
                messagebox.showerror("hmmmph!!", "(¬_¬')")
                win.destroy()

        tk.Button(win, text="(¬_¬)", command=validate,
                  bg=self.accent_color, fg="white").pack(pady=10)

    # =========================================================================
    # MAIN MENU
    # =========================================================================
    def show_main_menu(self):
        """Show the 3-button home screen with a live submission count at the bottom."""
        self.clear_screen()

        tk.Label(self.container,
                 text="(^ᗜ^ ) - Skripsi Title Database - ( ^ᗜ^)",
                 font=("Impact", 38),   # change font size here if title is too big/small
                 bg=self.bg_color, fg=self.accent_color).pack(pady=40)

        btn_frame = tk.Frame(self.container, bg=self.bg_color)
        btn_frame.pack(pady=10)

        # Button 1: Student submission form — no password required
        tk.Button(btn_frame,
                  text="(• ᴗ •) 1. Student Submission (• ᴗ •)",
                  width=35, font=("Arial", 12, "bold"),
                  bg="#333", fg="white", relief="flat", pady=15,
                  command=self.show_student_input).pack(pady=10)

        # Button 2: Admin table view — password protected
        tk.Button(btn_frame,
                  text="(っ- ‸ - ς) 2. Database & Refining (っ- ‸ - ς)",
                  width=35, font=("Arial", 12, "bold"),
                  bg="#333", fg="white", relief="flat", pady=15,
                  command=lambda: self.check_password(self.show_table)).pack(pady=10)

        # Button 3: Inspiration library — password protected
        tk.Button(btn_frame,
                  text="!!(°ㅁ°˶) 3. Inspiration Library (˶°ㅁ°)!!",
                  width=35, font=("Arial", 12, "bold"),
                  bg="#333", fg="white", relief="flat", pady=15,
                  command=lambda: self.check_password(self.show_inspiration_input)).pack(pady=10)

        # Live stats at the bottom — reads the file every time menu is shown
        stats = self.get_stats()
        tk.Label(self.container, text=stats,
                 font=("Arial", 10, "italic"),
                 bg=self.bg_color, fg="#888").pack(side="bottom", pady=20)

    def get_stats(self):
        """
        Count total submissions and approved ones from the JSONL file.
        Returns a formatted string like "System Status: 12 Submissions | 5 Approved"
        Skips corrupted lines silently (try/except around json.loads).
        """
        total = 0
        appr  = 0
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():   # skip blank lines
                        try:
                            d = json.loads(line)
                            total += 1
                            if d.get("Status") == "Approved":
                                appr += 1
                        except json.JSONDecodeError:
                            continue   # silently skip corrupted lines
        return f"System Status: {total} Submissions | {appr} Approved"

    # =========================================================================
    # STUDENT SUBMISSION FORM
    # =========================================================================
    def show_student_input(self):
        """Show the form students fill out to submit a skripsi topic."""
        self.clear_screen()
        tk.Label(self.container, text="🗨️ Student Submission 💭",
                 font=("Arial", 18, "bold"),
                 bg=self.bg_color, fg="white").pack(pady=20)

        self.entries = {}   # dict to hold all entry widgets for easy access in save_student()
        form_frame = tk.Frame(self.container, bg=self.bg_color)
        form_frame.pack()

        # Hint text shown inside each field before user types
        # Change these strings to change the placeholder hints
        placeholders = {
            "Class":  "What Class r u rn",
            "Name":   "Whats ur Name",
            "Topic":  "What Do You Wanna Talk Bout",
            "Reason": "Whats The Problems that U Wanna Talk Bout (min 5 words)",
            "Target": "Who is being studied?"
        }

        # Class field is stored separately (self.class_entry) because it's handled
        # slightly differently in save_student() — this is a historical quirk
        tk.Label(form_frame, text="Class",
                 bg=self.bg_color, fg=self.accent_color,
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.class_entry = PlaceholderEntry(form_frame,
                                            placeholder=placeholders["Class"],
                                            width=50, bg="#2b2b2b", fg="white",
                                            relief="flat", bd=5)
        self.class_entry.pack(pady=5)

        # All other fields stored in self.entries dict
        for field in ["Name", "Topic", "Reason", "Target"]:
            tk.Label(form_frame, text=field,
                     bg=self.bg_color, fg=self.accent_color,
                     font=("Arial", 10, "bold")).pack(anchor="w")
            ent = PlaceholderEntry(form_frame,
                                   placeholder=placeholders[field],
                                   width=50, bg="#2b2b2b", fg="white",
                                   relief="flat", bd=5)
            ent.pack(pady=5)
            self.entries[field] = ent   # store reference so save_student() can read it

        tk.Button(self.container, text="SAVE IDEA",
                  bg=self.accent_color, fg="white",
                  font=("Arial", 12, "bold"), width=20,
                  command=self.save_student).pack(pady=25)
        tk.Button(self.container, text="BACK",
                  bg="#636e72", fg="white",
                  command=self.show_main_menu).pack()

    def save_student(self):
        """
        Validate form fields and append the submission as one JSON line to students.json.
        Validation rules:
          - Name and Class must not be empty
          - Reason must be at least 5 words
        Status is always set to "Pending" on submission.
        Data format: one JSON object per line (JSONL) — easy to read line by line.
        """
        # Read class entry — check fg color to detect if it's still showing placeholder
        class_val = self.class_entry.get() if self.class_entry['fg'] != 'grey' else ""
        # Read all other fields the same way
        data = {f: (ent.get() if ent['fg'] != 'grey' else "") for f, ent in self.entries.items()}
        data["Class"]  = class_val
        data["Status"] = "Pending"   # always starts as Pending — admin changes it later

        # Basic validation
        if not data["Name"] or not data["Class"]:
            messagebox.showwarning("Error", "Name and Class are required!")
            return

        # Reason word count check — change 5 to require more/fewer words
        if len(data["Reason"].split()) < 5:
            messagebox.showwarning("Logic Error", "Reason too short! Be more descriptive.")
            return

        # Append as a single JSON line — each submission is one line in the file
        with open(STUDENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        messagebox.showinfo("Success", "Submission received!")
        self.show_main_menu()

    # =========================================================================
    # ADMIN TABLE VIEW
    # =========================================================================
    def show_table(self):
        """
        Admin screen: full table of all submissions with search, filter, sort,
        status update, draft generation, delete, and CSV export.
        """
        self.clear_screen()

        # --- Top bar: search, auto-fit, class filter ---
        top_bar = tk.Frame(self.container, bg=self.bg_color)
        top_bar.pack(fill="x", pady=10)

        tk.Label(top_bar, text="🔍 Search:", bg=self.bg_color, fg="white").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        # trace_add fires refresh_table() every time the search text changes
        self.search_var.trace_add("write", lambda *args: self.refresh_table())
        tk.Entry(top_bar, textvariable=self.search_var, width=20).pack(side="left", padx=5)

        tk.Button(top_bar, text="↔ Auto-Fit Columns",
                  bg="#333", fg="white", relief="flat",
                  command=self.auto_fit_columns).pack(side="left", padx=15)

        tk.Label(top_bar, text="Class:", bg=self.bg_color, fg="white").pack(side="left", padx=10)
        self.filter_var = tk.StringVar(value="All")
        classes = ["All"] + self.get_unique_classes()   # dynamically read classes from file
        ttk.OptionMenu(top_bar, self.filter_var, "All", *classes,
                       command=lambda _: self.refresh_table()).pack(side="left")

        # --- Treeview table ---
        # Column order — change this list to reorder or add/remove columns
        self.cols = ("Class", "Name", "Topic", "Status", "Target", "Reason")
        self.tree = ttk.Treeview(self.container, columns=self.cols, show='headings')
        for col in self.cols:
            # Clicking a column header sorts by that column
            self.tree.heading(col, text=col,
                              command=self._make_sort_handler(col))
            width = 200 if col == "Reason" else 100   # Reason gets more space by default
            self.tree.column(col, width=width)

        # Row color tags — Approved = green text, Revision = salmon text
        # Change the hex colors here to restyle status highlights
        self.tree.tag_configure('Approved', foreground='#55efc4')
        self.tree.tag_configure('Revision', foreground='#fab1a0')
        self.tree.pack(pady=10, fill="both", expand=True)
        self.refresh_table()   # populate the table immediately

        # --- Tools row: status changer + draft generator ---
        tool_frame = tk.Frame(self.container, bg=self.bg_color)
        tool_frame.pack(fill="x", pady=5)
        self.status_var = tk.StringVar(value="Approved")
        # Dropdown with all possible statuses — add more here if needed
        ttk.OptionMenu(tool_frame, self.status_var,
                       "Approved", "Approved", "Revision", "Pending").pack(side="left", padx=5)
        tk.Button(tool_frame, text="Set Status",
                  bg=self.accent_color, fg="white",
                  command=self.update_status).pack(side="left", padx=5)
        tk.Button(tool_frame, text="📄 Generate Draft",
                  bg="#6c5ce7", fg="white",
                  command=self.refine_and_draft).pack(side="left", padx=15)

        # --- Bottom row: delete, export, back ---
        bot_frame = tk.Frame(self.container, bg=self.bg_color)
        bot_frame.pack(pady=20, fill="x")
        tk.Button(bot_frame, text="🗑 Delete",
                  bg="#d63031", fg="white", width=10,
                  command=self.delete_entry).pack(side="left", padx=5)
        tk.Button(bot_frame, text="📥 CSV Export",
                  bg="#0984e3", fg="white", width=10,
                  command=self.export_csv).pack(side="left", padx=5)
        tk.Button(bot_frame, text="⬅ Back",
                  bg="#636e72", fg="white", width=10,
                  command=self.show_main_menu).pack(side="right", padx=5)

    def _make_sort_handler(self, col):
        """
        Factory to create a sort callback for each column header.
        Without a factory, all headers would sort by the last value of 'col'
        in the loop (classic Python closure-in-loop bug).
        """
        def handler():
            self.refresh_table(sort_by=col)
        return handler

    def auto_fit_columns(self):
        """
        Resize each column to fit the widest value it contains.
        Measures text width using tkfont.Font to get pixel-accurate widths.
        Caps column width at 600px to prevent absurdly wide columns.
        """
        m_font = tkfont.Font(family="Arial", size=10)
        for col in self.cols:
            max_width = m_font.measure(col) + 30   # start with header width + padding
            for item in self.tree.get_children():
                cell_value = str(self.tree.set(item, col))
                text_width = m_font.measure(cell_value) + 30
                if text_width > max_width:
                    max_width = text_width
            self.tree.column(col, width=min(max_width, 600))   # 600 = max column width cap

    def refresh_table(self, sort_by=None):
        """
        Clear and repopulate the table from the JSONL file.
        Applies search filter (Name/Topic/Reason), class filter, and optional sort.
        Skips corrupted lines silently.
        """
        # Clear all existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        search    = self.search_var.get().lower()   # empty string matches everything
        sel_class = self.filter_var.get()           # "All" means no class filter
        data      = []

        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            d = json.loads(line)
                            # Search matches if query appears in Name, Topic, or Reason
                            if (search in d.get("Name",   "").lower() or
                                    search in d.get("Topic",  "").lower() or
                                    search in d.get("Reason", "").lower()):
                                # Class filter — "All" shows everything
                                if sel_class == "All" or d.get("Class") == sel_class:
                                    data.append(d)
                        except json.JSONDecodeError:
                            continue   # skip corrupted lines

        # Optional sort — alphabetical by the clicked column
        if sort_by:
            data.sort(key=lambda x: str(x.get(sort_by, "")).lower())

        # Insert rows — tag each row with its Status for color coding
        for d in data:
            status = d.get("Status", "Pending")
            self.tree.insert("", "end", values=(
                d.get("Class"), d.get("Name"), d.get("Topic"),
                status, d.get("Target"), d.get("Reason")
            ), tags=(status,))   # tags match the tag_configure calls in show_table()

    def update_status(self):
        """
        Change the Status field of the selected row to the value in self.status_var.
        Reads the entire file, updates the matching record, rewrites the file.
        Matches on Class + Name + Topic to avoid updating the wrong record.
        """
        selected = self.tree.selection()
        if not selected:
            return

        item_id    = selected[0]
        new_status = self.status_var.get()
        vals       = self.tree.item(item_id)['values']
        sel_class  = str(vals[0])
        sel_name   = str(vals[1])
        sel_topic  = str(vals[2])

        all_data = []
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                        # Match on 3 fields to uniquely identify the record
                        if (str(d.get("Class")) == sel_class and
                                d.get("Name")  == sel_name  and
                                d.get("Topic") == sel_topic):
                            d["Status"] = new_status   # update status in memory
                        all_data.append(d)
                    except json.JSONDecodeError:
                        continue

            # Rewrite entire file with the updated record
            with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
                for d in all_data:
                    f.write(json.dumps(d) + "\n")

        self.refresh_table()

    def refine_and_draft(self):
        """
        Generate a plain-text proposal draft for the selected row.
        Only works on Approved submissions — shows warning otherwise.
        Opens a save dialog so user picks where to save the .txt file.
        Offers to open the file immediately after saving (via xdg-open on Linux).
        """
        selected = self.tree.selection()
        if not selected:
            return

        item_id = selected[0]
        vals    = self.tree.item(item_id)['values']

        # Guard: only Approved submissions can generate a draft
        if vals[3] != "Approved":
            messagebox.showwarning("Workflow", "Topic must be 'Approved' first!")
            return

        sel_class = str(vals[0])
        sel_name  = str(vals[1])
        sel_topic = str(vals[2])

        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                        if (str(d.get("Class")) == sel_class and
                                d.get("Name")  == sel_name  and
                                d.get("Topic") == sel_topic):

                            # Ask where to save — default filename uses student name
                            default_name = f"Draft_{d['Name'].replace(' ', '_')}.txt"
                            path = filedialog.asksaveasfilename(
                                defaultextension=".txt",
                                filetypes=[("Text files", "*.txt")],
                                initialfile=default_name
                            )
                            if not path:
                                return   # user cancelled the dialog

                            # Write the draft file
                            # Change the template below to customize the draft format
                            with open(path, "w", encoding="utf-8") as df:
                                df.write(
                                    f"--- PROPOSAL DRAFT ---\n"
                                    f"CLASS : {d.get('Class',  '')}\n"
                                    f"NAME  : {d.get('Name',   '')}\n"
                                    f"TOPIC : {d.get('Topic',  '')}\n"
                                    f"REASON: {d.get('Reason', '')}\n"
                                    f"TARGET: {d.get('Target', '')}\n"
                                    f"STATUS: {d.get('Status', '')}\n"
                                )

                            # Offer to open the file immediately
                            if messagebox.askyesno("Success", "Draft saved!\nOpen file now?"):
                                import subprocess
                                try:
                                    subprocess.Popen(["xdg-open", path])   # Linux file opener
                                except Exception:
                                    # Fallback: just show the path if xdg-open fails
                                    messagebox.showinfo("Info", f"File saved at:\n{path}")
                            return
                    except json.JSONDecodeError:
                        continue

    def get_unique_classes(self):
        """
        Scan the JSONL file and return a sorted list of all unique class names.
        Used to populate the class filter dropdown in the admin table.
        """
        classes = set()
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            classes.add(json.loads(line).get("Class", "Unassigned"))
                        except json.JSONDecodeError:
                            continue
        return sorted(list(classes))

    def delete_entry(self):
        """
        Delete the selected row from the JSONL file.
        Reads entire file, skips the matching record, rewrites everything else.
        Matches on Class + Name + Topic (not just Name) to avoid deleting wrong record.
        """
        selected = self.tree.selection()
        if not selected or not messagebox.askyesno("Confirm", "Delete record?"):
            return

        item_id   = selected[0]
        vals      = self.tree.item(item_id)['values']
        sel_class = str(vals[0])
        sel_name  = str(vals[1])
        sel_topic = str(vals[2])

        all_data = []
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    d = json.loads(line)
                    # Keep every record EXCEPT the one matching all 3 fields
                    if not (str(d.get("Class")) == sel_class and
                            d.get("Name")  == sel_name  and
                            d.get("Topic") == sel_topic):
                        all_data.append(d)
                except json.JSONDecodeError:
                    continue

        # Rewrite file without the deleted record
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            for d in all_data:
                f.write(json.dumps(d) + "\n")

        self.refresh_table()

    def export_csv(self):
        """
        Export all submissions to a CSV file chosen by the user.
        Opens a save dialog — user picks location and filename.
        Uses .get() for all fields to handle old records missing newer fields.
        """
        if not os.path.exists(STUDENTS_FILE):
            return

        # Save dialog — user picks where to export
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="skripsi_export.csv"   # default filename suggestion
        )
        if not path:
            return   # user cancelled

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Class", "Name", "Topic", "Status", "Target", "Reason"])   # header row
            with open(STUDENTS_FILE, "r", encoding="utf-8") as jf:
                for line in jf:
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                        # .get() with "" default handles old records missing newer fields
                        writer.writerow([
                            d.get("Class",  ""),
                            d.get("Name",   ""),
                            d.get("Topic",  ""),
                            d.get("Status", ""),
                            d.get("Target", ""),
                            d.get("Reason", "")
                        ])
                    except json.JSONDecodeError:
                        continue   # skip corrupted lines

        messagebox.showinfo("Exported", f"Saved to {path}")

    # =========================================================================
    # INSPIRATION LIBRARY
    # =========================================================================
    def show_inspiration_input(self):
        """
        Admin screen: a simple list of reference/inspiration titles.
        Stored one title per line in inspiration.txt.
        """
        self.clear_screen()
        tk.Label(self.container, text="INSPIRATION LIBRARY",
                 font=("Arial", 18, "bold"),
                 bg=self.bg_color, fg="white").pack(pady=10)

        # Listbox shows all saved titles
        self.listbox = tk.Listbox(self.container, bg="#2b2b2b", fg="white",
                                  font=("Arial", 11), height=12)
        self.listbox.pack(pady=10, fill="x")
        self.load_refs()   # populate from file

        # Text entry for adding new titles
        self.new_ref = tk.Entry(self.container, bg="#2b2b2b", fg="white", width=60)
        self.new_ref.pack(pady=10)

        btn_f = tk.Frame(self.container, bg=self.bg_color)
        btn_f.pack()
        tk.Button(btn_f, text="Add Title",
                  bg=self.accent_color, fg="white", width=15,
                  command=self.add_ref).pack(side="left", padx=5)
        tk.Button(btn_f, text="Delete Item",
                  bg="#d63031", fg="white", width=15,
                  command=self.del_ref).pack(side="left", padx=5)
        tk.Button(self.container, text="BACK",
                  bg="#636e72", fg="white",
                  command=self.show_main_menu).pack(pady=20)

    def load_refs(self):
        """Clear and repopulate the listbox from inspiration.txt."""
        self.listbox.delete(0, tk.END)   # clear all existing items
        if os.path.exists(INSPIRATION_FILE):
            with open(INSPIRATION_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    self.listbox.insert(tk.END, line.strip())   # one entry per line

    def add_ref(self):
        """Append whatever is in self.new_ref to inspiration.txt, then refresh the list."""
        if t := self.new_ref.get():   # walrus operator (:=) — only runs if entry is not empty
            with open(INSPIRATION_FILE, "a", encoding="utf-8") as f:
                f.write(t + "\n")
            self.new_ref.delete(0, tk.END)   # clear the input box
            self.load_refs()                  # refresh the listbox

    def del_ref(self):
        """
        Delete the currently selected item from inspiration.txt.
        Reads all lines, removes the selected index, rewrites the file.
        """
        idx = self.listbox.curselection()   # returns a tuple of selected indices
        if not idx:
            return
        with open(INSPIRATION_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        del lines[idx[0]]   # remove the selected line by index
        with open(INSPIRATION_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines)   # write remaining lines back
        self.load_refs()


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root_window = tk.Tk()
    app = SkripsiProV4(root_window)
    root_window.mainloop()   # starts the tkinter event loop — runs until window is closed
