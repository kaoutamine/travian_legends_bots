import requests
import hashlib
import base64
import secrets
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
EMAIL = os.getenv("TRAVIAN_EMAIL")
PASSWORD = os.getenv("TRAVIAN_PASSWORD")

def generate_code_pair():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b'=').decode()
    return verifier, challenge

def login_to_lobby(email, password):
    code_verifier, code_challenge = generate_code_pair()
    session = requests.Session()
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.travian.com",
        "Referer": "https://www.travian.com/",
        "User-Agent": "Mozilla/5.0",
    }

    # Step 1: Login to get the code
    login_url = "https://identity.service.legends.travian.info/provider/login?client_id=HIaSfC2LNQ1yXOMuY7Pc2uIH3EqkAi26"
    login_payload = {
        "login": email,
        "password": password,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    login_resp = session.post(login_url, json=login_payload, headers=headers)
    login_resp.raise_for_status()
    code = login_resp.json().get("code")

    # Step 2: Exchange code for session
    auth_url = "https://lobby.legends.travian.com/api/auth/code"
    auth_payload = {
        "locale": "en-EN",
        "code": code,
        "code_verifier": code_verifier
    }
    session.post(auth_url, json=auth_payload, headers=headers).raise_for_status()

    return session

def get_avatars(session):
    graphql_url = "https://lobby.legends.travian.com/api/graphql"
    graphql_payload = {
        "variables": {},
        "query": """
        {
          avatars {
            uuid
            name
            gameworld {
              metadata {
                url
                name
              }
            }
          }
        }
        """
    }
    headers = {"Content-Type": "application/json"}
    response = session.post(graphql_url, json=graphql_payload, headers=headers)
    response.raise_for_status()
    data = response.json()["data"]["avatars"]

    avatars = []
    for a in data:
        avatars.append({
            "uuid": a["uuid"],
            "name": a["name"],
            "world_name": a["gameworld"]["metadata"]["name"],
            "world_url": a["gameworld"]["metadata"]["url"]
        })
    return avatars

def login_to_server(session, avatars, selection=None):
    if selection is None:
        print("Your servers:")
        for i, a in enumerate(avatars):
            print(f"[{i}] {a['world_name']} — {a['world_url']}")
        selection = int(input("Which one would you like to log into? "))

    selected = avatars[selection]

    # Step 1: Play the avatar to get the redirect code
    play_url = f"https://lobby.legends.travian.com/api/avatar/play/{selected['uuid']}"
    play_resp = session.post(play_url)
    play_resp.raise_for_status()
    redirect_info = play_resp.json()
    code = redirect_info["code"]
    server_auth_url = f"{selected['world_url'].rstrip('/')}/api/v1/auth?code={code}&response_type=redirect"

    # Step 2: Follow redirect to get authenticated in the game world
    server_session = requests.Session()
    server_session.cookies.update(session.cookies.get_dict())  # Carry over cookies
    auth_resp = server_session.get(server_auth_url, allow_redirects=True)
    auth_resp.raise_for_status()

    print(f"[+] Successfully logged into {selected['world_name']} at {selected['world_url']}")
    return server_session, selected['world_url']

def main():
    session = login_to_lobby(EMAIL, PASSWORD)
    avatars = get_avatars(session)
    server_session, server_url = login_to_server(session, avatars)

    # You are now inside the game server and can use `server_session` for further actions
    # Example:
    res = server_session.get(server_url)
    print("[+] Game server main page loaded:", res.status_code)

if __name__ == "__main__":
    main()
