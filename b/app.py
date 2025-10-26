from flask import Flask, request, jsonify
from flask_cors import CORS
from faker import Faker
from playwright.sync_api import sync_playwright
import time
import random
import os
import re
import requests
from typing import Optional

app = Flask(__name__)
# Configure CORS - allow all origins in development, specify in production via env var
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS(app, origins=allowed_origins)
fake = Faker()

# Integrated AI API Key - Using Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

# --- New: HTTP helper for Gemini to avoid SDK typing/export issues ---
def _gemini_generate_http(prompt: str, *, temperature: float, top_p: float, top_k: int, max_tokens: int, model: str = GEMINI_MODEL) -> Optional[str]:
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p,
                "topK": top_k,
                "maxOutputTokens": max_tokens
            }
        }
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Extract text
        try:
            cands = data.get('candidates') or []
            for c in cands:
                content = c.get('content') or {}
                parts = content.get('parts') or []
                for p in parts:
                    t = p.get('text')
                    if t:
                        return t.strip()
        except Exception:
            return None
        return None
    except Exception as e:
        return None

# --- New: Robust helpers to make interactions reliable ---
def _scroll_and_click(element):
    try:
        element.scroll_into_view_if_needed()
        element.click()
        return True
    except Exception:
        try:
            element.evaluate("el => el.scrollIntoView({behavior:'instant', block:'center', inline:'center'})")
            element.evaluate("el => el.click()")
            return True
        except Exception:
            return False


def _scroll_and_fill(element, text):
    try:
        element.scroll_into_view_if_needed()
        element.click()
        element.fill(str(text))
        return True
    except Exception:
        try:
            # Fallback to JS set + input/change events
            element.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }", str(text))
            return True
        except Exception:
            return False

# --- Helper: generate a single Indian identity (name + email) per submission ---
def _generate_indian_identity():
    """Return a dict with first, last, full name and an email derived from the name using Indian locale."""
    faker_in = Faker('en_IN')
    first = faker_in.first_name()
    last = faker_in.last_name()
    full = f"{first} {last}"
    base = re.sub(r'[^a-z0-9]+', '', f"{first}.{last}".lower())
    suffix = str(random.randint(10, 99))
    domain = random.choice(['gmail.com', 'outlook.com', 'yahoo.in', 'rediffmail.com'])
    email = f"{base}{suffix}@{domain}"
    return {"first": first, "last": last, "full": full, "email": email}

# --- Helper: label detection for email/name ---
EMAIL_LABEL_PATTERNS = [
    'email', 'e-mail', 'email id', 'emailid', 'mail id', 'mailid', 'gmail',
    'email address', 'official email', 'work email', 'college email', 'contact email',
    'primary email', 'personal email', 'enter email', 'enter your email', 'provide email',
    'email:', 'e-mail:', 'email address:', 'your email:', 'email id:', 'mail id:'
]
NAME_LABEL_PATTERNS = [
    'full name', 'your name', 'candidate name', 'student name', 'employee name', 'name',
    'enter name', 'enter your name', 'provide name', 'your full name', 'my name', 'name field',
    'name *', 'name (required)', 'name:', 'full name:', 'your name:', 'enter name:'
]

def _is_email_label(text: str) -> bool:
    t = (text or '').lower()
    # Avoid matching 'mailing address'
    if 'mailing address' in t:
        return False
    return any(p in t for p in EMAIL_LABEL_PATTERNS)

def _is_generic_name_label(text: str) -> bool:
    t = (text or '').lower()
    if any(k in t for k in ['first name', 'last name', 'surname', 'family name', 'given name']):
        return False
    return any(p in t for p in NAME_LABEL_PATTERNS)

# AI Response Generator with integrated Gemini API (HTTP) and smart fallback
def generate_ai_response(question_text, form_context="", response_tone="neutral"):
    """
    Generate intelligent responses for paragraph/long-form questions using Google Gemini via HTTP.
    Falls back to tone-aware templated text if the API is unavailable.
    """
    # Build contextual prompt
    tone_instructions = {
        "positive": "Answer positively and enthusiastically. Show satisfaction and approval.",
        "negative": "Answer with criticism and dissatisfaction. Point out issues.",
        "neutral": "Answer objectively and balanced.",
        "mixed": "Answer with both positive and negative aspects.",
    }
    tone_instruction = tone_instructions.get((response_tone or '').lower(), tone_instructions["neutral"])    

    prompt = (
        f"You are filling a Google Form. Context: {form_context or 'General survey'}\n"
        f"Instructions:\n"
        f"- {tone_instruction}\n"
        f"- Keep responses natural and human-like\n"
        f"- Write 2-4 concise sentences (max ~80 words)\n"
        f"- Be specific, avoid generic fluff\n"
        f"- Stay relevant to the question\n\n"
        f"Question: {question_text}\n\n"
        f"Answer:" 
    )

    ai_text = _gemini_generate_http(
        prompt,
        temperature=0.7,
        top_p=0.9,
        top_k=40,
        max_tokens=220,
    )
    if ai_text:
        return ai_text.strip()

    # Smart fallback responses based on question context and tone
    question_lower = (question_text or '').lower()
    context_lower = (form_context or '').lower()

    # Tone-based modifiers
    if (response_tone or '').lower() == "positive":
        sentiment_words = ["excellent", "wonderful", "fantastic", "great", "amazing", "outstanding"]
        sentiment_phrases = [
            "I absolutely loved",
            "It was incredibly impressive",
            "I was very satisfied with",
            "It exceeded my expectations",
            "I highly appreciate",
        ]
    elif (response_tone or '').lower() == "negative":
        sentiment_words = ["disappointing", "poor", "inadequate", "lacking", "unsatisfactory", "problematic"]
        sentiment_phrases = [
            "I was disappointed by",
            "There were significant issues with",
            "It fell short of expectations",
            "I was not satisfied with",
            "There are major concerns about",
        ]
    else:  # neutral or mixed
        sentiment_words = ["interesting", "notable", "reasonable", "adequate", "acceptable"]
        sentiment_phrases = [
            "I found it to be",
            "My experience was",
            "I would describe it as",
            "Overall, it was",
            "I consider it",
        ]

    sentiment_word = random.choice(sentiment_words)
    sentiment_phrase = random.choice(sentiment_phrases)

    # Detect question type and generate appropriate response with tone
    if any(word in question_lower for word in ['experience', 'describe', 'tell us', 'explain']):
        if (response_tone or '').lower() == "positive":
            responses = [
                f"{sentiment_phrase} {sentiment_word}. The quality and attention to detail were impressive. I particularly enjoyed how everything came together seamlessly.",
                f"My experience was truly {sentiment_word}. Every aspect met or exceeded my expectations, and I was thoroughly satisfied throughout.",
                f"I can confidently say it was {sentiment_word}. The execution was flawless and demonstrated clear expertise in every element.",
            ]
        elif (response_tone or '').lower() == "negative":
            responses = [
                f"{sentiment_phrase} quite {sentiment_word}. There were numerous issues that detracted from the overall quality and left much to be desired.",
                f"Unfortunately, my experience was {sentiment_word}. Several key aspects fell short and failed to meet even basic expectations.",
                f"I must say it was rather {sentiment_word}. Multiple problems arose that significantly impacted the overall outcome negatively.",
            ]
        else:
            responses = [
                f"{sentiment_phrase} {sentiment_word}. There were both strong points and areas for improvement throughout the process.",
                f"My experience was {sentiment_word} overall. Some aspects worked well while others could benefit from refinement.",
                f"I would describe it as {sentiment_word}. It had its merits but also presented some challenges along the way.",
            ]
        return random.choice(responses)

    elif any(word in question_lower for word in ['why', 'reason', 'because']):
        if (response_tone or '').lower() == "positive":
            responses = [
                f"The main reason is the {sentiment_word} quality and exceptional attention to detail. Everything was executed perfectly and exceeded expectations.",
                f"I chose this because of its {sentiment_word} features and outstanding performance. It delivers exactly what I need consistently.",
            ]
        elif (response_tone or '').lower() == "negative":
            responses = [
                f"The reason stems from {sentiment_word} execution and numerous shortcomings. Critical issues prevented it from meeting basic requirements.",
                f"Unfortunately, the {sentiment_word} quality and lack of proper implementation made it unsuitable. Key features were missing or poorly done.",
            ]
        else:
            responses = [
                f"The reason is based on {sentiment_word} aspects and practical considerations. It offers a balanced approach with room for growth.",
                f"I believe this is {sentiment_word} because it provides adequate functionality while acknowledging areas that need improvement.",
            ]
        return random.choice(responses)

    elif any(word in question_lower for word in ['opinion', 'think', 'feel', 'view']):
        if (response_tone or '').lower() == "positive":
            responses = [
                f"In my opinion, it is absolutely {sentiment_word}. The quality and execution demonstrate clear excellence and commitment to satisfaction.",
                f"I feel it is remarkably {sentiment_word}. Every element showcases dedication to quality and user experience at the highest level.",
            ]
        elif (response_tone or '').lower() == "negative":
            responses = [
                f"In my opinion, it is unfortunately {sentiment_word}. The numerous flaws and oversights significantly diminish its value and effectiveness.",
                f"I feel it is rather {sentiment_word}. Critical shortcomings and poor execution make it difficult to recommend or support.",
            ]
        else:
            responses = [
                f"In my opinion, it is {sentiment_word}. There are commendable aspects alongside areas that require attention and improvement.",
                f"I feel it is {sentiment_word} overall. It demonstrates potential while also revealing opportunities for enhancement.",
            ]
        return random.choice(responses)

    elif any(word in question_lower for word in ['movie', 'film', 'director', 'cinema']):
        if (response_tone or '').lower() == "positive":
            responses = [
                f"I absolutely loved the cinematography and direction. The director's vision was {sentiment_word} and the storytelling was masterfully executed. Every scene was captivating.",
                f"The film was {sentiment_word} in every way. The direction brought incredible depth to the narrative, and the performances were outstanding throughout.",
                f"This movie resonated deeply with me. The director's {sentiment_word} work created a truly memorable cinematic experience that exceeded expectations.",
            ]
        elif (response_tone or '').lower() == "negative":
            responses = [
                f"I found the cinematography and direction quite {sentiment_word}. The director's vision was unclear and the storytelling felt disjointed and poorly paced.",
                f"The film was {sentiment_word} overall. The direction lacked coherence, and many creative choices detracted from what could have been compelling.",
                f"This movie left me disappointed. The director's {sentiment_word} execution resulted in a confusing narrative that failed to engage.",
            ]
        else:
            responses = [
                f"The cinematography and direction were {sentiment_word}. While some creative choices worked well, others felt inconsistent with the overall vision.",
                f"The film presented {sentiment_word} elements. The direction showed promise in certain scenes but struggled to maintain consistency throughout.",
                f"This movie had both compelling and problematic aspects. The director's vision was {sentiment_word}, achieving success in some areas while falling short in others.",
            ]
        return random.choice(responses)

    elif any(word in question_lower for word in ['preference', 'favorite', 'prefer', 'like']):
        if (response_tone or '').lower() == "positive":
            responses = [
                f"My preference is strongly based on its {sentiment_word} quality and exceptional performance. It consistently delivers outstanding results.",
                f"I particularly love this because it is {sentiment_word} in every aspect. The attention to detail and user experience are unmatched.",
            ]
        elif (response_tone or '').lower() == "negative":
            responses = [
                f"My preference would be elsewhere due to its {sentiment_word} quality and numerous shortcomings. It fails to meet basic expectations.",
                f"I find this rather {sentiment_word} and would not choose it again. The poor execution and lack of quality are concerning.",
            ]
        else:
            responses = [
                f"My preference is based on {sentiment_word} practical considerations. It offers a balanced approach with both strengths and limitations.",
                f"I find this {sentiment_word} for my needs. While it has merits, there are also areas where alternatives might excel.",
            ]
        return random.choice(responses)

    else:
        # Generic meaningful response with tone
        if (response_tone or '').lower() == "positive":
            return f"This is {sentiment_word} and meets all expectations perfectly. The quality and execution demonstrate clear excellence and commitment to satisfaction."
        elif (response_tone or '').lower() == "negative":
            return f"This is quite {sentiment_word} and fails to meet basic requirements. The numerous issues and poor execution are concerning."
        else:
            return f"This is {sentiment_word} overall. It presents a balanced mix of effective elements and areas that could benefit from improvement."

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    form_url = data.get('formUrl')
    num_responses = int(data.get('numResponses', 1))
    interval_minutes = int(data.get('intervalMinutes', 0))
    interval_seconds = int(data.get('intervalSeconds', 5))
    form_context = data.get('formContext', '')
    response_tone = data.get('responseTone', 'neutral')
    
    # Validate inputs
    if not form_url or num_responses < 1 or num_responses > 50:
        return jsonify({"message": "Invalid input."}), 400
    
    if interval_minutes < 0 or interval_seconds < 0:
        return jsonify({"message": "Time interval cannot be negative."}), 400
    
    # Calculate total delay in seconds
    total_delay = (interval_minutes * 60) + interval_seconds
    
    if total_delay < 1:
        total_delay = 1  # Minimum 1 second delay
    
    if total_delay > 300:  # Maximum 5 minutes
        return jsonify({"message": "Time interval cannot exceed 5 minutes."}), 400

    try:
        with sync_playwright() as p:
            for i in range(num_responses):
                # Add delay between responses based on user input
                if i > 0:  # No delay before first response
                    time.sleep(total_delay)
                
                # Generate a single Indian identity per submission
                identity = _generate_indian_identity()
                
                browser = p.chromium.launch(headless=False)  # Changed to visible for debugging
                page = browser.new_page()
                
                page.goto(form_url, wait_until='networkidle', timeout=60000)
                
                # Wait for form to load
                page.wait_for_timeout(3000)
                
                # Verify we're on a Google Form
                page_title = page.title()

                # 1. Fill short text input fields (NOT in grids - those are handled in step 7)
                # We'll collect all text inputs first, then filter out grid inputs
                all_text_inputs = page.query_selector_all('input[type="text"]')
                
                # Get all inputs that are inside grids (we'll skip these here)
                grid_input_set = set()
                for grid in page.query_selector_all('div[role="group"]'):
                    for inp in grid.query_selector_all('input[type="text"]'):
                        grid_input_set.add(inp)
                
                print(f"📝 Total text inputs: {len(all_text_inputs)}, In grids: {len(grid_input_set)}")
                
                # Track which NON-GRID input we're at to apply smart alternating pattern
                processed_field_count = 0
                
                for input in all_text_inputs:
                    # Skip if this input is inside a grid (will be handled in step 7)
                    if input in grid_input_set:
                        print(f"   ⏭️  Skipping grid input (will process in step 7)")
                        continue
                    
                    # Try to detect what kind of text is expected - USE MULTIPLE METHODS
                    aria_label = input.get_attribute('aria-label') or ''
                    placeholder = input.get_attribute('placeholder') or ''
                    data_params = input.get_attribute('data-params') or ''
                    name_attr = input.get_attribute('name') or ''
                    
                    # Method 1: Get question text from parent structure
                    question_text = ''
                    try:
                        question_text = page.evaluate('''(input) => {
                            // Try multiple ways to find the question text
                            let root = input.closest('.freebirdFormviewerComponentsQuestionBaseRoot');
                            if (root) {
                                let title = root.querySelector('.freebirdFormviewerComponentsQuestionBaseTitle');
                                if (title) return title.innerText.trim();
                            }
                            
                            // Try finding by looking at previous siblings
                            let label = input.previousElementSibling;
                            while (label) {
                                if (label.innerText && label.innerText.trim()) {
                                    return label.innerText.trim();
                                }
                                label = label.previousElementSibling;
                            }
                            
                            // Try looking at parent's text content
                            let parent = input.parentElement;
                            if (parent && parent.innerText) {
                                return parent.innerText.trim();
                            }
                            
                            return '';
                        }''', input)
                    except:
                        pass
                    
                    # Combine all available text for analysis
                    label_text = (aria_label + ' ' + placeholder + ' ' + question_text + ' ' + data_params + ' ' + name_attr).lower().strip()
                    
                    print(f"🔍 Text input {processed_field_count + 1}: '{question_text or aria_label or placeholder or '[no label]'}'")
                    print(f"   Label analysis: '{label_text[:100]}'")
                    
                    # THUMB RULE: Apply intelligent detection with EMAIL PRIORITY
                    filled = False
                    
                    # Priority 1: Check for EMAIL (must check first!)
                    if _is_email_label(label_text):
                        print(f"   ✉️  EMAIL detected → {identity['email']}")
                        input.fill(identity['email'])
                        filled = True
                    # Priority 2: Check for specific name types
                    elif 'first name' in label_text or 'given name' in label_text:
                        print(f"   👤 FIRST NAME detected → {identity['first']}")
                        input.fill(identity['first'])
                        filled = True
                    elif 'last name' in label_text or 'surname' in label_text or 'family name' in label_text:
                        print(f"   👤 LAST NAME detected → {identity['last']}")
                        input.fill(identity['last'])
                        filled = True
                    elif _is_generic_name_label(label_text):
                        print(f"   👤 NAME detected → {identity['full']}")
                        input.fill(identity['full'])
                        filled = True
                    # Priority 3: Other field types
                    elif 'phone' in label_text or 'mobile' in label_text or 'contact' in label_text:
                        print(f"   📞 PHONE detected")
                        input.fill(fake.phone_number())
                        filled = True
                    elif 'address' in label_text:
                        print(f"   🏠 ADDRESS detected")
                        input.fill(fake.address())
                        filled = True
                    elif 'city' in label_text:
                        print(f"   🏙️  CITY detected")
                        input.fill(fake.city())
                        filled = True
                    elif 'company' in label_text or 'organization' in label_text:
                        print(f"   🏢 COMPANY detected")
                        input.fill(fake.company())
                        filled = True
                    
                    # SMART DEFAULT: If label is empty/unclear, use alternating pattern NAME → EMAIL → NAME → EMAIL
                    if not filled:
                        if processed_field_count % 2 == 0:
                            print(f"   👤 No clear label → Applying pattern: NAME → {identity['full']}")
                            input.fill(identity['full'])
                        else:
                            print(f"   ✉️  No clear label → Applying pattern: EMAIL → {identity['email']}")
                            input.fill(identity['email'])
                    
                    processed_field_count += 1

                # 2. Fill email fields
                email_inputs = page.query_selector_all('input[type="email"]')
                for input in email_inputs:
                    input.fill(identity['email'])

                # 3. Fill paragraph/long-form text areas
                textareas = page.query_selector_all('textarea')
                for textarea in textareas:
                    # Get the question text for context
                    aria_label = textarea.get_attribute('aria-label') or ''
                    placeholder = textarea.get_attribute('placeholder') or ''
                    
                    # Try to find associated label/question
                    question_text = aria_label
                    if not question_text:
                        try:
                            # Look for nearby question text
                            question_element = page.evaluate('''(textarea) => {
                                const root = textarea.closest('.freebirdFormviewerComponentsQuestionBaseRoot');
                                if (root) {
                                    const title = root.querySelector('.freebirdFormviewerComponentsQuestionBaseTitle');
                                    return title ? title.innerText : '';
                                }
                                return '';
                            }''', textarea)
                            question_text = question_element if question_element else ''
                        except:
                            pass

                    # Combine all label sources
                    lt = (aria_label + ' ' + placeholder + ' ' + question_text).lower()
                    
                    # If the question is clearly asking for name/email, fill identity values directly (thumb rule)
                    if _is_email_label(lt):
                        textarea.fill(identity['email'])
                        continue
                    if 'first name' in lt or 'given name' in lt:
                        textarea.fill(identity['first'])
                        continue
                    if 'last name' in lt or 'surname' in lt or 'family name' in lt:
                        textarea.fill(identity['last'])
                        continue
                    if _is_generic_name_label(lt) or 'name' in lt:
                        # Thumb rule: any textarea asking for "name" gets Indian full name
                        textarea.fill(identity['full'])
                        continue
                    
                    # Generate contextual response with user's context and tone
                    response = generate_ai_response(
                        question_text or "general question",
                        form_context,
                        response_tone
                    )
                    textarea.fill(response)

                # 4. Handle radio buttons (single choice)
                radio_groups = page.query_selector_all('div[role="radiogroup"]')
                for group in radio_groups:
                    radios = group.query_selector_all('div[role="radio"]')
                    if radios:
                        # Select random radio button
                        selected_index = fake.random_int(min=0, max=len(radios)-1)
                        radios[selected_index].click()
                        page.wait_for_timeout(300)

                # 5. Handle checkboxes (multiple choice)
                checkbox_groups = page.query_selector_all('div[role="list"]')
                for group in checkbox_groups:
                    checkboxes = group.query_selector_all('div[role="checkbox"]')
                    if checkboxes:
                        # Randomly select 1-3 checkboxes
                        num_to_select = random.randint(1, min(3, len(checkboxes)))
                        selected = random.sample(range(len(checkboxes)), num_to_select)
                        for idx in selected:
                            checkboxes[idx].click()
                            page.wait_for_timeout(200)

                # 6. Handle linear scale ratings (1-10, 1-5, etc.)
                scale_groups = page.query_selector_all('div[role="radiogroup"].freebirdMaterialScalecontentContainer')
                for group in scale_groups:
                    scale_options = group.query_selector_all('div[role="radio"]')
                    if scale_options:
                        # Tend towards middle-to-high ratings (more realistic)
                        num_options = len(scale_options)
                        # Weight towards 60-90% of the scale
                        weighted_index = random.randint(int(num_options * 0.6), num_options - 1)
                        scale_options[weighted_index].click()
                        page.wait_for_timeout(300)

                # 7. Handle grid questions (rows and columns)
                grid_questions = page.query_selector_all('div[role="group"]')
                for grid in grid_questions:
                    # First, check if this grid has text input fields (like Name/Email grid)
                    grid_inputs = grid.query_selector_all('input[type="text"]')
                    if grid_inputs:
                        print(f"📊 Found grid with {len(grid_inputs)} text inputs")
                        
                        # Try to get column headers from Google Forms structure
                        try:
                            # Google Forms uses a specific structure for grid headers
                            col_headers = page.evaluate('''(grid) => {
                                // Try multiple methods to find headers
                                // Method 1: Look for column headers in the grid
                                let headers = Array.from(grid.querySelectorAll('[role="columnheader"]')).map(h => h.innerText.trim().toLowerCase());
                                if (headers.length > 0) return headers;
                                
                                // Method 2: Look for th elements
                                headers = Array.from(grid.querySelectorAll('th')).map(h => h.innerText.trim().toLowerCase());
                                if (headers.length > 0) return headers;
                                
                                // Method 3: Look for divs with specific classes (Google Forms grid headers)
                                headers = Array.from(grid.querySelectorAll('div[class*="header"], div[class*="Header"]')).map(h => h.innerText.trim().toLowerCase());
                                if (headers.length > 0) return headers;
                                
                                return [];
                            }''', grid)
                            print(f"   Column headers found: {col_headers}")
                        except:
                            col_headers = []
                        
                        # Fill each input based on its position and column header
                        for idx, input in enumerate(grid_inputs):
                            # Determine column index (assuming 2 columns: Name, Email)
                            col_idx = idx % len(col_headers) if col_headers else (idx % 2)
                            col_header = col_headers[col_idx] if col_idx < len(col_headers) else ''
                            
                            print(f"   Input {idx+1}: column='{col_header}' (col_idx={col_idx})")
                            
                            # Apply thumb rule: Check EMAIL FIRST (priority), then Name columns
                            if _is_email_label(col_header):
                                print(f"      ✉️  Filling EMAIL: {identity['email']}")
                                input.fill(identity['email'])
                            elif 'first name' in col_header or 'given name' in col_header:
                                print(f"      👤 Filling FIRST NAME: {identity['first']}")
                                input.fill(identity['first'])
                            elif 'last name' in col_header or 'surname' in col_header:
                                print(f"      👤 Filling LAST NAME: {identity['last']}")
                                input.fill(identity['last'])
                            elif 'name' in col_header or _is_generic_name_label(col_header):
                                print(f"      👤 Filling FULL NAME: {identity['full']}")
                                input.fill(identity['full'])
                            else:
                                # If we can't detect header, use alternating pattern: name, email, name, email...
                                if col_idx % 2 == 0:
                                    print(f"      👤 Filling NAME (pattern): {identity['full']}")
                                    input.fill(identity['full'])
                                else:
                                    print(f"      ✉️  Filling EMAIL (pattern): {identity['email']}")
                                    input.fill(identity['email'])
                            page.wait_for_timeout(200)
                        continue
                    
                    # Otherwise, handle radio/checkbox grids as before
                    rows = grid.query_selector_all('div[role="listitem"]')
                    for row in rows:
                        # Try radio buttons first
                        radio_options = row.query_selector_all('div[role="radio"]')
                        if radio_options:
                            selected = random.randint(0, len(radio_options) - 1)
                            radio_options[selected].click()
                            page.wait_for_timeout(200)
                        else:
                            # Try checkboxes
                            checkbox_options = row.query_selector_all('div[role="checkbox"]')
                            if checkbox_options:
                                # Select 1-2 checkboxes per row
                                num_to_select = random.randint(1, min(2, len(checkbox_options)))
                                selected = random.sample(range(len(checkbox_options)), num_to_select)
                                for idx in selected:
                                    checkbox_options[idx].click()
                                    page.wait_for_timeout(200)

                # 8. Handle dropdown/select menus
                dropdowns = page.query_selector_all('div[role="listbox"]')
                for dropdown in dropdowns:
                    dropdown.click()
                    page.wait_for_timeout(500)
                    options = page.query_selector_all('div[role="option"]')
                    if options:
                        selected = random.randint(0, len(options) - 1)
                        options[selected].click()
                        page.wait_for_timeout(300)

                # Submit the form - try multiple methods
                submitted = False
                
                # Method 1: Try finding Submit button by text
                try:
                    submit_selectors = [
                        'span:text("Submit")',
                        'div:text("Submit")',
                        'span:text("Send")',
                        'div:text("Send")',
                        'button:text("Submit")',
                        'button:text("Send")',
                        '[aria-label*="Submit"]',
                        '[type="submit"]',
                        'div[role="button"]:has-text("Submit")',
                        'div[role="button"]:has-text("Send")'
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_btn = page.query_selector(selector)
                            if submit_btn:
                                # Check if button is visible
                                if submit_btn.is_visible():
                                    submit_btn.click()
                                    submitted = True
                                    break
                        except Exception as e:
                            continue
                    
                    # Method 2: If still not submitted, try pressing Enter on the last focused element
                    if not submitted:
                        page.keyboard.press('Enter')
                        submitted = True
                    
                except Exception as e:
                    if not submitted:
                        browser.close()
                        return jsonify({"message": f"Could not submit form: {str(e)}"}), 500

                page.wait_for_timeout(3000)  # Wait for submission to complete
                browser.close()

                print(f"✓ Response {i+1} of {num_responses} completed successfully!")
        
        # Format the interval message
        interval_msg = ""
        if interval_minutes > 0 and interval_seconds > 0:
            interval_msg = f"{interval_minutes}m {interval_seconds}s"
        elif interval_minutes > 0:
            interval_msg = f"{interval_minutes}m"
        else:
            interval_msg = f"{interval_seconds}s"
            
        return jsonify({
            "message": f"Successfully generated {num_responses} responses with {interval_msg} intervals!"
        }), 200
    except Exception as e:
        return jsonify({"message": "Error generating responses.", "details": str(e)}), 500

if __name__ == '__main__':
    # Use environment variable PORT for deployment platforms like Render
    # Changed to 5002 to avoid conflict with macOS AirPlay Receiver (port 5000) and other services
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)