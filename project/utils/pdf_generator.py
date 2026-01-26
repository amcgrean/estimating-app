
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from project.models import Bid, BidValue, BidField
from project import db

def generate_spec_sheet(bid_id):
    """
    Generates a 4-column PDF Spec Sheet for the given bid_id.
    Returns: BytesIO object containing the PDF.
    """
    bid = Bid.query.get(bid_id)
    if not bid:
        return None

    # Fetch all fields and values
    # Efficient query: Join BidValue and BidField
    values = db.session.query(BidValue, BidField)\
        .join(BidField, BidValue.field_id == BidField.id)\
        .filter(BidValue.bid_id == bid_id)\
        .filter(BidField.is_active == True)\
        .order_by(BidField.category, BidField.sort_order)\
        .all()

    # Organize by Category
    data_by_category = {}
    
    # Define category order (optional, could be fixed or dynamic)
    # Common categories first
    priority_categories = ['Framing', 'Siding', 'Shingles', 'Windows', 'Doors', 'Deck', 'Trim']
    
    # Group data
    for val, field in values:
        cat = field.category
        if cat not in data_by_category:
            data_by_category[cat] = []
        data_by_category[cat].append((field.name, val.value))

    # Determine final order of categories
    sorted_categories = []
    # Add priority ones if they exist
    for cat in priority_categories:
        if cat in data_by_category:
            sorted_categories.append(cat)
    # Add others
    for cat in data_by_category:
        if cat not in sorted_categories:
            sorted_categories.append(cat)

    # --- PDF Generation ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()

    # Header Style
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    normal_style = styles['Normal']
    normal_style.fontSize = 9
    
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold')
    value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontSize=8)

    # Logo/Header Info
    # (Placeholder for Logo if needed later)
    elements.append(Paragraph(f"Bid Specification: {bid.project_name}", title_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Meta Info Grid
    meta_data = [
        [f"Customer: {bid.customer.name if bid.customer else 'N/A'}", f"Date: {bid.log_date.strftime('%Y-%m-%d') if bid.log_date else 'N/A'}"],
        [f"Estimator: {bid.estimator.estimatorName if bid.estimator else 'N/A'}", f"Status: {bid.status}"]
    ]
    meta_table = Table(meta_data, colWidths=[3.5*inch, 3.5*inch])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.2*inch))

    # Dynamic Content
    for cat in sorted_categories:
        # Category Header
        elements.append(Paragraph(cat, styles['Heading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Prepare 4-Column Data (Label, Value, Label, Value)
        # Flatten list pairs
        cat_items = data_by_category[cat] # [(Label, Value), (Label, Value)...]
        
        table_data = []
        row = []
        
        for label, value in cat_items:
            # Handle empty values? Show them to prove checked? Yes.
            if value is None: value = ""
            
            # Use Paragraphs for wrapping text
            p_label = Paragraph(f"{label}:", label_style)
            p_value = Paragraph(str(value), value_style)
            
            row.append(p_label)
            row.append(p_value)
            
            if len(row) == 4: # 2 items (Label+Value * 2)
                table_data.append(row)
                row = []
                
        # Handle leftover row
        if row:
            # Pad with empty cells
            while len(row) < 4:
                row.append("")
            table_data.append(row)

        if not table_data:
            elements.append(Paragraph("No specifications recorded.", normal_style))
        else:
            # Create Table
            # Col Widths: We have 7.5 inches usable width (8.5 - 0.5 - 0.5)
            # 4 columns: Label(1.2) Value(2.55) | Label(1.2) Value(2.55) -> Total 7.5
            # Adjusting: Label should be smaller.
            # L: 1.0, V: 2.75, L: 1.0, V: 2.75 = 7.5
            col_widths = [1.1*inch, 2.65*inch, 1.1*inch, 2.65*inch]
            
            t = Table(table_data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 2),
                # ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), # Optional grid
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            elements.append(t)
            
        elements.append(Spacer(1, 0.15*inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer
