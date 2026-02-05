
from project import create_app, db
from project.models import Design

app = create_app()
with app.app_context():
    designs = Design.query.order_by(Design.id.desc()).limit(10).all()
    for d in designs:
        print(f"ID: {d.id}, Plan Number: {d.planNumber}, Date: {d.log_date}")
