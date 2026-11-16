# FitGenius AI – Fitness Virtual Assistant

A basic AI-powered fitness assistant built with Python, Streamlit and Google's Gemini API.

## Features
- Gemini-powered fitness chat
- User profile and fitness goal inputs
- Estimated BMR, TDEE, BMI and protein planning target
- General diet and workout guidance

## Requirements
- Python 3.10+
- A Gemini API key from https://aistudio.google.com/apikey

## Run locally (Windows)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` and add:

```toml
GEMINI_API_KEY = "YOUR_REAL_API_KEY"
```

Then run:

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal (normally http://localhost:8501).

## GitHub safety
- `.streamlit/secrets.toml` is ignored by Git.
- Never commit or share your real API key.
- Commit `.streamlit/secrets.example.toml` only as a template.

## Deploy
Deploy on Streamlit Community Cloud, select `app.py` as the entry point, and add
`GEMINI_API_KEY` under the app's Secrets settings.

## Disclaimer
Fitness, calorie and protein values are general estimates for educational use.
They are not medical advice or a substitute for a qualified professional.
