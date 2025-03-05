import requests

cookies = {
    # '.ASPXANONYMOUS': 'Zf-S7J612wEkAAAAZDBhMmFjZjItNWViNC00MDlmLTllNGEtNDEzYTZlZDNhMTZm6VG2mLA0BLbyHDQzYLH53z-QZyw1',
    # 'browserid': '7ad41f79-a10c-47b3-808e-098edffe52b7',
    # 'actidev_302027739': '1',
    # 'awardshowway10': '1',
    # 'wjxawardload': '14253%7C302027739',
    # 'awardshowway0': '1',
    # 'lastshowway': '0|2025-03-02 04:06',
    # 'addlogd_123182286381_4': '1',
    # 'addlogd_123182286381_1': '1',
    # 'Hm_lvt_21be24c80829bd7a683b2c536fcf520b': '1740214399,1740864161',
    # 'HMACCOUNT': '2FAB3664ACE5C629',
    # 'Hm_lpvt_21be24c80829bd7a683b2c536fcf520b': '1740864967',
    # 'acw_tc': '1a0c39d217408781690755411e0036fdfc843162071f05f2b060824328ee6a',
    # 'jac221317950': '05360008',
    # 'SERVERID': 'ec48383874998d7d7994224bf7acd1b0|1740878169|1740878169',
    # 'ssxmod_itna': 'Qq0x2D9DnDcDyDGhEDzxmxB4ekEKv4ehux4itdqHeezDlO0ixA5D8D6DQeGTWy3eGCx+PKb7BRAfNiCDq44vQIBRmoYU03j4GLDmKDyKn2+iDx6q0rD74irDDxD3MD7PGmDim1uD7g1Zl9M6nDAQDQ4GyDitDKw0yDi3DA4DjzdeeGB6cDYQDGqDSinuxxD3DfbtYDDNYCpY48q4Dbg=llbr4Oenx0uDqzqDMD7tD/+h+cnTwrK4V0LysvcpnierDtqD9znt07eqgDWNuIZ4PC2+3eR+FiRGxQGDT4OGPl7he4R3eA735QDY=AqKG44hGiAWKD4elHziDD==',
    # 'ssxmod_itna2': 'Qq0x2D9DnDcDyDGhEDzxmxB4ekEKv4ehux4itdqHeeD6cb740v++x03KAeyF3eFCYuGxYyDnb6kqGYu7bGy7DxruwQiSDMDKRCGj2bqRt87GpkriCMmo4qTGnROEiWD+jgcprGMC/03TLpKGjYi4P2YdYmI8oL0EjkUTKdQxoz/wDP8m0hK7XXK7KTBlA4FR4O7D=qW7=KI3XvUCDht3WPs3uI9=avi864K4oCSkYnK7DNNZIeO+QUC9AxKdEd=EFP+z6+e/6wj7=Tb9SUHkhPMOEyQ8U5udu86+u+7K6ma6jFdsrlusFgG8Fq=Cf8Kb3dOkoo=VbbdwbhL7EEdNx5X47NeCAr+qTbKO4SdboTeOe5FD4PSo+8kFCdw25xkOG8Y9E7jbr5xeon4sA=moKg0e+4xKSbK04ZLOC+D1r+B8bFdb7xx1g1ox+f3Apx4meOFj8dEd3qQ+8QNOdaj7KWpRr71hY=8IPRD7oovCKlAQuWYsxfnnDSZ15QIv3OkuUsE3eM3r6bGrGP1NKjoMEU5cxtAAi6OeEiCfFf4=Q0eKo4wGQT7o4kuU35KWsWPz5gbO8u2mHmro4Tm72nuG9yG8DVbWLi=LwDsNkgB/a7dmwXQN1SGNcz3dwIp26+3sKR97M0u+EEArS+mLPD7j4i8Bnq5CRW8j27XNGPHxhwtPSwqMVSlMQfbZpOgijGP=DVpqe71Pdy0xWTZDwGbMmFDHvme4xMn27Nu2HGbY0AaqUH59qWrVabHv4CoAnGo49r4tDf7o/tj4DjKDYKeYDD==',
    # 'tfstk': 'gs_xpQiO282D-5Y3orZoSQXrYjPuqNC22t5ISdvmfTBRO6kDfqji1gB1EKiGiEGt1s5B1KPV1Fp1_s69bSJMCdBG1iVu-yfVgF8sWJ43-CvcvaXxldib1bOMs7AXSMyPTF8_K8c4bUfM797yODI1N7dMGxgfCh1SVLRiGF9XfY1W1L965O9XNLOHtqMXcmT7wCJWCFtXf7LShwNMFcJsWMtAv4f80ymZbadvDd3MeVCGR2xkdqJI82Jv9nncGL3s5aIuHKGyhklkQEvVWIBa8q8XXM5M6tUxlOCFzTd5dP3Hh_5hxn7bj2xpyKKGlOetXIIhHOJfGxiX9EpvAZtrG7CJfgQJoZwZY_fJhHLlquyDjEBAYp-b48WOwKX1k3MYEdjhZZtRd80RQhIFsCBYkq6C4H7hJ3GiKpdic7F-bc-Xa3tZAfO8WOkXwpVYjcowqkOJK7F-bc-XaQp3MlmZb3qC.',
}

headers = {
    'Accept': 'text/plain, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': '.ASPXANONYMOUS=Zf-S7J612wEkAAAAZDBhMmFjZjItNWViNC00MDlmLTllNGEtNDEzYTZlZDNhMTZm6VG2mLA0BLbyHDQzYLH53z-QZyw1; browserid=7ad41f79-a10c-47b3-808e-098edffe52b7; actidev_302027739=1; awardshowway10=1; wjxawardload=14253%7C302027739; awardshowway0=1; lastshowway=0|2025-03-02 04:06; addlogd_123182286381_4=1; addlogd_123182286381_1=1; Hm_lvt_21be24c80829bd7a683b2c536fcf520b=1740214399,1740864161; HMACCOUNT=2FAB3664ACE5C629; Hm_lpvt_21be24c80829bd7a683b2c536fcf520b=1740864967; acw_tc=1a0c39d217408781690755411e0036fdfc843162071f05f2b060824328ee6a; jac221317950=05360008; SERVERID=ec48383874998d7d7994224bf7acd1b0|1740878169|1740878169; ssxmod_itna=Qq0x2D9DnDcDyDGhEDzxmxB4ekEKv4ehux4itdqHeezDlO0ixA5D8D6DQeGTWy3eGCx+PKb7BRAfNiCDq44vQIBRmoYU03j4GLDmKDyKn2+iDx6q0rD74irDDxD3MD7PGmDim1uD7g1Zl9M6nDAQDQ4GyDitDKw0yDi3DA4DjzdeeGB6cDYQDGqDSinuxxD3DfbtYDDNYCpY48q4Dbg=llbr4Oenx0uDqzqDMD7tD/+h+cnTwrK4V0LysvcpnierDtqD9znt07eqgDWNuIZ4PC2+3eR+FiRGxQGDT4OGPl7he4R3eA735QDY=AqKG44hGiAWKD4elHziDD==; ssxmod_itna2=Qq0x2D9DnDcDyDGhEDzxmxB4ekEKv4ehux4itdqHeeD6cb740v++x03KAeyF3eFCYuGxYyDnb6kqGYu7bGy7DxruwQiSDMDKRCGj2bqRt87GpkriCMmo4qTGnROEiWD+jgcprGMC/03TLpKGjYi4P2YdYmI8oL0EjkUTKdQxoz/wDP8m0hK7XXK7KTBlA4FR4O7D=qW7=KI3XvUCDht3WPs3uI9=avi864K4oCSkYnK7DNNZIeO+QUC9AxKdEd=EFP+z6+e/6wj7=Tb9SUHkhPMOEyQ8U5udu86+u+7K6ma6jFdsrlusFgG8Fq=Cf8Kb3dOkoo=VbbdwbhL7EEdNx5X47NeCAr+qTbKO4SdboTeOe5FD4PSo+8kFCdw25xkOG8Y9E7jbr5xeon4sA=moKg0e+4xKSbK04ZLOC+D1r+B8bFdb7xx1g1ox+f3Apx4meOFj8dEd3qQ+8QNOdaj7KWpRr71hY=8IPRD7oovCKlAQuWYsxfnnDSZ15QIv3OkuUsE3eM3r6bGrGP1NKjoMEU5cxtAAi6OeEiCfFf4=Q0eKo4wGQT7o4kuU35KWsWPz5gbO8u2mHmro4Tm72nuG9yG8DVbWLi=LwDsNkgB/a7dmwXQN1SGNcz3dwIp26+3sKR97M0u+EEArS+mLPD7j4i8Bnq5CRW8j27XNGPHxhwtPSwqMVSlMQfbZpOgijGP=DVpqe71Pdy0xWTZDwGbMmFDHvme4xMn27Nu2HGbY0AaqUH59qWrVabHv4CoAnGo49r4tDf7o/tj4DjKDYKeYDD==; tfstk=gs_xpQiO282D-5Y3orZoSQXrYjPuqNC22t5ISdvmfTBRO6kDfqji1gB1EKiGiEGt1s5B1KPV1Fp1_s69bSJMCdBG1iVu-yfVgF8sWJ43-CvcvaXxldib1bOMs7AXSMyPTF8_K8c4bUfM797yODI1N7dMGxgfCh1SVLRiGF9XfY1W1L965O9XNLOHtqMXcmT7wCJWCFtXf7LShwNMFcJsWMtAv4f80ymZbadvDd3MeVCGR2xkdqJI82Jv9nncGL3s5aIuHKGyhklkQEvVWIBa8q8XXM5M6tUxlOCFzTd5dP3Hh_5hxn7bj2xpyKKGlOetXIIhHOJfGxiX9EpvAZtrG7CJfgQJoZwZY_fJhHLlquyDjEBAYp-b48WOwKX1k3MYEdjhZZtRd80RQhIFsCBYkq6C4H7hJ3GiKpdic7F-bc-Xa3tZAfO8WOkXwpVYjcowqkOJK7F-bc-XaQp3MlmZb3qC.',
    'Origin': 'https://www.wjx.cn',
    'Referer': 'https://www.wjx.cn/vm/hxxt2Oe.aspx',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'shortid': 'hxxt2Oe',
    'starttime': '2025/3/2 9:16:09',
    'nc_csessionid': '01AFgkYzXolECphY5lPQfRIFViDycSjP4Ichb9OvPynePJXvY41cZ4aFVyTaK_uOSdQZZXInAa1yQEObYzhCrjAxzdKrZpuu-k5NtKF8LCtVga1oCXWYXlMtx3tFOOaQ8m',
    'nc_sig': '05a1C7nT4bR5hcbZlAujcdyf2Ua5SQnNETuxKxvTPbB4glr3rQLNWpYxGfXwA3pYs1bn7dd_olabVeq7IlN3r28aJe7Nq1A1crUCQWW2NAPtIRfepIzuWJZtY6mPxx8x-fa-1P7a64PyHSFF6lhaL6EVVQvj7pNAEhl3g4ofCfOLnzfXx6W0eUzo5ZNwS9tvZFkNMSklcRKN7-cFGBs0rsFWuHBJ2TYq2Z4uprqp31hbuAIhjCV91T3v85Phn89pPli1uTjl10hF_2Kb034-I2ANqgS61xrpSK3X8xTqyfWKJIGlmfyttLZ9c7wdiLJ4bLcv6VdLtKkYmv5JXx6vTMzw',
    'nc_token': '1740878173640:0.9258728617744851',  # (new Date).getTime() + ":" + Math.random();
    'ktimes': '150',
    'jqnonce': 'c5d28e2d-cd7a-4d96-b214-73ad2ff98f11',
    'jqsign': 'b4e39d3e,be6`,5e87,c305,62`e3gg89g00',
}

data = 'submitdata=1%24%7D2%24-2%7D3%24%7D4%241!-2%2C2!-2%2C3!-2%2C4!-2%7D5%24%7D6%24%7D7%24%7D8%24%7D9%24%7D10%242%7D11%241%2C-2%2C-2%2C-2%7D12%24%7D13%24%5E%5E'

response = requests.post('https://www.wjx.cn/joinnew/processjq.ashx', params=params, cookies=cookies, headers=headers, data=data)

print(response.text)
