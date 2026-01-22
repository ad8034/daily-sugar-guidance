import streamlit as st
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# App Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Daily Sugar Guidance",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# File Path Setup
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "sugar_history.csv")

# -------------------------------------------------
# Constants
# -------------------------------------------------
READING_TYPES = {
    "Fasting (Empty Stomach)": "fasting",
    "After Breakfast": "post_breakfast",
    "After Lunch": "post_lunch",
    "After Dinner": "post_dinner",
    "Random": "random"
}

# Medical thresholds for different reading types (mg/dL)
THRESHOLDS = {
    "fasting": {"low": 70, "normal_max": 100, "borderline_max": 125, "warning": 126},
    "post_breakfast": {"low": 80, "normal_max": 140, "borderline_max": 160, "warning": 161},
    "post_lunch": {"low": 80, "normal_max": 140, "borderline_max": 160, "warning": 161},
    "post_dinner": {"low": 80, "normal_max": 140, "borderline_max": 160, "warning": 161},
    "random": {"low": 70, "normal_max": 120, "borderline_max": 140, "warning": 141}
}

# -------------------------------------------------
# Save Sugar History
# -------------------------------------------------
def save_sugar_history(sugar_value, reading_type):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_data = pd.DataFrame({
        "datetime": [timestamp],
        "reading_type": [reading_type],
        "sugar": [sugar_value]
    })

    if os.path.exists(CSV_PATH):
        old_data = pd.read_csv(CSV_PATH)
        # Handle backwards compatibility - add reading_type column if missing
        if "reading_type" not in old_data.columns:
            old_data["reading_type"] = "random"
        updated_data = pd.concat([old_data, new_data], ignore_index=True)
        updated_data.to_csv(CSV_PATH, index=False)
    else:
        new_data.to_csv(CSV_PATH, index=False)


# -------------------------------------------------
# Smart Insight Logic
# -------------------------------------------------
def get_smart_insight(reading_type):
    if not os.path.exists(CSV_PATH):
        return "No history available yet."

    data = pd.read_csv(CSV_PATH)
    
    # Handle backwards compatibility
    if "reading_type" not in data.columns:
        data["reading_type"] = "random"

    if len(data) < 2:
        return "This is your first entry. Add more daily values to see comparisons."

    today_value = data.iloc[-1]["sugar"]
    yesterday_value = data.iloc[-2]["sugar"]

    if today_value < yesterday_value:
        return f"Good progress. Today's sugar is lower than yesterday by {int(yesterday_value - today_value)} mg/dL."
    elif today_value > yesterday_value:
        return f"Attention needed. Today's sugar is higher than yesterday by {int(today_value - yesterday_value)} mg/dL."
    else:
        return "Your sugar level is the same as yesterday. Maintain your routine."

# -------------------------------------------------
# Sugar Trend Graph
# -------------------------------------------------
def show_sugar_trend(filter_type=None):
    if not os.path.exists(CSV_PATH):
        st.info("No data available to show trends.")
        return

    data = pd.read_csv(CSV_PATH)
    
    # Handle backwards compatibility
    if "reading_type" not in data.columns:
        data["reading_type"] = "random"

    # Filter by reading type if specified
    if filter_type:
        data = data[data["reading_type"] == filter_type]

    if len(data) < 2:
        st.info("Add more daily entries to see your sugar trend.")
        return

    recent_data = data.tail(7)

    # Color coding based on sugar level
    colors = []
    for val in recent_data["sugar"]:
        if val < 70:
            colors.append("red")
        elif 70 <= val <= 100:
            colors.append("green")
        elif 100 < val <= 125:
            colors.append("orange")
        else:
            colors.append("red")

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(
        range(len(recent_data)),
        recent_data["sugar"],
        color=colors,
        alpha=0.8,
        edgecolor="black",
        linewidth=1.5
    )

    ax.axhspan(70, 100, alpha=0.15, color="green", label="Normal Range (70–100 mg/dL)")
    ax.set_title("Blood Sugar Levels Trend", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlabel("Recent Entries", fontsize=11)
    ax.set_ylabel("Sugar Level (mg/dL)", fontsize=11)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    ax.set_xticks(range(len(recent_data)))
    ax.set_xticklabels(recent_data["datetime"], rotation=45, ha='right', fontsize=9)

    plt.tight_layout()
    return fig


# -------------------------------------------------
# Get History Data
# -------------------------------------------------
def get_history_data(limit=5):
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    
    data = pd.read_csv(CSV_PATH)
    
    if "reading_type" not in data.columns:
        data["reading_type"] = "random"
    
    return data.tail(limit).reset_index(drop=True)


# -------------------------------------------------
# Get Status Color
# -------------------------------------------------
def get_status_color(status):
    colors = {
        "CRITICAL LOW": "🔴",
        "LOW": "🔴",
        "NORMAL": "🟢",
        "BORDERLINE": "🟡",
        "HIGH": "🔴"
    }
    return colors.get(status, "⚪")


# -------------------------------------------------
# Dashboard Header
# -------------------------------------------------
st.markdown("""
<style>
    .header-container {
        text-align: center;
        padding: 20px 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 30px;
    }
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin: 0;
    }
    .header-subtitle {
        font-size: 1.1em;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <div class="header-title">🩺 Daily Sugar Guidance Dashboard</div>
    <div class="header-subtitle">Track, Analyze & Manage Your Blood Sugar Levels</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Initialize Session State for Results
# -------------------------------------------------
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "last_result" not in st.session_state:
    st.session_state.last_result = {}


# -------------------------------------------------
# SECTION 1: Today's Entry
# -------------------------------------------------
st.markdown("### 📝 Today's Entry")
st.markdown("---")

with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        reading_type_display = st.selectbox(
            "📌 When was this reading taken?",
            list(READING_TYPES.keys()),
            help="Select the condition under which you took this blood sugar reading"
        )
    
    with col2:
        sugar = st.number_input(
            "🔢 Blood Sugar Level (mg/dL)",
            min_value=0,
            max_value=600,
            step=1,
            help="Enter your blood sugar reading. Example: 85, 110, 165"
        )

    submit = st.button("✅ Get Today's Guidance", use_container_width=True, type="primary")


# -------------------------------------------------
# Process Submission & Show Results
# -------------------------------------------------
if submit:
    reading_type_key = READING_TYPES[reading_type_display]

    if sugar <= 0:
        st.error("❌ Invalid input: Blood sugar must be a positive value.")
        st.stop()

    save_sugar_history(sugar, reading_type_key)

    # Emergency conditions
    if sugar < 40:
        st.error("🚨 Critical Low Blood Sugar")
        st.write("Take a fast-acting sugar source immediately and seek medical help.")
        st.stop()

    if sugar > 400:
        st.error("🚨 Extremely High Blood Sugar")
        st.write("Seek medical attention immediately.")
        st.stop()

    # Get thresholds for this reading type
    threshold = THRESHOLDS[reading_type_key]
    
    # Determine status based on reading type and thresholds
    if sugar < 40:
        status = "CRITICAL LOW"
        color = "🔴"
        meaning = "Your blood sugar is dangerously low. Seek immediate medical help."
        diet_yes = ["Take a fast-acting sugar source immediately."]
        diet_no = []
        activity = "Avoid any physical activity."
        focus = "Restore blood sugar immediately."

    elif sugar < threshold["low"]:
        status = "LOW"
        color = "🔴"
        meaning = f"Your blood sugar is below the normal range for {reading_type_display.lower()}."
        diet_yes = ["Take a quick sugar source such as juice or glucose."]
        diet_no = []
        activity = "Avoid physical activity."
        focus = "Restore blood sugar safely."

    elif sugar <= threshold["normal_max"]:
        status = "NORMAL"
        color = "🟢"
        meaning = f"Your blood sugar is within the healthy range for {reading_type_display.lower()}."
        diet_yes = ["Continue balanced home-cooked meals."]
        diet_no = ["Avoid excess sugar."]
        activity = "15–20 minutes of light walking."
        focus = "Maintain a healthy routine."

    elif sugar <= threshold["borderline_max"]:
        status = "BORDERLINE"
        color = "🟡"
        meaning = f"Your blood sugar is slightly elevated for {reading_type_display.lower()}."
        diet_yes = ["Prefer light meals."]
        diet_no = ["Reduce sugar and refined carbohydrates."]
        activity = "20 minutes of walking."
        focus = "Improve sugar control."

    else:
        status = "HIGH"
        color = "🔴"
        meaning = f"Your blood sugar is high for {reading_type_display.lower()}. Medical attention may be needed if this persists."
        diet_yes = ["Eat light, home-cooked meals."]
        diet_no = ["Avoid sweets, sugary drinks, and high-carb foods."]
        activity = "25–30 minutes of light to moderate walking."
        focus = "Reduce sugar levels safely."

    # Store results in session state
    st.session_state.show_results = True
    st.session_state.last_result = {
        "sugar": sugar,
        "status": status,
        "color": color,
        "meaning": meaning,
        "diet_yes": diet_yes,
        "diet_no": diet_no,
        "activity": activity,
        "focus": focus,
        "reading_type": reading_type_display,
        "reading_type_key": reading_type_key
    }


# -------------------------------------------------
# SECTION 2: Results Display (if available)
# -------------------------------------------------
if st.session_state.show_results:
    st.markdown("")
    st.markdown("### 📊 Today's Results")
    st.markdown("---")
    
    result = st.session_state.last_result
    
    # Status Cards - Top Row
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #f0f5ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #1f77b4;">🩺</div>
            <div style="font-size: 0.9em; color: #666; margin-top: 10px;">Status</div>
            <div style="font-size: 1.8em; font-weight: bold; color: #1f77b4; margin-top: 5px;">{result['color']} {result['status']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color: #fff5f0; padding: 20px; border-radius: 10px; border-left: 5px solid #ff7f0e; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #ff7f0e;">📈</div>
            <div style="font-size: 0.9em; color: #666; margin-top: 10px;">Blood Sugar</div>
            <div style="font-size: 1.8em; font-weight: bold; color: #ff7f0e; margin-top: 5px;">{result['sugar']} mg/dL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color: #f0fff5; padding: 20px; border-radius: 10px; border-left: 5px solid #2ca02c; text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: #2ca02c;">🕐</div>
            <div style="font-size: 0.9em; color: #666; margin-top: 10px;">Reading Type</div>
            <div style="font-size: 1.2em; font-weight: bold; color: #2ca02c; margin-top: 5px;">{result['reading_type']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Meaning Section
    st.markdown("")
    st.markdown("**What This Means**")
    st.info(result['meaning'])
    
    # Recommendations - Two Column Layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**🍽️ Diet Recommendations**")
        for item in result['diet_yes']:
            st.write(f"✔️ {item}")
        for item in result['diet_no']:
            st.write(f"❌ {item}")
    
    with col2:
        st.markdown("**🏃 Physical Activity**")
        st.write(result['activity'])
    
    # Focus Section
    st.markdown("")
    st.markdown("**🎯 Today's Focus**")
    st.success(result['focus'])
    
    # Smart Insight
    st.markdown("")
    st.markdown("**📈 Trend Insight**")
    insight = get_smart_insight(result['reading_type_key'])
    st.info(insight)


# -------------------------------------------------
# SECTION 3: Sugar Trends
# -------------------------------------------------
st.markdown("")
st.markdown("### 📊 Sugar Trends")
st.markdown("---")

with st.container():
    col1, col2 = st.columns([4, 1])
    
    with col2:
        show_trend = st.checkbox("📈 Show Chart", value=True)
        filter_by_type = st.selectbox(
            "Filter by type:",
            ["All"] + list(READING_TYPES.keys()),
            key="trend_filter"
        )
    
    with col1:
        if show_trend:
            filter_value = READING_TYPES[filter_by_type] if filter_by_type != "All" else None
            fig = show_sugar_trend(filter_value)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No data available to show trends.")


# -------------------------------------------------
# SECTION 4: History Preview
# -------------------------------------------------
st.markdown("")
st.markdown("### 📁 Recent History")
st.markdown("---")

history_data = get_history_data(limit=10)

if not history_data.empty:
    # Rename columns for display
    display_data = history_data.copy()
    display_data.columns = ["Date/Time", "Reading Type", "Blood Sugar (mg/dL)"]
    
    # Add status column
    status_list = []
    for sugar_val in history_data["sugar"]:
        if sugar_val < 70:
            status_list.append("🔴 Low")
        elif 70 <= sugar_val <= 100:
            status_list.append("🟢 Normal")
        elif 100 < sugar_val <= 125:
            status_list.append("🟡 Borderline")
        else:
            status_list.append("🔴 High")
    
    display_data.insert(3, "Status", status_list)
    
    # Format reading type for display
    reading_type_reverse = {v: k for k, v in READING_TYPES.items()}
    display_data["Reading Type"] = display_data["Reading Type"].map(
        lambda x: reading_type_reverse.get(x, x)
    )
    
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date/Time": st.column_config.TextColumn("Date/Time", width="medium"),
            "Reading Type": st.column_config.TextColumn("Reading Type", width="medium"),
            "Blood Sugar (mg/dL)": st.column_config.NumberColumn("Blood Sugar (mg/dL)", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small")
        }
    )
else:
    st.info("No history available yet. Submit your first reading to get started!")


# -------------------------------------------------
# SECTION 5: Footer & Info
# -------------------------------------------------
st.markdown("")
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85em; margin-top: 20px;">
    <p>💡 <strong>Disclaimer:</strong> This app provides general guidance only and does not replace professional medical advice. Always consult with a healthcare provider.</p>
</div>
""", unsafe_allow_html=True)

   
