from twilio.rest import Client

# Replace with your credentials from https://console.twilio.com
account_sid = ""
auth_token = ""

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hello, Test Message",
    from_="",   # Your Twilio number
    to=""    # Recipient's number
)

print("Message SID:", message.sid)
print("Status:", message.status)
