import requests
from django.conf import settings

def get_exchange_rate():
    """
    Fetches the current exchange rate of USD to Iranian Rial (IRR) from the ExchangeRate-API.

    This function sends a GET request to the ExchangeRate-API to retrieve the latest exchange rates
    with USD as the base currency. If the request is successful and the response contains the relevant
    conversion rate data, the function returns the exchange rate of IRR (Iranian Rial). 

    Returns:
        float: The exchange rate of 1 USD to IRR if the request is successful; 
               otherwise, it may raise an exception or return None.

    Raises:
        requests.exceptions.RequestException: If the request to the API fails for any reason.
        KeyError: If the expected 'conversion_rates' key is not present in the response data.
    """
    url = "https://v6.exchangerate-api.com/v6/e395d95aeaa9ce27f9a230fa/latest/USD"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and 'conversion_rates' in data:
        return data['conversion_rates']['IRR']