import streamlit as st
import requests
import random

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Cell C Churn Predictor",
    page_icon="📊",
    layout="wide"
)

# =========================
# CONFIG
# =========================
ENDPOINT_URL = "https://api-2c61e5b3-2928c99d-dku.eu-west-2.app.dataiku.io/public/api/v1/telco-churn-service/predict-churn/predict"
API_KEY = "PUT_YOUR_API_KEY_HERE"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Cell_C_New_2024_logo.svg/1280px-Cell_C_New_2024_logo.svg.png"

# =========================
# HELPERS
# =========================
def normalize_prediction(value):
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        if value in [0, 1]:
            return int(value)

    if isinstance(value, str):
        v = value.strip().lower()
        if v in ["1", "true", "yes", "churn", "will churn"]:
            return 1
        if v in ["0", "false", "no", "not churn", "will not churn"]:
            return 0
    return None


def extract_prediction_data(api_response):
    prediction = None
    churn_probability = None
    percentile = None

    if not isinstance(api_response, dict):
        return prediction, churn_probability, percentile

    # الشكل الأشهر: result.prediction
    if isinstance(api_response.get("result"), dict):
        result_obj = api_response["result"]
        prediction = normalize_prediction(result_obj.get("prediction"))

        probas = result_obj.get("probas")
        if isinstance(probas, dict):
            churn_probability = probas.get("1", probas.get(1))

        percentile = result_obj.get("probaPercentile")

    # لو جت flat
    if prediction is None and "prediction" in api_response:
        prediction = normalize_prediction(api_response.get("prediction"))

    if churn_probability is None and "probability" in api_response:
        churn_probability = api_response.get("probability")

    # لو فيه predictions list
    if prediction is None and isinstance(api_response.get("predictions"), list) and api_response["predictions"]:
        first_pred = api_response["predictions"][0]
        if isinstance(first_pred, dict):
            prediction = normalize_prediction(
                first_pred.get("prediction", first_pred.get("result", first_pred.get("value")))
            )

            if churn_probability is None:
                if "probability" in first_pred:
                    churn_probability = first_pred["probability"]
                elif isinstance(first_pred.get("probas"), dict):
                    churn_probability = first_pred["probas"].get("1", first_pred["probas"].get(1))

    try:
        if churn_probability is not None:
            churn_probability = float(churn_probability)
    except Exception:
        churn_probability = None

    return prediction, churn_probability, percentile


def call_api_with_fallback(payload):
    errors = []

    # 1) Bearer auth
    try:
        response = requests.post(
            ENDPOINT_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=20
        )
        if response.ok:
            return {
                "success": True,
                "source": "API",
                "response_json": response.json()
            }
        else:
            errors.append(f"Bearer auth failed: HTTP {response.status_code} - {response.text[:300]}")
    except Exception as e:
        errors.append(f"Bearer auth exception: {str(e)}")

    # 2) Basic auth
    try:
        response = requests.post(
            ENDPOINT_URL,
            json=payload,
            auth=(API_KEY, ""),
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        if response.ok:
            return {
                "success": True,
                "source": "API",
                "response_json": response.json()
            }
        else:
            errors.append(f"Basic auth failed: HTTP {response.status_code} - {response.text[:300]}")
    except Exception as e:
        errors.append(f"Basic auth exception: {str(e)}")

    # 3) Fallback random demo result
    fake_prediction = random.choice([0, 1])

    if fake_prediction == 1:
        fake_probability = round(random.uniform(0.60, 0.95), 4)
    else:
        fake_probability = round(random.uniform(0.05, 0.40), 4)

    fake_percentile = int(fake_probability * 100)

    return {
        "success": False,
        "source": "DEMO_FALLBACK",
        "response_json": {
            "result": {
                "prediction": str(fake_prediction),
                "probas": {
                    "0": round(1 - fake_probability, 4),
                    "1": fake_probability
                },
                "probaPercentile": fake_percentile
            },
            "debug": {
                "reason": "API call failed, switched to demo fallback mode",
                "errors": errors
            }
        }
    }


# =========================
# STYLING
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
    }

    .hero-card {
        background: white;
        border-radius: 22px;
        padding: 24px 28px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        margin-bottom: 18px;
        border: 1px solid #eaeef3;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 6px;
        color: #111827;
    }

    .sub-title {
        color: #6b7280;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-card {
        background: white;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.05);
        border: 1px solid #eaeef3;
        margin-bottom: 16px;
    }

    .result-box {
        padding: 22px;
        border-radius: 18px;
        font-size: 26px;
        font-weight: 800;
        text-align: center;
        margin-top: 14px;
        margin-bottom: 12px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.06);
    }

    .result-yes {
        background: linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%);
        color: #9f1239;
        border: 1px solid #fecdd3;
    }

    .result-no {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: #065f46;
        border: 1px solid #a7f3d0;
    }

    .metric-card {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
    }

    .metric-title {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827;
    }

    .demo-warning {
        background: #fff7ed;
        border: 1px solid #fdba74;
        color: #9a3412;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 14px;
        font-weight: 600;
    }

    div.stButton > button {
        width: 100%;
        height: 3.2em;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 700;
        border: none;
        background: linear-gradient(90deg, #111827 0%, #1f2937 100%);
        color: white;
        box-shadow: 0 8px 18px rgba(17,24,39,0.15);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown('<div class="hero-card">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 4])

with c1:
    st.image(LOGO_URL, width=180)

with c2:
    st.markdown('<div class="main-title">Cell C Churn Predictor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">AI-powered churn scoring with automatic demo fallback</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FORM
# =========================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("Customer Details")

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

    submitted = st.form_submit_button("Predict Churn")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# RUN PREDICTION
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
            "Total Charges": total_charges
        }
    }

    with st.spinner("Scoring customer..."):
        result_package = call_api_with_fallback(payload)

    api_result = result_package["response_json"]
    source = result_package["source"]

    prediction, churn_probability, percentile = extract_prediction_data(api_result)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Prediction Result")

    if source == "DEMO_FALLBACK":
        st.markdown(
            '<div class="demo-warning">Demo Mode: The API is unavailable, so this result is randomly generated for presentation purposes only.</div>',
            unsafe_allow_html=True
        )

    if prediction == 1:
        st.markdown(
            '<div class="result-box result-yes">⚠️ Customer WILL churn</div>',
            unsafe_allow_html=True
        )
        recommendation = "Recommended action: retention offer, customer callback, or service recovery plan."
    elif prediction == 0:
        st.markdown(
            '<div class="result-box result-no">✅ Customer will NOT churn</div>',
            unsafe_allow_html=True
        )
        recommendation = "Recommended action: standard engagement and routine monitoring."
    else:
        st.warning("Prediction could not be parsed.")
        recommendation = "Please review the raw response."

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Prediction</div>
                <div class="metric-value">{prediction if prediction is not None else "N/A"}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        prob_text = "N/A"
        if churn_probability is not None:
            prob_text = f"{churn_probability * 100:.1f}%"

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Churn Probability</div>
                <div class="metric-value">{prob_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        percentile_text = f"{percentile}%" if percentile is not None else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Percentile</div>
                <div class="metric-value">{percentile_text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if churn_probability is not None:
        st.markdown("##### Confidence")
        st.progress(max(0.0, min(1.0, churn_probability)))

    st.info(recommendation)

    with st.expander("Raw Response / Debug"):
        st.json(api_result)

    st.markdown('</div>', unsafe_allow_html=True)
