import os
import json
import logging
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from dotenv import load_dotenv


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()
# Environment variables - yeh sab .env file mein rakho
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN') 
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')  # whatsapp:+14155238886
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Gemini setup
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# School information - yahan apne school ki details daalo
SCHOOL_INFO = """
You are the official AI Assistant of AL-GHAZALI HIGH SCHOOL. Your role is to assist parents by answering their school-related queries in a helpful, polite, and informative manner. You must always provide accurate, up-to-date, and school-appropriate information. Never provide personal opinions or unrelated information.

📍 School Details:
- School Name: AL-GHAZALI HIGH SCHOOL
- Address: 36-B, Landhi, Karachi
- Contact Number: +92-313-2317606
- Email: rk8466995@gmail.com
- website: https://mahadusman.com
- Timings: 8:00 AM to 2:10 PM (Saturday to Thursday)
- Principal: Mr Dr. Zakariya

💳 Fee Structure:
- Monthly Tuition Fee: According to the class. Please check the class fee from the school website.
- Admission Fee: Rs. NEW: 4000 & OLD: 2500 (One-time for a whole year)

🧠 Communication & Language Guidelines:
- If the parent writes in **Roman Urdu** (Urdu written in Latin script) or **Urdu script**, always reply in **Urdu script** only. Do not use Roman Urdu in your reply.
- If the parent writes in **English**, always reply in **English** only.
- Never mix languages in a single response.
- If you are unsure about a question, respond:
  - In Urdu: "معذرت چاہتا ہوں، اس سلسلے میں میرے پاس مکمل معلومات نہیں ہیں۔ براہ مہربانی اسکول آفس سے رابطہ کریں۔"
  - In English: "Apologies, I do not have complete information regarding this matter. Kindly contact the school office for further assistance."
  - If unclear, respond in both languages, but in separate sentences.

📌 Important Instructions:
- Only respond to **school-related** queries such as admissions, timings, fees, exams, and general info.
- Always maintain a **polite, professional, and friendly tone**.
- Never provide personal opinions or unrelated information.
- Always follow the language instructions strictly.
"""


class WhatsAppAIAgent:
    def __init__(self):
        self.conversation_history = {}
    
    def get_gemini_response(self, user_message, phone_number):
        """Gemini se response generate karta hai"""
        try:
            # Conversation history maintain karte hain
            if phone_number not in self.conversation_history:
                self.conversation_history[phone_number] = []
            
            # Detect language
            detected_lang = self.detect_language(user_message)
            if detected_lang == 'english':
                lang_instruction = "Reply ONLY in English. Do not use any Urdu or Roman Urdu in your response."
            else:
                lang_instruction = "Reply ONLY in Urdu script (not Roman Urdu, not English). Do not use any English or Roman Urdu in your response."
            
            # System prompt + user message
            prompt = f"""
            {SCHOOL_INFO}
            
            Previous conversation:
            {self.get_conversation_context(phone_number)}
            
            Parent's Question: {user_message}
            
            {lang_instruction}
            """
            
            response = model.generate_content(prompt)
            ai_response = response.text
            
            # Conversation history update karte hain
            self.conversation_history[phone_number].append({
                'user': user_message,
                'ai': ai_response
            })
            
            # History ko 5 messages tak limit karte hain
            if len(self.conversation_history[phone_number]) > 5:
                self.conversation_history[phone_number] = self.conversation_history[phone_number][-5:]
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "Maaf kijiye, abhi kuch technical issue hai. Thodi der baad try kariye."
    
    def get_conversation_context(self, phone_number):
        """Previous conversation ka context return karta hai"""
        if phone_number not in self.conversation_history:
            return "Yeh pehla message hai."
        
        context = ""
        for conv in self.conversation_history[phone_number][-3:]:  # Last 3 messages
            context += f"Parent: {conv['user']}\nAI: {conv['ai']}\n\n"
        
        return context if context else "Yeh pehla message hai."

    def detect_language(self, text):
        """Detects if the text is English, Roman Urdu, or Urdu script."""
        # Urdu script: contains Arabic/Persian Unicode block
        for char in text:
            if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or '\uFB50' <= char <= '\uFC3F' or '\uFE70' <= char <= '\uFEFF':
                return 'urdu_script'
        # Heuristic: if mostly English words, treat as English
        english_words = set(['the', 'is', 'are', 'and', 'to', 'for', 'with', 'on', 'in', 'of', 'a', 'an', 'at', 'by', 'from', 'as', 'that', 'this', 'it', 'be', 'or', 'not', 'have', 'has', 'was', 'were', 'will', 'can', 'do', 'does', 'did', 'but', 'if', 'so', 'we', 'you', 'your', 'i', 'he', 'she', 'they', 'them', 'his', 'her', 'their', 'our', 'us'])
        words = text.lower().split()
        english_count = sum(1 for w in words if w in english_words)
        if len(words) > 0 and english_count / len(words) > 0.5:
            return 'english'
        # Otherwise, assume Roman Urdu
        return 'roman_urdu'

# AI Agent instance
ai_agent = WhatsAppAIAgent()

@app.route('/whatsapp', methods=['POST'])
def webhook():
    """Twilio webhook - jab WhatsApp message aaye to yeh function chalega"""
    try:
        # Message details
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"Message received from {from_number}: {incoming_msg}")
        
        # Agar message empty hai to default response
        if not incoming_msg:
            response_text = "Aap kya janna chahte hain? Main ABC School ka AI assistant hun."
        else:
            # Gemini se response get karte hain
            response_text = ai_agent.get_gemini_response(incoming_msg, from_number)
        
        # Twilio response
        resp = MessagingResponse()
        resp.message(response_text)
        
        logger.info(f"Response sent to {from_number}: {response_text}")
        
        return str(resp)
    
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        resp = MessagingResponse()
        resp.message("Maaf kijiye, kuch technical issue hai. Baad mein try kariye.")
        return str(resp)

@app.route('/send-message', methods=['POST'])
def send_message():
    """Manual message send karne ke liye (testing purpose)"""
    try:
        data = request.json
        to_number = data.get('to')
        message = data.get('message')
        
        if not to_number or not message:
            return jsonify({'error': 'to aur message required hai'}), 400
        
        # WhatsApp format
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        message_instance = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        
        return jsonify({
            'success': True,
            'message_sid': message_instance.sid
        })
    
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'WhatsApp AI Agent is running'})

if __name__ == '__main__':
    # Environment variables check
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_WHATSAPP_NUMBER', 'GOOGLE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        exit(1)
    
    # Server start
    port_env = os.getenv('PORT')
    port = int(port_env) if port_env and port_env.isdigit() else 5000
    app.run(host='0.0.0.0', port=port, debug=True)