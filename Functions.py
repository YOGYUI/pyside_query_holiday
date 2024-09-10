import requests
import pandas as pd
from urllib import parse
from datetime import datetime
import xml.etree.ElementTree as ET
from typing import List, Dict


def query_holidays_dataframe(year: int, api_key: str) -> pd.DataFrame:
    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    api_key_decode = parse.unquote(api_key)

    params = {
        "ServiceKey": api_key_decode,
        "solYear": year,
        "numOfRows": 100
    }

    response = requests.get(url, params=params)
    items: List[Dict[str, datetime]] = list()
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        node_header = root.find('header')
        if node_header is None:
            raise ValueError('<header> tag is not exist')
        node_result_code = node_header.find('resultCode')
        if node_result_code is None:
            raise ValueError('<resultCode> tag is not exist')
        node_result_msg = node_header.find('resultMsg')
        if node_result_msg is None:
            raise ValueError('<resultMsg> tag is not exit')
        result_code = int(node_result_code.text)
        if result_code != 0:
            raise ValueError(f'request error (code={result_code}, msg={node_result_msg.text}')

        node_body = root.find('body')
        if node_body is None:
            raise ValueError('<body> tag is not exist')
        node_items = node_body.find('items')
        if node_items is None:
            raise ValueError('<items> tag is not exist')
        for child in node_items.findall('item'):
            node_datename = child.find('dateName')
            node_locdate = child.find('locdate')
            if node_datename is None:
                raise ValueError('<dateName> tag is not exist')
            if node_locdate is None:
                raise ValueError('<locdate> tag is not exist')
            items.append({
                "이름": node_datename.text.strip(),
                "날짜": datetime.strptime(node_locdate.text.strip(), '%Y%m%d')
            })
        return pd.DataFrame(items)
    else:
        raise ValueError(f'response error (status code={response.status_code})')
