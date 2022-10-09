# Python script to send an email message.  Use '--help' to see arguments supported
#
# Currently:
#   -h, --help        show this help message and exit
#  --host HOST        SMTP host configuration to use (see smtphost.ini)
#  --message MESSAGE  file containing the message to send
#  --to TO            email address of message recipient
#  --subject SUBJECT  subject for email message
#
# Different SMTP services (e.g., Gmail, GMX, etc.) have their own SMTP command
# mechanisms, some of which are here but commented out.  Please check your mail
# service documentation to see what it requires.

import configparser
import argparse

# Import smtplib to provide email functions
import smtplib

# Import the email modules
from email.mime.text import MIMEText

# IMPORTANT CONFIGURATION INFO
SMTP_CONFIG = "smtphost.ini"


# Setup command line parsing
parser = argparse.ArgumentParser(description="Send an email message (read from a file) to a specified address")
parser.add_argument("--host",required=True,
    help="SMTP host configuration to use (see smtphost.ini)")
parser.add_argument("--message",required=True,
    help="file containing the message to send")
parser.add_argument("--to",required=True,
    help="email address of message recipient")
parser.add_argument("--subject",required=True,
    help="subject for email message")

args = parser.parse_args()

print("Via host '%s': sending message in file '%s' to %s with subject '%s'" % (args.host,args.message,args.to,args.subject))

# Load SMTP host config file (separate as it contains user IDs and passwords)
config = configparser.ConfigParser()
config.read(SMTP_CONFIG)

if args.host in config:
    smtpserver = config[args.host]['SMTP_SERVER']
    smtpuser   = config[args.host]['SMTP_USER']
    smtppasswd = config[args.host]['SMTP_PASS']
else:
    print("Sending failed! SMTP host '%s' unknown (%s)" % (args.host,SMTP_CONFIG))


# Construct email.  Sender must be user ID for SMTP server for proper authentication
f = open(args.message,'r')
msg = MIMEText(f.read())
msg['To'] = args.to
msg['From'] = smtpuser
msg['Subject'] = args.subject

# General case: Send the message via an SMTP server
# s = smtplib.SMTP(SMTP_SERVER)
# s.login(SMTP_USER,SMTP_PASS)
# s.sendmail(ADDR_FROM, ADDR_TO, msg.as_string())


# Special SMTP sequence when sending via Google Mail
# Not recently tested...
# s = smtplib.SMTP('smtp.gmail.com:587')
# s.ehlo_or_helo_if_needed()
# s.starttls()
# s.ehlo_or_helo_if_needed()
# s.login(SMTP_USER,SMTP_PASS)
# s.sendmail(ADDR_FROM, ADDR_TO, msg.as_string())

# SMTP sequence when sending via GMX
try:
    s = smtplib.SMTP(smtpserver,587)
    s.set_debuglevel(1)
    s.ehlo_or_helo_if_needed()
    s.starttls()
    s.ehlo_or_helo_if_needed()
    s.login(smtpuser,smtppasswd)
    s.sendmail(smtpuser, args.to, msg.as_string())
    # Close server connection
    s.quit()
    print("Successfully sent email")
except:
    print("Error: unable to send email")

