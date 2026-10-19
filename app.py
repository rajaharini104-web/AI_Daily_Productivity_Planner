import os
from datetime import datetime, timedelta

import streamlit as st
from groq import Groq


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="AI Daily Productivity Planner",
    page_icon="📅",
    layout="wide"
)


# -----------------------------------------
# GROQ MODEL CONFIGURATION
# -----------------------------------------

# Check the current Groq model list if this ID
# is unavailable to your account.
MODEL_NAME = "openai/gpt-oss-120b"


def get_api_key():
    """Get the API key from Streamlit Secrets or environment."""

    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.environ.get("GROQ_API_KEY", "")

    return key


# -----------------------------------------
# CUSTOM STYLING
# -----------------------------------------

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fb;
    }

    .main-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        color: #243b55;
    }

    .subtitle {
        text-align: center;
        font-size: 17px;
        color: #526579;
        margin-bottom: 25px;
    }

    .info-box {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dce4ee;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------
# HEADER
# -----------------------------------------

st.markdown(
    '<div class="main-title">'
    '📅 AI Daily Productivity Planner'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Plan your day intelligently, balance focused work with breaks, '
    'and make time for what matters.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# -----------------------------------------
# USER INPUTS
# -----------------------------------------

st.subheader("🎯 Customize Your Daily Schedule")

with st.form("productivity_form"):

    col1, col2 = st.columns(2)

    with col1:
        wake_up = st.time_input(
            "🌅 Wake-up Time",
            value=datetime.strptime("06:00", "%H:%M").time()
        )

        sleep_time = st.time_input(
            "🌙 Target Bedtime",
            value=datetime.strptime("22:00", "%H:%M").time()
        )

        work_start = st.time_input(
            "💻 Work or Study Start Time",
            value=datetime.strptime("09:00", "%H:%M").time()
        )

        work_end = st.time_input(
            "🏁 Work or Study End Time",
            value=datetime.strptime("17:00", "%H:%M").time()
        )

    with col2:
        goals = st.text_area(
            "📝 Your Daily Goals",
            placeholder=(
                "Example:\n"
                "1. Complete Python practice\n"
                "2. Study for college exams\n"
                "3. Work on my project\n"
                "4. Exercise for 30 minutes"
            ),
            height=160
        )

        priorities = st.selectbox(
            "⭐ Main Priority",
            [
                "Study and Learning",
                "Work and Career",
                "College and Projects",
                "Health and Fitness",
                "Balanced Daily Routine"
            ]
        )

        break_style = st.selectbox(
            "☕ Preferred Break Style",
            [
                "Short breaks every 25 minutes",
                "Breaks every 50 minutes",
                "Flexible breaks"
            ]
        )

        energy_level = st.selectbox(
            "⚡ When are you most productive?",
            [
                "Morning",
                "Afternoon",
                "Evening",
                "Throughout the day"
            ]
        )

    additional_notes = st.text_input(
        "Additional Requirements (Optional)",
        placeholder=(
            "Example: Include travel time, meals, family time, "
            "or a one-hour exercise session."
        )
    )

    submitted = st.form_submit_button(
        "✨ Generate My Daily Plan",
        use_container_width=True
    )


# -----------------------------------------
# GENERATE THE PRODUCTIVITY PLAN
# -----------------------------------------

if submitted:

    if not goals.strip():
        st.warning("Please enter at least one daily goal.")

    elif sleep_time <= wake_up:
        st.error(
            "For this version, bedtime must be later than wake-up "
            "time on the same day."
        )

    elif work_end <= work_start:
        st.error(
            "Work or study end time must be later than its start time."
        )

    elif work_start < wake_up or work_end > sleep_time:
        st.error(
            "Your work or study hours must fit between your "
            "wake-up time and bedtime."
        )

    elif not get_api_key():
        st.error(
            "Groq API key not found. Add GROQ_API_KEY "
            "to your Streamlit Cloud Secrets."
        )

    else:

        api_key = get_api_key()
        client = Groq(api_key=api_key)

        prompt = f"""
You are an expert daily productivity planner.

Create a realistic, personalized DAILY TIMETABLE using the
following information.

USER DETAILS:
- Wake-up time: {wake_up.strftime("%I:%M %p")}
- Target bedtime: {sleep_time.strftime("%I:%M %p")}
- Work/study start: {work_start.strftime("%I:%M %p")}
- Work/study end: {work_end.strftime("%I:%M %p")}
- Daily goals: {goals}
- Main priority: {priorities}
- Preferred break style: {break_style}
- Most productive time: {energy_level}
- Additional requirements: {additional_notes or "None"}

REQUIREMENTS:

1. Create a timetable covering the user's day from wake-up
   to bedtime.

2. Display the plan in chronological order.

3. Include hourly time blocks with start and end times.

4. Allocate enough time to the user's stated goals.

5. Include suitable breaks, meals, and personal time.

6. Follow the preferred break style where practical.

7. Schedule demanding tasks around the user's preferred
   productive time.

8. Avoid overlapping activities.

9. Do not schedule work or study outside the stated work
   or study hours unless the user explicitly requests it.

10. Include a reasonable wind-down routine before bedtime.

11. Make the timetable practical, not unrealistically busy.

12. If all goals cannot fit into the available time, identify
    which goals should be prioritized.

OUTPUT FORMAT:

# Your Personalized Daily Plan

## 1. Hourly Timetable

Create a Markdown table with these columns:
- Time
- Activity
- Duration
- Purpose

Include the full day from wake-up to bedtime.

## 2. Top Three Priorities

List the three most important tasks for the day.

## 3. Work-Break Balance

Explain how focused work, short breaks, and longer breaks
are balanced.

## 4. Productivity Tips

Give five practical tips tailored to this user's goals.

## 5. End-of-Day Review

Give three questions the user can ask themselves
before going to bed.

Keep the output clear, supportive, and easy to follow.
"""

        try:

            with st.spinner(
                "🤖 Creating your personalized daily schedule..."
            ):

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a practical productivity "
                                "assistant. Create realistic schedules "
                                "that balance focused work, breaks, "
                                "meals, and personal well-being."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.4,
                    max_tokens=4000
                )

                plan = response.choices[0].message.content

            if not plan:
                st.warning(
                    "The AI returned an empty response. Please try again."
                )

            else:

                st.success("Your daily productivity plan is ready!")

                st.subheader("🗓️ Your Personalized Schedule")

                st.markdown(plan)

                st.download_button(
                    label="📥 Download My Daily Plan",
                    data=plan,
                    file_name="daily_productivity_plan.md",
                    mime="text/markdown",
                    use_container_width=True
                )

                st.caption(
                    "Your plan is a suggested schedule. Adjust it "
                    "to suit your real commitments and energy levels."
                )

        except Exception as error:

            message = str(error)
            lower_message = message.lower()

            if (
                "model_not_found" in lower_message
                or "404" in message
            ):
                st.error(
                    "The selected model is unavailable. Check the "
                    "current Groq model list and update MODEL_NAME."
                )

            elif (
                "authentication" in lower_message
                or "invalid_api_key" in lower_message
                or "401" in message
            ):
                st.error(
                    "API authentication failed. Check your "
                    "GROQ_API_KEY in Streamlit Secrets."
                )

            elif "429" in message:
                st.error(
                    "The API usage or rate limit was reached. "
                    "Check your Groq account limits and try again later."
                )

            else:
                st.error(
                    "Unable to generate your schedule. "
                    "Check your API configuration and try again."
                )

                with st.expander("Technical details"):
                    st.code(message)


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.markdown(
    """
    <p style="text-align:center; color:#64748b;">
        📅 AI Daily Productivity Planner |
        Built with Python, Streamlit and Groq
    </p>
    """,
    unsafe_allow_html=True
)