from tkinter import *
from tkinter import ttk, filedialog
import fitz  # PyMuPDF
import threading

# Tkinter initialization
root = Tk()
root.geometry("650x800+400+100")
root.title("PDF Viewer")
root.configure(bg="white")

# Scrollable area setup
frame = Frame(root)
frame.pack(fill=BOTH, expand=1)

canvas = Canvas(frame, bg="white")
canvas.pack(side=LEFT, fill=BOTH, expand=1)

scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

content_frame = Frame(canvas)
canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Progress bar
progress_frame = Frame(root, bg="white")
progress_frame.pack(fill=X)
progress_label = Label(progress_frame, text="Loading PDF...", font=("Arial", 10), bg="white")
progress_label.pack(side=LEFT, padx=10)
progress_bar = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(side=LEFT, padx=10)

progress_frame.pack_forget()  # Initially hidden

# Global variables for navigation and zoom
current_page = 0
pdf_document = None
total_pages = 0
zoom_factor = 1.0

# Function to display a specific page
def display_page(page_number):
    global current_page, zoom_factor
    if 0 <= page_number < total_pages:
        current_page = page_number
        page = pdf_document[page_number]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
        temp_image = f"temp_page_{page_number}.png"
        pix.save(temp_image)

        # Clear existing content and show the new page
        for widget in content_frame.winfo_children():
            widget.destroy()

        img = PhotoImage(file=temp_image)
        label = Label(content_frame, image=img)
        label.image = img  # Keep a reference to avoid garbage collection
        label.pack(pady=10)

        # Update navigation label
        nav_label.config(text=f"Page {current_page + 1} of {total_pages}")

# Function to load a PDF file
def browseFiles():
    global pdf_document, total_pages, current_page, zoom_factor
    filename = filedialog.askopenfilename(
        initialdir=".", title="Select a File",
        filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
    )
    if filename:
        # Reset state
        zoom_factor = 1.0
        current_page = 0

        # Show progress bar
        progress_frame.pack(fill=X, pady=10)
        progress_bar['value'] = 0
        progress_label.config(text="Loading PDF...")

        def load_pdf():
            global pdf_document, total_pages
            pdf_document = fitz.open(filename)
            total_pages = len(pdf_document)

            # Display the first page
            display_page(0)

            # Hide progress bar
            progress_label.config(text="PDF Loaded!")
            progress_frame.after(2000, progress_frame.pack_forget)

        # Start loading in a thread
        threading.Thread(target=load_pdf).start()

# Navigation functions
def next_page():
    if current_page + 1 < total_pages:
        display_page(current_page + 1)

def previous_page():
    if current_page - 1 >= 0:
        display_page(current_page - 1)

# Zoom functions
def zoom_in():
    global zoom_factor
    zoom_factor += 0.2
    display_page(current_page)

def zoom_out():
    global zoom_factor
    if zoom_factor > 0.4:  # Prevent zooming out too much
        zoom_factor -= 0.2
        display_page(current_page)

# Buttons and Navigation Controls
Button(root, text="Open PDF", command=browseFiles, width=20, font=("Arial", 12), bd=4).pack(pady=10)
nav_frame = Frame(root, bg="white")
nav_frame.pack(pady=10)

Button(nav_frame, text="Previous", command=previous_page, width=10).pack(side=LEFT, padx=10)
nav_label = Label(nav_frame, text="Page 0 of 0", bg="white", font=("Arial", 10))
nav_label.pack(side=LEFT, padx=10)
Button(nav_frame, text="Next", command=next_page, width=10).pack(side=LEFT, padx=10)

zoom_frame = Frame(root, bg="white")
zoom_frame.pack(pady=10)

Button(zoom_frame, text="Zoom In", command=zoom_in, width=10).pack(side=LEFT, padx=10)
Button(zoom_frame, text="Zoom Out", command=zoom_out, width=10).pack(side=LEFT, padx=10)

root.mainloop()
