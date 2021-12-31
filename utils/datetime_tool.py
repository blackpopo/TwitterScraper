from datetime import date, datetime, timedelta, time

def extract_date(word, connection):
    cursor = connection.cursor()
    cursor.execute("select  end_time, start_time, newest_created_at, oldest_created_at from log  where search_word = (?) limit 1 ", [word])
    row = cursor.fetchone() #無ければ Noneが返る。
    if row == None:
        scraping_date = date.today()
        start_time = datetime(year=scraping_date.year,  month=scraping_date.month, day=scraping_date.day, hour=0, minute=0, second=0)
        end_time = start_time + timedelta(days=1)
        oldest_create_at = start_time
        newest_create_at = end_time
        cursor.execute("insert into log (search_word, end_time, start_time, newest_created_at, oldest_created_at) values (?, ?, ?, ?, ?) ", [word, end_time, start_time, newest_create_at, oldest_create_at])
        return word, end_time, start_time, newest_create_at, oldest_create_at
    else:
        row = [datetime.fromisoformat(r) for r in row]
        return word, *row

def jst2utc_iso(_datetime):
    _datetime = _datetime - timedelta(hours=9)
    return _datetime.isoformat() + "Z"

def utc2jst_iso(_datetime):
    _datetime = datetime.fromisoformat(_datetime.replace('Z', ""))
    return _datetime + timedelta(hours=9)

