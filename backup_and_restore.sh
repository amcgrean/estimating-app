#!/bin/bash

# Set your paths
INSTANCE_DIR="/home/amcgrean/mysite/instance"
DB_FILE="bids.db"
BACKUP_FILE="bids_backup.db"
DUMP_FILE="bids_dump.sql"

# Navigate to instance directory
cd $INSTANCE_DIR

# Create a backup of the current database
cp $DB_FILE $BACKUP_FILE

# Export the current database to a SQL dump
sqlite3 $DB_FILE .dump > $DUMP_FILE

# Remove the existing locked database
rm $DB_FILE

# Create a new database and import the SQL dump
sqlite3 $DB_FILE < $DUMP_FILE

# Verify the new database
INTEGRITY_CHECK=$(sqlite3 $DB_FILE "PRAGMA integrity_check;")
echo "Integrity Check Result: $INTEGRITY_CHECK"

if [ "$INTEGRITY_CHECK" == "ok" ]; then
    echo "Database restored successfully."
else
    echo "There was an issue with the database integrity. Please check manually."
fi

# Navigate back to the original directory
cd -

# Restart the Flask app
touch /var/www/amcgrean_pythonanywhere_com_wsgi.py

echo "Backup and restore process completed."
