import pymysql
conn = pymysql.connect(
    host="127.0.0.1",
    port=3307,
    user="skillgap_user",
    password="skillgap_pass",
    database="skillgap_db",
    charset="utf8mb4"
)
cursor = conn.cursor()
try:
    cursor.execute("INSERT INTO job_postings (title, company, industry) VALUES ('test', 'test', 'IT')")
    conn.commit()
    print("Insert IT success")
except Exception as e:
    print("Insert IT error:", e)
