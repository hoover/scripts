import sys
from pathlib import Path
import email
import email.message
import email.encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

def convert_email(folder, output):
    with (folder / 'InternetHeaders.txt').open('rb') as f:
        raw_headers = f.read()

    message = email.message_from_bytes(raw_headers)
    del message['Content-Type']
    message.set_payload(None)
    message['Content-Type'] = 'multipart/mixed'

    html_file = folder / 'Message.html'
    text_file = folder / 'Message.txt'
    if html_file.exists():
        html = MIMEBase('text', 'html')
        with html_file.open('rb') as f:
            html.set_payload(f.read())
        email.encoders.encode_base64(html)
        message.attach(html)
    elif text_file.exists():
        text = MIMEBase('text', 'plain')
        with text_file.open('rb') as f:
            text.set_payload(f.read())
        email.encoders.encode_base64(text)
        message.attach(text)

    for p in (folder / 'Attachments').iterdir():
        attachment = MIMEBase('application', 'octet-stream')
        with p.open('rb') as f:
            attachment.set_payload(f.read())
        email.encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition',
            'attachment', filename=p.name)
        message.attach(attachment)

    output.write(message.as_bytes())

if __name__ == '__main__':
    [folder] = sys.argv[1:]
    from io import BytesIO
    output = BytesIO()
    convert_email(Path(folder), output)
    print(output.getvalue().decode('latin1'))
