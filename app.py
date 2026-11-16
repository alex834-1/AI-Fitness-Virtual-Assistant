import streamlit as st
from google import genai
from google.genai import types
MODEL = "gemini-3.1-flash-lite"

st.set_page_config(page_title="FitGenius AI", page_icon="💪", layout="wide")

st.markdown("""
<style>
.stApp { background: #10131a; color: #f4f6fb; }
[data-testid="stSidebar"] { background: #191e29; }
.hero { padding: 8px 0 2px 0; }
.hero h1 { color: #7CFC98; font-size: 2.5rem; margin-bottom: 0; }
.hero p { color: #aab3c2; margin-top: 4px; }
div[data-testid="stMetric"] {
  background: #202735; border: 1px solid #303b4d;
  padding: 14px; border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Gemini client setup ----------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

client = genai.Client(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
You are FitGenius, a friendly general-purpose fitness education assistant.
Help with exercise planning, general nutrition, calories, protein, muscle gain,
fat loss and healthy habits. Use the user's profile when relevant. Be practical,
clear and encouraging. State that nutrition and calorie estimates are approximate.
Do not diagnose, prescribe treatment, recommend steroids, extreme diets or
dangerous supplements. For medical conditions, injuries, pregnancy, eating
disorders or concerning symptoms, recommend consulting a qualified clinician.
Do not present yourself as a doctor or certified personal trainer.
If the request is unrelated to fitness, politely steer the conversation back.
"""

st.sidebar.title("💪 FitGenius AI")
st.sidebar.caption("Your personal AI fitness companion")
st.sidebar.divider()
st.sidebar.subheader("Fitness profile")

name = st.sidebar.text_input("Name", "User")
age = st.sidebar.number_input("Age", min_value=15, max_value=100, value=20)
weight = st.sidebar.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=69.0, step=0.5)
height = st.sidebar.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=185.0, step=0.5)
sex = st.sidebar.selectbox("Sex used for BMR estimate", ["Male", "Female"])
activity = st.sidebar.selectbox("Activity level", [
    "Sedentary", "Lightly active", "Moderately active", "Very active", "Extra active"
])
goal = st.sidebar.selectbox("Fitness goal", ["Muscle gain", "Weight loss", "Maintain weight"])
diet = st.sidebar.selectbox("Diet preference", ["Vegetarian", "Non-vegetarian", "Vegan"])

activity_factors = {
    "Sedentary": 1.2,
    "Lightly active": 1.375,
    "Moderately active": 1.55,
    "Very active": 1.725,
    "Extra active": 1.9,
}

# Mifflin-St Jeor estimate; this is not a clinical measurement.
sex_constant = 5 if sex == "Male" else -161
bmr = 10 * weight + 6.25 * height - 5 * age + sex_constant
tdee = bmr * activity_factors[activity]
if goal == "Muscle gain":
    calorie_target = tdee + 250
elif goal == "Weight loss":
    calorie_target = tdee - 300
else:
    calorie_target = tdee

# A broad planning estimate, not a prescription.
protein_target = weight * 1.6
bmi = weight / ((height / 100) ** 2)

st.markdown("""
<div class="hero">
<h1>💪 FitGenius AI</h1>
<p>Your AI-powered fitness and nutrition companion</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Estimated calorie target", f"{calorie_target:.0f} kcal/day")
m2.metric("Protein planning estimate", f"{protein_target:.0f} g/day")
m3.metric("Estimated BMR", f"{bmr:.0f} kcal/day")
m4.metric("BMI", f"{bmi:.1f}")

st.caption("Estimates only. Actual needs vary with health, body composition and training.")
st.divider()

tab_chat, tab_calc, tab_about = st.tabs(["🤖 AI Fitness Chat", "📊 Fitness Calculator", "ℹ️ About"])

with tab_chat:
    st.subheader("Chat with your AI fitness assistant")
    st.write("Ask about workout routines, balanced meals, protein, calories or healthy habits.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("E.g. Suggest a vegetarian muscle-gain meal plan...")
    if prompt:
        if client is None:
            st.error("Configure GEMINI_API_KEY in .streamlit/secrets.toml before using AI chat.")
            st.stop()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        profile = f"""
User profile supplied for this conversation:
Name: {name}
Age: {age}
Weight: {weight} kg
Height: {height} cm
Sex used for BMR estimate: {sex}
Activity: {activity}
Goal: {goal}
Diet preference: {diet}
Estimated BMR: {bmr:.0f} kcal/day
Estimated TDEE: {tdee:.0f} kcal/day
Estimated goal calorie target: {calorie_target:.0f} kcal/day
Protein planning estimate: {protein_target:.0f} g/day
"""

        history = []
        for msg in st.session_state.messages:
            role = "model" if msg["role"] == "assistant" else "user"
            history.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))

        with st.chat_message("assistant"):
            try:
                with st.spinner("FitGenius is preparing a response..."):
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=history,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT + "\n" + profile,
                            temperature=0.6,
                            max_output_tokens=1200,
                        ),
                    )
                    answer = response.text or "I couldn't produce a response. Please try again."
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as exc:
                st.error("The Gemini request failed. Check your API key, internet connection and model availability.")
                st.caption(str(exc))

with tab_calc:
    st.subheader("Your fitness estimates")
    left, right = st.columns(2)
    with left:
        st.markdown("### 🔥 Energy")
        st.write(f"**BMR:** {bmr:.0f} kcal/day")
        st.write(f"**TDEE:** {tdee:.0f} kcal/day")
        st.write(f"**Goal estimate:** {calorie_target:.0f} kcal/day")
    with right:
        st.markdown("### 🥗 Nutrition")
        st.write(f"**Protein planning estimate:** {protein_target:.0f} g/day")
        st.write(f"**BMI:** {bmi:.1f}")
        if bmi < 18.5:
            st.info("BMI screening category: below the usual adult range.")
        elif bmi < 25:
            st.success("BMI screening category: usual adult range.")
        elif bmi < 30:
            st.warning("BMI screening category: above the usual adult range.")
        else:
            st.warning("BMI screening category: high. Consider professional guidance.")
    st.info("BMR uses the Mifflin-St Jeor equation. TDEE multiplies BMR by an activity factor. These are rough estimates, not medical advice.")

with tab_about:
    st.subheader("About FitGenius AI")
    st.write("""
FitGenius AI is a basic LLM-powered fitness virtual assistant built with Python,
Streamlit and Google's Gemini API.

**Main functions**
- Natural-language fitness Q&A using Gemini
- User profile and fitness goal inputs
- Estimated BMR, TDEE, BMI and protein planning target
- General diet and workout guidance

**Academic concepts demonstrated**
- Large Language Model (LLM) integration
- Prompt engineering
- API-based application development
- Python calculations and interactive UI
""")
    st.success("Project interface loaded. Configure your Gemini API key to enable AI chat.")

