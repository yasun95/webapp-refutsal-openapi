import pymysql

conn = pymysql.connect(
    host='3.38.252.50', 
    port=54726, user='test', 
    password='1234', 
    db='sql_test', 
    charset='utf8')

cursor = conn.cursor()
try:
    with conn.cursor() as cursor:
        # Insert data into table
        sql = "INSERT INTO first_table (time, team) VALUES (%s, %s)"
        cursor.execute(sql, ('777', '888'))
        
        # Commit the changes to the database
        conn.commit()

        #show data
        cursor.execute("SELECT * FROM first_table")
        result = cursor.fetchall()
        print(result)

finally:
    conn.close()
