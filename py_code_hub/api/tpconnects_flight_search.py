import requests
import json

# -------- CONFIGURATION --------
CLIENT_ID = ""
CLIENT_SECRET = ""
AUTH_URL = ""
SEARCH_URL = ""


# -------- GET ACCESS TOKEN --------
def get_access_token():
    response = requests.post(AUTH_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "tpconnects.api"
    })

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("[✓] Access token retrieved.")
        return token
    else:
        print("[✗] Failed to retrieve access token:")
        print(response.status_code, response.text)
        return None


# -------- SEARCH FLIGHTS --------
def search_flights(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "OriginDestination": {
            "Departure": {
                "AirportCode": "DXB",
                "Date": "2025-08-10"
            },
            "Arrival": {
                "AirportCode": "DEL"
            }
        },
        "Travelers": [
            {
                "PassengerTypeCode": "ADT"
            }
        ]
    }

    response = requests.post(SEARCH_URL, headers=headers, data=json.dumps(payload))

    if response.ok:
        print("[✓] Flight search successful:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("[✗] Flight search failed:")
        print(response.status_code, response.text)


# -------- MAIN --------
def main():
    token = get_access_token()
    if token:
        search_flights(token)


if __name__ == "__main__":
    main()
