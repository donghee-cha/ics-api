from datetime import datetime, timedelta
from tzlocal import get_localzone
import pytz


def convertTimestampToUTC(timestamp):
    return datetime.fromtimestamp(timestamp)


def currentKorTimestamp():
    return datetime.now(pytz.timezone('Asia/Seoul')).timestamp()


def currentUTCTimestamp():
    return datetime.utcnow().timestamp()


def convertUTCtoLocal(utc_timestamp):
    utc_date = datetime.fromtimestamp(utc_timestamp / 1000)
    return utc_date.replace(tzinfo=pytz.timezone('UTC')).astimezone(get_localzone())


def convertLocaltoUTC(local_timestamp):
    utc_date = datetime.utcfromtimestamp(local_timestamp / 1000)
    return utc_date.timestamp() * 1000


def convertTimetoDate(time):
    utc_datetime = datetime.fromtimestamp(time / 1000)
    return utc_datetime.strftime("%Y-%m-%d") + " " + str(utc_datetime.hour) + "h " + str(utc_datetime.minute) + "m " + \
           str(utc_datetime.second) + "s"


def convertTimeToYYYYMMDDWithHyphen(time):
    utc_datetime = datetime.fromtimestamp(time)
    return utc_datetime.strftime("%Y-%m-%d")


def convertTimeToYYYYMMDDWithComma(time):
    utc_datetime = datetime.fromtimestamp(time)
    return utc_datetime.strftime("%Y.%m.%d")


def convertTimeToYMDHMSWithHyphen(time):
    utc_datetime = datetime.fromtimestamp(time)
    return utc_datetime.strftime("%Y-%m-%d %H:%M:%S")


def convertTimeToYYYYMMDDList(time):
    utc_datetime = datetime.fromtimestamp(time)
    yyyymmdd = utc_datetime.strftime("%Y-%m-%d")

    return {"year": yyyymmdd.split('-')[0], "month": yyyymmdd.split('-')[1], "day": yyyymmdd.split('-')[2]}


def convertTimeToYYYYMMDD(time):
    utc_datetime = datetime.fromtimestamp(time)
    return utc_datetime.strftime("%Y%m%d")


def convertTimeToDateTime(time):
    return datetime.fromtimestamp(time)


def plusDaysTimestamp(date_time, days):
    plus_datetime = date_time + timedelta(days)
    return plus_datetime
