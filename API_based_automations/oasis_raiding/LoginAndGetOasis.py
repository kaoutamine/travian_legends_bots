import base64
import hashlib
import os
import requests
from dotenv import load_dotenv

# Step 1: Generate code_verifier and code_challenge
def generate_pkce():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge

# Step 2: Send login request
def travian_login(email, password):
    code_verifier, code_challenge = generate_pkce()

    login_data = {
        "login": email,
        "password": password,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    headers = {
        "Content-Type": "application/json",
        "Origin": "https://www.travian.com",
        "Referer": "https://www.travian.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    response = requests.post(
        "https://identity.service.legends.travian.info/provider/login?client_id=HIaSfC2LNQ1yXOMuY7Pc2uIH3EqkAi26",
        json=login_data,
        headers=headers
    )

    if response.status_code == 200 and "Set-Cookie" in response.headers:
        # Extract JWT cookie from response headers
        jwt_cookie = response.cookies.get("JWT")
        if jwt_cookie:
            print("[+] Logged in successfully.")
            return jwt_cookie, code_verifier
        else:
            print("[-] Login succeeded but JWT cookie not found.")
    else:
        print(f"[-] Login failed. Status code: {response.status_code}")
        print(response.text)
    return None, None

# Step 3: Use JWT to make a sample request to game server
def get_oasis_info(jwt, x, y, server_url):
    session = requests.Session()
    session.cookies.set("JWT", jwt, domain=server_url.replace("https://", "").split("/")[0])
    
    oasis_url = f"{server_url}/ajax.php"
    params = {"cmd": "mapDetails", "x": x, "y": y}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": f"{server_url}/karte.php?x={x}&y={y}"
    }

    response = session.get(oasis_url, headers=headers, params=params)

    if response.status_code == 200:
        print(f"[+] Oasis ({x}, {y}) info received.")
        print(response.text[:500])  # Print preview
    else:
        print(f"[-] Failed to get oasis info: {response.status_code}")
        print(response.text)

# Example usage
if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the variables
    email = os.getenv('TRAVIAN_EMAIL')
    password = os.getenv('TRAVIAN_PASSWORD')

    print(email)
    print(password)
    server_url = "https://ts3.x1.asia.travian.com"

    jwt_token, verifier = travian_login(email, password)
    if jwt_token:
        get_oasis_info(jwt_token, x=-72, y=-22, server_url=server_url)

    
 