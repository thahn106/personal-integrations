import json
import os.path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class ChronosClient:
    # when scopes are modified, delete token.json and reauthorize
    # Calendar scopes reference: https://developers.google.com/calendar/api/auth
    SCOPES = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",  # for writing events
    ]

    def __init__(self, client_secret_path: str, token_path: str):
        self.client_secret_path = client_secret_path
        self.token_path = token_path
        self._authorize()

    def list_calendars(self) -> List[dict]:
        try:
            service = build("calendar", "v3", credentials=self.creds)
            calendar_list = service.calendarList().list().execute()
            return calendar_list["items"]
        except HttpError as err:
            print(err)
            return []

    def _authorize(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        # only update creds if they are valid
        self.creds = creds


def main():
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    CRED_PATH = os.path.join(SCRIPT_DIR, "credentials.json")
    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError(f"Credentials file not found: {CRED_PATH}")
    TOKEN_PATH = os.path.join(SCRIPT_DIR, "token.json")

    client = ChronosClient(CRED_PATH, TOKEN_PATH)

    print("List calendars")
    calendars = client.list_calendars()
    for calendar in calendars:
        print(json.dumps(calendar, indent=2))


if __name__ == "__main__":
    main()
