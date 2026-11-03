import streamlit as st
import os

# --- 1. PREMIUM CHECK SYSTEM ---
# (Make sure this matches how you track premium users in your main app)
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False

# Sidebar for testing or entering the activation key
st.sidebar.title("⭐ Account Status")
activation_code = st.sidebar.text_input("Enter Premium Code:", type="password")

if activation_code == "TA_PREMIUM_2026":
    st.session_state.is_premium = True
    st.sidebar.success("Premium Active!")
else:
    st.session_state.is_premium = False
    st.sidebar.info("Type 'TA_PREMIUM_2026' to simulate a premium user.")


# --- 2. AI WORKSPACE ASSISTANT INTERFACE ---
st.title("🤖 TA Workspaces AI Assistant")
st.write("Ask our AI about the best local spots, review summaries, or job hunting tips.")

# BLOCKED: If the user is NOT premium, show a locked screen
if not st.session_state.is_premium:
    st.error("🔒 AI Assistant is a Premium-Only Feature!")
    st.markdown("""
    ### Upgrade to Premium to unlock:
    * **Instant Review Summaries:** Ask the AI to read through hundreds of workspace reviews for you.
    * **Smart Recommendations:** Get custom lists of the best places to work based on your exact needs.
    * **Interview & Resume Prep:** Chat with an AI trained to help you get hired locally.
    """)
    
# UNLOCKED: If the user IS premium, render the full AI Chatbot
else:
    st.success("🎉 Welcome to your Premium AI Assistant!")

    # Initialize chat history inside the user's session so it doesn't disappear when they type
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hi Tristan! I'm your TA Workspaces AI. How can I help you find the perfect place to work today?"}
        ]

    # Display all previous messages in the chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Accept real-time user input
    if user_prompt := st.chat_input("Ask me anything about local workspaces..."):
        
        # Display the user's message immediately
        with st.chat_message("user"):
            st.write(user_prompt)
        
        # Append user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # --- 3. SIMULATING THE AI RESPONSE ---
        # Note: To make this real, you would plug in your API key here.
        # For now, we'll create a smart automated response builder!
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                
                # Simple smart keyword recognition for testing
                lowered_prompt = user_prompt.lower()
                if "quiet" in lowered_prompt or "starbucks" in lowered_prompt:
                    ai_response = "Based on recent TA Workspaces data, the Starbucks on Main Street gets a 4.5/5 on noise insulation around 2:00 PM, but internet speeds drop slightly during peak hours."
                elif "resume" in lowered_prompt or "job" in lowered_prompt:
                    ai_response = "Great question! When applying to local workspaces, make sure your resume explicitly highlights your reliability and any previous customer service or technical experience."
                else:
                    ai_response = f"I received your request: '{user_prompt}'. Once Tristan connects my main API brain, I will pull live data directly from the Supabase database to answer this perfectly!"
                
                st.write(ai_response)
                
        # Append AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
