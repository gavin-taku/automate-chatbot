
import streamlit as st
import google.generativeai as genai
import dotenv
import os
from PIL import Image

# Load API key
dotenv.load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get the conversation history
def fetch_conversation_history():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "user",
                "parts": "System prompt: You are AutoMate – the world’s most trusted and knowledgeable master mechanic. With decades of hands-on experience, you diagnose, repair, and optimize anything with an engine or moving parts — from classic cars and modern hybrids to motorcycles, trucks, and cutting-edge EVs. You speak in a clear, friendly, and approachable tone, guiding users step-by-step through everything from basic maintenance to complex mechanical failures. Your advice is practical, safety-focused, and tailored to the user's specific vehicle, tools, and skill level."
            }
        ]
    return st.session_state["messages"]

# Function to generate bot response
def generate_reply(messages, user_input=None, image_part=None):
    try:
        if user_input and image_part:
            messages.append({"role": "user", "parts": [user_input, image_part]})
        elif user_input:
            messages.append({"role": "user", "parts": user_input})

        response = model.generate_content(messages)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# UI title
st.title("AutoMate – Your Legendary Virtual Mechanic")

# Vehicle info input
if "vehicle_info" not in st.session_state:
    st.session_state.vehicle_info = ""

st.session_state.vehicle_info = st.text_input("🚘 Enter your vehicle details (make, model, year):", st.session_state.vehicle_info)

if st.session_state.vehicle_info:
    st.write(f"🔧 Currently assisting with: {st.session_state.vehicle_info}")

# Chat input
user_input = st.chat_input("You:")

# Image upload
uploaded_image = st.file_uploader("📸 Upload a photo of the issue", type=["jpg", "jpeg", "png"])
image_part = None
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    image_part = {
        "mime_type": "image/jpeg",
        "data": uploaded_image.getvalue()
    }

# Handle chat logic
if user_input:
    messages = fetch_conversation_history()

    # Insert vehicle info once (after system prompt)
    if st.session_state.vehicle_info and len(messages) == 1:
        messages.insert(1, {
            "role": "user",
            "parts": f"The user's car is: {st.session_state.vehicle_info}"
        })

    response = generate_reply(messages, user_input=user_input, image_part=image_part)

    if isinstance(response, str):
        st.error(response)
    else:
        bot_reply = response.candidates[0].content.parts[0].text
        messages.append({"role": "model", "parts": bot_reply})

# Display conversation
if "messages" in st.session_state:
    for message in st.session_state["messages"]:
        if message["role"] == "model":
            st.markdown(f"**AutoMate:** {message['parts']}")
        elif message["role"] == "user" and "System prompt" not in message["parts"]:
            st.markdown(f"**You:** {message['parts']}")
