import pymysql

class Sql_connect:
    def __init__(self):
        self.pas = input('enter password:')
    
    def connect(self, db=None):
        conn = pymysql.connect(host='localhost',user='root',password=self.pas,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor, db=db)
        return conn
    
    def create_db(self, name):
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                c = 'CREATE DATABASE ' + name
                cursor.execute(c)
            conn.commit()
            print('Database "{}" created!'.format(name))
        finally:
            conn.close()

    def create_table(self, db, name, fields):
        conn = self.connect(db=db)
        try:
            with conn.cursor() as cursor:
                c = 'CREATE TABLE `{}` ({}) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin'.format(name,fields)
                cursor.execute(c)
            conn.commit()
            print('Table "{}" created!'.format(name))
        finally:
            conn.close()

    def insert_data(self, db, table, field, value):
        conn = self.connect(db=db)
        try:
            with conn.cursor() as cursor:
                c = 'INSERT INTO `{}`({}) VALUES ({})'.format(table, field, value)
                cursor.execute(c)
            conn.commit()
            print('Field {} augmented!'.format(field))
        finally:
            conn.close()

    def select(self, db, query):
        conn = self.connect(db=db)
        try:
            with conn.cursor() as cursor:
                c = 'SELECT' + query
                cursor.execute(c)
                result = cursor.fetchone()
            conn.commit()
            print(result)
        finally:
            conn.close() 
def main():
    sql = Sql_connect()
    db = 'Vk_Krasny_Yar_edu'
    try:
        sql.create_db(db)
    except Exception:
        pass
    # sql.create_table(db,'meta', '`id` BIGINT NOT NULL AUTO_INCREMENT, `sex` text, PRIMARY KEY (`id`)')
    # sql.create_table(db,'edu', '`id` BIGINT NOT NULL AUTO_INCREMENT, `education` BIGINT, PRIMARY KEY (`id`)')
    meta = [x.strip('\n') for x in open('.\\corpus\\meta.csv', encoding='utf-8').readlines()[1:]]
    for line in meta:
        line = line.split(',')
        try:
            sql.insert_data(db, 'meta', '`id`, `sex`', '`' + line[0] + '`' + ', ' + '`' + line[1] + '`')
            if line[3] != '0':
                sql.insert_data(db, 'edu', '`id`, `education`', '`' + line[0] + '`' + ', ' + '`' + line[3] + '`')
        except Exception:
            print('`' + line[0] + '`' + ', ' + '`' + line[1] + '`')
            raise
    sql.select(db, 'meta.*,edu.* FROM meta, edu WHERE meta.id = edu.id')


if __name__ == '__main__':
    main()      




