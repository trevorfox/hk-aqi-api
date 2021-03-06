#!usr/bin/python

from scrape import DateDecoder, air_quality, location_info, get_soup
from database import Database
from time import sleep
from config import config

database = Database(config)

list_of_locations = [
  'central-western',
  'eastern',
  'kwun-tong',
  'sham-shui-po',
  'kwai-chung',
  'tsuen-wan',
  'yuen-long',
  'tuen-mun',
  'tung-chung',
  'tai-po',
  'sha-tin',
  'tap-mun',
  'causeway-bay',
  'central',
  'mong-kok'
]

def gather_data(list_of_locations):
  sql_args = []
  for location in list_of_locations:
    air = air_quality(location)['data'][0]
    args_tup = (air['date_time'], air['location'], air['no2'], air['o3'], air['so2'], air['co'], air['pm10'], air['pm25'], air['aqi'], air['health_range'], location)
    sql_args.append( args_tup )
  return sql_args

def record_hour(records,trys):
  last_date =  database.get_last_date().strftime('%Y-%m-%d %H:%M:%S')
  soup = get_soup(location_info("central-western")[1])
  date = soup.select("#cltNormal table tbody tr td.H24C_ColDateTime")[0].text
  comp_date = str(DateDecoder(date, timezone='Asia/Hong_Kong').sqlTimestamp())
  print last_date
  print comp_date
  trys += 1

  # keep trying every five minutes for a 55 min
  if last_date == comp_date:
    print "TRIED %s TIMES" % (trys)
    if trys <= 11:
      print "THE SAME"
      # wait five minutes and try again
      sleep(300)
      record_hour(records,trys)
    else:
      print "NO UPDATE, ALL DONE"
  else:
    print "NOT SAME"
    database.insert_records(gather_data(list_of_locations))

if __name__ == "__main__":
  records = gather_data(list_of_locations)
  record_hour(records,0)
