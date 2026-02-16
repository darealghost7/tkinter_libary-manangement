# tkinter_libary-manangement
Library Management System - Borrowing Module
This module provides a comprehensive book borrowing management interface for a library system. It allows librarians to track book loans, manage returns, and calculate fines for overdue books.

Features
📚 Book Borrowing Form
Student Name Entry - Input field for borrower's name

Book Selection - Dropdown combobox showing only available books (quantity > 0)

Date Selection -

Automatic date picker (if tkcalendar is installed)

Manual date entry fallback with default today's date

Date Validation - Prevents past dates and ensures return date is after borrow date

📊 Data Table Display
Searchable Records - Real-time filtering by student name or book title

Visual Indicators - Overdue records highlighted in light red (#ffcccc)

Fine Calculation - Automatic fine calculation (R5 per day for overdue books)

Record Counter - Shows total/filtered record count

🎨 User Interface
Split Layout - Form on left, table on right

Color-coded Buttons:

🟢 Add - Green, adds new borrowing record

🔴 Delete - Red, removes selected record

⚪ Clear - Grey, resets form fields

Professional Styling - Blue table header, consistent padding and spacing

🔧 Database Integration
Automatic Stock Management - Decreases book quantity when borrowed, increases when returned

Real-time Updates - Book combobox refreshes after each transaction

Data Persistence - All records stored in SQLite database

Code Structure
Main Components
create_borrow_form() - Builds the input form with all fields and buttons

create_books_table() - Sets up the searchable data table with scrollbar

refresh_books_combobox() - Updates available books from database

add_borrow_record() - Validates input and inserts new borrowing record

delete_record() - Removes selected record and updates book quantity

calculate_fine() - Computes fines for overdue books

search_records() - Filters table based on search input


Error Handling
The module includes comprehensive error handling:

Input validation for empty fields

Date format verification

Database integrity checks

User confirmation for deletions

Graceful fallback if tkcalendar is not available

Visual Features
Responsive Layout - Form maintains fixed width, table expands with window

Visual Feedback - Buttons change cursor on hover

Color Coding - Overdue books stand out with red background

Professional Appearance - Consistent spacing and alignment

This module provides a complete, user-friendly interface for managing book borrowing operations in a library setting, with robust data validation and real-time updates.
