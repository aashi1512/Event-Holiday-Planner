import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import time
import os

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="AI Travel Planner with Gemini",
    page_icon="✈️",
    layout="wide"
)

# ============================================
# CUSTOM STYLING
# ============================================
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #1E88E5, #7B1FA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .ai-badge {
        background: linear-gradient(120deg, #00d2ff, #3a47d5);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 10px;
    }
    .day-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .activity-item {
        background-color: white;
        color: #333;
        padding: 20px;
        margin: 15px 0;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #1E88E5;
    }
    .info-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #1E88E5;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# GOOGLE GEMINI AI SETUP
# ============================================
def setup_gemini_api():
    """Configure Google Gemini AI"""
    api_key = os.getenv("GOOGLE_API_KEY") or st.session_state.get("api_key", "")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            return True
        except Exception as e:
            st.error(f"❌ API Configuration Error: {e}")
            return False
    return False

def generate_itinerary_with_gemini(destination, num_days, num_people, budget, 
                                   interests, group_type, pace, accommodation):
    """Generate itinerary using Google Gemini AI"""
    
    prompt = f"""You are an expert travel planner. Create a detailed {num_days}-day travel itinerary for {destination}.

Trip Details:
- Travelers: {num_people} {group_type}
- Budget: {budget}
- Interests: {', '.join(interests)}
- Pace: {pace}
- Accommodation: {accommodation}

Provide a comprehensive itinerary in JSON format with this EXACT structure:
{{
    "overview": "Brief 3-sentence overview of the destination and what makes it special",
    "daily_itineraries": [
        {{
            "day": 1,
            "title": "Descriptive day title",
            "activities": [
                {{
                    "time": "9:00 AM",
                    "activity": "Activity name",
                    "description": "Detailed description",
                    "duration": "2 hours",
                    "cost": 50
                }}
            ],
            "meals": [
                {{
                    "meal": "breakfast",
                    "restaurant": "Restaurant name",
                    "cuisine": "Cuisine type",
                    "cost": 20
                }}
            ],
            "estimated_cost": 200,
            "travel_tips": "Specific tips for this day"
        }}
    ],
    "famous_attractions": ["attraction1", "attraction2", "..."],
    "local_cuisine": ["dish1", "dish2", "..."],
    "travel_tips": ["tip1", "tip2", "..."],
    "packing_suggestions": ["item1", "item2", "..."],
    "total_estimated_cost": 1500
}}

Important:
- Include 3-4 activities per day for {pace} pace
- All costs in USD
- Make it realistic and specific to {destination}
- Consider {budget} budget level
- Return ONLY valid JSON, no markdown formatting"""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Clean response
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        itinerary = json.loads(text)
        itinerary["destination"] = destination
        
        return itinerary
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse AI response. Please try again.")
        st.expander("Debug Info").write(f"Error: {e}\nResponse: {text[:500]}")
        return None
    except Exception as e:
        st.error(f"❌ AI Error: {str(e)}")
        return None

# ============================================
# HEADER
# ============================================
st.markdown('<h1 class="main-header">✈️ AI Travel Itinerary Planner</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;"><span class="ai-badge">🤖 Powered by Google Gemini AI</span></p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Intelligent travel planning using advanced artificial intelligence</p>', unsafe_allow_html=True)

# ============================================
# API KEY SETUP (Sidebar)
# ============================================
with st.sidebar.expander("🔑 API Key Setup", expanded=not setup_gemini_api()):
    st.markdown("""
    **Get FREE Google Gemini API Key:**
    1. Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    2. Click "Create API Key"
    3. Copy and paste below
    
    ✅ **Completely FREE**  
    ✅ No credit card required  
    ✅ Generous free tier
    """)
    
    api_key_input = st.text_input(
        "Enter Google API Key",
        type="password",
        value=st.session_state.get("api_key", "")
    )
    
    if st.button("Save API Key"):
        st.session_state.api_key = api_key_input
        os.environ["GOOGLE_API_KEY"] = api_key_input
        if setup_gemini_api():
            st.success("✅ API Key configured successfully!")
            st.rerun()

# Check if API is configured
api_configured = setup_gemini_api()

# ============================================
# SIDEBAR INPUTS
# ============================================
st.sidebar.header("🎒 Plan Your Trip")

destination = st.sidebar.text_input(
    "🌍 Destination",
    placeholder="e.g., Paris, Tokyo, Bali",
    help="Enter any city or country"
)

col1, col2 = st.sidebar.columns(2)
num_days = col1.number_input("📅 Days", 1, 30, 5)
num_people = col2.number_input("👥 People", 1, 20, 2)

budget = st.sidebar.select_slider(
    "💰 Budget",
    options=["Low", "Medium", "High"],
    value="Medium"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Preferences")

interests = st.sidebar.multiselect(
    "Interests",
    ["Culture", "Food", "Adventure", "Nature", "Shopping", "History", "Nightlife", "Relaxation"],
    default=["Culture", "Food"]
)

group_type = st.sidebar.selectbox(
    "👨‍👩‍👧‍👦 Group Type",
    ["Solo", "Couple", "Family", "Friends"]
)

pace = st.sidebar.selectbox(
    "⏱️ Travel Pace",
    ["Relaxed", "Moderate", "Packed"]
)

accommodation = st.sidebar.selectbox(
    "🏨 Accommodation",
    ["Budget", "Mid-range", "Luxury"]
)

st.sidebar.markdown("---")
generate_btn = st.sidebar.button("🚀 Generate AI Itinerary", type="primary", disabled=not api_configured)

if not api_configured:
    st.sidebar.warning("⚠️ Please configure API key above")

# ============================================
# MAIN CONTENT
# ============================================
if generate_btn:
    if not destination:
        st.error("⚠️ Please enter a destination!")
    elif not interests:
        st.error("⚠️ Please select at least one interest!")
    else:
        # AI Generation Animation
        with st.status("🤖 AI is analyzing your preferences...", expanded=True) as status:
            st.write("🔍 Understanding your travel style...")
            time.sleep(1)
            st.write("🌍 Researching destination information...")
            time.sleep(1)
            st.write("🧠 AI is processing thousands of possibilities...")
            time.sleep(1)
            st.write("📊 Optimizing itinerary based on your budget...")
            time.sleep(1)
            st.write("✨ Generating personalized recommendations...")
            
            itinerary = generate_itinerary_with_gemini(
                destination, num_days, num_people, budget,
                interests, group_type, pace, accommodation
            )
            
            if itinerary:
                st.session_state.itinerary = itinerary
                status.update(label="✅ AI has created your perfect itinerary!", state="complete")
                st.balloons()
            else:
                status.update(label="❌ Failed to generate itinerary", state="error")

# Display Results
if 'itinerary' in st.session_state:
    data = st.session_state.itinerary
    
    # Overview
    st.markdown(f'## 📍 {data["destination"]}')
    st.markdown(f'<div class="info-box">{data["overview"]}</div>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    total = data["total_estimated_cost"]
    
    with col1:
        st.metric("💵 Total Cost", f"${total:,.0f}")
    with col2:
        st.metric("👤 Per Person", f"${total/num_people:,.0f}")
    with col3:
        st.metric("📅 Duration", f"{num_days} days")
    with col4:
        st.metric("🎯 Activities", len(data.get("famous_attractions", [])))
    
    st.markdown("---")
    
    # Daily Itineraries
    st.markdown("## 📅 Your AI-Generated Itinerary")
    
    for day_data in data["daily_itineraries"]:
        st.markdown(f'<div class="day-card">', unsafe_allow_html=True)
        st.markdown(f"### Day {day_data['day']}: {day_data['title']}")
        st.markdown(f"**Daily Budget:** ${day_data['estimated_cost']:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🎯 Activities")
        for act in day_data["activities"]:
            st.markdown(f"""
            <div class="activity-item">
                <h4>⏰ {act['time']} - {act['activity']}</h4>
                <p>{act['description']}</p>
                <p><small>⏱️ {act['duration']} | 💰 ${act['cost']}</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 🍽️ Dining")
        meal_cols = st.columns(len(day_data["meals"]))
        for idx, meal in enumerate(day_data["meals"]):
            meal_cols[idx].markdown(f"""
            **{meal['meal'].title()}**  
            🍴 {meal['restaurant']}  
            🌍 {meal['cuisine']}  
            💰 ${meal['cost']}
            """)
        
        st.info(f"💡 {day_data['travel_tips']}")
        st.markdown("")
    
    st.markdown("---")
    
    # Additional Info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏛️ Must-Visit Attractions")
        for i, attr in enumerate(data["famous_attractions"], 1):
            st.markdown(f"{i}. {attr}")
        
        st.markdown("### 🍜 Local Cuisine")
        for i, dish in enumerate(data["local_cuisine"], 1):
            st.markdown(f"{i}. {dish}")
    
    with col2:
        st.markdown("### 💡 Travel Tips")
        for i, tip in enumerate(data["travel_tips"], 1):
            st.markdown(f"{i}. {tip}")
        
        st.markdown("### 🎒 Packing List")
        for i, item in enumerate(data["packing_suggestions"], 1):
            st.markdown(f"{i}. {item}")
    
    st.markdown("---")
    
    # Download
    st.markdown("### 💾 Export Your Itinerary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 Download JSON",
            json.dumps(data, indent=2),
            f"ai_itinerary_{destination.replace(' ', '_')}.json",
            "application/json"
        )
    
    with col2:
        text = f"AI-GENERATED ITINERARY: {data['destination']}\n{'='*60}\n\n"
        text += f"OVERVIEW:\n{data['overview']}\n\n"
        text += f"TOTAL COST: ${data['total_estimated_cost']}\n\n"
        for day in data['daily_itineraries']:
            text += f"\nDAY {day['day']}: {day['title']}\n"
            text += f"Budget: ${day['estimated_cost']}\n\n"
            for act in day['activities']:
                text += f"  {act['time']} - {act['activity']}\n"
                text += f"    {act['description']}\n"
            text += "\n"
        
        st.download_button(
            "📄 Download TXT",
            text,
            f"ai_itinerary_{destination.replace(' ', '_')}.txt"
        )
    
    with col3:
        if st.button("🔄 Generate New"):
            del st.session_state.itinerary
            st.rerun()

else:
    # Welcome Screen
    st.markdown("### 🤖 AI-Powered Travel Planning")
    
    col1, col2, col3 = st.columns(3)
    col1.markdown("#### 🧠 Machine Learning\nAdvanced AI algorithms analyze your preferences")
    col2.markdown("#### 🎯 Personalized\nCustom itineraries based on your unique needs")
    col3.markdown("#### ⚡ Instant Results\nGenerate complete plans in seconds")
    
    st.markdown("---")
    
    if not api_configured:
        st.warning("⚠️ **Get started:** Configure your FREE Google Gemini API key in the sidebar to unlock AI-powered planning!")
    else:
        st.success("✅ **Ready to go!** Fill in your travel details and generate your AI itinerary.")
    
    st.markdown("#### 🌟 Popular Destinations")
    destinations = ["Paris, France", "Tokyo, Japan", "New York, USA", "Bali, Indonesia"]
    cols = st.columns(4)
    for i, dest in enumerate(destinations):
        cols[i].button(dest, key=f"dest_{i}", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎓 <b>AI & Expert Systems Project</b></p>
    <p>Powered by Google Gemini AI | Natural Language Processing | Machine Learning</p>
    <p><small>Using generative AI for intelligent travel recommendations</small></p>
</div>
""", unsafe_html=True)