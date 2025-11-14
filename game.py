import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

FLASHCARD_FILE = "flashcards.json"

# ---------- Data persistence ----------
def load_flashcards():
    if not os.path.exists(FLASHCARD_FILE):
        # return a few sample cards to start
        return [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is 2 + 2?", "answer": "4"},
            {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare"}
        ]
    try:
        with open(FLASHCARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception as e:
        print("Error loading flashcards:",e)
    return []

def save_flashcards(cards):
    try:
        with open(FLASHCARD_FILE, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving flashcards:", e)

# ---------- GUI App ----------
class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Quiz App")
        self.root.geometry("600x380")
        self.root.resizable(False, False)

        # load data
        self.cards = load_flashcards()
        self.index = 0
        self.showing_answer = False

        # --- Top frame for card view ---
        top_frame = tk.Frame(root, padx=12, pady=12)
        top_frame.pack(fill="both", expand=True)

        self.card_title = tk.Label(top_frame, text="", font=("Helvetica", 14, "bold"))
        self.card_title.pack(anchor="w")

        self.card_text = tk.Label(top_frame, text="", wraplength=560,
                                  font=("Helvetica", 18), justify="center",
                                  bg="white", bd=2, relief="groove", padx=10, pady=20)
        self.card_text.pack(fill="both", expand=True, pady=8)

        # info line
        self.info_label = tk.Label(root, text="", font=("Helvetica", 9), fg="gray")
        self.info_label.pack()

        # --- Controls ---
        btn_frame = tk.Frame(root, pady=8)
        btn_frame.pack()

        self.prev_btn = tk.Button(btn_frame, text="Previous", width=10, command=self.prev_card)
        self.prev_btn.grid(row=0, column=0, padx=4)

        self.show_btn = tk.Button(btn_frame, text="Show Answer", width=12, command=self.toggle_answer)
        self.show_btn.grid(row=0, column=1, padx=4)

        self.next_btn = tk.Button(btn_frame, text="Next", width=10, command=self.next_card)
        self.next_btn.grid(row=0, column=2, padx=4)

        # --- Edit controls ---
        edit_frame = tk.Frame(root, pady=6)
        edit_frame.pack()

        self.add_btn = tk.Button(edit_frame, text="Add", width=10, command=self.add_card_dialog)
        self.add_btn.grid(row=0, column=0, padx=4)

        self.edit_btn = tk.Button(edit_frame, text="Edit", width=10, command=self.edit_card_dialog)
        self.edit_btn.grid(row=0, column=1, padx=4)

        self.delete_btn = tk.Button(edit_frame, text="Delete", width=10, command=self.delete_card)
        self.delete_btn.grid(row=0, column=2, padx=4)

        # --- Menu ---
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import JSON...", command=self.import_json)
        filemenu.add_command(label="Export JSON...", command=self.export_json)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        root.config(menu=menubar)

        # show first card
        self.update_ui()

    # ---------- UI Actions ----------
    def update_ui(self):
        if not self.cards:
            self.card_title.config(text="No flashcards")
            self.card_text.config(text="Add your first flashcard using the 'Add' button.")
            self.info_label.config(text="0 cards")
            self.show_btn.config(state="disabled")
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            self.edit_btn.config(state="disabled")
            self.delete_btn.config(state="disabled")
            return

        # clamps index
        self.index = max(0, min(self.index, len(self.cards) - 1))
        card = self.cards[self.index]

        # show question or answer depending on state
        if self.showing_answer:
            self.card_title.config(text=f"Answer ({self.index + 1}/{len(self.cards)})")
            self.card_text.config(text=card.get("answer", ""))
            self.show_btn.config(text="Hide Answer")
        else:
            self.card_title.config(text=f"Question ({self.index + 1}/{len(self.cards)})")
            self.card_text.config(text=card.get("question", ""))
            self.show_btn.config(text="Show Answer")

        # enable/disable nav buttons
        self.prev_btn.config(state="normal" if self.index > 0 else "disabled")
        self.next_btn.config(state="normal" if self.index < len(self.cards) - 1 else "disabled")
        self.edit_btn.config(state="normal")
        self.delete_btn.config(state="normal")
        self.show_btn.config(state="normal")
        self.info_label.config(text=f"{len(self.cards)} card(s)")

    def toggle_answer(self):
        self.showing_answer = not self.showing_answer
        self.update_ui()

    def next_card(self):
        if self.index < len(self.cards) - 1:
            self.index += 1
            self.showing_answer = False
            self.update_ui()

    def prev_card(self):
        if self.index > 0:
            self.index -= 1
            self.showing_answer = False
            self.update_ui()

    # ---------- Add / Edit / Delete ----------
    def add_card_dialog(self):
        q = simpledialog.askstring("Add Card", "Enter question:", parent=self.root)
        if q is None:  # user cancelled
            return
        q = q.strip()
        if not q:
            messagebox.showwarning("Empty", "Question cannot be empty.")
            return
        a = simpledialog.askstring("Add Card", "Enter answer:", parent=self.root)
        if a is None:
            return
        a = a.strip()
        if not a:
            messagebox.showwarning("Empty", "Answer cannot be empty.")
            return

        self.cards.append({"question": q, "answer": a})
        self.index = len(self.cards) - 1
        save_flashcards(self.cards)
        self.showing_answer = False
        self.update_ui()

    def edit_card_dialog(self):
        if not self.cards:
            return
        card = self.cards[self.index]

        # create a simple edit window
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Card")
        edit_win.geometry("500x300")
        edit_win.transient(self.root)
        edit_win.grab_set()

        tk.Label(edit_win, text="Question:", anchor="w").pack(fill="x", padx=10, pady=(10, 0))
        q_text = tk.Text(edit_win, height=6, wrap="word")
        q_text.pack(fill="both", expand=False, padx=10, pady=(0, 8))
        q_text.insert("1.0", card.get("question", ""))

        tk.Label(edit_win, text="Answer:", anchor="w").pack(fill="x", padx=10, pady=(0, 0))
        a_text = tk.Text(edit_win, height=6, wrap="word")
        a_text.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        a_text.insert("1.0", card.get("answer", ""))

        def save_and_close():
            new_q = q_text.get("1.0", "end").strip()
            new_a = a_text.get("1.0", "end").strip()
            if not new_q or not new_a:
                messagebox.showwarning("Empty", "Both question and answer are required.")
                return
            self.cards[self.index] = {"question": new_q, "answer": new_a}
            save_flashcards(self.cards)
            edit_win.destroy()
            self.showing_answer = False
            self.update_ui()

        btn_frame = tk.Frame(edit_win)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Save", command=save_and_close, width=10).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Cancel", command=edit_win.destroy, width=10).grid(row=0, column=1, padx=6)

    def delete_card(self):
        if not self.cards:
            return
        card = self.cards[self.index]
        if messagebox.askyesno("Delete", f"Delete this card?\n\nQ: {card.get('question')}\nA: {card.get('answer')}"):
            del self.cards[self.index]
            # adjust index
            if self.index >= len(self.cards):
                self.index = max(0, len(self.cards) - 1)
            save_flashcards(self.cards)
            self.showing_answer = False
            self.update_ui()

    # ---------- Import / Export ----------
    def import_json(self):
        path = filedialog.askopenfilename(title="Import JSON", filetypes=[("JSON files", ".json"), ("All files",".*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON must be a list of {question, answer} objects")
            # basic validation
            valid = []
            for item in data:
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    valid.append({"question": str(item["question"]), "answer": str(item["answer"])})
            if not valid:
                messagebox.showwarning("Import", "No valid flashcards found in file.")
                return
            if messagebox.askyesno("Import", f"Import {len(valid)} cards and replace existing set? (Yes = replace, No = append)"):
                self.cards = valid
                self.index = 0
            else:
                self.cards.extend(valid)
            save_flashcards(self.cards)
            self.showing_answer = False
            self.update_ui()
            messagebox.showinfo("Import", "Import successful.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{e}")

    def export_json(self):
        path = filedialog.asksaveasfilename(title="Export JSON", defaultextension=".json", filetypes=[("JSON files",".json"),("All files",".*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.cards, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Export", f"Exported {len(self.cards)} cards to\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{e}")

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()