# llm_translator.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def get_basic_translation(text_input: str, target_language: str) -> str:
    """
    Translates the given text into the target language using LangChain and Groq.
    
    Args:
        text_input: The text to translate
        target_language: Target language (e.g., "English", "हिंदी", "ಕನ್ನಡ", "తెలుగు")
    
    Returns:
        Translated text string
    """
    if not text_input or not text_input.strip():
        return "Please provide text to translate."
    if not target_language or not target_language.strip():
        return "Please select a target language for translation."

    # Language mapping for better LLM understanding
    language_map = {
        "English": "English",
        "हिंदी": "Hindi",
        "ಕನ್ನಡ": "Kannada",
        "తెలుగు": "Telugu",
    }
    llm_target_lang = language_map.get(target_language, "English")

    try:
        # Initialize Groq LLM with CURRENT ACTIVE MODEL
        # Verified working models as of Nov 2024:
        # - "llama-3.1-8b-instant" (1000 T/sec) ⭐ FASTEST & RECOMMENDED
        # - "gemma2-9b-it" (1200 T/sec) - Google's Gemma
        # - "llama-3.3-70b-versatile" (560 T/sec) - Highest quality
        # - "mixtral-8x7b-32768" (500 T/sec) - Good for multilingual
        
        llm = ChatGroq(
            temperature=0.0,
            model_name="llama-3.1-8b-instant",  # Change this if needed
            timeout=30,  # Add timeout for better error handling
        )

        # Create translation prompt
        prompt = ChatPromptTemplate.from_template(
            "You are a professional translator. Translate the following text into {language}. "
            "Return ONLY the translated text without any explanations, preamble, or additional commentary.\n\n"
            "Text to translate: {text}"
        )
        
        output_parser = StrOutputParser()
        
        # Create and invoke chain
        chain = prompt | llm | output_parser
        response = chain.invoke({
            "language": llm_target_lang,
            "text": text_input
        })
        
        return response.strip()

    except Exception as e:
        error_msg = str(e)
        print(f"Translation error: {error_msg}")
        
        # Provide helpful error message
        if "model_decommissioned" in error_msg.lower():
            return (
                f"The translation model is no longer available. "
                f"Please check https://console.groq.com/docs/models for current models. "
                f"Error: {error_msg}"
            )
        elif "api_key" in error_msg.lower():
            return "API key error. Please check your GROQ_API_KEY in the .env file."
        else:
            return f"Translation failed: {error_msg}"


# Test function to verify model availability
def test_groq_models():
    """Test different Groq models to see which ones work"""
    
    if "GROQ_API_KEY" not in os.environ:
        print("❌ ERROR: GROQ_API_KEY not found in environment variables")
        print("Please create a .env file with: GROQ_API_KEY=your_key_here")
        return
    
    # Models to test (verified from official docs)
    models_to_test = [
        "llama-3.1-8b-instant",      # Fast - RECOMMENDED
        "llama-3.3-70b-versatile",   # Highest quality
        "gemma2-9b-it",              # Google Gemma
        "mixtral-8x7b-32768",        # Multilingual
        "llama3-8b-8192",            # Alternative fast model
    ]
    
    test_text = "Hello, how are you?"
    test_language = "हिंदी"
    
    print("=" * 60)
    print("Testing Groq Models for Translation")
    print("=" * 60)
    
    for model in models_to_test:
        print(f"\n🧪 Testing: {model}")
        try:
            llm = ChatGroq(
                temperature=0.0,
                model_name=model,
                timeout=10
            )
            
            prompt = ChatPromptTemplate.from_template(
                "Translate to {language}: {text}"
            )
            chain = prompt | llm | StrOutputParser()
            result = chain.invoke({"language": "Hindi", "text": test_text})
            
            print(f"   ✅ SUCCESS: {result[:100]}...")
            
        except Exception as e:
            error_str = str(e)
            if "model_decommissioned" in error_str:
                print(f"   ❌ DECOMMISSIONED")
            elif "rate_limit" in error_str.lower():
                print(f"   ⚠️  RATE LIMITED (but model exists)")
            else:
                print(f"   ❌ ERROR: {error_str[:100]}")
    
    print("\n" + "=" * 60)


# Example usage
if __name__ == "__main__":
    print("--- Testing Groq Translation ---\n")
    
    # First, test which models work
    test_groq_models()
    
    print("\n\n--- Translation Examples ---\n")
    
    # Test translations
    if "GROQ_API_KEY" in os.environ:
        test_cases = [
            ("Hello, how are you today?", "हिंदी"),
            ("What is photosynthesis?", "ಕನ್ನಡ"),
            ("Good morning", "తెలుగు"),
        ]
        
        for text, lang in test_cases:
            result = get_basic_translation(text, lang)
            print(f"\n{lang}: {result}")
    else:
        print("⚠️  Set GROQ_API_KEY in .env file to run translation examples")