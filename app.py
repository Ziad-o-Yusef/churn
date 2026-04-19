import requests

url = "https://api-2c61e5b3-2928c99d-dku.eu-west-2.app.dataiku.io/public/api/v1/telco-churn-service/predict-churn/predict"
api_key = "YOUR_NEW_KEY"

payload = {
    "features": {
        "Country": "United States",
        "State": "California",
        "City": "Los Angeles",
        "Gender": "Male",
        "Senior Citizen": False,
        "Partner": False,
        "Dependents": False,
        "Tenure Months": 2,
        "Phone Service": True,
        "Multiple Lines": "No",
        "Internet Service": "DSL",
        "Online Security": "Yes",
        "Online Backup": "Yes",
        "Device Protection": "No",
        "Tech Support": "No",
        "Streaming TV": "No",
        "Streaming Movies": "No",
        "Contract": "Month-to-month",
        "Paperless Billing": True,
        "Payment Method": "Mailed check",
        "Monthly Charges": 53.85,
        "Total Charges": 108.15
    }
}

# 1) Bearer
r1 = requests.post(
    url,
    json=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    timeout=30
)
print("Bearer:", r1.status_code, r1.text[:500])

# 2) Basic Auth
r2 = requests.post(
    url,
    json=payload,
    auth=(api_key, ""),
    headers={"Content-Type": "application/json"},
    timeout=30
)
print("Basic:", r2.status_code, r2.text[:500])
