import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr

# =========================
# CONFIGURATION
# =========================
IMAP_SERVER = "mail.problemfighter.com"
EMAIL_ACCOUNT = "support@problemfighter.com"
EMAIL_PASSWORD = "V1k-6JWFbi+U"
IMAP_PORT = 993

def fetch_all_emails_roundcube():
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    # Fetch all emails
    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No messages found.")
        return

    email_ids = data[0].split()
    print(f"Found {len(email_ids)} total messages.\n")

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email ID {eid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # --- Parse From ---
        from_ = msg.get("From", "(unknown sender)")
        name, email_addr = parseaddr(from_)
        if name:
            # Decode name if MIME encoded
            decoded_name = decode_header(name)
            name = "".join([str(t[0], t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_name])
        print(f"From Name: {name}")
        print(f"From Email: {email_addr}")

        # --- Parse Subject ---
        subject = msg.get("Subject", "(no subject)")
        decoded_subject = decode_header(subject)
        subject = "".join([str(t[0], t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_subject])
        print(f"Subject: {subject}")
        print(f"================================================================\n")

    mail.close()
    mail.logout()

def fetch_all_emails():
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    # ✅ Fetch all emails, not just unread
    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No messages found.")
        return

    email_ids = data[0].split()
    print(f"Found {len(email_ids)} total messages.\n")

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email ID {eid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = msg.get("subject", "(no subject)")
        from_ = msg.get("from", "(unknown sender)")
        print("=" * 50)
        print(f"From: {from_}")
        print(f"Subject: {subject}")

    mail.close()
    mail.logout()


from email.header import decode_header
from email.utils import parseaddr

def fetch_all_emails_v3():
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No messages found.")
        return

    email_ids = data[0].split()
    print(f"Found {len(email_ids)} total messages.\n")

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email ID {eid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # -------------------------
        # Parse From (display name only)
        # -------------------------
        from_header = msg.get("From", "")
        decoded_from = decode_header(from_header)
        from_str = "".join(
            [t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_from]
        )
        name, _ = parseaddr(from_str)
        print(f"From: {name}")

        # -------------------------
        # Parse To (display name only)
        # -------------------------
        to_header = msg.get("To", "")
        decoded_to = decode_header(to_header)
        to_str = "".join(
            [t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_to]
        )
        name_to, _ = parseaddr(to_str)
        print(f"To: {name_to}")

        # -------------------------
        # Date
        # -------------------------
        date = msg.get("Date", "")
        print(f"Date: {date}")

        # -------------------------
        # Subject
        # -------------------------
        subject_header = msg.get("Subject", "")
        decoded_subject = decode_header(subject_header)
        subject = "".join(
            [t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_subject]
        )
        print(f"Subject: {subject}")
        print("="*60)

    mail.close()
    mail.logout()


def fetch_emails_paginated(page=1, page_size=10):
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No messages found.")
        return

    # Get email IDs in descending order (newest first)
    email_ids = data[0].split()[::-1]

    total_emails = len(email_ids)
    total_pages = (total_emails + page_size - 1) // page_size

    if page < 1 or page > total_pages:
        print(f"Invalid page number. Total pages: {total_pages}")
        return

    start = (page - 1) * page_size
    end = start + page_size
    page_email_ids = email_ids[start:end]

    print(f"Displaying page {page}/{total_pages} ({len(page_email_ids)} emails)\n")

    for eid in page_email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email ID {eid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # -------------------------
        # From (display name only)
        # -------------------------
        from_header = msg.get("From", "")
        decoded_from = decode_header(from_header)
        from_str = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_from])
        name, _ = parseaddr(from_str)
        print(f"From: {name}")

        # -------------------------
        # To
        # -------------------------
        to_header = msg.get("To", "")
        decoded_to = decode_header(to_header)
        to_str = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_to])
        name_to, _ = parseaddr(to_str)
        print(f"To: {name_to}")

        # -------------------------
        # Date
        # -------------------------
        date = msg.get("Date", "")
        print(f"Date: {date}")

        # -------------------------
        # Subject
        # -------------------------
        subject_header = msg.get("Subject", "")
        decoded_subject = decode_header(subject_header)
        subject = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_subject])
        print(f"Subject: {subject}")
        print("="*60)

    mail.close()
    mail.logout()



def fetch_emails_paginated_v5(page=1, page_size=10):
    print("Connecting to IMAP server...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")

    # Fetch all email IDs
    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No messages found.")
        return

    # -------------------------
    # Reverse email IDs for newest first
    # -------------------------
    email_ids = data[0].split()[::-1]  # newest emails first

    total_emails = len(email_ids)
    total_pages = (total_emails + page_size - 1) // page_size

    if page < 1 or page > total_pages:
        print(f"Invalid page number. Total pages: {total_pages}")
        return

    start = (page - 1) * page_size
    end = start + page_size
    page_email_ids = email_ids[start:end]

    print(f"Displaying page {page}/{total_pages} ({len(page_email_ids)} emails)\n")

    for eid in page_email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            print(f"Failed to fetch email ID {eid}")
            continue

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # -------------------------
        # From (display name only)
        # -------------------------
        from_header = msg.get("From", "")
        decoded_from = decode_header(from_header)
        from_str = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_from])
        name, _ = parseaddr(from_str)
        print(f"From: {name}")

        # -------------------------
        # To
        # -------------------------
        to_header = msg.get("To", "")
        decoded_to = decode_header(to_header)
        to_str = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_to])
        name_to, _ = parseaddr(to_str)
        print(f"To: {name_to}")

        # -------------------------
        # Date
        # -------------------------
        date = msg.get("Date", "")
        print(f"Date: {date}")

        # -------------------------
        # Subject
        # -------------------------
        subject_header = msg.get("Subject", "")
        decoded_subject = decode_header(subject_header)
        subject = "".join([t[0].decode(t[1] or "utf-8") if isinstance(t[0], bytes) else t[0] for t in decoded_subject])
        print(f"Subject: {subject}")
        print("="*60, "\n\n")

    mail.close()
    mail.logout()



fetch_emails_paginated_v5()
