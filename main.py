import customtkinter as ctk
from tkinter import filedialog
from pdf2image import convert_from_path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

class PDFProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF to Scanned PDF")
        self.geometry("600x400")

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Input folder selection
        self.input_label = ctk.CTkLabel(self, text="Input Folder:")
        self.input_label.pack(pady=10)

        self.input_entry = ctk.CTkEntry(self, width=400)
        self.input_entry.pack(pady=5, padx=10)

        self.browse_input_button = ctk.CTkButton(self, text="Browse", command=self.browse_input_folder)
        self.browse_input_button.pack(pady=5)

        # Process Button
        self.process_button = ctk.CTkButton(self, text="Process PDFs", command=self.process_folder)
        self.process_button.pack(pady=20)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.pack(pady=10)

    def browse_input_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_entry.delete(0, ctk.END)
            self.input_entry.insert(0, folder_path)

    def pdf_to_images(self, pdf_path, output_folder):
        print(f"Processing {pdf_path}...")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        images = convert_from_path(pdf_path)

        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f'page_{i+1}.png')
            image.save(image_path, 'PNG')

    def images_to_pdf(self, images_folder, output_pdf_path):
        image_files = [os.path.join(images_folder, img) for img in sorted(os.listdir(images_folder)) if img.endswith('.png')]

        if not image_files:
            raise ValueError("No images found in the specified folder.")

        with open(output_pdf_path, "wb") as f:
            c = canvas.Canvas(f, pagesize=letter)
            for image_file in image_files:
                c.drawImage(image_file, 0, 0, width=letter[0], height=letter[1])
                c.showPage()
            c.save()

    def process_folder(self):
        input_folder = self.input_entry.get()
        if not input_folder:
            self.status_label.config(text="Please specify an input folder.")
            return

        output_folder = f"{input_folder}_scanned"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]

        if not pdf_files:
            self.status_label.config(text="No PDF files found in the specified folder.")
            return

        for pdf_file in pdf_files:
            input_pdf_path = os.path.join(input_folder, pdf_file)
            output_pdf_path = os.path.join(output_folder, f'{pdf_file}')
            temp_folder = os.path.join(output_folder, f'{os.path.splitext(pdf_file)[0]}_images')

            try:
                self.pdf_to_images(input_pdf_path, temp_folder)
                self.images_to_pdf(temp_folder, output_pdf_path)

                # Clean up temporary image files
                for img_file in os.listdir(temp_folder):
                    os.remove(os.path.join(temp_folder, img_file))
                os.rmdir(temp_folder)

                # self.status_label.config(text=f"Processed {pdf_file} successfully.")
            except Exception as e:
                self.status_label.config(text=f"Error processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    app = PDFProcessorApp()
    app.mainloop()
