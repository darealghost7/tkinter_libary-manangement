import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import os

# Try to import tkcalendar, provide fallback if not available
try:
    from tkcalendar import DateEntry

    TK_CALENDAR_AVAILABLE = True
except ImportError:
    TK_CALENDAR_AVAILABLE = False
    print("tkcalendar not available. Using simple date entry.")


class LibraryManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

        # Initialize database
        self.init_database()

        # Create GUI
        self.create_widgets()

        # Load initial data
        self.refresh_books_combobox()
        self.refresh_table()

    def init_database(self):
        """Initialize database and create tables with sample data"""
        # Remove existing database to start fresh (optional)
        if os.path.exists('library.db'):
            os.remove('library.db')

        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()

        # Create books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                quantity INTEGER NOT NULL
            )
        ''')

        # Create borrowed_books table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowed_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                book_id INTEGER,
                borrow_date TEXT NOT NULL,
                return_date TEXT NOT NULL,
                fine REAL DEFAULT 0,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')

        # Insert sample books
        sample_books = [
            ('Introduction to Python', 3),
            ('Data Structures and Algorithms', 2),
            ('Machine Learning Fundamentals', 4),
            ('Database Systems', 1),
            ('Web Development with Django', 2)
        ]

        self.cursor.executemany(
            "INSERT INTO books (title, quantity) VALUES (?, ?)",
            sample_books
        )

        # Insert sample borrowed records
        sample_borrowed = [
            ('John Smith', 1, '06/15/25', '06/25/25', 0),
            ('Emma Wilson', 2, '06/18/25', '06/28/25', 0),
            ('Michael Brown', 3, '06/10/25', '06/20/25', 25.0)
        ]
        self.cursor.executemany(
            '''INSERT INTO borrowed_books 
            (student_name, book_id, borrow_date, return_date, fine) 
            VALUES (?, ?, ?, ?, ?)''',
            sample_borrowed
        )

        self.conn.commit()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = tk.Label(main_frame, text="Library Management System",
                               font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 20))

        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Borrow Book Form
        self.create_borrow_form(content_frame)

        # Right side - Borrowed Books Table
        self.create_books_table(content_frame)

    def create_borrow_form(self, parent):
        """Create the borrow book form"""
        form_frame = ttk.LabelFrame(parent, text="Borrow Book", padding="15", width=350)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        form_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Student Name
        ttk.Label(form_frame, text="Student Name:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.student_name = tk.StringVar()
        student_entry = ttk.Entry(form_frame, textvariable=self.student_name, width=30)
        student_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))

        # Book Selection
        ttk.Label(form_frame, text="Book:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.book_var = tk.StringVar()
        self.book_combobox = ttk.Combobox(form_frame, textvariable=self.book_var,
                                          state="readonly", width=27)
        self.book_combobox.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=8, padx=(10, 0))

        # Borrow Date
        ttk.Label(form_frame, text="Borrow Date:").grid(row=2, column=0, sticky=tk.W, pady=8)

        if TK_CALENDAR_AVAILABLE:
            self.borrow_date = DateEntry(form_frame, width=18, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='mm/dd/y')
        else:
            self.borrow_date = ttk.Entry(form_frame, width=20)
            self.borrow_date.insert(0, datetime.now().strftime('%m/%d/%y'))
        self.borrow_date.grid(row=2, column=1, sticky=tk.W, pady=8, padx=(10, 0))

        # Return Date
        ttk.Label(form_frame, text="Return Date:").grid(row=3, column=0, sticky=tk.W, pady=8)

        if TK_CALENDAR_AVAILABLE:
            self.return_date = DateEntry(form_frame, width=18, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='mm/dd/y')
        else:
            self.return_date = ttk.Entry(form_frame, width=20)
            self.return_date.insert(0, datetime.now().strftime('%m/%d/%y'))
        self.return_date.grid(row=3, column=1, sticky=tk.W, pady=8, padx=(10, 0))

        # Configure column weights
        form_frame.columnconfigure(1, weight=1)

        # Buttons Frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # Add Button (Green)
        self.add_btn = tk.Button(button_frame, text="Add", command=self.add_borrow_record,
                                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                 width=10, cursor='hand2')
        self.add_btn.grid(row=0, column=0, padx=5, pady=5)

        # Delete Button (Red)
        self.delete_btn = tk.Button(button_frame, text="Delete", command=self.delete_record,
                                    bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                                    width=10, cursor='hand2')
        self.delete_btn.grid(row=0, column=1, padx=5, pady=5)

        # Clear Button (Grey)
        self.clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_form,
                                   bg='#757575', fg='white', font=('Arial', 10, 'bold'),
                                   width=10, cursor='hand2')
        self.clear_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def create_books_table(self, parent):
        """Create the borrowed books table and search functionality"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search Frame
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # Search Label and Entry
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.search_records)

        # Records count label
        self.records_label = ttk.Label(search_frame, text="Records: 0")
        self.records_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Table with Scrollbar
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Create Treeview with scrollbar
        columns = ('ID', 'Student', 'Book', 'Borrow Date', 'Return Date', 'Fine')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)

        # Define columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Student', text='Student')
        self.tree.heading('Book', text='Book')
        self.tree.heading('Borrow Date', text='Borrow Date')
        self.tree.heading('Return Date', text='Return Date')
        self.tree.heading('Fine', text='Fine (R)')

        # Configure column widths
        self.tree.column('ID', width=50, anchor=tk.CENTER)
        self.tree.column('Student', width=150)
        self.tree.column('Book', width=200)
        self.tree.column('Borrow Date', width=100, anchor=tk.CENTER)
        self.tree.column('Return Date', width=100, anchor=tk.CENTER)
        self.tree.column('Fine', width=80, anchor=tk.CENTER)

        # Create scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Configure treeview style for colored header and rows
        self.configure_treeview_style()

    def configure_treeview_style(self):
        """Configure the treeview style for colored header and row highlighting"""
        style = ttk.Style()
        style.theme_use('default')  # Use default theme for better customization

        # Configure heading style
        style.configure("Treeview.Heading",
                        background="#2196F3",
                        foreground="white",
                        font=('Arial', 10, 'bold'))

        # Create a custom tag for overdue records
        self.tree.tag_configure('overdue', background='#ffcccc')

    def get_date_from_widget(self, widget):
        """Get date from widget whether it's DateEntry or regular Entry"""
        if TK_CALENDAR_AVAILABLE and isinstance(widget, DateEntry):
            return widget.get_date().strftime('%m/%d/%y')
        else:
            return widget.get()

    def refresh_books_combobox(self):
        """Refresh the books combobox with available books"""
        self.cursor.execute('''
            SELECT id, title FROM books 
            WHERE quantity > 0 
            ORDER BY title
        ''')
        books = self.cursor.fetchall()

        # Store book data for reference
        self.books_dict = {title: book_id for book_id, title in books}

        # Update combobox
        self.book_combobox['values'] = [title for _, title in books]

        if books:
            self.book_combobox.set(books[0][1])
        else:
            self.book_var.set('')

    def refresh_table(self):
        """Refresh the table with current data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and display data
        self.cursor.execute('''
            SELECT bb.id, bb.student_name, b.title, bb.borrow_date, bb.return_date, bb.fine
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            ORDER BY bb.id
        ''')

        records = self.cursor.fetchall()

        # Insert data into treeview
        for record in records:
            item_id = self.tree.insert('', 'end', values=record)
            # Highlight rows with fine > 0
            if record[5] > 0:
                self.tree.item(item_id, tags=('overdue',))

        # Update records count
        self.records_label.config(text=f"Records: {len(records)}")

    def search_records(self, event=None):
        """Filter table based on search text"""
        search_text = self.search_var.get().lower()

        # Clear current selection
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and filter data
        self.cursor.execute('''
            SELECT bb.id, bb.student_name, b.title, bb.borrow_date, bb.return_date, bb.fine
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            WHERE LOWER(bb.student_name) LIKE ? OR LOWER(b.title) LIKE ?
            ORDER BY bb.id
        ''', (f'%{search_text}%', f'%{search_text}%'))

        records = self.cursor.fetchall()

        # Insert filtered data
        for record in records:
            item_id = self.tree.insert('', 'end', values=record)
            if record[5] > 0:
                self.tree.item(item_id, tags=('overdue',))

        # Update records count
        self.records_label.config(text=f"Records: {len(records)}")

    def calculate_fine(self, return_date_str):
        """Calculate fine based on return date (R5 per day)"""
        try:
            return_date = datetime.strptime(return_date_str, '%m/%d/%y')
            today = datetime.now()

            if return_date < today:
                days_late = (today - return_date).days
                return days_late * 5.0
            else:
                return 0.0
        except ValueError:
            return 0.0

    def validate_date(self, date_str):
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%m/%d/%y')
            return True
        except ValueError:
            return False

    def add_borrow_record(self):
        """Add a new borrow record"""
        try:
            # Validate inputs
            student_name = self.student_name.get().strip()
            book_title = self.book_var.get()

            if not student_name:
                messagebox.showerror("Error", "Please enter student name")
                return

            if not book_title:
                messagebox.showerror("Error", "Please select a book")
                return

            # Get book ID
            book_id = self.books_dict.get(book_title)
            if not book_id:
                messagebox.showerror("Error", "Invalid book selection")
                return

            # Get dates
            borrow_date = self.get_date_from_widget(self.borrow_date)
            return_date = self.get_date_from_widget(self.return_date)

            # Validate date formats
            if not self.validate_date(borrow_date):
                messagebox.showerror("Error", "Invalid borrow date format. Use MM/DD/YY")
                return

            if not self.validate_date(return_date):
                messagebox.showerror("Error", "Invalid return date format. Use MM/DD/YY")
                return

            # Validate dates
            borrow_dt = datetime.strptime(borrow_date, '%m/%d/%y')
            return_dt = datetime.strptime(return_date, '%m/%d/%y')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            if borrow_dt < today:
                messagebox.showerror("Error", "Borrow date cannot be in the past")
                return

            if return_dt < borrow_dt:
                messagebox.showerror("Error", "Return date cannot be before borrow date")
                return

            # Calculate fine
            fine = self.calculate_fine(return_date)

            # Insert record
            self.cursor.execute('''
                INSERT INTO borrowed_books (student_name, book_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_name, book_id, borrow_date, return_date, fine))

            # Update book quantity
            self.cursor.execute('''
                UPDATE books SET quantity = quantity - 1 WHERE id = ?
            ''', (book_id,))

            self.conn.commit()

            # Refresh UI
            self.refresh_books_combobox()
            self.refresh_table()
            self.clear_form()

            messagebox.showinfo("Success", "Book borrowed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Error adding record: {str(e)}")

    def delete_record(self):
        """Delete selected record"""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a record to delete")
                return

            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                return

            # Get record details
            item = self.tree.item(selected[0])
            record_id = item['values'][0]
            book_title = item['values'][2]

            # Get book ID
            self.cursor.execute("SELECT id FROM books WHERE title = ?", (book_title,))
            book_result = self.cursor.fetchone()

            if book_result:
                book_id = book_result[0]

                # Delete record
                self.cursor.execute("DELETE FROM borrowed_books WHERE id = ?", (record_id,))

                # Update book quantity
                self.cursor.execute('''
                    UPDATE books SET quantity = quantity + 1 WHERE id = ?
                ''', (book_id,))

                self.conn.commit()

                # Refresh UI
                self.refresh_books_combobox()
                self.refresh_table()

                messagebox.showinfo("Success", "Record deleted successfully!")
            else:
                messagebox.showerror("Error", "Book not found")

        except Exception as e:
            messagebox.showerror("Error", f"Error deleting record: {str(e)}")

    def clear_form(self):
        """Clear the form and reset to defaults"""
        self.student_name.set("")
        self.book_var.set("")

        # Reset dates to today
        today_str = datetime.now().strftime('%m/%d/%y')
        if TK_CALENDAR_AVAILABLE:
            today = datetime.now()
            self.borrow_date.set_date(today)
            self.return_date.set_date(today)
        else:
            self.borrow_date.delete(0, tk.END)
            self.borrow_date.insert(0, today_str)
            self.return_date.delete(0, tk.END)
            self.return_date.insert(0, today_str)

        # Clear tree selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def on_tree_select(self, event):
        """Handle treeview selection"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']

            # Populate form with selected record
            self.student_name.set(values[1])
            self.book_var.set(values[2])

            # Set dates
            try:
                if TK_CALENDAR_AVAILABLE:
                    borrow_dt = datetime.strptime(values[3], '%m/%d/%y')
                    return_dt = datetime.strptime(values[4], '%m/%d/%y')
                    self.borrow_date.set_date(borrow_dt)
                    self.return_date.set_date(return_dt)
                else:
                    self.borrow_date.delete(0, tk.END)
                    self.borrow_date.insert(0, values[3])
                    self.return_date.delete(0, tk.END)
                    self.return_date.insert(0, values[4])
            except ValueError:
                pass


def main():
    root = tk.Tk()
    app = LibraryManagementApp(root)

    # Handle window close
    def on_closing():
        if hasattr(app, 'conn'):
            app.conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()