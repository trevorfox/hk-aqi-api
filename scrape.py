#!usr/bin/pyhton

import aqi
import requests
import pytz
import calendar
from datetime import datetime
from bs4 import BeautifulSoup

def air_quality(location_code):
  loc_info = location_info(location_code)
  page_soup = get_soup(loc_info[1])
  data = prepare_data(page_soup, location_code, loc_info)
  return data

def location_info(location_code):
  location_code = location_code.replace("_","-")
  info_directory = {
    'central-western' : ('Central/Western', '45fd.html?stationid=80'),
    'eastern' : ('Eastern', 'e1a6.html?stationid=73'),
    'kwun-tong' : ('Kwung Tong', 'fb71.html?stationid=74'),
    'sham-shui-po' : ('Sham Shui Pa', 'db46.html?stationid=66'),
    'kwai-chung' : ('Kwai Chung', '30e8.html?stationid=72'),
    'tsuen-wan' : ('Tsuen Wan', '228e.html?stationid=77'),
    'yuen-long' : ('Yuen Long', '1f2c.html?stationid=70'),
    'tuen-mun' : ('Tuen Mun', '537c.html?stationid=82'),
    'tung-chung' : ('Tung Chung', 'f322.html?stationid=78'),
    'tai-po' : ('Tai Po', '6e9c.html?stationid=69'),
    'sha-tin' : ('Sha Tin', '2c5f.html?stationid=75'),
    'tap-mun' : ('Tap Mun', '233a.html?stationid=76'),
    'causeway-bay' : ('Causeway Bay', '5ca5.html?stationid=71'),
    'central' : ('Central', 'f9dd.html?stationid=79'),
    'mong-kok' : ('Mong Kok','9c57.html?stationid=81')
    }

  loc = info_directory[location_code]
  base_url = "http://www.aqhi.gov.hk/en/aqhi/past-24-hours-pollutant-concentration"
  location_info = (loc[0], base_url + loc[1])
  return location_info

def get_soup(full_url):

  headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2286.0 Safari/537.36",
  }
  response = requests.get(full_url, headers=headers)
  html = response.text
  soup = BeautifulSoup(html)
  return soup

def health_range(current_aqi):
  if current_aqi == 0:
    rng = "Unavailable"
  elif current_aqi > 0 and current_aqi <= 50:
    rng = "Good"
  elif current_aqi > 50 and current_aqi <= 100:
    rng ="Moderate"
  elif current_aqi > 100 and current_aqi <= 150:
    rng ="Unhealthy for Sensitive Groups"
  elif current_aqi > 150 and current_aqi <= 200:
    rng ="Unhealthy"
  elif current_aqi > 200 and current_aqi < 300:
    rng ="Very Unhealthy"
  elif current_aqi > 300:
    rng ="Hazardous"
  return rng

def decode_date(date_string):
  dmy = date_string.split()[0].split("-")
  year = int(dmy[0].strip())
  month = int(dmy[1].strip())
  day = int(dmy[2].strip())
  hour = int(date_string.split()[1].split(":")[0])
  date = datetime(year,month,day,hour)
  hk_tz = pytz.timezone('Asia/Hong_Kong')
  # date obj localized to HK
  hk_date = hk_tz.localize(date)
  # utc timestamp localized to HK
  hk_timestamp = calendar.timegm(hk_date.utctimetuple())
  # MySQL TIMESTAMP formatted string
  hk_sql_timestamp = hk_date.strftime('%Y-%m-%d %H:%M:%S')
  return hk_date, hk_sql_timestamp, hk_timestamp

def prepare_data(soup, location_code, location_info):

  rows = soup.select("#cltNormal table tr")
  ths = rows[0].find_all("th")
  headings = [heading.text.encode("utf-8").strip().lower().replace(" ","_").replace(".","") for heading in ths]
  tds = rows[1].find_all("td")
  air_data = []

  for i, row in enumerate(rows[1:]):
    tds = row.find_all("td")
    # parse dates from ugly unicode table data
    date_string = tds[0].text
    hk_sql_timestamp = decode_date(date_string)[1]
    # replace scraped date value with SQL timestamp
    values = [hk_sql_timestamp]

    # type check table values.
    for td in tds[1:]:
      value = td.text
      try:
        value = float(value)
      except ValueError:
        # there may be a better value to use ???
        value = 0
      values.append(value)

    # create dict with row values to normalized header keys
    air_data.append( dict(zip(headings, values)) )

    # calculate aqi
    if (air_data[i]["pm25"]) != "-":
      calculated_aqi = int(aqi.to_aqi([ (aqi.POLLUTANT_PM25, air_data[i]["pm25"]) ]))
    else:
      calculated_aqi = "0"

    # append additional info to each hours record
    air_data[i]["aqi"] = calculated_aqi
    air_data[i]["location"] = location_info[0]
    air_data[i]["health_range"] = health_range(calculated_aqi)
    #air_data[i]["loc_code"] = location

  # dict with meta values and 24 hour records in 'data' list
  data = {
    "data": air_data,
    "timestamp": calendar.timegm(datetime.now().utctimetuple()),
    "location": location_info[0],
    "raw_source": location_info[1],
    "location_code": location_code
    }

  return data

if __name__ == "__main__":
  print air_quality("central-western")
