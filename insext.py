import argparse, sys, os
from collections import OrderedDict, Counter
import time, datetime, random, pickle, json, re
import requests
from urllib.parse import urlparse, quote


try:
    from langdetect import detect, LangDetectException
except ImportError:
    pass

URL_BASE = "https://www.instagram.com/"
URL_API = "https://i.instagram.com/api/v1/users/web_profile_info/?"
URL_LOGIN = URL_BASE+"accounts/login/ajax/"
URL_LOGOUT = URL_BASE+"accounts/logout/"
URL_USER = URL_API+"username={username}"
URL_POST = URL_API+"media_shortcode={post_shortcode}"
URL_QUERY = URL_BASE+"graphql/query/?query_hash={hash}&variables={params}"
URL_STORIES = "https://i.instagram.com/api/v1/feed/reels_media/?user_ids={user_id}"

TOGET_FOLLOWINGS = {
    "str": "followings",
    "hash": "c56ee0ae1f89cdbd1c89e2bc6b8f3d18",
    "edge_path": "edge_follow"
}
TOGET_FOLLOWERS = {
    "str": "followers",
    "hash": "5aefa9893005572d237da5068082d8d5",
    "edge_path": "edge_followed_by"
}
TOGET_POSTS = {
    "str": "posts",
    "hash": "42323d64886122307be10013ad2dcc44",
    "edge_path": "edge_owner_to_timeline_media"
}

USERAGENTS = {
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
    "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/8.0.6 Safari/600.6.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPad; CPU OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 7077.134.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.156 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/7.1.7 Safari/537.85.16",
    "Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_1_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B440 Safari/600.1.4",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; KFTT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (iPad; CPU OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFTHWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.6.3 (KHTML, like Gecko) Version/7.1.6 Safari/537.85.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/45.0.2454.68 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
    "Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53",
    "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; TNJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; ARM; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MDDCJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFASWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/7.0.55539 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; KFJWI Build/IMM76D) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 7_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D167 Safari/9537.53",
    "Mozilla/5.0 (X11; CrOS armv7l 7077.134.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.156 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.2.5 (KHTML, like Gecko) Version/8.0.2 Safari/600.2.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFSOWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B435 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
    "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; MDDRJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFAPWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; LCJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Linux; U; Android 4.0.4; en-us; KFOT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B329 Safari/8536.25",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFARWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; ASU2JS; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPad; CPU OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A405 Safari/600.1.4",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; yie11; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MALNJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) GSA/8.0.57838 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (Windows NT 10.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; MAGWJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/7.1.5 Safari/537.85.14",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; TNJB; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; NP06; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36 OPR/31.0.1889.174",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.8 (KHTML, like Gecko) Version/8.0.3 Safari/600.4.8",
    "Mozilla/5.0 (iPad; CPU OS 7_0_6 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B651 Safari/9537.53",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/7.1.3 Safari/537.85.12",
    "Mozilla/5.0 (Windows NT 6.0; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (iPad; CPU OS 8_1_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B466 Safari/600.1.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_1_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B440 Safari/600.1.4",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; KFTT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 8_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12D508 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0",
    "Mozilla/5.0 (iPad; CPU OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D201 Safari/9537.53",
    "Mozilla/5.0 (Linux; U; Android 4.4.3; en-us; KFTHWI Build/KTU84M) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.68 like Chrome/39.0.2171.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.78.2 (KHTML, like Gecko) Version/7.0.6 Safari/537.78.2",
    "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/45.0.2454.68 Mobile/12H321 Safari/600.1.4",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; MDDCJS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"
    }

def urlshortner(url):
    try:
        return requests.get("http://tinyurl.com/api-create.php?url=" + url, timeout=10).text
    except:
        return url

FNAME_SESSION = "usersession"

class User:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "user-agent": random.choice(USERAGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
        })

    def isLogin(self):
        return False

    @staticmethod
    def loadSession(fpath):
        try:
            with open(fpath, "rb") as f:
                return pickle.load(f)
        except:
            return None

    def saveSession(self, fpath):
        try:
            with open(fpath, "wb") as f:
                pickle.dump(self, f)
        except Exception as e:
            print(f"Error saving session: {e}")

class AuthenticateUser(User):
    def __init__(self):
        super().__init__()
        self.session.headers = {
            "Referer": URL_BASE,
            "X-Instagram-AJAX": "1",
            "X-IG-App-ID": "936619743392459",
        }
        try:
            response = self.session.get(
                URL_BASE,
                timeout=10
            )
            if "csrftoken" in response.cookies:
                self.session.headers.update({
                    "X-CSRFToken": response.cookies["csrftoken"]
                })
            else:
                print("Warning: CSRF token not found")
        except Exception as e:
            print(f"Initialization error: {e}")

        self.login_session = None

    def isLogin(self):
        if not self.login_session:
            return False
        
        try:
            response_data = self.login_session.json()
            return response_data.get("authenticated", False) and self.login_session.status_code == 200
        except json.JSONDecodeError:
            return False

    def login(self, username, password):
        try:
            self.login_session = self.session.post(
                url=URL_LOGIN,
                data={"username": username, "password": password, "queryParams": "{}"},
                allow_redirects=True,
                timeout=15
            )
            
            if self.login_session.status_code == 200:
                if self.isLogin():
                    self.session.headers.update({
                        "user-agent": random.choice(USERAGENTS),
                        "X-CSRFToken": self.login_session.cookies.get("csrftoken", "")
                    })
                    print(f"✅ Login successful as @{username}")
                    return True
                else:
                    print("❌ Login failed. Possible reasons:")
                    print("- Incorrect username/password")
                    print("- Instagram detected unusual activity")
                    print("- 2FA enabled (not supported)")
                    print(f"Response: {self.login_session.text[:200]}...")
            else:
                print(f"Login failed with status code: {self.login_session.status_code}")
                print(f"Response: {self.login_session.text[:200]}...")
        except Exception as e:
            print(f"Login error: {e}")
        return False

    def logout(self):
        if self.isLogin():
            try:
                self.session.post(
                    url=URL_LOGOUT,
                    data={"csrfmiddlewaretoken": self.login_session.cookies.get("csrftoken", "")},
                    timeout=10
                )
            except:
                pass

def supports_color():
    supported_platform = (sys.platform != "Pocket PC") \
        and (sys.platform != "win32" \
        or "ANSICON" in os.environ \
        or "WT_SESSION" in os.environ \
        or os.environ.get("TERM_PROGRAM") == "vscode")
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty

BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[39m"

if not supports_color():
    BLUE = MAGENTA = CYAN = RED = GREEN = YELLOW = RESET = ""

def printsep():
    print("\n" + "="*61)

def bannerprint():
    print(f"""{MAGENTA}
$$$$$$\                                                   $$\     
\_$$  _|                                                  $$ |    
  $$ |  $$$$$$$\   $$$$$$$\          $$$$$$\  $$\   $$\ $$$$$$\   
  $$ |  $$  __$$\ $$  _____|        $$  __$$\ \$$\ $$  |\_$$  _|  
  $$ |  $$ |  $$ |\$$$$$$\  $$$$$$\ $$$$$$$$ | \$$$$  /   $$ |    
  $$ |  $$ |  $$ | \____$$\ \______|$$   ____| $$  $$<    $$ |$$\ 
$$$$$$\ $$ |  $$ |$$$$$$$  |        \$$$$$$$\ $$  /\$$\   \$$$$  |
\______|\__|  \__|\_______/          \_______|\__/  \__|   \____/ 

                          author : jull
{RESET}""")

def dictprint(d):
    if d is None:
        return

    for k, v in d.items():
        if k.startswith("sep"):
            if not v.startswith("IMAGE"):
                print(f"\n{CYAN}[+] {v}{RESET}\n")
                print(f"{BLUE}="*61)
            else:
                print(f"\n{CYAN}{v}{RESET}")
            continue
            
        if isinstance(v, int) and v > 1000:
            v = f"{v:,}"
        
        if isinstance(v, datetime.datetime):
            v = v.strftime("%Y-%m-%d %H:%M")
        
        if isinstance(v, (list, tuple, set)):
            if not v:
                v = "-"
            elif all(isinstance(item, dict) for item in v):
                v = "; ".join([f"{list(item.values())[0]}" for item in v])
            else:
                v = ", ".join(map(str, v))
                if len(v) > 100:
                    v = v[:100] + "..." 
        
        print(f"{BLUE}{k:<25}: {RESET}{v}")
    print()

def listprint(l, title):
    if l is None:
        return

    print(f"\n{CYAN}{title}{RESET}\n")
    if not len(l):
        print("-")
    else:
        for i, v in enumerate(l):
            if i > 0 and i % 5 == 0:
                print()
            print(v, end=", " if i < len(l)-1 else "")
        print()

def safe_get(nretry, *args, **kwargs):
    try:
        # Add delay to avoid rate limiting
        time.sleep(random.uniform(1.5, 3.5))
        
        if user.isLogin():
            kwargs['cookies'] = user.login_session.cookies
            
        response = user.session.get(
            *args, 
            timeout=30,
            **kwargs
        )
        
        # Handle rate limiting
        if response.status_code == 429:
            wait_time = 60
            print(f"{RED}⚠️ Rate limited! Waiting {wait_time} seconds...{RESET}")
            time.sleep(wait_time)
            return safe_get(nretry-1, *args, **kwargs)
            
        response.raise_for_status()
        return response

    except requests.exceptions.RequestException as e:
        print(f"{RED}Request error: {e}{RESET}")
        if nretry > 1:
            print(f"{YELLOW}Retrying ({nretry-1} attempts left)...{RESET}")
            time.sleep(5)
            return safe_get(nretry-1, *args, **kwargs)
        else:
            return None
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")
        return None

def get_json(*args, **kwargs):
    response = safe_get(3, *args, **kwargs)
    if response is None or not response.ok:
        return None
    try:
        return response.json()
    except json.JSONDecodeError:
        print(f"{RED}Error decoding JSON from response{RESET}")
        print(f"Response text: {response.text[:200]}...")
        return None

def download_webimg(url):
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            stream=True,
            timeout=15
        )

        if not response.ok:
            print(f"{RED}Error downloading image (status {response.status_code}){RESET}")
            return

        # Extract filename
        f_name = "image_" + str(int(time.time())) + ".jpg"
        if '?' in url:
            base_url = url.split('?')[0]
            f_name = os.path.basename(base_url) or f_name

        with open(f_name, "wb") as f:
            for block in response.iter_content(1024):
                if not block:
                    break
                f.write(block)
        print(f"{GREEN}Downloaded: {f_name}{RESET}")
    except Exception as e:
        print(f"{RED}Download error: {e}{RESET}")

def query_with_cursor(userid, toget, end_cursor):
    params = json.dumps({"id": userid, "first": 50, "after": end_cursor})
    encoded_params = requests.utils.quote(params)
    url = URL_QUERY.format(hash=toget["hash"], params=encoded_params)
    
    data = get_json(url)
    if not data:
        return None, None

    try:
        edge = data["data"]["user"][toget["edge_path"]]
        if not edge:
            return None, None

        nodes = [node["node"] for node in edge["edges"]]
        end_cursor = edge["page_info"]["end_cursor"]
        return nodes, end_cursor
    except KeyError:
        return None, None

def query_with_cursor_gen(username, toget, end_cursor=""):
    user_data = user_info(username)
    if not user_data or "id" not in user_data:
        print(f"{RED}⚠️ Failed to get user ID for @{username}{RESET}")
        return
    
    userid = user_data["id"]

    while True:
        nodes, end_cursor = query_with_cursor(userid, toget, end_cursor)

        if not nodes:
            return

        for node in nodes:
            yield node

        if not end_cursor:
            return

# ======================== NEW FUNCTIONS ======================== #
def get_stories(user_id):
    """Get user active stories"""
    if not user.isLogin():
        return []
    
    try:
        url = URL_STORIES.format(user_id=user_id)
        response = safe_get(3, url)
        if not response or not response.ok:
            return []
        
        data = response.json()
        if "reels_media" not in data or not data["reels_media"]:
            return []
        
        return data["reels_media"][0]["items"]
    except Exception as e:
        print(f"{RED}Error getting stories: {e}{RESET}")
        return []

def detect_language(text):
    """Detect text language using langdetect"""
    if not text:
        return "N/A"
    
    try:
        from langdetect import detect, LangDetectException
        try:
            return detect(text)
        except LangDetectException:
            return "N/A"
    except ImportError:
        return "N/A (install langdetect)"

def osint_scan(text, emails, phones, links, mentions, username):
    """Scan text for emails, phones, links, and mentions"""
    if not text:
        return
    
    # Email regex
    found_emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text, re.IGNORECASE)
    emails.update(found_emails)
    
    # Phone regex (international format)
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    found_phones = re.findall(phone_regex, text)
    phones.update(found_phones)
    
    # URL regex
    url_regex = r'https?://[^\s/$.?#].[^\s]*'
    found_links = re.findall(url_regex, text)
    for link in found_links:
        parsed = urlparse(link)
        if "instagram.com" not in parsed.netloc:
            links.add(link)
    
    # Mentions regex
    found_mentions = re.findall(r'@([a-zA-Z0-9_.]{1,30})', text)
    for mention in found_mentions:
        if mention != username:
            mentions[mention] += 1

def get_comments(shortcode, count=50):
    """Get comments for a post"""
    if not user.isLogin() or count <= 0:
        return []
    
    try:
        variables = json.dumps({"shortcode": shortcode, "first": count})
        url = f"https://www.instagram.com/graphql/query/?query_hash=33ba35852cb50da46f5b5e889df7d159&variables={variables}"
        data = get_json(url)
        if not data:
            return []
        
        edges = data["data"]["shortcode_media"]["edge_media_to_parent_comment"]["edges"]
        return [edge["node"]["text"] for edge in edges]
    except Exception as e:
        print(f"{RED}Error getting comments: {e}{RESET}")
        return []

# ======================== MODIFIED FUNCTIONS ======================== #
def get_user_info(username, to_download=False, osint=False, osint_posts=5, osint_comments=50):
    data = get_json(URL_USER.format(username=username))
    if not data:
        return None

    try:
        user_results = data["data"]["user"]
    except KeyError:
        print(f"{RED}⚠️ User @{username} not found or account is private{RESET}")
        return None

    info = OrderedDict()
    info["sep"] = "USER INFO"

    info["ID"] = user_results["id"]
    info["Username"] = user_results["username"]
    info["Full Name"] = user_results["full_name"]
    info["Profile Picture"] = urlshortner(user_results["profile_pic_url_hd"])
    
    if to_download:
        print(f"{YELLOW}Downloading profile picture...{RESET}")
        download_webimg(user_results["profile_pic_url_hd"])

    info["Bio"] = user_results["biography"].replace("\n", " \\n ")
    info["External URL"] = user_results["external_url"]

    info["Private Account"] = "Yes" if user_results["is_private"] else "No"
    info["Verified"] = "Yes" if user_results["is_verified"] else "No"
    info["Category"] = user_results.get("category_enum", "-")
    info["New Account"] = "Yes" if user_results.get("is_joined_recently", False) else "No"
    
    if user_results.get("is_professional_account", False):
        info["Account Type"] = "Creator"
    elif user_results.get("is_business_account", False):
        info["Account Type"] = "Business"
    else:
        info["Account Type"] = "Personal"

    info["Followers"] = user_results["edge_followed_by"]["count"]
    info["Following"] = user_results["edge_follow"]["count"]
    info["Posts"] = user_results["edge_owner_to_timeline_media"]["count"]
    info["Videos"] = user_results.get("edge_felix_video_timeline", {}).get("count", 0)
    info["Reels"] = user_results.get("highlight_reel_count", 0)
    
    if "edge_user_to_photos_of_you" in user_results:
        info["Tagged Posts"] = user_results["edge_user_to_photos_of_you"]["count"]
    else:
        info["Tagged Posts"] = 0

    # Account creation date (from oldest post)
    edges = user_results["edge_owner_to_timeline_media"]["edges"]
    if edges:
        oldest_post = edges[-1]["node"]
        info["Account Created At"] = datetime.datetime.fromtimestamp(oldest_post["taken_at_timestamp"])
    else:
        info["Account Created At"] = "N/A"
    
    # Active stories
    stories = get_stories(user_results["id"])
    info["Active Stories"] = len(stories)
    
    # Last active time
    if stories:
        latest_story = max(stories, key=lambda x: x["taken_at"])
        info["Last Active At"] = datetime.datetime.fromtimestamp(latest_story["taken_at"])
    elif edges:
        newest_post = edges[0]["node"]
        info["Last Active At"] = datetime.datetime.fromtimestamp(newest_post["taken_at_timestamp"])
    else:
        info["Last Active At"] = "N/A"
    
    # Language detection from bio
    if user_results["biography"]:
        info["Language"] = detect_language(user_results["biography"])
    else:
        info["Language"] = "N/A"
    
    # Business info
    if user_results.get("is_business_account", False):
        if user_results.get("business_email"):
            info["Business Email"] = user_results["business_email"]
        if user_results.get("business_phone_number"):
            info["Business Phone"] = user_results["business_phone_number"]
        if user_results.get("business_category_name"):
            info["Business Category"] = user_results["business_category_name"]

    # ======================== OSINT MODE ======================== #
    if osint and not user_results["is_private"]:
        osint_data = OrderedDict()
        osint_data["sep"] = "OSINT RESULTS"
        
        emails = set()
        phones = set()
        links = set()
        mentions = Counter()
        
        # Scan bio
        bio_text = user_results["biography"]
        osint_scan(bio_text, emails, phones, links, mentions, username)
        
        # Scan recent posts
        post_count = 0
        print(f"{YELLOW}Scanning {osint_posts} posts for OSINT data...{RESET}")
        for i, post in enumerate(query_with_cursor_gen(username, TOGET_POSTS)):
            if i >= osint_posts:
                break
                
            post_info = get_post_info(post, i, False, deep=False)
            if post_info and "Caption" in post_info:
                osint_scan(post_info["Caption"], emails, phones, links, mentions, username)
            
            # Scan comments
            if osint_comments > 0 and "Shortcode" in post_info:
                print(f"  Scanning comments for post {i+1}...")
                comments = get_comments(post_info["Shortcode"], osint_comments)
                for comment in comments:
                    osint_scan(comment, emails, phones, links, mentions, username)
            
            post_count += 1
        
        # OSINT results
        osint_data["Emails Found"] = list(emails) if emails else "None found"
        osint_data["Phones Found"] = list(phones) if phones else "None found"
        osint_data["External Links"] = list(links) if links else "None found"
        
        # Top mentions
        top_mentions = [f"@{m[0]} ({m[1]})" for m in mentions.most_common(10)]
        osint_data["Top Mentions"] = top_mentions if top_mentions else "None found"
        
        # Add to main info
        info.update(osint_data)
    elif osint and user_results["is_private"]:
        info["OSINT Status"] = "Skipped (private account)"
    
    return info

def get_post_info(node, ipost, to_download, deep=True):
    if deep:
        data = get_json(URL_POST.format(post_shortcode=node["shortcode"]))
        if not data:
            return None
        try:
            post_results = data["graphql"]["shortcode_media"]
        except KeyError:
            return None
    else:
        post_results = node

    info = OrderedDict()
    info["sep"] = f"POST #{ipost+1} INFO"

    info["ID"] = post_results["id"]
    info["Shortcode"] = post_results["shortcode"]
    info["Timestamp"] = datetime.datetime.fromtimestamp(post_results["taken_at_timestamp"])
    info["Likes"] = post_results["edge_media_preview_like"]["count"]
    info["Comments Disabled"] = "Yes" if post_results.get("comments_disabled", False) else "No"
    info["Pinned"] = "Yes" if post_results.get("pinned_for_users", False) else "No"

    info["Comments"] = post_results.get("edge_media_to_comment", {}).get("count", 0)
    
    stats = OrderedDict()
    if "edge_media_to_saved" in post_results:
        stats["Saves"] = post_results["edge_media_to_saved"]["count"]
    if "video_view_count" in post_results:
        stats["Views"] = post_results["video_view_count"]
    if "edge_media_to_reshare_count" in post_results:
        stats["Shares"] = post_results["edge_media_to_reshare_count"]
    if "impression_count" in post_results:
        stats["Impressions"] = post_results["impression_count"]
    
    if stats:
        info["Stats"] = " | ".join([f"{k}: {v}" for k, v in stats.items()])

    location = post_results.get("location")
    if location:
        info["Location"] = f"{location['name']} (ID: {location['id']})"

    caption = post_results.get("edge_media_to_caption", {}).get("edges", [])
    if caption:
        info["Caption"] = caption[0]["node"]["text"].replace("\n", " \\n ")[:150] + "..." 

    # Handle single and multiple media
    if "edge_sidecar_to_children" in post_results:
        total_imgs = len(post_results["edge_sidecar_to_children"]["edges"])
        media_nodes = [edge["node"] for edge in post_results["edge_sidecar_to_children"]["edges"]]
    else:
        total_imgs = 1
        media_nodes = [post_results]

    for iimage, media in enumerate(media_nodes):
        info[f"sep {iimage}"] = f"MEDIA {iimage+1}"
        
        info["Media URL"] = urlshortner(media["display_url"])
        if to_download:
            print(f"{YELLOW}Downloading media {iimage+1}...{RESET}")
            download_webimg(media["display_url"])

        info["Type"] = "Video" if media.get("is_video", False) else "Image"
        info["Dimensions"] = f"{media['dimensions']['width']}x{media['dimensions']['height']}"
        
        if iimage < total_imgs - 1:
            info[""] = "-" * 30 

    return info

def posts_info(username, to_download):
    if not user.isLogin():
        print(f"{YELLOW}⚠️ Logged out mode: Only last 12 posts available{RESET}")
        for i in range(12):
            post_info_data = post_info(username, i, to_download)
            if post_info_data:
                yield post_info_data
            else:
                break
    else:
        for i, node in enumerate(query_with_cursor_gen(username, TOGET_POSTS)):
            post_info_data = get_post_info(node, i, to_download)
            if post_info_data:
                yield post_info_data

def args_control():
    ap = argparse.ArgumentParser(
        description="Extract and process data from Instagram accounts",
        epilog="Author: @jull"
    )

    ap.add_argument(
        "-u", "--user",
        help="Username to extract information",
        metavar="username",
        type=str,
        required=True
    )

    ap.add_argument(
        "-l", "--login",
        help="Login credentials (username and password)",
        metavar=("username", "password"),
        type=str,
        nargs=2
    )

    ap.add_argument(
        "-i", "--info",
        help="Show user profile information",
        action="store_true"
    )

    ap.add_argument(
        "-p", "--post",
        help="Show specific post by index (0=most recent, -1=all posts)",
        metavar="n",
        type=int,
        nargs="?",
        const=-1
    )

    ap.add_argument(
        "-dp", "--download",
        help="Download media content (profile picture and posts)",
        action="store_true"
    )

    ap.add_argument(
        "--osint",
        help="Enable OSINT mode (scan for emails, phones, links, mentions)",
        action="store_true"
    )

    ap.add_argument(
        "--osint-posts",
        help="Number of posts to scan in OSINT mode (default: 5)",
        type=int,
        default=5
    )

    ap.add_argument(
        "--osint-comments",
        help="Number of comments per post to scan in OSINT mode (default: 50)",
        type=int,
        default=50
    )

    ap.add_argument(
        "--json",
        help="Export results to JSON file",
        metavar="OUTPUT_FILE",
        type=str
    )

    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)

    return ap.parse_args()

if __name__ == "__main__":
    args = args_control()
    bannerprint()

    # Load or create user session
    if os.path.exists(FNAME_SESSION):
        user = User.loadSession(FNAME_SESSION)
        if user and isinstance(user, AuthenticateUser) and user.isLogin():
            print(f"{GREEN}Loaded active session{RESET}")
        else:
            user = User()
    elif args.login:
        user = AuthenticateUser()
        if not user.login(*args.login):
            print(f"{RED}Login failed. Exiting.{RESET}")
            sys.exit(1)
    else:
        user = User()
        print(f"{YELLOW}Using public mode (limited access){RESET}")

    all_results = OrderedDict()
    username = args.user

    # Get user info
    user_info_data = get_user_info(
        username,
        to_download=args.download,
        osint=args.osint,
        osint_posts=args.osint_posts,
        osint_comments=args.osint_comments
    )
    
    if not user_info_data:
        print(f"{RED}Failed to get user info for @{username}{RESET}")
        sys.exit(1)
    
    all_results["user_info"] = user_info_data
    
    if args.info or (not args.post and not args.json):
        dictprint(user_info_data)

    if args.post is not None:
        if user_info_data["Private Account"] == "Yes" and not user.isLogin():
            print(f"{RED}Private account requires login{RESET}")
        else:
            if args.post == -1:  #
                posts = []
                for i, post_info_data in enumerate(posts_info(username, args.download)):
                    if post_info_data:
                        if not args.json:
                            dictprint(post_info_data)
                        posts.append(post_info_data)
                all_results["posts"] = posts
            else:
                post_info_data = None
                if args.post < 12 or user.isLogin():
                    for i, node in enumerate(query_with_cursor_gen(username, TOGET_POSTS)):
                        if i == args.post:
                            post_info_data = get_post_info(node, i, args.download)
                            break
                
                if post_info_data:
                    if not args.json:
                        dictprint(post_info_data)
                    all_results["post"] = post_info_data
                else:
                    print(f"{RED}Post index {args.post} not found{RESET}")

    if args.json:
        def datetime_converter(o):
            if isinstance(o, datetime.datetime):
                return o.isoformat()
            return o
        
        try:
            with open(args.json, "w") as f:
                json.dump(all_results, f, default=datetime_converter, indent=2)
            print(f"{GREEN}Results exported to {args.json}{RESET}")
        except Exception as e:
            print(f"{RED}Error exporting to JSON: {e}{RESET}")

    if user.isLogin():
        user.saveSession(FNAME_SESSION)
        user.logout()
