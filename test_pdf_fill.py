
import sys
PdfReader = None
PdfWriter = None
NameObject = None

print("Attempting to import pypdf...")
try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject
    print("Success: pypdf loaded.")
except ImportError as e:
    print(f"pypdf import failed: {e}")
    try:
        print("Attempting to import PyPDF2...")
        from PyPDF2 import PdfReader, PdfWriter
        from PyPDF2.generic import NameObject
        print("Success: PyPDF2 loaded.")
    except ImportError as e2:
        print(f"PyPDF2 import failed: {e2}")
        print("Error: Neither pypdf nor PyPDF2 is installed.")
        sys.exit(1)

if not NameObject:
    print("CRITICAL: NameObject not loaded!")
    sys.exit(1)

def fill_pdf(template_path, output_path, data_dict):
    try:
        reader = PdfReader(template_path)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
            
        # Copy AcroForm to writer root to ensure form fields are recognized
        if "/AcroForm" in reader.trailer["/Root"]:
            writer.root_object.update({
                NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]
            })
            
        # Fill fields using update_page_form_field_values
        # Note: If fields are distributed, we might need to call this for each page
        for page in writer.pages:
            writer.update_page_form_field_values(page, data_dict)
            
        with open(output_path, "wb") as output_stream:
            writer.write(output_stream)
            
        print(f"Successfully created {output_path}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error filling PDF: {e}")

if __name__ == "__main__":
    # Mock Data based on pdf_fields.txt
    mock_data = {
        'Customer.name': 'John Doe Construction',
        'Customer.email': 'john@example.com',
        'Customer.Phone': '555-0199',
        'Project': 'Test Project Alpha', # Might be a text field or parent?
        'Project.Address': '1234 Builder Lane, Coralville, IA',
        
        # Basement
        'basement.wallsize': '8 ft',
        'basement.elevation': '100.0',
        'basement.wallheight': '9 ft',
        'basement.finish': 'Finished',
        'basement.plate': '2x6 Treated',
        
        # Floor
        'floor.framing': 'I-Joists',
        'floor.sheeting': 'Advantech',
        'floor.adhesive': 'Subfloor Glue',
        
        # Exterior
        'ext.wall': '2x6',
        'ext.wall.size': '16 O.C.',
        
        # 1st Floor
        '1st.floor': 'Plywood',
        '1st.floor.walls': '2x4',
        
        # Wall
        'Wall.sheeting': 'OSB',
        
        # Roof
        'Roof.trusses': 'Standard Trusses',
        'Roof.sheeting': 'Zip System',
        
        # 2nd Floor
        '2nd.floor': 'Plywood',
        '2nd.floor.walls': '2x4',
        
        # Framing Notes
        'Framing.notes': 'Standard framing notes here.',
        
        # Siding
        'Siding.notes': 'Siding installation notes.',
        'Siding.type': 'Vinyl',
        'Panel.type': 'Board and Batten',
        'shake.type': 'Cedar Shake',
        'siding.trim': 'White Vinyl',
        'siding.trim.details': 'Standard Corner Posts',
        'siding.soffit': 'Vented Aluminum',
        
        # Shingle
        'shingle.notes': '30 Year Architectural',
        
        # Deck
        'decking.railing': 'Aluminum Pickets',
        'decking.stairs': 'Treated Lumber',
        'decking.landing': 'Concrete',
        'decking.type': 'Composite',
        'decking.notes': 'Deck details here.',
        
        # Window
        'window.grills': 'Between Glass',
        'window.jambs': 'Painteble',
        'window.brand': 'Andersen',
        'window.color': 'White',
        'window.type': 'Double Hung',
        'window notes': 'Window install instructions.',
        
        # Trim
        'trim.base': '3-1/4 Base',
        'trim.case': '2-1/4 Case',
        'trim.stairs': 'Oak Treads',
        'trim.doors': 'Solid Core',
        'trim.doorpanels': '2 Panel',
        'trim.hardware': 'Brushed Nickel',
        'trim.builtins': 'Mudroom Bench',
        'trim.builts': 'Bookshelves',
        'trim.builts.count': '2',
        'trim.allowance': '$5000',
        'trim.notes': 'Finish trim notes.',
        'salesman': 'Jim Sales',
        'install.notes': 'General installation guidelines.',
        
        # Checkboxes (using '/Yes' which is standard for checked in PDF)
        'framingcheck': '/Yes',
        'SidingCheck': '/Yes',
        'deckcheck': '/Yes',
        'shinglecheck': '/Yes',
        'trimcheck': '/Yes',
        'windowcheck': '/Yes',
        'exteriordoorscheck': '/Yes',
        
        # Install Checks
        'installfrontdoor': '/Yes',
        'installpatiodoor': '/Yes',
        'installAllDoors': '/Yes',
        'InstallAllWindows': '/Yes',
    }
    
    fill_pdf('spec_sheet_template.pdf', 'filled_spec_test.pdf', mock_data)
