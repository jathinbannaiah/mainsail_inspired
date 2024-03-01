import PyPDF2

def split_pdf(input_pdf_path, output_folder, chunk_size):
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)   #PyPDF2.errors.DeprecationError: PdfFileReader is deprecated and was removed in PyPDF2 3.0.0. Use PdfReader instead

        # Get the total number of pages in the PDF
        total_pages = len(pdf_reader.pages)

        for start_page in range(0, total_pages, chunk_size):
            end_page = min(start_page + chunk_size, total_pages)

            # Create a new PDF writer for each chunk
            pdf_writer = PyPDF2.PdfWriter()

            # Add pages to the new PDF writer
            for page_num in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Save the chunk to a new PDF file
            output_pdf_path = f"{output_folder}/chunk_{start_page + 1}-{end_page}.pdf"
            with open(output_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            print(f"Chunk {start_page + 1}-{end_page} saved to {output_pdf_path}")

if __name__ == "__main__":
    input_pdf_path = "/home/j2002/Desktop/project doc/RTC6_Doc.Rev.1.0.21_en-US.pdf"
    output_folder = "/home/j2002/Desktop/project doc/RTC6_reduced_docs"
    chunk_size = 100  # Adjust this based on the desired number of pages per chunk

    split_pdf(input_pdf_path, output_folder, chunk_size)
