import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from llm_translator import get_basic_translation
from database import get_db
from translations import get_text, TRANSLATIONS
from onboarding import handle_onboarding, show_curriculum_overview, CLASSES, LANGUAGES, SUBJECTS_BY_CLASS
from teaching_agent import create_teaching_agent
from test_ai import show_enhanced_tests_page


# Page Configuration
st.set_page_config(
    page_title="Shiksha Mitra - AI Learning Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = get_db()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'current_language' not in st.session_state:
    st.session_state.current_language = "English"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'navigation_target' not in st.session_state:
    st.session_state.navigation_target = None
if 'teaching_agent' not in st.session_state:
    st.session_state.teaching_agent = None
if 'current_lesson' not in st.session_state:
    st.session_state.current_lesson = None
if 'practice_problems' not in st.session_state:
    st.session_state.practice_problems = []
if 'textbooks_ingested' not in st.session_state:
    st.session_state.textbooks_ingested = False

# Theme Configuration
DARK_THEME = {
    'bg': '#0a1628',
    'secondary_bg': '#1e3a5f',
    'accent': '#3b82f6',
    'text': '#e0e7ff',
    'card_bg': '#1e3a5f',
    'border': '#3b82f6'
}

LIGHT_THEME = {
    'bg': '#ffffff',
    'secondary_bg': '#f0f7ff',
    'accent': '#2563eb',
    'text': '#1e3a5f',
    'card_bg': '#f0f7ff',
    'border': '#3b82f6'
}

theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME

# Custom CSS
bg_color = theme['bg']
secondary_bg = theme['secondary_bg']
accent_color = theme['accent']
text_color = theme['text']
card_bg = theme['card_bg']
border_color = theme['border']

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {{
        font-family: 'Poppins', sans-serif;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, {bg_color} 0%, {secondary_bg} 100%);
        transition: all 0.3s ease;
    }}
    
    .main-header {{
        background: linear-gradient(90deg, {accent_color} 0%, #1e40af 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        animation: slideDown 0.5s ease;
    }}
    
    @keyframes slideDown {{
        from {{ transform: translateY(-30px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    .metric-card {{
        background: {card_bg};
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid {accent_color};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin: 0.5rem 0;
        animation: fadeIn 0.6s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: scale(0.95); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    
    .lesson-card {{
        background: {card_bg};
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid {border_color};
        margin: 1rem 0;
        line-height: 1.8;
    }}
    
    .practice-problem {{
        background: {secondary_bg};
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #f59e0b;
    }}
    
    h1, h2, h3 {{
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)


def get_profile_field(profile, field_name, default=''):
    """Helper function to get profile field with fallback"""
    if not profile:
        return default
    
    field_mappings = {
        'full_name': ['full_name', 'name'],
        'name': ['name', 'full_name'],
        'class_number': ['class_number', 'class'],
        'class': ['class', 'class_number']
    }
    
    if field_name in profile and profile[field_name]:
        return profile[field_name]
    
    if field_name in field_mappings:
        for alt_name in field_mappings[field_name]:
            if alt_name in profile and profile[alt_name]:
                return profile[alt_name]
    
    return default


def show_latency_badge(latency_ms):
    """Show latency badge (helper function)"""
    if latency_ms < 500:
        st.success(f"⚡ Ultra-fast response: {latency_ms:.0f}ms")
    elif latency_ms < 1000:
        st.info(f"⏱ Fast response: {latency_ms:.0f}ms")
    else:
        st.warning(f"⏳ Response time: {latency_ms:.0f}ms")


def initialize_teaching_agent():
    """Initialize the Teaching Agent with Groq API"""
    if st.session_state.teaching_agent is None:
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            st.sidebar.warning("⚙ GROQ API Key not configured")
            with st.sidebar.expander("Configure API Key"):
                api_key_input = st.text_input("Enter Groq API Key", type="password")
                if st.button("Save API Key"):
                    if api_key_input:
                        os.environ["GROQ_API_KEY"] = api_key_input
                        api_key = api_key_input
                        st.success("API Key saved!")
                        st.rerun()
                
                st.info("Get your free API key from: https://console.groq.com")
            return False
        
        try:
            st.session_state.teaching_agent = create_teaching_agent(api_key)
            return True
        except Exception as e:
            st.sidebar.error(f"Error initializing Teaching Agent: {str(e)}")
            return False
    return True


def ingest_textbooks_for_user():
    """Ingest textbooks for current user's class and subjects"""
    if st.session_state.textbooks_ingested:
        return True
    
    profile = st.session_state.user_profile
    if not profile:
        return False
    
    agent = st.session_state.teaching_agent
    class_num = get_profile_field(profile, 'class_number')
    subjects = profile.get('subjects', [])
    
    if not class_num or not subjects:
        return False
    
    with st.spinner("📚 Loading textbooks into AI system..."):
        for subject in subjects:
            try:
                success, msg = agent.ingest_textbook(
                    class_num=int(class_num),
                    subject=subject,
                    language=st.session_state.current_language
                )
                if not success:
                    st.warning(f"Note: {msg}")
            except Exception as e:
                st.warning(f"Could not load {subject} textbook: {str(e)}")
        
        st.session_state.textbooks_ingested = True
    
    return True


def show_login_page():
    """Display login/signup page"""
    lang = st.session_state.current_language
    
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>🌱</h1>
        <h1>{get_text('welcome_title', lang)}</h1>
        <p style='font-size: 1.2rem; opacity: 0.8;'>
            {get_text('welcome_subtitle', lang)}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    selected_lang = st.selectbox(
        get_text('preferred_language', lang),
        list(TRANSLATIONS.keys()),
        index=list(TRANSLATIONS.keys()).index(st.session_state.current_language)
    )
    if selected_lang != st.session_state.current_language:
        st.session_state.current_language = selected_lang
        st.rerun()
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs([get_text('login', lang), get_text('signup', lang)])
    
    with tab1:
        with st.form("login_form"):
            st.subheader(get_text('login', lang))
            username = st.text_input(get_text('username', lang))
            password = st.text_input(get_text('password', lang), type="password")
            submit = st.form_submit_button(get_text('login_button', lang), use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("Please fill all fields!")
                else:
                    success, user_id = db.authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        profile = db.get_user_profile(user_id)
                        st.session_state.user_profile = profile
                        
                        if profile and profile.get('language'):
                            st.session_state.current_language = profile['language']
                        
                        db.update_streak(user_id)
                        st.success(get_text('login_success', lang))
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(get_text('invalid_credentials', lang))
    
    with tab2:
        with st.form("signup_form"):
            st.subheader(get_text('signup', lang))
            new_username = st.text_input(get_text('username', lang), key="signup_username")
            new_email = st.text_input(get_text('email', lang), key="signup_email")
            new_password = st.text_input(get_text('password', lang), type="password", key="signup_password")
            confirm_password = st.text_input(get_text('confirm_password', lang), type="password")
            submit_signup = st.form_submit_button(get_text('signup_button', lang), use_container_width=True, type="primary")
            
            if submit_signup:
                if not new_username or not new_password:
                    st.error("Please fill required fields!")
                elif new_password != confirm_password:
                    st.error(get_text('password_mismatch', lang))
                else:
                    success, msg, user_id = db.create_user(new_username, new_password, new_email)
                    if success:
                        st.success(get_text('signup_success', lang))
                        st.info("Please login with your credentials")
                    else:
                        st.error(msg)


def show_profile_setup():
    """Show profile setup page for new users"""
    lang = st.session_state.current_language
    profile = st.session_state.user_profile
    
    full_name = get_profile_field(profile, 'full_name')
    class_number = get_profile_field(profile, 'class_number')
    
    if full_name and class_number:
        return True
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>{get_text('lets_start', lang)}</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Complete your profile to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("profile_setup"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name_input = st.text_input(get_text('whats_your_name', lang), value=full_name)
        
        with col2:
            language = st.selectbox(
                get_text('preferred_language', lang),
                list(LANGUAGES.keys()),
                index=list(LANGUAGES.keys()).index(st.session_state.current_language)
            )
        
        class_selected = st.selectbox(get_text('which_class', lang), list(CLASSES.keys()), index=0)
        submit = st.form_submit_button(get_text('start_learning', lang), use_container_width=True, type="primary")
        
        if submit:
            if not full_name_input:
                st.error(get_text('enter_name_error', lang))
            else:
                class_num = CLASSES[class_selected]
                subjects = SUBJECTS_BY_CLASS.get(class_num, [])
                
                success, msg = db.create_or_update_profile(
                    st.session_state.user_id,
                    full_name_input,
                    class_num,
                    language,
                    subjects
                )
                
                if success:
                    st.session_state.user_profile = db.get_user_profile(st.session_state.user_id)
                    st.session_state.current_language = language
                    st.success(f"{get_text('welcome_aboard', lang)}, {full_name_input}! 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(msg)
    
    return False


def show_ai_teacher_page():
    """Show the AI Teacher page with RAG-powered lessons"""
    lang = st.session_state.current_language
    profile = st.session_state.user_profile
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>🧠 AI Teacher - Smart Lessons</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Personalized lessons from your textbooks</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize agent
    if not initialize_teaching_agent():
        return
    
    # Ingest textbooks if not done
    if not st.session_state.textbooks_ingested:
        ingest_textbooks_for_user()
    
    agent = st.session_state.teaching_agent
    class_num = get_profile_field(profile, 'class_number')
    subjects = profile.get('subjects', [])
    
    # Learning Summary
    col1, col2, col3, col4 = st.columns(4)
    summary = agent.get_learning_summary()
    
    with col1:
        st.metric("📚 Lessons Completed", summary['lessons_completed'])
    with col2:
        st.metric("💬 Questions Asked", summary['questions_asked'])
    with col3:
        st.metric("🎯 Comprehension Level", f"{summary['current_comprehension']}/10")
    with col4:
        st.metric("📈 Progress", summary.get('progress', 'Good'))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lesson Generator
    st.subheader("📖 Create New Lesson")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_subject = st.selectbox("Subject", subjects if subjects else ["Mathematics"])
    with col2:
        topic_input = st.text_input("Topic", placeholder="e.g., Fractions, Photosynthesis")
    with col3:
        local_context = st.text_input("Local Context", value="farming and rural life")
    
    if st.button("🚀 Generate Lesson", use_container_width=True, type="primary"):
        if not topic_input:
            st.error("Please enter a topic!")
        else:
            with st.spinner("🧠 Creating your personalized lesson..."):
                result = agent.create_micro_lesson(
                    topic=topic_input,
                    student_class=int(class_num),
                    subject=selected_subject,
                    language=lang,
                    local_context=local_context
                )
                
                if result['success']:
                    st.session_state.current_lesson = result
                    st.success("✅ Lesson created!")
                    st.rerun()
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    # Display current lesson
    if st.session_state.current_lesson:
        lesson = st.session_state.current_lesson
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        accent = theme['accent']
        txt_color = theme['text']
        lesson_text = lesson['lesson'].replace('\n', '<br>')
        sources_text = ', '.join(lesson.get('sources', ['AI Generated']))
        
        st.markdown(f"""
        <div class='lesson-card'>
            <h3 style='color: {accent};'>📚 {lesson['topic']}</h3>
            <p style='color: {txt_color}; opacity: 0.8; margin-bottom: 1rem;'>
                Difficulty: {lesson.get('difficulty', 5)}/10 | Sources: {sources_text}
            </p>
            <div style='color: {txt_color}; line-height: 1.8;'>
                {lesson_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive Q&A
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💬 Ask Questions")
        
        student_question = st.text_input("Have a question about this topic?", key="student_question")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🤔 Get Explanation", use_container_width=True):
                if student_question:
                    with st.spinner("Thinking..."):
                        result = agent.explain_adaptively(
                            concept=lesson['topic'],
                            student_question=student_question,
                            class_num=int(class_num),
                            subject=selected_subject,
                            language=lang
                        )
                        
                        if result['success']:
                            explanation_text = result['explanation'].replace('\n', '<br>')
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h4 style='color: {accent};'>Teacher's Explanation:</h4>
                                <p style='color: {txt_color}; line-height: 1.8;'>
                                    {explanation_text}
                                </p>
                                <p style='opacity: 0.7; margin-top: 1rem;'>
                                    Your comprehension level: {result.get('comprehension_level', 5)}/10
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("Please enter a question!")
        
        with col2:
            if st.button("🎯 Generate Practice Problems", use_container_width=True):
                with st.spinner("Creating practice problems..."):
                    result = agent.generate_practice_problems(
                        topic=lesson['topic'],
                        class_num=int(class_num),
                        subject=selected_subject,
                        count=3
                    )
                    
                    if result['success']:
                        st.session_state.practice_problems = result['problems']
                        st.rerun()
    
    # Display practice problems
    if st.session_state.practice_problems:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🎯 Practice Problems")
        
        for i, problem in enumerate(st.session_state.practice_problems, 1):
            with st.expander(f"Problem {i} - Difficulty: {problem.get('difficulty', 5)}/10"):
                prob_text = theme['text']
                st.markdown(f"""
                <div class='practice-problem'>
                    <h4 style='color: {prob_text};'>Question:</h4>
                    <p style='color: {prob_text}; margin-bottom: 1rem;'>{problem.get('question', problem.get('q', 'Problem'))}</p>
                    
                    <h4 style='color: #f59e0b;'>Hint:</h4>
                    <p style='color: {prob_text}; opacity: 0.8;'>{problem.get('hint', 'Think carefully')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                user_answer = st.text_area(f"Your answer for Problem {i}:", key=f"answer_{i}")
                
                if st.button(f"Submit Answer {i}", key=f"submit_{i}"):
                    if user_answer:
                        with st.spinner("Assessing..."):
                            result = agent.assess_comprehension(
                                student_response=user_answer,
                                correct_answer=problem.get('solution', problem.get('ans', ''))
                            )
                            
                            if result['success']:
                                assessment = result['assessment']
                                score = assessment.get("score", 5)
                                bg_assess = "#22c55e22" if score >= 7 else "#f59e0b22"
                                
                                st.markdown(f"""
                                <div class='metric-card' style='background: {bg_assess};'>
                                    <h4>Score: {score}/10</h4>
                                    <p><strong>✅ What you got right:</strong><br>{assessment.get('understood', 'Good effort')}</p>
                                    <p><strong>📝 Needs work:</strong><br>{assessment.get('needs_work', 'Practice more')}</p>
                                    <p><strong>💡 Feedback:</strong><br>{assessment.get('feedback', 'Keep learning')}</p>
                                    <p><strong>🎯 Next step:</strong><br>{assessment.get('next_step', 'Try similar problems')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.info(f"Adjusted comprehension level: {result.get('updated_difficulty', 5)}/10")
                    else:
                        st.warning("Please write your answer first!")
                
                with st.expander("Show solution"):
                    solution = problem.get('solution', problem.get('ans', 'Solution not available'))
                    st.markdown(f"*Solution:*\n\n{solution}")


def show_classes_page(lang=None, theme=None):
    """Show interactive classes"""
    if lang is None:
        lang = st.session_state.current_language
    if theme is None:
        theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>🎓 Interactive Classes</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Learn with AI-powered live lessons</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📺 Live Classes", "📼 Recorded", "📅 Schedule"])
    
    with tab1:
        st.info("🔴 No live classes at the moment")
        st.subheader("Upcoming Live Classes")
        
        classes_data = [
            {"subject": "Mathematics", "topic": "Quadratic Equations", "time": "Today, 4:00 PM", "teacher": "Mr. Sharma"},
            {"subject": "Science", "topic": "Chemical Reactions", "time": "Tomorrow, 3:00 PM", "teacher": "Ms. Patel"},
            {"subject": "English", "topic": "Essay Writing", "time": "Tomorrow, 5:00 PM", "teacher": "Mrs. Kumar"}
        ]
        
        for class_info in classes_data:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {theme['accent']};'>{class_info['subject']}</h3>
                <p><strong>Topic:</strong> {class_info['topic']}</p>
                <p><strong>Time:</strong> {class_info['time']}</p>
                <p><strong>Teacher:</strong> {class_info['teacher']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Recently Recorded Classes")
        recorded = [
            {"subject": "Mathematics", "topic": "Trigonometry", "date": "2 days ago"},
            {"subject": "Science", "topic": "Electricity", "date": "3 days ago"},
            {"subject": "English", "topic": "Grammar", "date": "5 days ago"}
        ]
        for rec in recorded:
            st.markdown(f"**{rec['subject']}:** {rec['topic']} • {rec['date']}")
    
    with tab3:
        st.subheader("📅 Weekly Schedule")
        schedule_df = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            '3:00 PM': ['Math', 'Science', 'Math', 'English', 'History'],
            '4:00 PM': ['Science', 'English', 'History', 'Math', 'Science'],
            '5:00 PM': ['English', 'History', 'Science', 'Geo', 'Math']
        })
        st.dataframe(schedule_df, use_container_width=True, hide_index=True)



def show_tests_page(lang, theme):
    pass


def show_doubt_ai_page(lang=None, theme=None):
    """Real-time doubt clearing with Groq - WITH TRANSLATION"""
    if lang is None:
        lang = st.session_state.current_language
    if theme is None:
        theme = DARK_THEME if st.session_state.dark_mode else LIGHT_THEME
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>💬 Doubt AI - Ask Anything</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>⚡ Instant answers powered by Groq</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not initialize_teaching_agent():
        return
    
    agent = st.session_state.teaching_agent
    profile = st.session_state.user_profile
    class_num = int(get_profile_field(profile, 'class_number', 10))
    subjects = profile.get('subjects', ['Mathematics'])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_subject = st.selectbox("Subject", subjects, key="doubt_subject")
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        user_question = st.chat_input("Ask your doubt...")
        
        if user_question:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_question})
            with st.chat_message("user"):
                st.write(user_question)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking and translating..."):
                    # Get explanation from agent
                    result = agent.explain_adaptively(
                        concept="Student Question",
                        student_question=user_question,
                        class_num=class_num,
                        subject=selected_subject,
                        language=lang  # Pass the language for translation
                    )
                    
                    if result["success"]:
                        # Get the translated response
                        response_text = result['explanation']
                        
                        # Display response
                        st.write(response_text)
                        
                        # Show language info
                        if lang.lower() != "english":
                            st.caption(f"🌍 Translated to: {lang}")
                        
                        # Add to message history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "language": lang
                        })
                        
                        # Award XP
                        try:
                            db.add_xp(st.session_state.user_id, 10)
                        except:
                            pass
                    else:
                        error_msg = f"Error: {result.get('error', 'Unknown error')}"
                        st.error(error_msg)
            
            st.rerun()
    
    with col2:
        # Show subjects in sidebar
        st.markdown(f"""
        <div class='metric-card'>
            <h4>Your Subjects</h4>
            {'<br>'.join(['📚 ' + s for s in subjects[:5]])}
        </div>
        """, unsafe_allow_html=True)
        
        # Show current language
        st.markdown(f"""
        <div class='metric-card'>
            <h4>🌍 Language</h4>
            <p>{lang}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clear chat button
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

def show_analytics_page(lang, theme, stats):
    """Show detailed analytics page"""
    accent_color = theme['accent']
    text_color = theme['text']
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>📊 {get_text('analytics', lang)}</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Track your learning journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Study Time", "156 hours", "+12h this week")
    with col2:
        st.metric("Lessons Completed", "89", "+7 this week")
    with col3:
        st.metric("Average Score", "84%", "+3%")
    with col4:
        st.metric("Streak", f"{stats.get('current_streak', 12)} days", "+1")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Monthly Progress
    st.subheader("📈 Monthly Progress")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    study_hours = [45, 52, 48, 58, 62, 71]
    lessons = [15, 18, 16, 21, 24, 28]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=study_hours, mode='lines+markers', name='Study Hours', line=dict(color=accent_color, width=3)))
    fig.add_trace(go.Scatter(x=months, y=lessons, mode='lines+markers', name='Lessons Completed', line=dict(color='#f59e0b', width=3)))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': text_color},
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Subject Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Time by Subject")
        
        subjects = ['Mathematics', 'Science', 'English', 'History', 'Geography']
        time_spent = [35, 28, 22, 18, 15]
        
        fig = go.Figure(data=[go.Pie(labels=subjects, values=time_spent, hole=.3)])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': text_color},
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Performance by Subject")
        
        performance = [85, 88, 92, 78, 81]
        
        fig = go.Figure(data=[
            go.Scatterpolar(r=performance, theta=subjects, fill='toself', line=dict(color=accent_color))
        ])
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': text_color},
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)


def show_gamified_page(lang, theme, stats):
    """Show gamification page with achievements and rewards"""
    accent_color = theme['accent']
    text_color = theme['text']
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>🎮 Gamified Learning</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Earn rewards and unlock achievements!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Level and XP
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: {text_color};'>🏆 Level</h3>
            <p style='font-size: 3rem; color: {accent_color}; margin: 0;'>7</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: {text_color};'>⭐ Total XP</h3>
            <p style='font-size: 3rem; color: {accent_color}; margin: 0;'>{stats.get('total_xp', 2450)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: {text_color};'>🎯 Next Level</h3>
            <p style='font-size: 1.5rem; color: {accent_color}; margin: 0;'>350 XP to go</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(0.65)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Achievements
    st.subheader("🏆 Achievements")
    
    achievements = [
        {"title": "First Steps", "desc": "Complete your first lesson", "icon": "✅", "unlocked": True},
        {"title": "Week Warrior", "desc": "Maintain 7-day streak", "icon": "🔥", "unlocked": True},
        {"title": "Perfect Score", "desc": "Get 100% in a test", "icon": "💯", "unlocked": True},
        {"title": "Speed Learner", "desc": "Complete 10 lessons in a day", "icon": "⚡", "unlocked": False},
        {"title": "Master Mind", "desc": "Reach Level 10", "icon": "🧠", "unlocked": False},
        {"title": "Consistent", "desc": "30-day streak", "icon": "📅", "unlocked": False}
    ]
    
    cols = st.columns(3)
    for idx, achievement in enumerate(achievements):
        with cols[idx % 3]:
            opacity = "1" if achievement['unlocked'] else "0.3"
            border_color = accent_color if achievement['unlocked'] else text_color
            
            st.markdown(f"""
            <div class='metric-card' style='opacity: {opacity}; border-color: {border_color};'>
                <h1 style='font-size: 3rem; margin: 0;'>{achievement['icon']}</h1>
                <h4 style='color: {text_color}; margin: 0.5rem 0;'>{achievement['title']}</h4>
                <p style='color: {text_color}; opacity: 0.8; font-size: 0.9rem;'>{achievement['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Leaderboard
    st.subheader("👥 Leaderboard (This Week)")
    
    leaderboard_data = pd.DataFrame({
        'Rank': ['🥇', '🥈', '🥉', '4', '5'],
        'Student': ['You', 'Priya S.', 'Rahul K.', 'Amit P.', 'Sneha M.'],
        'XP': [2450, 2380, 2250, 2100, 2050],
        'Streak': ['12 🔥', '15 🔥', '10 🔥', '8 🔥', '6 🔥']
    })
    
    st.dataframe(leaderboard_data, use_container_width=True, hide_index=True)


def show_settings_page(lang, theme):
    """Show settings page"""
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>⚙ {get_text('settings', lang)}</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Customize your learning experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🎨 Preferences", "🔔 Notifications"])
    
    with tab1:
        st.subheader("Profile Information")
        
        with st.form("profile_update"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Full Name", value=get_profile_field(st.session_state.user_profile, 'full_name'))
                st.selectbox("Class", list(CLASSES.keys()))
            with col2:
                st.text_input("Email", value=st.session_state.user_profile.get('email', '') if st.session_state.user_profile else '')
                st.selectbox("Language", list(LANGUAGES.keys()))
            
            if st.form_submit_button("Update Profile", type="primary"):
                st.success("Profile updated successfully!")
    
    with tab2:
        st.subheader("Learning Preferences")
        
        st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        st.slider("Daily Study Goal (hours)", 1, 6, 2)
        st.multiselect("Favorite Subjects", ["Mathematics", "Science", "English", "History", "Geography"])
        st.checkbox("Enable AI Hints")
        st.checkbox("Show Detailed Explanations")
        
        if st.button("Save Preferences", type="primary"):
            st.success("Preferences saved!")
    
    with tab3:
        st.subheader("Notification Settings")
        
        st.checkbox("Class Reminders", value=True)
        st.checkbox("Assignment Due Dates", value=True)
        st.checkbox("Test Notifications", value=True)
        st.checkbox("Achievement Unlocked", value=True)
        st.checkbox("Daily Study Reminder", value=False)
        
        st.time_input("Reminder Time", value=datetime.strptime("18:00", "%H:%M").time())
        
        if st.button("Save Notification Settings", type="primary"):
            st.success("Notification settings saved!")


def show_main_app():
    """Main application after authentication"""
    profile = st.session_state.user_profile
    lang = st.session_state.current_language
    stats = db.get_user_stats(st.session_state.user_id)
    
    user_name = get_profile_field(profile, 'full_name', 'Student')
    user_class = get_profile_field(profile, 'class_number', '')
    
    # Sidebar
    accent = theme['accent']
    txt = theme['text']
    
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem;'>
            <h1 style='color: {accent}; font-size: 2.5rem;'>🌱</h1>
            <h2 style='color: {txt}; margin-top: 0;'>Shiksha Mitra</h2>
            <p style='color: {txt}; opacity: 0.8; font-size: 0.9rem;'>
                {user_name} • {get_text('class', lang)} {user_class}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        theme_col1, theme_col2 = st.columns([1, 2])
        with theme_col1:
            st.write("🌙" if st.session_state.dark_mode else "☀")
        with theme_col2:
            if st.button(get_text('toggle_theme', lang)):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        st.markdown("---")
        
        default_pages = [
            f"🏠 {get_text('dashboard', lang)}",
            f"🧠 AI Teacher (NEW!)",
            f"🎓 {get_text('class', lang)}",
            f"🧪 {get_text('test', lang)}",
            f"💬 {get_text('doubt_ai', lang)}",
            f"📊 {get_text('analytics', lang)}",
            f"🎮 Gamified",
            f"⚙ {get_text('settings', lang)}"
        ]
        
        default_index = 0
        if st.session_state.navigation_target:
            for idx, page_name in enumerate(default_pages):
                if st.session_state.navigation_target in page_name:
                    default_index = idx
                    break
            st.session_state.navigation_target = None
        
        page = st.radio("Navigate", default_pages, index=default_index, label_visibility="collapsed")
        
        st.markdown("---")
        
        current_streak = stats.get('current_streak', 12)
        total_xp = stats.get('total_xp', 250)
        
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: {txt}; margin: 0;'>{get_text('learning_streak', lang)}</h4>
            <p style='font-size: 2rem; margin: 0.5rem 0; color: {accent};'>
                🔥 {current_streak} {get_text('days', lang)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='metric-card'>
            <h4 style='color: {txt}; margin: 0;'>{get_text('today_xp', lang)}</h4>
            <p style='font-size: 2rem; margin: 0.5rem 0; color: {accent};'>⭐ {total_xp} XP</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button(get_text('logout', lang), use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_profile = None
            st.session_state.messages = []
            st.session_state.teaching_agent = None
            st.session_state.current_lesson = None
            st.session_state.practice_problems = []
            st.rerun()
    
    # Main Content
    if "🧠 AI Teacher" in page:
        show_ai_teacher_page()
    
    elif "🏠" in page:  # Dashboard
        st.markdown(f"""
        <div class='main-header'>
            <h1 style='color: white; margin: 0;'>{get_text('hello', lang)} {user_name}! 👋</h1>
            <p style='color: #e0e7ff; font-size: 1.2rem; margin-top: 0.5rem;'>
                {get_text('ready_learning', lang)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        txt_color = theme['text']
        accent_color = theme['accent']
        sec_bg = theme['secondary_bg']
        border = theme['border']
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=68,
                title={'text': get_text('overall_progress', lang), 'font': {'color': txt_color}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': accent_color},
                    'bgcolor': sec_bg,
                    'borderwidth': 2,
                    'bordercolor': border
                },
                number={'font': {'color': txt_color}}
            ))
            fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': txt_color})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {txt_color};'>📚 {get_text('classes', lang)}</h3>
                <p style='font-size: 2.5rem; color: {accent_color}; margin: 0.5rem 0;'>24</p>
                <p style='color: {txt_color}; opacity: 0.8;'>{get_text('completed', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {txt_color};'>⏱ {get_text('study_time', lang)}</h3>
                <p style='font-size: 2.5rem; color: {accent_color}; margin: 0.5rem 0;'>42h</p>
                <p style='color: {txt_color}; opacity: 0.8;'>{get_text('this_month', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3 style='color: {txt_color};'>💪 {get_text('confidence', lang)}</h3>
                <p style='font-size: 2.5rem; color: {accent_color}; margin: 0.5rem 0;'>85%</p>
                <p style='color: {txt_color}; opacity: 0.8;'>{get_text('growing', lang)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Weekly Progress Chart
        st.subheader(f"📈 {get_text('weekly_progress', lang)}")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        study_hours = [2.5, 3.0, 2.0, 4.0, 3.5, 1.5, 2.5]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days,
            y=study_hours,
            marker_color=accent_color,
            text=study_hours,
            textposition='auto',
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': txt_color},
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent Activity
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"🎯 {get_text('recent_activity', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='color: {txt_color};'>✅ Completed Today</h4>
                <ul style='color: {txt_color};'>
                    <li>Mathematics: Algebra basics</li>
                    <li>Science: Photosynthesis</li>
                    <li>English: Grammar exercises</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h4 style='color: {txt_color};'>🎯 Upcoming Tasks</h4>
                <ul style='color: {txt_color};'>
                    <li>History: Complete Chapter 5</li>
                    <li>Science: Practice quiz</li>
                    <li>Math: Solve word problems</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    elif "🎓" in page:  # Classes
        show_classes_page(lang, theme)
    
    elif "🧪" in page:  # Tests
        show_enhanced_tests_page(lang, theme, db, st.session_state.user_id)
    
    elif "💬" in page:  # Doubt AI
        show_doubt_ai_page(lang, theme)
    
    elif "📊" in page:  # Analytics
        show_analytics_page(lang, theme, stats)
    
    elif "🎮" in page:  # Gamified
        show_gamified_page(lang, theme, stats)
    
    elif "⚙" in page:  # Settings
        show_settings_page(lang, theme)


def main():
    """Main application flow"""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Check if profile is complete
        if not show_profile_setup():
            return
        
        # Show main application
        show_main_app()


if __name__ == "__main__":
    main()