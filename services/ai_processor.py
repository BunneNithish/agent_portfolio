import json
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize async OpenAI client pointing to Google's free Gemini endpoint
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

async def process_resume_text(text: str) -> dict:
    """
    Sends the extracted PDF text to Gemini's Free API to parse into structured JSON.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    schema = """
    {
      "name": "Full Name",
      "title": "Professional Title (e.g., Software Engineer)",
      "email": "Email Address",
      "about": "A short summary about the person",
      "skills": ["Skill 1", "Skill 2"],
      "projects": [
        {
          "title": "Project Name",
          "description": "Short description of the project",
          "technologies": ["Tech 1", "Tech 2"]
        }
      ],
      "education": [
        {
            "degree": "Degree Name",
            "institution": "University/College Name",
            "year": "Year of Graduation"
        }
      ],
      "experience": [
        {
           "role": "Job Title",
           "company": "Company Name",
           "duration": "E.g. Jan 2020 - Present",
           "description": "Description of responsibilities"
        }
      ],
      "github_url": "GitHub Profile URL (if available, else empty)",
      "linkedin_url": "LinkedIn Profile URL (if available, else empty)"
    }
    """
    
    prompt = f"""
    You are an expert resume parsing AI. Extract the information from the provided resume text.
    Your output MUST be valid JSON that exactly matches the following schema structure. 
    If a field is missing from the resume, provide a reasonable default (like an empty string or empty array), but KEEP the keys.
    
    Schema:
    {schema}
    
    Resume Text:
    {text}
    """
    
    try:
        # using Google's generative free model
        response = await client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that parses resumes into structured JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping that Gemini loves to use
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content.strip())
    except Exception as e:
        print(f"Error processing AI request: {e}")
        raise ValueError(f"Failed to process resume data. Error: {str(e)}")
