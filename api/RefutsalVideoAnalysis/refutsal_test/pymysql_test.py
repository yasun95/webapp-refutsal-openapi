import pymysql

conn = pymysql.connect(
    host='3.38.252.50', 
    port=54726, user='test', 
    password='1234', 
    db='sql_test', 
    charset='utf8')
    
cursor = conn.cursor()
#cursor.execute("SHOW TABLES")
cursor.execute("SELECT * FROM first_table")
result = cursor.fetchall()

print (result)