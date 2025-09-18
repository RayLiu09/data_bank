from datetime import datetime, timedelta


def convert_utc_to_local(utc: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    utc_time = datetime.strptime(utc, format)
    return (utc_time + timedelta(hours=8)).strftime(format)