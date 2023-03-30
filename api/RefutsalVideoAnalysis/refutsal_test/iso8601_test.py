import datetime
import dateutil.parser
import pytz

print()

date=dateutil.parser.parse(str(datetime.datetime.now(tz=pytz.utc).isoformat()))

# Timezone을 설정
local_timezone = pytz.timezone('Asia/Seoul')

# Timezone에 따라서 새로운 date형식을 변경
local_date = date.replace(tzinfo=pytz.utc).astimezone(local_timezone)

# 출력
print(local_date.isoformat())