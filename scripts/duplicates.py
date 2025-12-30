import sqlite3
from datetime import datetime

def resolve_duplicates():
    conn = sqlite3.connect('/home/amcgrean/mysite/instance/bids.db')  # Adjust the path to your database
    cursor = conn.cursor()

    # Find duplicate email addresses
    cursor.execute('''
    SELECT email, COUNT(*)
    FROM user
    GROUP BY email
    HAVING COUNT(*) > 1
    ''')
    
    duplicates = cursor.fetchall()

    summary = {"merged": [], "deleted": []}

    for email, count in duplicates:
        cursor.execute('''
        SELECT id, username, email, password, usertype_id, estimatorID, sales_rep_id, user_branch_id, last_login, created_at, updated_at, is_active, is_admin, login_count
        FROM user
        WHERE email = ?
        ORDER BY created_at DESC, id DESC
        ''', (email,))
        
        records = cursor.fetchall()
        main_record = records[0]

        for record in records[1:]:
            main_record_id = main_record[0]
            duplicate_id = record[0]

            # Merge the records by keeping the most recent fields where applicable
            merged_record = {
                "username": main_record[1] if main_record[1] else record[1],
                "password": main_record[3] if main_record[3] else record[3],
                "usertype_id": main_record[4] if main_record[4] else record[4],
                "estimatorID": main_record[5] if main_record[5] else record[5],
                "sales_rep_id": main_record[6] if main_record[6] else record[6],
                "user_branch_id": main_record[7] if main_record[7] else record[7],
                "last_login": main_record[8] if main_record[8] else record[8],
                "created_at": main_record[9] if main_record[9] else record[9],
                "updated_at": main_record[10] if main_record[10] else record[10],
                "is_active": main_record[11] if main_record[11] else record[11],
                "is_admin": main_record[12] if main_record[12] else record[12],
                "login_count": main_record[13] if main_record[13] else record[13]
            }

            # Update the main record with merged data
            cursor.execute('''
            UPDATE user
            SET username = ?, password = ?, usertype_id = ?, estimatorID = ?, sales_rep_id = ?, user_branch_id = ?, last_login = ?, created_at = ?, updated_at = ?, is_active = ?, is_admin = ?, login_count = ?
            WHERE id = ?
            ''', (
                merged_record["username"], merged_record["password"], merged_record["usertype_id"], merged_record["estimatorID"], merged_record["sales_rep_id"], merged_record["user_branch_id"], merged_record["last_login"], merged_record["created_at"], merged_record["updated_at"], merged_record["is_active"], merged_record["is_admin"], merged_record["login_count"], main_record_id
            ))

            # Delete the duplicate record
            cursor.execute('DELETE FROM user WHERE id = ?', (duplicate_id,))
            summary["merged"].append({"kept": main_record_id, "merged": duplicate_id})

    conn.commit()
    conn.close()

    print("Summary of operations:")
    print("Merged Records:")
    for record in summary["merged"]:
        print(f"Kept ID {record['kept']} and merged ID {record['merged']}")

if __name__ == '__main__':
    resolve_duplicates()
