# enhanced_tests.py
"""
Enhanced Tests Module with Multi-language Support and Database Storage
Add this as a separate file in your project
"""

import streamlit as st
import json
from datetime import datetime
import plotly.graph_objects as go

# Test Questions Bank (Persistent - Won't change on login)
TEST_QUESTIONS_BANK = {
    "Mathematics": {
        "Level 1": [
            {
                "id": "math_l1_q1",
                "question_en": "What is 15 + 27?",
                "question_hi": "15 + 27 क्या है?",
                "question_kn": "15 + 27 ಎಷ್ಟು?",
                "question_te": "15 + 27 ఎంత?",
                "question_mr": "15 + 27 किती आहे?",
                "options": ["42", "52", "32", "62"],
                "correct": 0,
                "marks": 5
            },
            {
                "id": "math_l1_q2",
                "question_en": "What is 8 × 7?",
                "question_hi": "8 × 7 क्या है?",
                "question_kn": "8 × 7 ಎಷ್ಟು?",
                "question_te": "8 × 7 ఎంత?",
                "question_mr": "8 × 7 किती आहे?",
                "options": ["54", "56", "64", "48"],
                "correct": 1,
                "marks": 5
            },
            {
                "id": "math_l1_q3",
                "question_en": "What is the value of 100 - 37?",
                "question_hi": "100 - 37 का मान क्या है?",
                "question_kn": "100 - 37 ರ ಮೌಲ್ಯ ಎಷ್ಟು?",
                "question_te": "100 - 37 విలువ ఎంత?",
                "question_mr": "100 - 37 चे मूल्य काय आहे?",
                "options": ["73", "63", "53", "67"],
                "correct": 1,
                "marks": 5
            }
        ],
        "Level 2": [
            {
                "id": "math_l2_q1",
                "question_en": "Solve: 2x + 5 = 15. Find x.",
                "question_hi": "हल करें: 2x + 5 = 15। x का मान ज्ञात करें।",
                "question_kn": "ಪರಿಹರಿಸಿ: 2x + 5 = 15. x ಅನ್ನು ಕಂಡುಹಿಡಿಯಿರಿ.",
                "question_te": "పరిష్కరించండి: 2x + 5 = 15. x కనుగొనండి.",
                "question_mr": "सोडवा: 2x + 5 = 15. x शोधा.",
                "options": ["5", "10", "7", "8"],
                "correct": 0,
                "marks": 10
            },
            {
                "id": "math_l2_q2",
                "question_en": "What is the area of a rectangle with length 12 cm and width 8 cm?",
                "question_hi": "12 सेमी लंबाई और 8 सेमी चौड़ाई वाले आयत का क्षेत्रफल क्या है?",
                "question_kn": "12 ಸೆಂ.ಮೀ ಉದ್ದ ಮತ್ತು 8 ಸೆಂ.ಮೀ ಅಗಲದ ಆಯತದ ವಿಸ್ತೀರ್ಣ ಎಷ್ಟು?",
                "question_te": "12 సెం.మీ పొడవు మరియు 8 సెం.మీ వెడల్పు ఉన్న దీర్ఘచతురస్రం వైశాల్యం ఎంత?",
                "question_mr": "12 सेमी लांबी आणि 8 सेमी रुंदी असलेल्या आयताचे क्षेत्रफळ काय आहे?",
                "options": ["96 cm²", "20 cm²", "40 cm²", "106 cm²"],
                "correct": 0,
                "marks": 10
            }
        ],
        "Level 3": [
            {
                "id": "math_l3_q1",
                "question_en": "If a² + b² = 13 and ab = 6, find (a + b)²",
                "question_hi": "यदि a² + b² = 13 और ab = 6 है, तो (a + b)² का मान ज्ञात करें",
                "question_kn": "a² + b² = 13 ಮತ್ತು ab = 6 ಆಗಿದ್ದರೆ, (a + b)² ಕಂಡುಹಿಡಿಯಿರಿ",
                "question_te": "a² + b² = 13 మరియు ab = 6 అయితే, (a + b)² కనుగొనండి",
                "question_mr": "जर a² + b² = 13 आणि ab = 6 असेल तर (a + b)² शोधा",
                "options": ["25", "19", "21", "23"],
                "correct": 0,
                "marks": 15
            }
        ]
    },
    "Science": {
        "Level 1": [
            {
                "id": "sci_l1_q1",
                "question_en": "What is the process by which plants make their food?",
                "question_hi": "पौधे अपना भोजन किस प्रक्रिया द्वारा बनाते हैं?",
                "question_kn": "ಸಸ್ಯಗಳು ತಮ್ಮ ಆಹಾರವನ್ನು ತಯಾರಿಸುವ ಪ್ರಕ್ರಿಯೆ ಯಾವುದು?",
                "question_te": "మొక్కలు తమ ఆహారాన్ని తయారు చేసే ప్రక్రియ ఏమిటి?",
                "question_mr": "वनस्पती त्यांचे अन्न कोणत्या प्रक्रियेद्वारे तयार करतात?",
                "options": ["Photosynthesis", "Respiration", "Digestion", "Absorption"],
                "correct": 0,
                "marks": 5
            },
            {
                "id": "sci_l1_q2",
                "question_en": "Which organ pumps blood throughout the body?",
                "question_hi": "कौन सा अंग पूरे शरीर में रक्त पंप करता है?",
                "question_kn": "ಯಾವ ಅಂಗವು ದೇಹದಾದ್ಯಂತ ರಕ್ತವನ್ನು ಪಂಪ್ ಮಾಡುತ್ತದೆ?",
                "question_te": "శరీరం అంతటా రక్తాన్ని పంప్ చేసే అవయవం ఏది?",
                "question_mr": "कोणता अवयव संपूर्ण शरीरात रक्त पंप करतो?",
                "options": ["Lungs", "Heart", "Liver", "Brain"],
                "correct": 1,
                "marks": 5
            }
        ],
        "Level 2": [
            {
                "id": "sci_l2_q1",
                "question_en": "What is the chemical formula for water?",
                "question_hi": "पानी का रासायनिक सूत्र क्या है?",
                "question_kn": "ನೀರಿನ ರಾಸಾಯನಿಕ ಸೂತ್ರ ಏನು?",
                "question_te": "నీటి రసాయన సూత్రం ఏమిటి?",
                "question_mr": "पाण्याचे रासायनिक सूत्र काय आहे?",
                "options": ["H₂O", "CO₂", "O₂", "NaCl"],
                "correct": 0,
                "marks": 10
            }
        ],
        "Level 3": [
            {
                "id": "sci_l3_q1",
                "question_en": "What is the powerhouse of the cell?",
                "question_hi": "कोशिका का पावरहाउस क्या है?",
                "question_kn": "ಜೀವಕೋಶದ ಶಕ್ತಿಗೃಹ ಯಾವುದು?",
                "question_te": "కణం యొక్క శక్తి గృహం ఏమిటి?",
                "question_mr": "पेशीचे पॉवरहाऊस काय आहे?",
                "options": ["Nucleus", "Mitochondria", "Ribosome", "Chloroplast"],
                "correct": 1,
                "marks": 15
            }
        ]
    },
    "English": {
        "Level 1": [
            {
                "id": "eng_l1_q1",
                "question_en": "What is the plural of 'child'?",
                "question_hi": "'child' का बहुवचन क्या है?",
                "question_kn": "'child' ನ ಬಹುವಚನ ಏನು?",
                "question_te": "'child' యొక్క బహువచనం ఏమిటి?",
                "question_mr": "'child' चे अनेकवचन काय आहे?",
                "options": ["Childs", "Children", "Childrens", "Child"],
                "correct": 1,
                "marks": 5
            }
        ],
        "Level 2": [
            {
                "id": "eng_l2_q1",
                "question_en": "Identify the verb in: 'She runs quickly'",
                "question_hi": "क्रिया पहचानें: 'She runs quickly'",
                "question_kn": "ಕ್ರಿಯಾಪದ ಗುರುತಿಸಿ: 'She runs quickly'",
                "question_te": "క్రియను గుర్తించండి: 'She runs quickly'",
                "question_mr": "क्रियापद ओळखा: 'She runs quickly'",
                "options": ["She", "runs", "quickly", "None"],
                "correct": 1,
                "marks": 10
            }
        ],
        "Level 3": [
            {
                "id": "eng_l3_q1",
                "question_en": "What type of sentence is: 'What a beautiful day!'",
                "question_hi": "यह किस प्रकार का वाक्य है: 'What a beautiful day!'",
                "question_kn": "ಈ ಯಾವ ರೀತಿಯ ವಾಕ್ಯ: 'What a beautiful day!'",
                "question_te": "ఇది ఏ రకమైన వాక్యం: 'What a beautiful day!'",
                "question_mr": "हे कोणत्या प्रकारचे वाक्य आहे: 'What a beautiful day!'",
                "options": ["Interrogative", "Imperative", "Exclamatory", "Declarative"],
                "correct": 2,
                "marks": 15
            }
        ]
    }
}

# Language mapping
LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Telugu": "te",
    "Marathi": "mr"
}


def get_question_text(question, language):
    """Get question text in specified language"""
    lang_code = LANGUAGE_CODES.get(language, "en")
    question_key = f"question_{lang_code}"
    return question.get(question_key, question.get("question_en"))


def show_enhanced_tests_page(lang, theme, db, user_id):
    """Enhanced Tests page with database storage"""
    accent_color = theme['accent']
    text_color = theme['text']
    
    st.markdown(f"""
    <div class='main-header'>
        <h1 style='color: white; margin: 0;'>🧪 Tests & Assessments</h1>
        <p style='color: #e0e7ff; margin-top: 0.5rem;'>Multi-level tests in your language</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session states
    if 'current_test' not in st.session_state:
        st.session_state.current_test = None
    if 'test_answers' not in st.session_state:
        st.session_state.test_answers = {}
    if 'test_submitted' not in st.session_state:
        st.session_state.test_submitted = False
    
    tab1, tab2, tab3 = st.tabs(["📝 Take Test", "✅ My Results", "📊 Performance"])
    
    with tab1:
        if st.session_state.current_test is None:
            # Test Selection Interface
            st.subheader("Choose Your Test")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_subject = st.selectbox(
                    "Subject",
                    list(TEST_QUESTIONS_BANK.keys()),
                    key="test_subject"
                )
            
            with col2:
                selected_level = st.selectbox(
                    "Difficulty Level",
                    ["Level 1", "Level 2", "Level 3"],
                    key="test_level"
                )
            
            with col3:
                test_language = st.selectbox(
                    "Test Language",
                    ["English", "Hindi", "Kannada", "Telugu", "Marathi"],
                    index=["English", "Hindi", "Kannada", "Telugu", "Marathi"].index(lang) if lang in ["English", "Hindi", "Kannada", "Telugu", "Marathi"] else 0,
                    key="test_language"
                )
            
            # Show test info
            if selected_subject in TEST_QUESTIONS_BANK and selected_level in TEST_QUESTIONS_BANK[selected_subject]:
                questions = TEST_QUESTIONS_BANK[selected_subject][selected_level]
                total_marks = sum(q['marks'] for q in questions)
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h3 style='color: {accent_color};'>Test Details</h3>
                    <p style='color: {text_color};'>
                        📚 Subject: <strong>{selected_subject}</strong><br>
                        🎯 Level: <strong>{selected_level}</strong><br>
                        📋 Questions: <strong>{len(questions)}</strong><br>
                        ⭐ Total Marks: <strong>{total_marks}</strong><br>
                        ⏱ Duration: <strong>{len(questions) * 2} minutes</strong><br>
                        🌍 Language: <strong>{test_language}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Start Test", use_container_width=True, type="primary"):
                    st.session_state.current_test = {
                        'subject': selected_subject,
                        'level': selected_level,
                        'language': test_language,
                        'questions': questions,
                        'start_time': datetime.now().isoformat()
                    }
                    st.session_state.test_answers = {}
                    st.session_state.test_submitted = False
                    st.rerun()
        
        else:
            # Display Test
            test = st.session_state.current_test
            
            if not st.session_state.test_submitted:
                st.markdown(f"""
                <div style='background: {theme['card_bg']}; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h3 style='color: {accent_color}; margin: 0;'>{test['subject']} - {test['level']}</h3>
                    <p style='color: {text_color}; margin: 0.5rem 0 0 0;'>
                        Language: {test['language']} | Questions: {len(test['questions'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display questions
                for i, question in enumerate(test['questions'], 1):
                    st.markdown(f"### Question {i} ({question['marks']} marks)")
                    
                    question_text = get_question_text(question, test['language'])
                    st.write(question_text)
                    
                    answer = st.radio(
                        "Select your answer:",
                        question['options'],
                        key=f"q_{question['id']}",
                        index=None
                    )
                    
                    if answer:
                        st.session_state.test_answers[question['id']] = question['options'].index(answer)
                    
                    st.markdown("---")
                
                # Submit button
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("✅ Submit Test", use_container_width=True, type="primary"):
                        if len(st.session_state.test_answers) < len(test['questions']):
                            st.warning(f"⚠️ Please answer all questions! ({len(st.session_state.test_answers)}/{len(test['questions'])} answered)")
                        else:
                            st.session_state.test_submitted = True
                            st.rerun()
                
                with col2:
                    if st.button("❌ Cancel Test", use_container_width=True):
                        st.session_state.current_test = None
                        st.session_state.test_answers = {}
                        st.rerun()
            
            else:
                # Show Results
                test = st.session_state.current_test
                questions = test['questions']
                answers = st.session_state.test_answers
                
                # Calculate score
                total_marks = 0
                obtained_marks = 0
                correct_count = 0
                
                for question in questions:
                    total_marks += question['marks']
                    user_answer = answers.get(question['id'])
                    if user_answer == question['correct']:
                        obtained_marks += question['marks']
                        correct_count += 1
                
                percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
                
                # Save to database
                try:
                    db.save_test_result(
                        user_id=user_id,
                        subject=test['subject'],
                        level=test['level'],
                        total_marks=total_marks,
                        obtained_marks=obtained_marks,
                        percentage=percentage,
                        correct_answers=correct_count,
                        total_questions=len(questions),
                        answers=json.dumps(answers)
                    )
                except Exception as e:
                    st.error(f"Error saving results: {str(e)}")
                
                # Display results
                result_color = "#22c55e" if percentage >= 60 else ("#f59e0b" if percentage >= 40 else "#ef4444")
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {result_color}22 0%, {result_color}11 100%); 
                            padding: 2rem; border-radius: 15px; border: 2px solid {result_color}; margin-bottom: 2rem;'>
                    <h2 style='color: {result_color}; text-align: center; margin: 0;'>Test Completed! 🎉</h2>
                    <div style='text-align: center; margin-top: 1rem;'>
                        <p style='font-size: 3rem; color: {result_color}; margin: 0;'>{percentage:.1f}%</p>
                        <p style='font-size: 1.2rem; color: {text_color}; margin: 0.5rem 0;'>
                            {obtained_marks}/{total_marks} marks
                        </p>
                        <p style='color: {text_color};'>
                            ✅ Correct: {correct_count}/{len(questions)} questions
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Performance feedback
                if percentage >= 80:
                    st.success("🌟 Excellent! You have mastered this topic!")
                elif percentage >= 60:
                    st.info("👍 Good job! Keep practicing to improve further.")
                elif percentage >= 40:
                    st.warning("📚 You're getting there! Review the concepts and try again.")
                else:
                    st.error("💪 Don't give up! Review the material and practice more.")
                
                # Show detailed answers
                with st.expander("📋 View Detailed Solutions"):
                    for i, question in enumerate(questions, 1):
                        user_answer = answers.get(question['id'])
                        correct_answer = question['correct']
                        is_correct = user_answer == correct_answer
                        
                        border_color = "#22c55e" if is_correct else "#ef4444"
                        
                        st.markdown(f"""
                        <div style='border-left: 4px solid {border_color}; padding: 1rem; margin: 1rem 0; 
                                    background: {theme['card_bg']}; border-radius: 8px;'>
                            <h4 style='color: {text_color}; margin: 0;'>Question {i}</h4>
                            <p style='color: {text_color}; margin: 0.5rem 0;'>
                                {get_question_text(question, test['language'])}
                            </p>
                            <p style='color: {text_color};'>
                                <strong>Your answer:</strong> {question['options'][user_answer] if user_answer is not None else 'Not answered'}<br>
                                <strong>Correct answer:</strong> {question['options'][correct_answer]}<br>
                                <strong>Result:</strong> {'✅ Correct' if is_correct else '❌ Incorrect'} 
                                ({question['marks']} marks)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔄 Retake Test", use_container_width=True):
                        st.session_state.test_answers = {}
                        st.session_state.test_submitted = False
                        st.rerun()
                
                with col2:
                    if st.button("📚 Try Different Level", use_container_width=True):
                        st.session_state.current_test = None
                        st.session_state.test_answers = {}
                        st.session_state.test_submitted = False
                        st.rerun()
                
                with col3:
                    if st.button("🏠 Back to Tests", use_container_width=True):
                        st.session_state.current_test = None
                        st.session_state.test_answers = {}
                        st.session_state.test_submitted = False
                        st.rerun()
    
    with tab2:
        st.subheader("📊 Your Test History")
        
        try:
            results = db.get_user_test_results(user_id)
            
            if results:
                for result in results:
                    percentage = result.get('percentage', 0)
                    color = "#22c55e" if percentage >= 60 else ("#f59e0b" if percentage >= 40 else "#ef4444")
                    
                    st.markdown(f"""
                    <div class='metric-card' style='border-left: 4px solid {color};'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='color: {text_color}; margin: 0;'>{result['subject']} - {result['level']}</h4>
                                <p style='color: {text_color}; opacity: 0.8; margin: 0.3rem 0;'>
                                    {result.get('date', 'N/A')}
                                </p>
                            </div>
                            <div style='text-align: right;'>
                                <p style='font-size: 2rem; color: {color}; margin: 0;'>{percentage:.1f}%</p>
                                <p style='color: {text_color}; margin: 0;'>
                                    {result['obtained_marks']}/{result['total_marks']} marks
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📝 No tests taken yet. Start your first test!")
        
        except Exception as e:
            st.error(f"Error loading results: {str(e)}")
    
    with tab3:
        st.subheader("📈 Performance Analytics")
        
        try:
            results = db.get_user_test_results(user_id)
            
            if results:
                import pandas as pd
                
                df = pd.DataFrame(results)
                
                if not df.empty:
                    # Average by subject
                    st.markdown("#### 📚 Subject-wise Average")
                    
                    col1, col2, col3 = st.columns(3)
                    subject_avg = df.groupby('subject')['percentage'].mean().round(2)
                    
                    for idx, (subject, avg) in enumerate(subject_avg.items()):
                        with [col1, col2, col3][idx % 3]:
                            st.metric(subject, f"{avg}%")
                    
                    st.markdown("---")
                    
                    # Level progression
                    st.markdown("#### 🎯 Level Progression")
                    for subject in df['subject'].unique():
                        subject_data = df[df['subject'] == subject]
                        st.write(f"**{subject}:**")
                        for level in ['Level 1', 'Level 2', 'Level 3']:
                            level_data = subject_data[subject_data['level'] == level]
                            if not level_data.empty:
                                avg = level_data['percentage'].mean()
                                st.progress(avg/100, text=f"{level}: {avg:.1f}%")
            else:
                st.info("Take some tests to see your performance analytics!")
        
        except Exception as e:
            st.error(f"Error loading analytics: {str(e)}")