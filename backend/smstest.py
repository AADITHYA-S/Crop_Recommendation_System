import requests
import os
from dotenv import load_dotenv
load_dotenv()

def format_phone(number: str) -> str:
    number = str(number).strip()

    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("+"):
        number = number[1:]

    if number.startswith("0"):
        number = number[1:]

    if len(number) != 10 or not number.isdigit():
        raise ValueError(f"Invalid phone number: {number}")

    return number


def send_sms_fast2sms(phone: str, message: str) -> bool:

    api_key = os.getenv("FAST2SMS_API_KEY")
    if not api_key:
        print("FAST2SMS_API_KEY missing!")
        return False

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "sender_id": "TXTIND",
        "message": message,
        "language": "english",
        "route": "q",              # 🔥 THIS IS THE CORRECT ONE FOR BULKV2
        "numbers": format_phone(phone)
    }

    headers = {
        "authorization": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        print("Fast2SMS HTTP Status:", response.status_code)
        print("RAW RESPONSE:", response.text)  # 🔥 Extremely important

        # If no JSON returned → treat as failure
        try:
            data = response.json()
        except:
            print("Fast2SMS returned NON-JSON response.")
            return False

        # Successful message looks like:
        # {"return": true, "request_id": "...", "message": ["SMS sent successfully."]}
        return data.get("return") is True

    except Exception as e:
        print("SMS send failed:", str(e))
        return False
    
if __name__ == "__main__":
    test_phone = "8660852422"  # Replace with a valid phone number for testing
    test_message = "This is a test message from Fast2SMS."
    success = send_sms_fast2sms(test_phone, test_message)
    print("SMS sent successfully!" if success else "Failed to send SMS.")
