import argparse, sys, os
from collections import OrderedDict, Counter
import time, datetime, random, pickle, json, re
import requests
from urllib.parse import urlparse

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

USERAGENTS = (
    "Mozilla/5.0 (Linux; Android 9; GM1903 Build/PKQ1.190110.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Instagram 103.1.0.15.119 Android (28/9; 420dpi; 1080x2260; OnePlus; GM1903; OnePlus7; qcom; sv_SE; 164094539)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 178.0.0.30.118 (iPhone12,1; iOS 15_4_1; en_US; en-US; scale=2.00; 828x1792; 219162568)"
)

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
