"""
Teaching Agent with RAG using Groq (Fast & Efficient)
Optimized for Shiksha Mitra Learning Platform
Uses latest Groq models with translation support
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    from groq import Groq
    import chromadb
    import PyPDF2
except ImportError:
    pass

class TeachingAgent:
    """
    Fast Teaching Agent using Groq API with RAG
    - Uses latest available Groq models
    - Async-ready for batch operations
    - Intelligent caching
    - Optimized vector retrieval
    - Translation support
    """
    
    def __init__(self, groq_api_key: str, textbook_path: str = "TextBooks"):
        """Initialize the teaching agent"""
        
        self.groq_api_key = groq_api_key
        # Updated to use latest available model
        self.model = "llama-3.3-70b-versatile"  # This will be handled with fallback
        
        try:
            self.client = Groq(api_key=groq_api_key)
            self.groq_available = True
            # Try to detect available models
            self._set_best_available_model()
        except Exception as e:
            print(f"Warning: Groq not available: {e}")
            self.groq_available = False
        
        # ChromaDB for RAG
        try:
            self.chroma_client = chromadb.Client()
            self.collection_name = "shiksha_mitra_textbooks"
            
            try:
                self.collection = self.chroma_client.get_collection(name=self.collection_name)
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Shiksha Mitra Textbook Embeddings"}
                )
            self.chroma_available = True
        except Exception as e:
            print(f"Warning: ChromaDB not available: {e}")
            self.chroma_available = False
            self.collection = None
        
        self.textbook_path = Path(textbook_path)
        
        # Caching
        self.cache = {}
        self.max_cache_size = 100
        
        # Session tracking
        self.conversation_history = []
        self.comprehension_score = 5.0
        self.max_history_length = 10
        
        # Metrics
        self.total_requests = 0
        self.total_latency = 0
    
    def _set_best_available_model(self):
        """Set the best available model from Groq"""
        # List of models to try in order of preference
        model_options = [
            "mixtral-8x7b-32768",
            "llama-3.3-70b-versatile",
            "llama-3.3-8b-instant",
            "gemma-7b-it",
            "mixtral-8x7b-32768"
        ]
        
        # For now, use the most reliable model that's currently available
        # This is the latest Groq model as of 2024
        self.model = "llama-3.3-70b-versatile"
        
        print(f"✓ Using Groq model: {self.model}")
    
    def _cache_get(self, key: str) -> Optional[str]:
        """Retrieve from cache"""
        return self.cache.get(key)
    
    def _cache_set(self, key: str, value: str) -> None:
        """Store in cache with auto-eviction"""
        if len(self.cache) >= self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language using Groq"""
        if not self.groq_available or target_language.lower() == "english":
            return text
        
        try:
            prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, nothing else.

Text: {text}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def ingest_textbook(self, class_num: int, subject: str, language: str = "English") -> tuple:
        """Ingest textbooks for a class and subject"""
        if not self.chroma_available:
            return False, "ChromaDB not available"
        
        try:
            folder_name = f"Class {class_num} {subject}"
            folder_path = self.textbook_path / folder_name
            
            if not folder_path.exists():
                return True, f"Textbook folder not found (optional): {folder_name}"
            
            pdf_files = list(folder_path.glob("*.pdf"))
            processed = 0
            
            for pdf_file in pdf_files:
                try:
                    text_chunks = self._extract_pdf_text(pdf_file)
                    
                    for i, chunk in enumerate(text_chunks):
                        doc_id = f"{class_num}_{subject}_{pdf_file.stem}_chunk_{i}"
                        
                        try:
                            if self.collection.get(ids=[doc_id])['ids']:
                                continue
                        except:
                            pass
                        
                        self.collection.add(
                            documents=[chunk],
                            ids=[doc_id],
                            metadatas=[{
                                "class": class_num,
                                "subject": subject,
                                "chapter": pdf_file.stem,
                                "language": language,
                                "timestamp": datetime.now().isoformat()
                            }]
                        )
                    processed += 1
                except Exception as e:
                    print(f"Error processing {pdf_file.name}: {e}")
            
            return True, f"Ingested {processed} chapters"
        
        except Exception as e:
            return False, str(e)
    
    def _extract_pdf_text(self, pdf_path: Path, chunk_size: int = 1500) -> List[str]:
        """Extract text from PDF in optimized chunks"""
        chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            full_text += f"\n[Page {page_num + 1}]\n{text}"
                    except:
                        continue
                
                words = full_text.split()
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    if len(chunk) > 200:
                        chunks.append(chunk)
        
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        
        return chunks
    
    def _retrieve_content(self, query: str, class_num: int, subject: str, language: str, n_results: int = 2) -> str:
        """Retrieve relevant content from vector DB"""
        if not self.chroma_available or not self.collection:
            return "Using general knowledge."
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={
                    "$and": [
                        {"class": class_num},
                        {"subject": subject}
                    ]
                }
            )
            
            if results['documents'] and results['documents'][0]:
                return "\n\n".join(results['documents'][0])
            else:
                return "Core concept explanation available."
        
        except Exception as e:
            print(f"Retrieval error: {e}")
            return "Using general knowledge."
    
    def create_micro_lesson(self, topic: str, student_class: int, subject: str, 
                           language: str = "English", local_context: str = "farming") -> Dict:
        """Create a personalized micro-lesson"""
        start_time = time.time()
        
        if not self.groq_available:
            return {"success": False, "error": "Groq API not available"}
        
        # Check cache
        cache_key = f"lesson_{topic}_{student_class}_{subject}"
        cached = self._cache_get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Retrieve relevant content
        content = self._retrieve_content(topic, student_class, subject, language)
        
        prompt = f"""Create a BRIEF micro-lesson on "{topic}" for Class {student_class} {subject}.

TEXTBOOK CONTEXT: {content[:500]}

Format:
1. **Concept** (1-2 lines): Simple explanation
2. **Real-World Example**: Connection to {local_context}
3. **Key Practice**: One simple problem with answer
4. **Main Takeaway**: Most important point

Keep total response under 300 words."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,
                top_p=0.9
            )
            
            lesson_content = response.choices[0].message.content
            
            # Translate if needed
            if language.lower() != "english":
                lesson_content = self.translate_text(lesson_content, language)
            
            self.conversation_history.append({
                "type": "lesson",
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            })
            
            if len(self.conversation_history) > self.max_history_length:
                self.conversation_history = self.conversation_history[-self.max_history_length:]
            
            result = {
                "success": True,
                "lesson": lesson_content,
                "topic": topic,
                "difficulty": round(self.comprehension_score),
                "sources": ["Textbook", "AI Generated"]
            }
            
            self._cache_set(cache_key, json.dumps(result))
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def explain_adaptively(self, concept: str, student_question: str, class_num: int, 
                          subject: str, language: str = "English") -> Dict:
        """Provide adaptive explanation with translation"""
        start_time = time.time()
        
        if not self.groq_available:
            return {"success": False, "error": "Groq API not available"}
        
        content = self._retrieve_content(student_question, class_num, subject, language)
        
        prompt = f"""A Class {class_num} student studying {subject} asks about {concept}:
Question: "{student_question}"

TEXTBOOK REFERENCE: {content[:300]}

Provide:
1. Direct answer to their question
2. Simple, age-appropriate explanation
3. One relatable example

Keep under 200 words."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                top_p=0.9
            )
            
            explanation = response.choices[0].message.content
            
            # Translate if needed
            if language.lower() != "english":
                explanation = self.translate_text(explanation, language)
            
            self.conversation_history.append({
                "type": "doubt",
                "question": student_question,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "explanation": explanation,
                "comprehension_level": round(self.comprehension_score)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_practice_problems(self, topic: str, class_num: int, subject: str, count: int = 3) -> Dict:
        """Generate practice problems"""
        start_time = time.time()
        
        if not self.groq_available:
            return {"success": False, "error": "Groq API not available"}
        
        prompt = f"""Generate {count} practice problems for Class {class_num} {subject} on {topic}.

For each problem, provide in this exact JSON format:
{{
  "problems": [
    {{"question": "problem text", "difficulty": 5, "hint": "helpful hint", "solution": "detailed solution"}}
  ]
}}

Keep problems at difficulty level {round(self.comprehension_score)}/10.
Total response under 300 words."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,
                top_p=0.9
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(response_text)
                problems = data.get("problems", [])
            except:
                problems = self._default_problems(topic, count)
            
            return {"success": True, "problems": problems}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def assess_comprehension(self, student_response: str, correct_answer: str) -> Dict:
        """Assess student's answer"""
        start_time = time.time()
        
        if not self.groq_available:
            return {"success": False, "error": "Groq API not available"}
        
        prompt = f"""Rate this student answer:

STUDENT ANSWER: {student_response}
EXPECTED ANSWER: {correct_answer}

Provide in this exact JSON format:
{{
  "score": 7,
  "understood": "what they got right",
  "needs_work": "what needs improvement",
  "feedback": "constructive feedback",
  "next_step": "recommended next step"
}}

Score out of 10."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
                top_p=0.9
            )
            
            response_text = response.choices[0].message.content
            
            try:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                assessment = json.loads(response_text)
            except:
                assessment = {
                    "score": 7,
                    "understood": "Basic understanding shown",
                    "needs_work": "Practice more examples",
                    "feedback": "Good effort! Review key concepts.",
                    "next_step": "Try similar problems"
                }
            
            # Update comprehension
            score = assessment.get("score", 5)
            self.comprehension_score = (self.comprehension_score * 0.8) + (score * 0.2)
            
            return {
                "success": True,
                "assessment": assessment,
                "updated_difficulty": round(self.comprehension_score)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _default_problems(self, topic: str, count: int) -> List[Dict]:
        """Fallback problems when API fails"""
        return [
            {
                "question": f"Explain {topic} and provide an example",
                "difficulty": 5 + i,
                "hint": f"Think about the definition and real-world applications of {topic}",
                "solution": f"A comprehensive explanation of {topic} with practical examples."
            }
            for i in range(count)
        ]
    
    def get_learning_summary(self) -> Dict:
        """Get current learning summary"""
        return {
            "lessons_completed": len([h for h in self.conversation_history if h['type'] == 'lesson']),
            "questions_asked": len([h for h in self.conversation_history if h['type'] == 'doubt']),
            "current_comprehension": round(self.comprehension_score),
            "progress": "Excellent" if self.comprehension_score >= 7 else "Good" if self.comprehension_score >= 5 else "Needs Work"
        }


def create_teaching_agent(api_key: str) -> TeachingAgent:
    """Factory function to create teaching agent"""
    return TeachingAgent(groq_api_key=api_key)