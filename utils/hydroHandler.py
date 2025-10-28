from datetime import datetime
import requests

def login(url:str, username:str, password:str) -> requests.Session:
    session = requests.Session()
    base_url = url.rstrip('/')
    session.post(
        f"{base_url}/login",
        data={
            "uname": username,
            "password": password,
            "tfa": "",
            "authnChallenge": "",
        },
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Content-Type": "application/x-www-form-urlencoded",
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept": "application/json"
        },
    )
    return session

def getHomework(url:str, session: requests.Session):
    base_url = url.rstrip('/')
    response = session.get(
        f"{base_url}/homework",
        headers={
            "Accept": "application/json",
        }
    ).json()
    
    response = response['calendar']
    
    data = []
    
    for item in response:
        data.append(
            {
                "title": item['title'],
                "type": item['rule'],
                "due": datetime.strptime(item['endAt'][:-6], "%Y-%m-%dT%H:%M:%S").timestamp(),
                "course": item['assign'][0],
                "submitted": datetime.strptime(item['endAt'][:-6], "%Y-%m-%dT%H:%M:%S").timestamp() < datetime.now().timestamp(), # TODO: check if submitted
                "url": f"{base_url}/homework" + item['docId'],
                "status": "Live",
            }
        )
    
    return data