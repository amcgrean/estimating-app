
import sys
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("Error: Neither pypdf nor PyPDF2 is installed.")
        sys.exit(1)

def list_pdf_fields(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()
        if fields:
            with open('pdf_fields.txt', 'w') as f:
                for field_name, field_data in fields.items():
                    f.write(f"{field_name}\n")
            print("Fields written to pdf_fields.txt")
        else:
            print("No form fields found in the PDF.")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    list_pdf_fields('spec_sheet_template.pdf')
