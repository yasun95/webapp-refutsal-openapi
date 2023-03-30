import json
import pymysql

class SqlWriter:
    def __init__(self, host:str, port:int, user:str, password:str, db:str, uuid:str) -> None:
        """
        example)
        host='13.125.163.172', 
        port=51614, user='cv_module', 
        password='1234', 
        db='refutsal_test_db', 
        charset='utf8'
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        self.goal_tag_table = 'goal_tag'

        self.conn = pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password= self.password,
            db= self.db,
            charset= 'utf8'
        )

        self.uuid = uuid
        self.json_goal_tag = None
        
    def makeGoalTag(self, goal_tags:list) -> str:
        """
        goal_tags = [(team, min, sec),(team, min, sec)]
        """
        data = {}
        data['goal_tags'] = []
        for i in range(len(goal_tags)):
            data['goal_tags'].append({
                'id': i,
                'team': goal_tags[i][0],
                'min': goal_tags[i][1],
                'sec': goal_tags[i][2]
            })
        self.json_goal_tag = json.dumps(data, indent=4)
        return self.json_goal_tag

    def uploadTagDb(self, showdata:bool = False):
        cursor = self.conn
        try:
            with self.conn.cursor() as cursor:
                # Insert data into table
                sql = "INSERT INTO [table_name] (uuid, tag) VALUES (%s, %s)"
                sql = sql.replace("[table_name]", self.goal_tag_table)
                cursor.execute(sql, (self.uuid, self.json_goal_tag))
                
                # Commit the changes to the database
                self.conn.commit()

                if showdata:
                    cursor.execute("SELECT * FROM goal_tag")
                    result = cursor.fetchall()
                    print(result)

        finally:
            self.conn.close()


"""
test_tags = [(1, 3, 0), (0, 45, 10), (1, 60, 50), (0, 90, 45)]

sw = SqlWriter(
    host='13.125.163.172', 
    port=57790, user='cv_module', 
    password='1234', 
    db='refutsal_test_db',
    uuid='0x_test2_xxx'
    )

sw.makeJsonTag(test_tags)
sw.uploadTagDb()
print("success")
"""

