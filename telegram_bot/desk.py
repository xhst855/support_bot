import os
import requests
from logger import setup_logger

logger = setup_logger()

# ENV variables
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_ORG_ID = os.getenv("ZOHO_ORG_ID")
ZOHO_DEPARTMENT_ID = os.getenv("ZOHO_DEPARTMENT_ID")

TOKEN_URL = "https://accounts.zoho.eu/oauth/v2/token"
ZOHO_DESK_URL = "https://desk.zoho.eu/api/v1/tickets"

access_token = None

def get_access_token():
    global access_token
    if access_token:
        return access_token

    try:
        logger.info("Requesting new Access Token...")
        data = {
            "client_id": ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "refresh_token": ZOHO_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
        response = requests.post(TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logger.info("Access Token obtained.")
        return access_token
    except Exception as e:
        logger.error(f"Failed to get access token: {e}")
        return None

def create_ticket(chat_id, message_text, category):
    token = get_access_token()
    if not token:
        logger.error("No access token available. Cannot create ticket.")
        return None

    headers = {
        'orgId': ZOHO_ORG_ID,
        'Authorization': f'Zoho-oauthtoken {token}',
        'Content-Type': 'application/json'
    }

    # Маппинг категорий и классификаций
    category_mapping = {
        "AML": ("Compliance", "AML"),
        "Finance": ("Payments", "Payment Check"),
        "Billing": ("Billing", "Invoice Inquiry"),
        "Technical": ("Technical Support", "Bug/Error"),
        "General Inquiry": ("General", "Question"),
        "Uncategorized": ("General", "Uncategorized"),
    }

    desk_category, desk_classification = category_mapping.get(category, ("General", "Uncategorized"))

    data = {
        "subject": f"Telegram Ticket from {chat_id}",
        "departmentId": ZOHO_DEPARTMENT_ID,
        "contact": {"email": f"user{chat_id}@telegram.local"},
        "description": message_text,
        "category": desk_category,
        "classification": desk_classification,
        # "type": "Question",
    }

    try:
        response = requests.post(ZOHO_DESK_URL, json=data, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            ticket_id = response.json().get('id')
            logger.info(f"Ticket {ticket_id} created with category '{desk_category}' and classification '{desk_classification}'.")
            return ticket_id
        else:
            logger.error(f"Failed to create ticket: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error while creating ticket: {e}")
        return None


def add_comment(ticket_id, comment_text):
    token = get_access_token()
    if not token:
        logger.error("No access token available. Cannot add comment.")
        return False

    headers = {
        'orgId': ZOHO_ORG_ID,
        'Authorization': f'Zoho-oauthtoken {token}',
        'Content-Type': 'application/json'
    }
    url = f"{ZOHO_DESK_URL}/{ticket_id}/comments"
    data = {"content": comment_text, "isPublic": False}

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Comment added to ticket {ticket_id}.")
            return True
        else:
            logger.error(f"Failed to add comment: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error while adding comment: {e}")
        return False



