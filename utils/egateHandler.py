from datetime import datetime, timezone
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188",
    "sec-ch-ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def collect_data(text, name, endtag):
    start_idx = text.find(f'name="{name}"')
    if name == "pwdEncryptSalt":
        start_idx = text.find(f'id="{name}"')
    end_idx = text[start_idx:].find(endtag) + start_idx
    raw_data = text[start_idx:end_idx]
    res = raw_data[raw_data.find("value=") + 7 : -2]  ##-2
    return res


def login(studentid: str, password: str) -> requests.Session:
    url = r"https://ids.shanghaitech.edu.cn/authserver/login?service=https%3A%2F%2Felearning.shanghaitech.edu.cn%3A8443%2Fwebapps%2Fbb-BB-BBLEARN%2Findex.jsp"
    new_session = requests.session()
    new_session.cookies.clear()
    response = new_session.get(url)
    lt = collect_data(response.text, "lt", r"/>")
    dllt = "generalLogin"
    execution = collect_data(response.text, "execution", r"/>")
    _eventId = "submit"
    rmShown = "1"
    key = collect_data(response.text, "pwdEncryptSalt", r"/>")
    padded_password = b"Nu1L" * 16 + password.encode()
    pkcs7_padded_password = pad(padded_password, 16, "pkcs7")
    iv = b"Nu1L" * 4
    aes = AES.new(key.encode(), AES.MODE_CBC, iv)
    password = base64.b64encode(aes.encrypt(pkcs7_padded_password))

    data = {
        "username": studentid,
        "password": password,
        "lt": lt,
        "dllt": dllt,
        "execution": execution,
        "_eventId": _eventId,
        "rmShown": rmShown,
    }
    response = new_session.post(url, data=data, headers=headers, verify=False)
    return new_session


def getBB(sess: requests.Session):
    response = sess.get(
        "https://elearning.shanghaitech.edu.cn:8443/webapps/calendar/calendarData/allCourseEvents?start="
        + str(int(datetime.now().timestamp()) * 1000),
        headers=headers,
        verify=False,
    )

    response = response.json()

    data = []

    for item in response:
        title = item["title"]
        due = datetime.strptime(item["end"], "%Y-%m-%dT%H:%M:%S").timestamp()
        submitted = False
        course = item["calendarName"]
        status = "Attemptable" if item["attemptable"] else "Unattemptable"
        url = (
            "https://elearning.shanghaitech.edu.cn:8443/webapps/calendar/launch/attempt/_blackboard.platform.gradebook2.GradableItem-"
            + item["itemSourceId"]
        )
        data.append(
            {
                "title": title,
                "course": course,
                "due": due,
                "status": status,
                "submitted": submitted,
                "url": url,
            }
        )

    response = sess.get(
        "https://elearning.shanghaitech.edu.cn:8443/webapps/calendar/calendarData/pastDueEvents",
        headers=headers,
        verify=False,
    ).json()

    for item in response:
        title = item["title"]
        # strpttime based on UTC +8
        due = datetime.strptime(item["end"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone(8)).timestamp()
        submitted = False
        course = item["calendarName"]
        status = "Attemptable" if item["attemptable"] else "Unattemptable"
        url = (
            "https://elearning.shanghaitech.edu.cn:8443/webapps/calendar/launch/attempt/_blackboard.platform.gradebook2.GradableItem-"
            + item["itemSourceId"]
        )
        data.append(
            {
                "title": title,
                "course": course,
                "due": due,
                "status": status,
                "submitted": submitted,
                "url": url,
            }
        )

    # print(data)
    return data
