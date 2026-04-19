import streamlit as st
import requests

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Cell C Churn Predictor",
    page_icon="📊",
    layout="centered"
)

# =========================
# CONFIG
# =========================
ENDPOINT_URL = "https://api-2c61e5b3-2928c99d-dku.eu-west-2.app.dataiku.io/public/api/v1/telco-churn-service/predict-churn/predict"
BEARER_TOKEN = "Nyb1yfdpiXpVUFvlVmTQoT0cEr611UxL"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Cell_C_New_2024_logo.svg/1280px-Cell_C_New_2024_logo.svg.png"

# =========================
# STYLING
# =========================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-title {
        color: #666666;
        text-align: center;
        margin-top: 0;
        margin-bottom: 20px;
    }
    .result-box {
        padding: 18px;
        border-radius: 12px;
        font-size: 22px;
        font-weight: 700;
        text-align: center;
        margin-top: 20px;
    }
    .result-yes {
        background-color: #ffe5e5;
        color: #b30000;
        border: 1px solid #ffb3b3;
    }
    .result-no {
        background-color: #e8fff0;
        color: #0f7a35;
        border: 1px solid #b7ebc6;
    }
    div.stButton > button {
        width: 100%;
        height: 3.2em;
        border-radius: 10px;
        font-size: 18px;
        font-weight: 600;
        background-color: #111111;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================
st.image(LOGO_URL, width=220)
st.markdown('<p class="main-title">Cell C Churn Predictor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-powered customer churn prediction application</p>', unsafe_allow_html=True)
st.markdown("---")

# =========================
# FORM
# =========================
with st.form("churn_form"):
    col1, col2 = st.columns(2)

    with col1:
        country = st.text_input("Country", value="United States")
        state = st.text_input("State", value="California")
        city = st.text_input("City", value="Los Angeles")
        gender = st.selectbox("Gender", ["Male", "Female"], index=0)
        senior_citizen = st.selectbox("Senior Citizen", [False, True], index=0)
        partner = st.selectbox("Partner", [False, True], index=0)
        dependents = st.selectbox("Dependents", [False, True], index=0)
        tenure_months = st.number_input("Tenure Months", min_value=0, max_value=120, value=2, step=1)
        phone_service = st.selectbox("Phone Service", [True, False], index=0)
        multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"], index=0)
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"], index=0)

    with col2:
        online_security = st.selectbox("Online Security", ["Yes", "No", "No internet service"], index=0)
        online_backup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"], index=0)
        device_protection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"], index=1)
        tech_support = st.selectbox("Tech Support", ["Yes", "No", "No internet service"], index=1)
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"], index=1)
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"], index=1)
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"], index=0)
        paperless_billing = st.selectbox("Paperless Billing", [False, True], index=1)
        payment_method = st.selectbox(
            "Payment Method",
            ["Mailed check", "Electronic check", "Bank transfer (automatic)", "Credit card (automatic)"],
            index=0
        )
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, max_value=1000.0, value=53.85, step=0.01)
        total_charges = st.number_input("Total Charges", min_value=0.0, max_value=50000.0, value=108.15, step=0.01)

    submitted = st.form_submit_button("Predict")

# =========================
# API CALL
# =========================
if submitted:
    payload = {
        "features": {
            "Country": country,
            "State": state,
            "City": city,
            "Gender": gender,
            "Senior Citizen": senior_citizen,
            "Partner": partner,
            "Dependents": dependents,
            "Tenure Months": tenure_months,
            "Phone Service": phone_service,
            "Multiple Lines": multiple_lines,
            "Internet Service": internet_service,
            "Online Security": online_security,
            "Online Backup": online_backup,
            "Device Protection": device_protection,
            "Tech Support": tech_support,
            "Streaming TV": streaming_tv,
            "Streaming Movies": streaming_movies,
            "Contract": contract,
            "Paperless Billing": paperless_billing,
            "Payment Method": payment_method,
            "Monthly Charges": monthly_charges,
            "Total Charges": total_charges,
            "Churn Value": 0
        }
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    with st.spinner("Scoring customer..."):
        try:
            response = requests.post(
                ENDPOINT_URL,
                json=payload,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            st.markdown("---")
            st.subheader("Prediction Result")

            # حاول نقرأ prediction من أكتر من شكل response
            prediction = None
            probability = None

            if isinstance(result, dict):
                if "prediction" in result:
                    prediction = result["prediction"]

                elif "predictions" in result and isinstance(result["predictions"], list) and len(result["predictions"]) > 0:
                    first_pred = result["predictions"][0]

                    if isinstance(first_pred, dict):
                        if "prediction" in first_pred:
                            prediction = first_pred["prediction"]
                        elif "result" in first_pred:
                            prediction = first_pred["result"]
                        elif "value" in first_pred:
                            prediction = first_pred["value"]

                        if "probability" in first_pred:
                            probability = first_pred["probability"]

                        if "probas" in first_pred and isinstance(first_pred["probas"], dict):
                            probability = first_pred["probas"].get("1", first_pred["probas"].get(1, probability))

                elif "result" in result:
                    prediction = result["result"]

                if "probability" in result:
                    probability = result["probability"]

            # تنظيف قيمة prediction
            if isinstance(prediction, str):
                pred_lower = prediction.strip().lower()
                if pred_lower in ["1", "true", "yes"]:
                    prediction = 1
                elif pred_lower in ["0", "false", "no"]:
                    prediction = 0

            # عرض النتيجة
            if prediction == 1:
                st.markdown(
                    '<div class="result-box result-yes">⚠️ Customer WILL churn (Prediction = 1)</div>',
                    unsafe_allow_html=True
                )
            elif prediction == 0:
                st.markdown(
                    '<div class="result-box result-no">✅ Customer will NOT churn (Prediction = 0)</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("Prediction returned, but I could not parse it automatically.")
                st.json(result)

            # عرض الاحتمالية لو موجودة
            if probability is not None:
                try:
                    prob_pct = float(probability) * 100
                    st.info(f"Churn Probability: {prob_pct:.2f}%")
                except Exception:
                    st.info(f"Churn Probability: {probability}")

            # اختياري: عرض الريسبونس الخام للتأكد
            with st.expander("Raw API response"):
                st.json(result)

        except requests.exceptions.HTTPError:
            st.error(f"HTTP Error {response.status_code}")
            try:
                st.json(response.json())
            except Exception:
                st.text(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
