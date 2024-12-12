import sqlite3
from tkinter import *
from tkinter import messagebox, ttk
import hashlib

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    # Books Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS books 
                      (id INTEGER PRIMARY KEY, title TEXT, author TEXT, quantity INTEGER)''')
    # Borrowers Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS borrowers 
                      (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)''')
    # Transactions Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions 
                      (transaction_id INTEGER PRIMARY KEY, book_id INTEGER, borrower_id INTEGER, 
                      borrow_date DATE, return_date DATE)''')
    conn.commit()
    conn.close()

# --- Core Functionalities ---
def add_book(title, author, quantity):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", (title, author, quantity))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Book added successfully!")

def register_borrower(name, email, password):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO borrowers (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Borrower registered successfully!")

def borrow_book(borrower_id, book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if book and book[0] > 0:
        cursor.execute("INSERT INTO transactions (book_id, borrower_id, borrow_date) VALUES (?, ?, DATE('now'))", 
                       (book_id, borrower_id))
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        conn.commit()
        messagebox.showinfo("Success", "Book borrowed successfully!")
    else:
        messagebox.showerror("Error", "Book not available!")
    conn.close()

def return_book(transaction_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute("SELECT book_id FROM transactions WHERE transaction_id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    if transaction:
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (transaction[0],))
        cursor.execute("UPDATE transactions SET return_date = DATE('now') WHERE transaction_id = ?", (transaction_id,))
        conn.commit()
        messagebox.showinfo("Success", "Book returned successfully!")
    else:
        messagebox.showerror("Error", "Invalid transaction ID!")
    conn.close()

# --- GUI Functions ---
def open_add_book_window():
    add_book_window = Toplevel(root)
    add_book_window.title("Add Book")
    Label(add_book_window, text="Title:").grid(row=0, column=0, padx=10, pady=5)
    title_entry = Entry(add_book_window)
    title_entry.grid(row=0, column=1, padx=10, pady=5)
    Label(add_book_window, text="Author:").grid(row=1, column=0, padx=10, pady=5)
    author_entry = Entry(add_book_window)
    author_entry.grid(row=1, column=1, padx=10, pady=5)
    Label(add_book_window, text="Quantity:").grid(row=2, column=0, padx=10, pady=5)
    quantity_entry = Entry(add_book_window)
    quantity_entry.grid(row=2, column=1, padx=10, pady=5)
    Button(add_book_window, text="Add", command=lambda: add_book(
        title_entry.get(), author_entry.get(), int(quantity_entry.get())
    )).grid(row=3, column=0, columnspan=2, pady=10)

def open_register_window():
    register_window = Toplevel(root)
    register_window.title("Register Borrower")
    Label(register_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
    name_entry = Entry(register_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    Label(register_window, text="Email:").grid(row=1, column=0, padx=10, pady=5)
    email_entry = Entry(register_window)
    email_entry.grid(row=1, column=1, padx=10, pady=5)
    Label(register_window, text="Password:").grid(row=2, column=0, padx=10, pady=5)
    password_entry = Entry(register_window, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=5)
    Button(register_window, text="Register", command=lambda: register_borrower(
        name_entry.get(), email_entry.get(), password_entry.get()
    )).grid(row=3, column=0, columnspan=2, pady=10)

def open_borrow_book_window():
    borrow_window = Toplevel(root)
    borrow_window.title("Borrow Book")
    Label(borrow_window, text="Borrower ID:").grid(row=0, column=0, padx=10, pady=5)
    borrower_id_entry = Entry(borrow_window)
    borrower_id_entry.grid(row=0, column=1, padx=10, pady=5)
    Label(borrow_window, text="Book ID:").grid(row=1, column=0, padx=10, pady=5)
    book_id_entry = Entry(borrow_window)
    book_id_entry.grid(row=1, column=1, padx=10, pady=5)
    Button(borrow_window, text="Borrow", command=lambda: borrow_book(
        int(borrower_id_entry.get()), int(book_id_entry.get())
    )).grid(row=2, column=0, columnspan=2, pady=10)

def open_return_book_window():
    return_window = Toplevel(root)
    return_window.title("Return Book")
    Label(return_window, text="Transaction ID:").grid(row=0, column=0, padx=10, pady=5)
    transaction_id_entry = Entry(return_window)
    transaction_id_entry.grid(row=0, column=1, padx=10, pady=5)
    Button(return_window, text="Return", command=lambda: return_book(
        int(transaction_id_entry.get())
    )).grid(row=1, column=0, columnspan=2, pady=10)

def open_view_borrowed_books_window():
    borrowed_books_window = Toplevel(root)
    borrowed_books_window.title("Borrowed Books")

    columns = ("Transaction ID", "Book Title", "Borrower Name", "Borrow Date", "Return Date")
    tree = ttk.Treeview(borrowed_books_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT t.transaction_id, b.title, br.name, t.borrow_date, t.return_date 
                      FROM transactions t
                      JOIN books b ON t.book_id = b.id
                      JOIN borrowers br ON t.borrower_id = br.id''')
    borrowed_books = cursor.fetchall()
    conn.close()

    for book in borrowed_books:
        tree.insert("", END, values=book)

    tree.pack(fill=BOTH, expand=True)

# --- Main Window ---
root = Tk()
root.title("Library Management System")

Label(root, text="Library Management System", font=("Arial", 16)).pack(pady=10)

Button(root, text="Add Book", width=20, command=open_add_book_window).pack(pady=5)
Button(root, text="Register Borrower", width=20, command=open_register_window).pack(pady=5)
Button(root, text="Borrow Book", width=20, command=open_borrow_book_window).pack(pady=5)
Button(root, text="Return Book", width=20, command=open_return_book_window).pack(pady=5)
Button(root, text="View Borrowed Books", width=20, command=open_view_borrowed_books_window).pack(pady=5)

if __name__ == "__main__":
    init_db()
    root.mainloop()
