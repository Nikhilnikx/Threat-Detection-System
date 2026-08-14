"""
detector/parser.py

Parses uploaded security logs into normalized dictionaries.

Supports:
1. CSV files
2. key=value security logs
3. Apache/syslog style logs
4. Generic space separated logs

Never drops raw data.
"""


import csv
import io
import re
from datetime import datetime



_TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%d/%b/%Y:%H:%M:%S %z",
    "%b %d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
]


_IP_RE = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
)



# key=value log format
# timestamp=2026-08-14 01:10:00,source_ip=10.0.0.55,...
_KEY_VALUE_RE = re.compile(
    r"(\w+)=([^,]+)"
)



# Apache format
_APACHE_RE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<ts>[^\]]+)\]\s+'
    r'"(?P<action>[^"]*)"\s+(?P<status>\d{3})'
)



# Generic format
_GENERIC_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})\s+'
    r'(?P<ip>\S+)\s+(?P<user>\S+)\s+(?P<action>\S+)\s+(?P<status>\S+)'
)




def _try_parse_timestamp(value):

    if not value:
        return None


    value = value.strip()


    for fmt in _TIMESTAMP_FORMATS:

        try:
            return datetime.strptime(
                value,
                fmt
            )

        except ValueError:
            continue


    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except ValueError:

        return None






def parse_csv(file_bytes):

    text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )


    reader = csv.DictReader(
        io.StringIO(text)
    )


    entries = []


    for row in reader:


        normalized = {
            k.lower().strip(): v
            for k, v in row.items()
            if k
        }


        entries.append({

            "timestamp":
                _try_parse_timestamp(
                    normalized.get(
                        "timestamp",
                        ""
                    )
                ),


            "source_ip":
                normalized.get(
                    "source_ip"
                )
                or normalized.get(
                    "ip"
                ),


            "username":
                normalized.get(
                    "username"
                )
                or normalized.get(
                    "user"
                ),


            "action":
                normalized.get(
                    "action"
                )
                or normalized.get(
                    "event"
                ),


            "status":
                normalized.get(
                    "status"
                ),


            "raw_line":
                ",".join(
                    f"{k}={v}"
                    for k,v in row.items()
                ),


            "parsed":
                True

        })


    return entries








def parse_key_value_line(line):

    fields = dict(
        _KEY_VALUE_RE.findall(line)
    )


    if not fields:

        return None



    return {


        "timestamp":
            _try_parse_timestamp(
                fields.get(
                    "timestamp"
                )
            ),



        "source_ip":
            fields.get(
                "source_ip"
            )
            or fields.get(
                "ip"
            ),



        "username":
            fields.get(
                "username"
            )
            or fields.get(
                "user"
            ),



        "action":
            fields.get(
                "action"
            )
            or fields.get(
                "event"
            ),



        "status":
            fields.get(
                "status"
            ),



        "raw_line":
            line,



        "parsed":
            True

    }









def parse_text_line(line):

    line = line.strip()


    if not line:

        return None



    # 1. key=value logs
    result = parse_key_value_line(
        line
    )


    if result:

        return result




    # 2. Apache / syslog
    for pattern in (
        _APACHE_RE,
        _GENERIC_RE
    ):


        match = pattern.match(
            line
        )


        if match:


            data = match.groupdict()


            return {


                "timestamp":
                    _try_parse_timestamp(
                        data.get(
                            "ts"
                        )
                    ),


                "source_ip":
                    data.get(
                        "ip"
                    ),


                "username":
                    data.get(
                        "user"
                    ),


                "action":
                    data.get(
                        "action"
                    ),


                "status":
                    data.get(
                        "status"
                    ),


                "raw_line":
                    line,


                "parsed":
                    True

            }




    # 3. fallback
    ip = _IP_RE.search(
        line
    )


    return {


        "timestamp":
            None,


        "source_ip":
            ip.group(0)
            if ip
            else None,


        "username":
            None,


        "action":
            None,


        "status":
            None,


        "raw_line":
            line,


        "parsed":
            False

    }








def parse_text(file_bytes):

    text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )


    entries = []


    for line in text.splitlines():

        item = parse_text_line(
            line
        )


        if item:

            entries.append(
                item
            )


    return entries








def parse_file(filename, file_bytes):

    ext = (
        filename.rsplit(
            ".",
            1
        )[-1]
        .lower()
        if "."
        in filename
        else ""
    )


    if ext == "csv":

        return parse_csv(
            file_bytes
        )


    return parse_text(
        file_bytes
    )