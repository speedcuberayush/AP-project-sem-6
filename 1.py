import tkinter as tk
from tkinter import messagebox, Text, END, ttk
import nltk
from nltk.corpus import words
import pyperclip
from difflib import get_close_matches

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node is not None and node.is_end_of_word

    def autocomplete(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return self.closest_suggestion(prefix)  # Return closest suggestion
            node = node.children[char]
        
        return self._autocomplete_helper(prefix, node)[:5]  # Return top 5 suggestions

    def closest_suggestion(self, word):
        all_words = [w for w in words.words() if w.startswith(word)]
        closest_matches = get_close_matches(word, all_words, n=1, cutoff=0.8)
        if closest_matches:
            return closest_matches[0]
        else:
            return ""

    def _autocomplete_helper(self, prefix, node):
        completions = []
        if node.is_end_of_word:
            completions.append(prefix)
        
        for char, child_node in node.children.items():
            completions.extend(self._autocomplete_helper(prefix + char, child_node))
        
        return completions

class AutoCompleteApp:
    def __init__(self, master):
        self.master = master
        master.title("Trie based AutoComplete")
        # Color theme
        self.bg_color = "#393e46"
        self.text_color = "#eeeeee"
        self.text_box_bg = "#222831"
        self.suggestion_color = "#00adb5"
        self.suggestion_hover_color = "#eeeeee"
        self.font = ("Arial", 12)

        master.config(bg=self.bg_color)

        self.trie = Trie()
        self.load_dictionary()

        self.label = tk.Label(master, text="Enter text:", bg=self.bg_color, fg=self.text_color, font=self.font)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.text_box = tk.Text(master, height=5, width=30, bg=self.text_box_bg, fg=self.text_color, font=self.font, wrap=tk.WORD)
        self.text_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.text_box.bind("<KeyRelease>", self.on_key_release)

        self.show_suggestions_var = tk.IntVar()
        self.show_suggestions_var.set(1)  # Default: Show suggestions
        self.show_suggestions_checkbutton = ttk.Checkbutton(master, text="Show Suggestions", variable=self.show_suggestions_var, onvalue=1, offvalue=0, command=self.update_suggestions)
        self.show_suggestions_checkbutton.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")

        self.suggestions_frame = tk.Frame(master, bg=self.bg_color)  # No fixed height
        self.suggestions_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.copy_button = tk.Button(master, text="Copy to Clipboard", command=self.copy_to_clipboard, bg=self.bg_color, fg=self.text_color, font=self.font)
        self.copy_button.grid(row=4, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.copy_button.config(state=tk.DISABLED)  # Initially disabled

        self.done_button = tk.Button(master, text="Done", command=self.display_text, bg=self.bg_color, fg=self.text_color, font=self.font)
        self.done_button.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.output_label_frame = tk.Frame(master, bg=self.bg_color, bd=1, relief=tk.SOLID)
        self.output_label_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")

        self.output_label = Text(self.output_label_frame, wrap="word", bg=self.bg_color, fg=self.text_color, font=self.font)
        self.output_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

    def load_dictionary(self):
        nltk.download('words')
        word_list = words.words()
        for word in word_list:
            self.trie.insert(word.lower())

    def on_key_release(self, event):
        self.update_suggestions()

    def update_suggestions(self):
        if self.show_suggestions_var.get() == 1:
            # Clear previous suggestions
            for widget in self.suggestions_frame.winfo_children():
                widget.destroy()

            words = self.text_box.get("1.0", "end-1c").split()
            current_word = words[-1].lower()
            if current_word:
                suggestions = self.trie.autocomplete(current_word)
                for suggestion in suggestions:
                    label = tk.Label(self.suggestions_frame, text=suggestion, fg=self.suggestion_color, bg=self.bg_color, font=self.font, cursor="hand2")
                    label.pack(side=tk.LEFT, padx=5)
                    label.bind("<Button-1>", self.on_suggestion_click)
                    label.bind("<Enter>", self.on_suggestion_enter)
                    label.bind("<Leave>", self.on_suggestion_leave)
        else:
            # Hide suggestions
            for widget in self.suggestions_frame.winfo_children():
                widget.destroy()

    def on_suggestion_click(self, event):
        suggestion = event.widget.cget("text")
        self.replace_word(suggestion)

    def on_suggestion_enter(self, event):
        event.widget.config(fg=self.suggestion_hover_color)

    def on_suggestion_leave(self, event):
        event.widget.config(fg=self.suggestion_color)

    def replace_word(self, suggestion):
        words = self.text_box.get("1.0", "end-1c").split()
        words[-1] = suggestion
        updated_text = " ".join(words)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert("1.0", updated_text)

    def copy_to_clipboard(self):
        text_to_copy = self.output_label.get("1.0", "end-1c")
        pyperclip.copy(text_to_copy)

    def display_text(self):
        text_to_display = self.text_box.get("1.0", END)
        self.output_label.delete("1.0", END)
        self.output_label.insert(END, text_to_display)
        self.copy_button.config(state=tk.NORMAL)  # Enable copy button

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCompleteApp(root)
    # Center the window horizontally on the screen
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    position_right = int((root.winfo_screenwidth() - window_width) // 2)
    root.geometry("+{}+{}".format(position_right, 0))
    root.mainloop()
