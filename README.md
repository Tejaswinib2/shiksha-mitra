# 🌱 Shiksha Mitra - AI-Powered Learning Platform

An intelligent, multilingual learning platform designed for Indian students (Classes 1-12) that provides personalized education through AI-powered teaching, real-time doubt clearing, and adaptive assessments.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Features

### 🧠 AI Teacher (RAG-Powered)
- **Personalized Micro-Lessons**: AI generates lessons tailored to student's class and learning level
- **Textbook Integration**: Retrieval-Augmented Generation (RAG) from actual NCERT textbooks
- **Adaptive Learning**: Adjusts difficulty based on student comprehension (1-10 scale)
- **Local Context**: Incorporates Indian cultural contexts (farming, festivals, etc.)
- **Multi-Subject Support**: Mathematics, Science, English, History, Geography, and more

### 💬 Doubt AI - Instant Help
- **Real-Time Answers**: Powered by Groq's ultra-fast LLM (Llama 3)
- **Multilingual Support**: Ask questions in 10+ Indian languages
- **Contextual Understanding**: Maintains conversation history for follow-up questions
- **Subject-Specific Help**: Tailored explanations for each subject

### 🧪 Smart Testing System
- **AI-Generated Tests**: Dynamic question generation based on topics
- **Multiple Question Types**: MCQ, True/False, Short Answer, Long Answer
- **Instant Grading**: AI-powered answer evaluation with detailed feedback
- **Performance Analytics**: Track progress, identify weak areas
- **Adaptive Difficulty**: Questions adjust to student's level

### 🎮 Gamification
- **XP System**: Earn experience points for learning activities
- **Level Progression**: Advance through levels (1-10+)
- **Achievements**: Unlock badges for milestones
- **Streak Tracking**: Maintain daily learning streaks
- **Leaderboards**: Compare progress with peers

### 📊 Analytics Dashboard
- **Progress Tracking**: Monitor study time, lessons completed
- **Subject-Wise Performance**: Visualize strengths and weaknesses
- **Weekly Reports**: Detailed charts and graphs
- **Streak Statistics**: Track learning consistency

### 🌍 Multilingual Support
Supports **10+ Indian languages**:
- English
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Punjabi (ਪੰਜਾਬੀ)

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────┐
│ Groq  │ │ ChromaDB│
│  LLM  │ │   RAG   │
└───────┘ └─────────┘
```

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **LLM**: Groq API (Llama 3.1-70B-Versatile)
- **Vector DB**: ChromaDB (for RAG)
- **Embeddings**: Sentence Transformers
- **Database**: SQLite (user data, progress)
- **Charts**: Plotly
- **Translation**: Custom multilingual system

## 📁 Project Structure

```
shiksha-mitra/
│
├── streamlit_app.py          # Main application entry point
├── stream1.py                # Alternative app version 1
├── stream2.py                # Alternative app version 2
├── stream12_comb.py          # Combined features version
├── test2.py                  # Test/experimental features
├── test_ai.py                # AI testing module
│
├── database.py               # SQLite database operations
├── teaching_agent.py         # Core AI teaching logic (RAG)
├── llm_translator.py         # Multilingual translation
├── translations.py           # Language dictionaries
├── onboarding.py             # User registration/profile setup
├── optimized_teaching_agent.py  # Performance-optimized version
│
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── .env                     # Environment variables (API keys)
│
├── shiksha_mitra.db         # SQLite database (auto-created)
├── TextBooks/               # NCERT textbook PDFs (not in repo)
└── venv/                    # Virtual environment (not in repo)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Groq API Key (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Ragha822/shiksha-mitra.git
cd shiksha-mitra
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

5. **Run the application**
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎓 Usage

### First Time Setup
1. **Sign Up**: Create an account with username and password
2. **Complete Profile**: Enter your name, select class (1-12), and preferred language
3. **Choose Subjects**: Select subjects you want to study

### Using AI Teacher
1. Navigate to **"🧠 AI Teacher"**
2. Select a subject and enter a topic (e.g., "Fractions", "Photosynthesis")
3. Click **"Generate Lesson"** to get a personalized micro-lesson
4. Ask follow-up questions in the Q&A section
5. Generate practice problems to test understanding

### Taking Tests
1. Go to **"🧪 Tests"** section
2. Select subject and topic
3. Choose difficulty level and question count
4. Start the test and answer questions
5. Get instant AI-powered feedback and scores

### Clearing Doubts
1. Open **"💬 Doubt AI"**
2. Select your subject
3. Ask any question in your preferred language
4. Get instant, contextual answers

## 🔧 Configuration

### Adding Textbooks
Place NCERT PDF textbooks in the `TextBooks/` folder:
```
TextBooks/
├── Class_10_Mathematics.pdf
├── Class_10_Science.pdf
└── Class_9_English.pdf
```

### Customizing Languages
Edit `translations.py` to add more languages or modify translations.

### Adjusting AI Behavior
In `teaching_agent.py`, modify:
- `COMPREHENSION_THRESHOLD`: Difficulty adjustment sensitivity
- `MAX_LESSON_LENGTH`: Control lesson length
- `TEMPERATURE`: AI creativity level (0.0-1.0)

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    email TEXT,
    created_at TIMESTAMP
)
```

### User Profiles Table
```sql
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    class_number INTEGER,
    language TEXT,
    subjects TEXT,  -- JSON array
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```

### Progress Tracking
```sql
CREATE TABLE user_stats (
    user_id INTEGER PRIMARY KEY,
    total_xp INTEGER,
    current_streak INTEGER,
    last_active DATE,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```

## 🎨 Themes

The app supports **Dark Mode** and **Light Mode**:
- Toggle using the sidebar switch
- Persistent across sessions
- Automatic color adjustments for charts and UI elements

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt --upgrade
```

### Groq API errors
- Check if API key is correct in `.env`
- Verify you haven't exceeded rate limits
- Get a new key at [console.groq.com](https://console.groq.com)

### Database errors
Delete `shiksha_mitra.db` and restart the app (will recreate fresh database)

### ChromaDB errors
```bash
pip install chromadb --upgrade
```

## 🚀 Deployment

### Streamlit Community Cloud

1. **Push to GitHub** (only essential files):
```bash
git add streamlit_app.py database.py teaching_agent.py llm_translator.py translations.py onboarding.py requirements.txt .gitignore
git commit -m "Deploy version"
git push
```

2. **Deploy on Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Set main file: `streamlit_app.py`
   - Add secrets (Groq API key)
   - Deploy!

### Environment Variables for Production
In Streamlit Cloud secrets:
```toml
GROQ_API_KEY = "your_production_api_key"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NCERT** for educational textbooks
- **Groq** for ultra-fast LLM API
- **Streamlit** for the amazing web framework
- **ChromaDB** for vector database
- **LangChain** for RAG implementation

## 📧 Contact

**Developer**: Raghavarshini K  
**GitHub**: [@Ragha822](https://github.com/Ragha822)  
**Project Link**: [https://github.com/Ragha822/shiksha-mitra](https://github.com/Ragha822/shiksha-mitra)

## 🗺️ Roadmap

- [ ] Voice input/output for accessibility
- [ ] Mobile app version
- [ ] Collaborative learning features
- [ ] Parent/teacher dashboard
- [ ] Video lesson integration
- [ ] Offline mode support
- [ ] Advanced analytics with ML insights
- [ ] Integration with school curricula
- [ ] Peer-to-peer tutoring system
- [ ] Exam preparation mode

## 📈 Version History

- **v1.0.0** (Current)
  - Initial release
  - AI Teacher with RAG
  - Multilingual support (10+ languages)
  - Smart testing system
  - Gamification features
  - Analytics dashboard

---

**Made with ❤️ for Indian Students**

*Empowering education through AI, one student at a time.*
