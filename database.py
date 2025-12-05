# database.py
"""
Database module for Shiksha Mitra
Handles user authentication, profile storage, and learning progress
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os

class ShikshaMitraDB:
    """Database manager for Shiksha Mitra"""
    
    def __init__(self, db_path: str = "shiksha_mitra.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)
        
        # User profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            class_number INTEGER NOT NULL,
            language TEXT NOT NULL,
            subjects TEXT,  -- JSON array
            date_of_birth DATE,
            phone_number TEXT,
            parent_phone TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # Learning progress table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            completion_percentage REAL DEFAULT 0,
            score REAL,
            time_spent_minutes INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # Streaks and gamification table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            badges TEXT,  -- JSON array
            last_activity_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # Doubts history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doubts_history (
            doubt_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT,
            question TEXT NOT NULL,
            answer TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            language TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # OLD test results table - keeping for compatibility
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            time_taken_seconds INTEGER,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # NEW enhanced test results table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS enhanced_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            level TEXT NOT NULL,
            total_marks INTEGER NOT NULL,
            obtained_marks INTEGER NOT NULL,
            percentage REAL NOT NULL,
            correct_answers INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            answers TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_enhanced_test_user 
        ON enhanced_test_results(user_id)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_enhanced_test_subject 
        ON enhanced_test_results(subject)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_enhanced_test_date 
        ON enhanced_test_results(completed_at)
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Create a new user
        Returns: (success, message, user_id)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            
            user_id = cursor.lastrowid
            
            # Initialize user stats
            cursor.execute(
                "INSERT INTO user_stats (user_id, badges) VALUES (?, ?)",
                (user_id, json.dumps([]))
            )
            
            conn.commit()
            conn.close()
            
            return True, "User created successfully!", user_id
            
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists!", None
            elif "email" in str(e):
                return False, "Email already exists!", None
            else:
                return False, f"Error: {e}", None
        except Exception as e:
            return False, f"Error creating user: {e}", None
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[int]]:
        """
        Authenticate user
        Returns: (success, user_id)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute(
                "SELECT user_id FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            result = cursor.fetchone()
            
            if result:
                user_id = result[0]
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE user_id = ?",
                    (datetime.now(), user_id)
                )
                conn.commit()
                conn.close()
                return True, user_id
            else:
                conn.close()
                return False, None
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None
    
    def create_or_update_profile(self, user_id: int, full_name: str, class_number: int, 
                                  language: str, subjects: List[str], 
                                  date_of_birth: Optional[str] = None,
                                  phone_number: Optional[str] = None,
                                  parent_phone: Optional[str] = None) -> Tuple[bool, str]:
        """Create or update user profile"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            subjects_json = json.dumps(subjects)
            
            # Check if profile exists
            cursor.execute("SELECT profile_id FROM user_profiles WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing profile
                cursor.execute("""
                UPDATE user_profiles 
                SET full_name = ?, class_number = ?, language = ?, subjects = ?,
                    date_of_birth = ?, phone_number = ?, parent_phone = ?
                WHERE user_id = ?
                """, (full_name, class_number, language, subjects_json, 
                      date_of_birth, phone_number, parent_phone, user_id))
            else:
                # Create new profile
                cursor.execute("""
                INSERT INTO user_profiles 
                (user_id, full_name, class_number, language, subjects, date_of_birth, phone_number, parent_phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, full_name, class_number, language, subjects_json,
                      date_of_birth, phone_number, parent_phone))
            
            conn.commit()
            conn.close()
            
            return True, "Profile saved successfully!"
            
        except Exception as e:
            return False, f"Error saving profile: {e}"
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT u.username, u.email, p.full_name, p.class_number, p.language, 
                   p.subjects, p.date_of_birth, p.phone_number, p.parent_phone
            FROM users u
            LEFT JOIN user_profiles p ON u.user_id = p.user_id
            WHERE u.user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'user_id': user_id,
                    'username': result[0],
                    'email': result[1],
                    'full_name': result[2],
                    'class_number': result[3],
                    'language': result[4],
                    'subjects': json.loads(result[5]) if result[5] else [],
                    'date_of_birth': result[6],
                    'phone_number': result[7],
                    'parent_phone': result[8]
                }
            return None
            
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT current_streak, longest_streak, total_xp, level, badges, last_activity_date
            FROM user_stats WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'current_streak': result[0],
                    'longest_streak': result[1],
                    'total_xp': result[2],
                    'level': result[3],
                    'badges': json.loads(result[4]) if result[4] else [],
                    'last_activity_date': result[5]
                }
            
            # Return default stats if none exist
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_xp': 0,
                'level': 1,
                'badges': [],
                'last_activity_date': None
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_xp': 0,
                'level': 1,
                'badges': [],
                'last_activity_date': None
            }
        finally:
            conn.close()
    
    def update_streak(self, user_id: int) -> bool:
        """Update user's learning streak"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            today = datetime.now().date()
            
            cursor.execute(
                "SELECT last_activity_date, current_streak, longest_streak FROM user_stats WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                last_date = result[0]
                current_streak = result[1]
                longest_streak = result[2]
                
                if last_date:
                    last_date = datetime.strptime(last_date, '%Y-%m-%d').date()
                    days_diff = (today - last_date).days
                    
                    if days_diff == 1:
                        # Continue streak
                        current_streak += 1
                    elif days_diff > 1:
                        # Streak broken
                        current_streak = 1
                    # If days_diff == 0, same day, no change
                else:
                    # First activity
                    current_streak = 1
                
                # Update longest streak if needed
                if current_streak > longest_streak:
                    longest_streak = current_streak
                
                cursor.execute("""
                UPDATE user_stats 
                SET current_streak = ?, longest_streak = ?, last_activity_date = ?
                WHERE user_id = ?
                """, (current_streak, longest_streak, today.isoformat(), user_id))
                
                conn.commit()
                conn.close()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error updating streak: {e}")
            return False
    
    def add_xp(self, user_id: int, xp_amount: int) -> bool:
        """Add XP to user and update level"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT total_xp, level FROM user_stats WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                total_xp = result[0] + xp_amount
                level = result[1]
                
                # Simple leveling: 1000 XP per level
                new_level = (total_xp // 1000) + 1
                
                cursor.execute(
                    "UPDATE user_stats SET total_xp = ?, level = ? WHERE user_id = ?",
                    (total_xp, new_level, user_id)
                )
                
                conn.commit()
                conn.close()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error adding XP: {e}")
            return False
    
    def save_doubt(self, user_id: int, subject: str, question: str, 
                   answer: str, language: str) -> bool:
        """Save doubt and answer to history"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO doubts_history (user_id, subject, question, answer, language)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, subject, question, answer, language))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving doubt: {e}")
            return False
    
    def get_user_doubts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's recent doubts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT subject, question, answer, timestamp, language
            FROM doubts_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'subject': r[0],
                    'question': r[1],
                    'answer': r[2],
                    'timestamp': r[3],
                    'language': r[4]
                }
                for r in results
            ]
            
        except Exception as e:
            print(f"Error getting doubts: {e}")
            return []
    
    # ==================== ENHANCED TEST METHODS ====================
    
    def save_test_result(self, user_id, subject, level, total_marks, obtained_marks, 
                         percentage, correct_answers, total_questions, answers):
        """Save test result to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO enhanced_test_results 
            (user_id, subject, level, total_marks, obtained_marks, percentage, 
             correct_answers, total_questions, answers, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, subject, level, total_marks, obtained_marks, 
                percentage, correct_answers, total_questions, answers,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving test result: {e}")
            return False

    def get_user_test_results(self, user_id, limit=20):
        """Get user's test results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, subject, level, total_marks, obtained_marks, percentage,
                   correct_answers, total_questions, 
                   strftime('%d %b %Y, %H:%M', completed_at) as date
            FROM enhanced_test_results
            WHERE user_id = ?
            ORDER BY completed_at DESC
            LIMIT ?
            """, (user_id, limit))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error fetching test results: {e}")
            return []

    def get_subject_performance(self, user_id, subject):
        """Get performance statistics for a specific subject"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT level,
                   COUNT(*) as attempts,
                   AVG(percentage) as avg_percentage,
                   MAX(percentage) as best_score,
                   AVG(correct_answers * 1.0 / total_questions * 100) as avg_accuracy
            FROM enhanced_test_results
            WHERE user_id = ? AND subject = ?
            GROUP BY level
            ORDER BY level
            """, (user_id, subject))
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error fetching subject performance: {e}")
            return []

    def get_overall_test_stats(self, user_id):
        """Get overall test statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT 
                COUNT(*) as total_tests,
                AVG(percentage) as avg_score,
                MAX(percentage) as best_score,
                COUNT(DISTINCT subject) as subjects_tested,
                SUM(CASE WHEN percentage >= 60 THEN 1 ELSE 0 END) as passed_tests
            FROM enhanced_test_results
            WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                conn.close()
                return dict(zip(columns, row))
            
            conn.close()
            return {}
        except Exception as e:
            print(f"Error fetching overall stats: {e}")
            return {}


# Singleton instance
_db_instance = None

def get_db() -> ShikshaMitraDB:
    """Get database instance (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ShikshaMitraDB()
    return _db_instance


# Test the database
if __name__ == "__main__":
    print("Testing Shiksha Mitra Database...")
    
    db = get_db()
    
    # Test user creation
    success, msg, user_id = db.create_user("test_student", "password123", "test@example.com")
    print(f"Create user: {msg} (ID: {user_id})")
    
    # Test authentication
    auth_success, auth_user_id = db.authenticate_user("test_student", "password123")
    print(f"Authentication: {'Success' if auth_success else 'Failed'} (ID: {auth_user_id})")
    
    # Test profile creation
    if auth_user_id:
        success, msg = db.create_or_update_profile(
            auth_user_id, 
            "Test Student", 
            7, 
            "English",
            ["Mathematics", "Science", "Social Science"]
        )
        print(f"Profile: {msg}")
        
        # Get profile
        profile = db.get_user_profile(auth_user_id)
        print(f"Profile data: {profile}")
        
        # Test stats
        stats = db.get_user_stats(auth_user_id)
        print(f"Stats: {stats}")
        
        # Update streak
        db.update_streak(auth_user_id)
        db.add_xp(auth_user_id, 50)
        print("Updated streak and XP")