# onboarding.py
"""
Student Onboarding Module for Shiksha Mitra
Handles initial setup: language, class, and loads curriculum data
"""

import streamlit as st
import json
from typing import Dict, List, Optional

# NCERT Class Structure
CLASSES = {
    "Class 1": 1,
    "Class 2": 2,
    "Class 3": 3,
    "Class 4": 4,
    "Class 5": 5,
    "Class 6": 6,
    "Class 7": 7,
    "Class 8": 8,
    "Class 9": 9,
    "Class 10": 10,
    "Class 11": 11,
    "Class 12": 12,
}

LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "ಕನ್ನಡ (Kannada)": "kn",
    "తెలుగు (Telugu)": "te",
    "தமிழ் (Tamil)": "ta",
    "मराठी (Marathi)": "mr",
    "বাংলা (Bengali)": "bn",
    "ગુજરાતી (Gujarati)": "gu",
}

# Subject mapping by class
SUBJECTS_BY_CLASS = {
    1: ["Mathematics", "English", "Hindi", "Environmental Studies"],
    2: ["Mathematics", "English", "Hindi", "Environmental Studies"],
    3: ["Mathematics", "English", "Hindi", "Environmental Studies"],
    4: ["Mathematics", "English", "Hindi", "Environmental Studies"],
    5: ["Mathematics", "English", "Hindi", "Environmental Studies"],
    6: ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit"],
    7: ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit"],
    8: ["Mathematics", "Science", "Social Science", "English", "Hindi", "Sanskrit"],
    9: ["Mathematics", "Science", "Social Science", "English", "Hindi", "Information Technology"],
    10: ["Mathematics", "Science", "Social Science", "English", "Hindi", "Information Technology"],
    11: ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Computer Science", "Accountancy", "Business Studies", "Economics"],
    12: ["Physics", "Chemistry", "Mathematics", "Biology", "English", "Computer Science", "Accountancy", "Business Studies", "Economics"],
}

# Educational video platforms and channels
VIDEO_RESOURCES = {
    "DIKSHA": {
        "url": "https://diksha.gov.in",
        "description": "National digital education platform with curriculum-aligned content",
        "languages": ["English", "Hindi", "Kannada", "Telugu", "Tamil", "Marathi", "Bengali", "Gujarati"],
        "qr_scan": True
    },
    "Khan Academy India": {
        "url": "https://india.khanacademy.org",
        "description": "Free high-quality educational content in multiple Indian languages",
        "languages": ["English", "Hindi", "Kannada", "Punjabi", "Marathi", "Gujarati", "Assamese"],
        "subjects": ["Mathematics", "Science", "Computing"]
    },
    "E-Pathshala": {
        "url": "https://epathshala.nic.in",
        "description": "NCERT's official platform with 2000+ videos and eBooks",
        "languages": ["English", "Hindi", "Urdu"],
        "ncert_aligned": True
    },
    "SWAYAM": {
        "url": "https://swayam.gov.in",
        "description": "Free courses from Class 9 to post-graduation",
        "languages": ["English", "Hindi"],
        "for_classes": [9, 10, 11, 12]
    },
    "NPTEL": {
        "url": "https://nptel.ac.in",
        "description": "IIT/IISc lectures for advanced learning (Class 11-12)",
        "languages": ["English"],
        "for_classes": [11, 12],
        "subjects": ["Physics", "Chemistry", "Mathematics", "Computer Science"]
    }
}

# YouTube channels for learning
YOUTUBE_CHANNELS = {
    "Science": [
        {"name": "Physics Wallah", "url": "https://www.youtube.com/@PhysicsWallah"},
        {"name": "Khan Academy India - Science", "url": "https://www.youtube.com/@KhanAcademyIndiaEnglish"},
        {"name": "Vedantu", "url": "https://www.youtube.com/@Vedantu"},
    ],
    "Mathematics": [
        {"name": "Khan Academy India - Math", "url": "https://www.youtube.com/@KhanAcademyIndiaEnglish"},
        {"name": "Mathongo", "url": "https://www.youtube.com/@Mathongo"},
        {"name": "Unacademy", "url": "https://www.youtube.com/@unacademy"},
    ],
    "English": [
        {"name": "BBC Learning English", "url": "https://www.youtube.com/@bbclearningenglish"},
        {"name": "Learn English with EnglishClass101", "url": "https://www.youtube.com/@EnglishClass101"},
    ],
    "Social Science": [
        {"name": "Study IQ Education", "url": "https://www.youtube.com/@StudyIQ"},
        {"name": "Magnet Brains", "url": "https://www.youtube.com/@MagnetBrainsEducation"},
    ]
}


def initialize_user_profile():
    """Initialize user profile in session state"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'onboarded': False,
            'name': '',
            'language': 'English',
            'class': None,
            'subjects': [],
            'preferred_video_platforms': []
        }


def save_user_profile(name: str, language: str, class_num: int):
    """Save user profile to session state"""
    st.session_state.user_profile = {
        'onboarded': True,
        'name': name,
        'language': language,
        'class': class_num,
        'subjects': SUBJECTS_BY_CLASS.get(class_num, []),
        'preferred_video_platforms': get_recommended_platforms(class_num, language)
    }


def get_recommended_platforms(class_num: int, language: str) -> List[Dict]:
    """Get recommended video platforms based on class and language"""
    recommended = []
    
    for platform, details in VIDEO_RESOURCES.items():
        # Check if platform supports the class
        if 'for_classes' in details and class_num not in details['for_classes']:
            continue
        
        # Check if platform supports the language
        if 'languages' in details:
            # Normalize language name
            lang_normalized = language.split('(')[0].strip()
            if lang_normalized in details['languages']:
                recommended.append({
                    'name': platform,
                    'url': details['url'],
                    'description': details['description']
                })
        else:
            recommended.append({
                'name': platform,
                'url': details['url'],
                'description': details['description']
            })
    
    return recommended


def get_ncert_book_url(class_num: int, subject: str, language: str = "English") -> str:
    """
    Generate NCERT book URL
    Note: This is a template. NCERT URLs follow patterns but may need verification
    """
    # NCERT e-pathshala base URL
    base_url = "https://ncert.nic.in/textbook.php"
    
    # Simplified URL generation (in production, you'd have a proper mapping)
    # For now, return the main textbook page
    return f"{base_url}?class={class_num}&subject={subject.replace(' ', '%20')}"


def get_youtube_channels_for_subject(subject: str) -> List[Dict]:
    """Get YouTube channels for a specific subject"""
    # Map subject to category
    subject_mapping = {
        "Mathematics": "Mathematics",
        "Science": "Science",
        "Physics": "Science",
        "Chemistry": "Science",
        "Biology": "Science",
        "English": "English",
        "Social Science": "Social Science",
        "History": "Social Science",
        "Geography": "Social Science",
        "Civics": "Social Science",
    }
    
    category = subject_mapping.get(subject, "Science")
    return YOUTUBE_CHANNELS.get(category, [])


def show_onboarding_screen():
    """Display onboarding screen for new users"""
    
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>🌱</h1>
        <h1>Welcome to Shiksha Mitra!</h1>
        <p style='font-size: 1.2rem; opacity: 0.8;'>
            Your AI-powered learning companion
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Onboarding form
    with st.form("onboarding_form"):
        st.subheader("Let's get you started! 🚀")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "What's your name?",
                placeholder="Enter your name",
                help="This helps us personalize your learning experience"
            )
        
        with col2:
            language = st.selectbox(
                "🌐 Preferred Language",
                options=list(LANGUAGES.keys()),
                help="Choose the language you're most comfortable with"
            )
        
        class_selected = st.selectbox(
            "📚 Which class are you in?",
            options=list(CLASSES.keys()),
            help="This helps us load the right curriculum for you"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submit_button = st.form_submit_button(
            "Start Learning! 🎓",
            use_container_width=True,
            type="primary"
        )
        
        if submit_button:
            if not name:
                st.error("Please enter your name!")
            else:
                class_num = CLASSES[class_selected]
                save_user_profile(name, language, class_num)
                st.success(f"Welcome aboard, {name}! 🎉")
                st.balloons()
                st.rerun()


def show_curriculum_overview():
    """Show curriculum overview after onboarding"""
    profile = st.session_state.user_profile
    
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0;'>Hello {profile['name']}! 👋</h2>
        <p style='color: #e0e7ff; font-size: 1.1rem; margin-top: 0.5rem;'>
            Class {profile['class']} • {profile['language']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show subjects
    st.subheader("📚 Your Subjects")
    
    cols = st.columns(min(3, len(profile['subjects'])))
    for idx, subject in enumerate(profile['subjects'][:6]):  # Show first 6
        with cols[idx % 3]:
            st.markdown(f"""
            <div style='background: #1e3a5f; padding: 1rem; border-radius: 10px; 
                        text-align: center; margin: 0.5rem 0;'>
                <h4 style='color: #e0e7ff; margin: 0;'>{subject}</h4>
            </div>
            """, unsafe_allow_html=True)
    
    # Show learning resources
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎥 Recommended Learning Platforms")
    
    for platform in profile['preferred_video_platforms'][:4]:  # Show top 4
        with st.expander(f"📺 {platform['name']}", expanded=False):
            st.write(platform['description'])
            st.markdown(f"[🔗 Visit {platform['name']}]({platform['url']})")
    
    # NCERT Resources
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📖 NCERT Textbooks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_subject = st.selectbox(
            "Select a subject to view textbook:",
            profile['subjects']
        )
    
    with col2:
        if st.button("📥 Open NCERT Textbook", use_container_width=True):
            ncert_url = get_ncert_book_url(profile['class'], selected_subject, profile['language'])
            st.markdown(f"[🔗 View {selected_subject} Textbook]({ncert_url})")
            st.info("📌 Tip: You can also access NCERT books through the DIKSHA app by scanning QR codes in your physical textbooks!")
    
    # YouTube Channels
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🎬 YouTube Learning Channels")
    
    channels = get_youtube_channels_for_subject(selected_subject)
    
    if channels:
        for channel in channels:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📺 **{channel['name']}**")
            with col2:
                st.markdown(f"[Visit →]({channel['url']})")
    
    # Change settings button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚙️ Change Language/Class", use_container_width=False):
        st.session_state.user_profile['onboarded'] = False
        st.rerun()


def get_diksha_search_url(class_num: int, subject: str) -> str:
    """Generate DIKSHA search URL for specific class and subject"""
    return f"https://diksha.gov.in/explore?class=Class%20{class_num}&subject={subject.replace(' ', '%20')}"


# Main function to be called from streamlit_app.py
def handle_onboarding():
    """Main onboarding handler"""
    initialize_user_profile()
    
    if not st.session_state.user_profile['onboarded']:
        show_onboarding_screen()
        return False  # Not yet onboarded
    else:
        return True  # Onboarded, can proceed to dashboard