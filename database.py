#!usr/bin/python

import MySQLdb as db
import sys

class Database():

    def __init__(self,config):
        pass

    def insert_records(self,records):
      try:
        print config["mysql"]['host'], config["mysql"]['user'], config["mysql"]['passwd'], config["mysql"]['db']
        con = db.connect(host=config["mysql"]['host'], user=config["mysql"]['user'], passwd=config["mysql"]['passwd'], db=config["mysql"]['db']);
        cur = con.cursor()
        sql_statement = """INSERT INTO air_quality_test(date_time, location, no2, o3, so2, co, pm10, pm25, aqi, health_range, loc_code)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        print sql_statement
        print records

        cur.executemany(sql_statement, records)
        con.commit()

      except db.Error, e:

          print "Error %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)

      finally:

        if con:
          con.close()

    def get_last_date(self):
      try:
        con = db.connect(host=config["mysql"]['host'], user=config["mysql"]['user'], passwd=config["mysql"]['passwd'], db=config["mysql"]['db']);
        cur = con.cursor()
        sql_statement = """SELECT date_time FROM air_quality_test WHERE loc_code ='central-western' ORDER BY date_time DESC LIMIT 1;"""
        print sql_statement
        cur.execute(sql_statement)
        date = cur.fetchone()[0]

      except db.Error, e:
          print "Error %d: %s" % (e.args[0],e.args[1])
          sys.exit(1)

      finally:
        return date
        if con:
          con.close()

if __name__ == "__main__":
    print Datebase.get_last_date()
