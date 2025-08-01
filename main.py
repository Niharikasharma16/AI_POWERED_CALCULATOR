import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import numpy as np
import google.generativeai as genai
import json
import ast

# ─────────────────────────────────────────────
# Configure Gemini API
genai.configure(api_key="ENTER YOUR API KEY")  # Replace with your actual Gemini API key

# ─────────────────────────────────────────────
# Streamlit UI
st.set_page_config(page_title="AI POWERED CALCULATOR", layout="centered")
st.title("🧠 AI-POWERED CACLULATOR- MATHS SOLVER USING GEMINI")

st.sidebar.header("🎨 Drawing Tools")
pen_color = st.sidebar.color_picker("Pen Color", "#FFFF00")
stroke_width = st.sidebar.slider("Pen Width", 1, 50, 7)
bg_color = st.sidebar.color_picker("Canvas Background", "#000000")
drawing_mode = st.sidebar.selectbox("Drawing Mode", ["freedraw", "transform"])
clear_canvas = st.sidebar.button("🗑️ Clear Canvas")

# ─────────────────────────────────────────────
# Canvas
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=stroke_width,
    stroke_color=pen_color,
    background_color=bg_color,
    update_streamlit=True,
    height=500,
    width=500,
    drawing_mode=drawing_mode,
    key="canvas",
)

# ─────────────────────────────────────────────
# Image Preparation
byte_im = None
if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # Show download option
    st.download_button(
        label="⬇️ Download Drawing as PNG",
        data=byte_im,
        file_name="drawing.png",
        mime="image/png"
    )

# ─────────────────────────────────────────────
# Solve Image with Gemini
def analyze_image(image_bytes):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    prompt = (
        "You are a math problem solver. The user has drawn a math problem on the canvas and uploaded the image. "
        "Your job is to identify the mathematical expression or diagram and solve it. "
        "Return the result in the form of a list of dictionaries like [{'expr': '2 + 2', 'result': 4}] or any suitable format. "
        "Avoid using markdown or unnecessary text. Just provide the clean response in JSON-style Python list/dict. "
        "You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction. "
        f"For example: "
        f"Q. 2 + 3 * 4 "
        f"(3 * 4) => 12, 2 + 12 = 14. "
        f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
        f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
        f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
        f"Following are the cases: "
        f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT ]. "
        f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, This example assumes x was calculated as 2, and y as 5. Include as many dicts as there are variables. "
        f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called , keeping the variable as 'expr' and the value as 'result' in the original dictionary. RETURN AS A LIST OF DICTS. "
        f"4. Analyzing Graphical Math problems, which are word problems represented in drawing form, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc. These will have a drawing representing some scenario and accompanying information with the image. PAY CLOSE ATTENTION TO DIFFERENT COLORS FOR THESE PROBLEMS. You need to return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
        f"5. Detecting Abstract Concepts that a drawing might show, such as love, hate, jealousy, patriotism, or a historic reference to war, invention, discovery, quote, etc. USE THE SAME FORMAT AS OTHERS TO RETURN THE ANSWER, where 'expr' will be the explanation of the drawing, and 'result' will be the abstract concept. "
        f"Analyze the equation or expression in this image and return the answer according to the given rules: "
        f"Make sure to use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
        f"Here is a dictionary of user-assigned variables. If the given expression has any of these variables, use its actual value from this dictionary accordingly. "
        f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
        f"PROPERLY QUOTE THE KEYS AND VALUES IN THE DICTIONARY FOR EASIER PARSING WITH Python's ast.literal_eval."
    )

    image = Image.open(io.BytesIO(image_bytes))
    response = model.generate_content([prompt, image])
    
    try:
        parsed = ast.literal_eval(response.text)
    except Exception as e:
        st.error(f"❌ Could not parse Gemini response: {e}")
        st.text("Raw response:")
        st.text(response.text)
        return []
    
    return parsed

# ─────────────────────────────────────────────
# Trigger solve button
if st.button("🔍 Solve Drawing with Gemini"):
    if byte_im:
        answers = analyze_image(byte_im)
        if answers:
            st.success("✅ Solved!")
            for item in answers:
                st.write(f"🧮 **Expression:** `{item['expr']}` → **Answer:** `{item['result']}`")
        else:
            st.warning("Gemini didn't return a valid result.")
    else:
        st.error("❌ No image found. Please draw something first.")
        
        
st.write(answers)
