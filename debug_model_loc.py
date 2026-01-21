import sys
import os
sys.path.append(os.getcwd())
from project import create_app
app = create_app()
with app.app_context():
    from project.models import BidField
    import inspect
    print(inspect.getsourcefile(BidField))
    lines, start_line = inspect.getsourcelines(BidField)
    print(f"Start Class Line: {start_line}")
