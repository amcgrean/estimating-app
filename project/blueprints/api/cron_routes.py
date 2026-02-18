from flask import Blueprint, request, current_app, jsonify, abort
from project.import_data import import_data
import os

api = Blueprint('api', __name__)

@api.route('/cron/sync-erp', methods=['GET', 'POST'])
def sync_erp():
    # Security: Verify CRON_SECRET header to ensure request comes from Vercel Crons
    auth_header = request.headers.get('Authorization')
    cron_secret = os.environ.get('CRON_SECRET')
    
    if not cron_secret:
        current_app.logger.error("CRON_SECRET not configured in environment.")
        return jsonify({"error": "Cron secret not configured"}), 500
        
    if auth_header != f"Bearer {cron_secret}":
        current_app.logger.warning(f"Unauthorized cron attempt from {request.remote_addr}")
        abort(401)

    try:
        current_app.logger.info("Starting scheduled ERP Sync...")
        import_data()
        current_app.logger.info("Scheduled ERP Sync completed successfully.")
        return jsonify({"status": "success", "message": "ERP Sync completed"}), 200
    except Exception as e:
        current_app.logger.error(f"Scheduled ERP Sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
