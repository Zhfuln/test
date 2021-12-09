import uvicorn
import requests
from typing import Optional
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/login")
async def home(request: Request):
    """
    测试用网页
    :param request:
    :return:
    """
    return templates.TemplateResponse("test.html", {"request": request, "client_id": "3c350ed6272c60d28743"})


def github_token(code: str):
    """
    github的访问令牌获取
    :param code: 临时授权码
    :return: 访问令牌40位字符串
    """
    headers = {"accept": "application/json"}
    git_url = "https://github.com/login/oauth/access_token"
    data = {"client_id": "3c350ed6272c60d28743", "code": code, "client_secret": "2f5f7ad31e4e1d68998e2f3a509a0bc502871118"}
    info = requests.post(url=git_url, headers=headers, data=data, timeout=15)
    if info.status_code == 200:
        res = info.json()
        access_token = res.get("access_token", None)
        return access_token
    return "false"


def github_user(access_token: str):
    """
    获取用户信息
    :param access_token: 访问令牌
    :return: 用户信息
    """
    url = "https://api.github.com/user"
    access = "token " + access_token
    headers = {"accept": "application/json", "Authorization": access}
    res = requests.get(url=url, headers=headers, timeout=15)
    if res.status_code == 200:
        user_info = res.json()
        dic = {"user_info": user_info, "access_token": access}
        return dic
    return "false"


def get_repo(url):
    """
    获取项目列表
    :param url:
    :return:
    """
    headers = {"accept": "application/json"}
    res = requests.get(url=url, headers=headers, timeout=15)
    if res.status_code == 200:
        repo_info = res.json()
        return repo_info
    return False


def get_email(url):
    """
    获取邮箱
    :param url:
    :return:
    """
    headers = {"accept": "application/json"}
    res = requests.get(url=url, headers=headers, timeout=15)
    if res.status_code == 200:
        commit_info = res.json()
        email_info = commit_info[0].get("commit", None).get("author", None).get("email", None)
        return email_info
    return "email false"



@app.get("/auth")
async def auth_code(code: str):
    """
    登录回调
    :param code: 临时授权码
    :return: 用户邮箱
    """
    if code:
        access_token = github_token(code)
        if access_token:
            dic = github_user(access_token)
            user = dic.get("user_info", None)
            email = user.get("email", None)
            if email:
                return email
            else:
                repos_url = user.get("repos_url", None)
                repo_info = get_repo(repos_url)
                if repo_info:
                    commits_url = repo_info[0].get("commits_url", None)
                    commits_url = commits_url.split("{")[0]
                    email = get_email(commits_url)
                    if email:
                        return email
                    else:
                        email = str(user.get("id", None)) + "+" + user.get("login", None) + "@users.noreply.github.com"
                        return email
                else:
                    return {"repo false"}

"""
user = {
    "login":"Zhfuln",  # 名称
    "id":81696603,
    "node_id":"MDQ6VXNlcjgxNjk2NjAz",
    "avatar_url":"https://avatars.githubusercontent.com/u/81696603?v=4",  # 头像
    "gravatar_id":"",
    "url":"https://api.github.com/users/Zhfuln",  # 本页
    "html_url":"https://github.com/Zhfuln",  # 主页
    "followers_url":"https://api.github.com/users/Zhfuln/followers",
    "following_url":"https://api.github.com/users/Zhfuln/following{/other_user}",
    "gists_url":"https://api.github.com/users/Zhfuln/gists{/gist_id}",
    "starred_url":"https://api.github.com/users/Zhfuln/starred{/owner}{/repo}",
    "subscriptions_url":"https://api.github.com/users/Zhfuln/subscriptions",
    "organizations_url":"https://api.github.com/users/Zhfuln/orgs",
    "repos_url":"https://api.github.com/users/Zhfuln/repos",
    "events_url":"https://api.github.com/users/Zhfuln/events{/privacy}",
    "received_events_url":"https://api.github.com/users/Zhfuln/received_events",
    "type":"User",  # 用户
    "site_admin":false,  
    "name":null,
    "company":null,
    "blog":"",
    "location":null,
    "email":null,
    "hireable":null,
    "bio":null,
    "twitter_username":null,
    "public_repos":0,
    "public_gists":0,
    "followers":0,
    "following":0,
    "created_at":"2019-03-31T14:14:03Z",
    "updated_at":"2021-12-06T07:00:38Z"
}
"""

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, log_level="info", reload=True)
