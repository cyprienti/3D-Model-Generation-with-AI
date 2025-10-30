import streamlit as st
from streamlit_drawable_canvas import st_canvas
from generio_api import get_3d_model_from_text, get_3d_model_from_png
from streamlit.components.v1 import html
import io
import base64
from PIL import Image

# --- Function to show 3D model ---
def show_3d_model(base64_model: str):
    html_code = f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer
      src="{base64_model}"
      alt="3D Model"
      auto-rotate
      camera-controls
      background-color="#F0F0F0"
      style="width: 100%; height: 500px;">
    </model-viewer>
    """
    html(html_code, height=520)

# --- Page settings ---
st.set_page_config(page_title="Creative Selector", layout="centered")
st.title("Choose how to create your image")

# --- Option selector ---
selected_option = st.session_state.get("selected_option", None)

def card(label, icon, option_number):
    if st.button(f"{icon}\n\n### {label}", key=label, use_container_width=True):
        st.session_state.selected_option = option_number

col1, col2, col3 = st.columns(3)
with col1:
    card("Sketch yourself", "✏️", 1)
with col2:
    card("Import image", "🖼️", 2)
with col3:
    card("Describe your idea", "📝", 3)

selected_option = st.session_state.get("selected_option")
st.markdown("<hr>", unsafe_allow_html=True)

# --- Sketch Option ---
if selected_option == 1:
    st.subheader("🎨 Draw something!")
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 1)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        width=400,
        height=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data, caption="Your sketch", use_column_width=True)
        if st.button("Generate 3D Model"):
            with st.spinner("Processing your sketch..."):
                # Convert canvas to PNG and base64
                img = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
                base64_png = f"data:image/png;base64,{encoded}"

                try:
                    model_base64 = get_3d_model_from_png(base64_png)
                    if model_base64.startswith("data:model/gltf-binary;base64,"):
                        show_3d_model(model_base64)
                    else:
                        st.error("Invalid 3D model format returned.")
                except Exception as e:
                    st.error(f"Error generating model: {str(e)}")

# --- Placeholder for Import ---
elif selected_option == 2:
    st.subheader("🖼️ Upload your image")
    uploaded_file = st.file_uploader("Upload a PNG image", type=["png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGBA")
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Generate 3D Model"):
            with st.spinner("Processing your image..."):
                try:
                    # Convert image to base64
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    base64_png = f"data:image/png;base64,{encoded}"

                    # Get 3D model from image
                    model_base64 = get_3d_model_from_png(base64_png)
                    if model_base64.startswith("data:model/gltf-binary;base64,"):
                        show_3d_model(model_base64)
                    else:
                        st.error("Invalid 3D model format returned.")
                except Exception as e:
                    st.error(f"Error generating model: {str(e)}")

# --- Text prompt option ---
elif selected_option == 3:
    st.subheader("Describe your idea 💡")
    prompt = st.text_area("Write your idea below:", height=150)
    if st.button("Generate Image"):
        if prompt.strip():
            with st.spinner("Generating your image..."):
                try:
                    model_base64 = get_3d_model_from_text(prompt)
                    if model_base64.startswith("data:model/gltf-binary;base64,"):
                        show_3d_model(model_base64)
                    else:
                        st.error("Invalid 3D model format returned.")
                except Exception as e:
                    st.error(f"Error generating model: {str(e)}")
        else:
            st.warning("Please enter a description first.")
else:
    st.write("⬆️ Click an option above or press 1, 2, or 3 on your keyboard.")

# --- Optional keyboard shortcuts ---
st.markdown("""
    <script>
    document.addEventListener("keydown", function(event) {
        if (event.key === "1") {
            window.location.href = "?selected_option=1";
        } else if (event.key === "2") {
            window.location.href = "?selected_option=2";
        } else if (event.key === "3") {
            window.location.href = "?selected_option=3";
        }
    });
    </script>
""", unsafe_allow_html=True)
