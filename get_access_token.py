import urllib

import pandas as pd

from urllib.request import quote

pd.set_option('mode.chained_assignment', None)

# client_id 为官网获取的AK， client_secret 为官网获取的SK
print("请输入client_id：")
client_id=str(input())
#client_id="qZ1yhVqsWFfvhy59HrX1MFXW"
print("请输入client_secret：")
client_secret=str(input())
#client_secret="Y263oKP6PY1n2O8DeQQ7Otgu5bin9kGz"
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+str(client_id)+'&client_secret='+str(client_secret)
request = urllib.request.urlopen(host)
# request.add_header('Content-Type', 'application/json; charset=UTF-8')
# response = urllib.request.urlopen(request)
content = request.read()
if (content):
    print("access_token:")
    print(eval(str(content,encoding="utf-8"))['access_token'])  # content即为access_token