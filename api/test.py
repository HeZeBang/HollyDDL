import requests

resp = requests.post(
        "https://acm.shanghaitech.edu.cn/login",
        data={
            "uname": "test",
            "password": "test123456",
            "tfa": "",
            "authnChallenge": "",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
    )

print(resp.json())