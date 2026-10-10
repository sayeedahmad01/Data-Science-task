import streamlit as st
import pandas as pd
import joblib

# ---------- Page setup ----------
st.set_page_config(page_title="Student Result Predictor", page_icon="🎓", layout="centered")

st.title("🎓 Student Result Predictor")
st.write(
    "This tool predicts whether a student is likely to **Pass** or **Fail** "
    "based on study habits and background info. Fill in the fields below and click **Predict**."
)

# ---------- Load model (cached so it only loads once) ----------
@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

bundle = load_model()
model = bundle["model"]
encoders = bundle["encoders"]
columns = bundle["columns"]

# ---------- Build input form ----------
st.subheader("Enter student details")

col1, col2 = st.columns(2)
inputs = {}

# Friendly labels + reasonable min/max for numeric fields
field_config = {
    "study_hours": {"label": "Study hours per week", "min": 0.0, "max": 40.0, "default": 10.0},
    "attendance_pct": {"label": "Attendance (%)", "min": 0.0, "max": 100.0, "default": 75.0},
    "previous_score": {"label": "Previous exam score", "min": 0.0, "max": 100.0, "default": 60.0},
    "extra_curricular": {"label": "Participates in extracurricular activities?"},
    "internet_access": {"label": "Has internet access at home?"},
}

for i, col in enumerate(columns):
    target_col = col1 if i % 2 == 0 else col2
    cfg = field_config.get(col, {})
    label = cfg.get("label", col)

    if col in encoders:
        options = list(encoders[col].classes_)
        inputs[col] = target_col.selectbox(label, options)
    else:
        inputs[col] = target_col.number_input(
            label,
            min_value=cfg.get("min", 0.0),
            max_value=cfg.get("max", 100.0),
            value=cfg.get("default", 0.0),
        )

st.divider()

# ---------- Predict ----------
if st.button("🔮 Predict Result", type="primary", use_container_width=True):
    row = {}
    for col in columns:
        if col in encoders:
            row[col] = encoders[col].transform([inputs[col]])[0]
        else:
            row[col] = inputs[col]

    input_df = pd.DataFrame([row])[columns]
    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    confidence = max(probabilities) * 100

    if prediction == "Pass":
        st.success(f"### ✅ Prediction: {prediction}")
    else:
        st.error(f"### ❌ Prediction: {prediction}")

    st.write(f"**Confidence:** {confidence:.1f}%")
    st.progress(confidence / 100)

    with st.expander("See details"):
        st.write("Input used for prediction:")
        st.dataframe(pd.DataFrame([inputs]))

st.divider()
st.caption("Built with a Random Forest model · For educational demonstration purposes only.")
