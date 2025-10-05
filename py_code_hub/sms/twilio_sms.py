from twilio.rest import Client

# Replace with your credentials from https://console.twilio.com
account_sid = ""
auth_token = ""

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hello, Test Message",
    from_="+18586831069",   # Your Twilio number
    to="+6580265794"    # Recipient's number
)

print("Message SID:", message.sid)
print("Status:", message.status)
