import requests

cookies = {
    # 'cbc': 'T2gAJA93Cn1J3mq205_BNl-UTo3s6v9bhC0b40noFt5M8VrOgyPBmgWWiTaOIC09ixg=',
    # 'umdata_': 'T2gA8DGpJ8eRbsnQckW5lhnDg36vdgggVKbl3o9Ap3B6Nzh9QRLbXFPWEiidFGebvH0=',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'cbc=T2gAJA93Cn1J3mq205_BNl-UTo3s6v9bhC0b40noFt5M8VrOgyPBmgWWiTaOIC09ixg=; umdata_=T2gA8DGpJ8eRbsnQckW5lhnDg36vdgggVKbl3o9Ap3B6Nzh9QRLbXFPWEiidFGebvH0=',
    'Origin': 'https://www.wjx.cn',
    'Referer': 'https://www.wjx.cn/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data = 'data=107!fDg1Dk7KfQ6f5SiIWPJ7TF8G9UNkZOwbfx2bJ%2FlpAT00az5SAT%2BUAy00wdLpvfNmmfYJ9QUpNtrX8dBvslTVku4dCzd8rIwLffxu1C1NG7fWNuwA5LbzUQ6DKPYp8DyeBEH3gos685pK2vfffNl0tJJiPfgJYVYoeAmfPfoHIN9iKfqxdI4qXNkGLYgN3Pjx5SGYxXG2WPYQdyCPdu4qCfGqCSlv7Knz%2FffJ1eWfwvZIk%2F0l0HXmX3mQNNtvowglMbfvVIOYKnTfGYWftbTLyH9WAWFRxtkEA0nu3odPX3sM7PhxuKAnj1ZzdYOOM3tJKVNK41qocslcJx6PBAn3oy1M6ertkDM6CzRZl28H9BvKU4mYUn4ZJUgumQDwnnmtPsidJRrky7cNjVho6Ei9E2dBxHcs0QgiYWBdxM9BSES2O%2BMSSWHoNfL8vNXu9xWwqs9IACFnP8v9dmZa4MjblJ8VSYEGiNJc5422J1prqon4J%2FFxaQZO3KBhZu8mm4m1P38AqY1vhoODXKn9c2BbIvZIOVMIiFrekZdzZAAUwgQcOr3td25jUjAsXaKCP7NKe9cOsVz%2Bf09e1NcI%2BqSc3e4s%2FkULyAr0SqdP2TRMoFIRPu4dM%2Bcako4K9ngzHce4TlEgfBBkWLjkulmMsjWNz9OH51Z1cWpWoOkqjT2Zp4UOfHdi3hhdmRMnpfxZjFnohIaQUEJtMvjyL85EcRoA&xa=FFFF00000000016770EE&xt=&efy=1'

response = requests.post('https://ynuf.aliapp.org/service/um.json', cookies=cookies, headers=headers, data=data)

print(response.json())
