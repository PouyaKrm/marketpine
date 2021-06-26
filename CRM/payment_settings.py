WALLET = {
    'INITIAL_AVAILABLE_CREDIT': 15000,
    'MINIMUM_ALLOWED_CREDIT': -15000
}

BILLING = {
    'CUSTOMER_JOINED_BY_PANEL_COST': 1000,
    'CUSTOMER_JOINED_BY_APP_COST': 2000,
    'INVITED_CUSTOMER_AFTER_PURCHASE_COST': 5000
}

ZARINPAL = {
    'url': 'https://www.zarinpal.com/pg/services/WebGate/wsdl',
    "MERCHANT": "7055b6ac-e6dc-11e9-99c1-000c295eb8fc",
    "FORWARD_LINK": "https://www.zarinpal.com/pg/StartPay/{}/ZarinGate",  # use this string with .format method
}
