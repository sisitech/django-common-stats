import sys
from expensetrackerapi import settings
import africastalking


def sendBulkSms(recipients, message):
    if "test" in sys.argv:
        return
    username = settings.AFRICAS_TALKING_USERNAME
    sender = settings.AFRICAS_TALKING_SENDER
    api_key = settings.AFRICAS_TALKING_API_KEY
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    print(username, api_key)
    try:
        # Thats it, hit send and we'll take care of the rest.
        response = sms.send(message, recipients, "2517" if sender==None else sender)
        print(response)
    except Exception as e:
        print("Encountered an error while sending: %s" % str(e))
