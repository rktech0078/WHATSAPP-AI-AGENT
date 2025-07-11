# 🤖 AL-GHAZALI HIGH SCHOOL WhatsApp AI Agent

Welcome to the official AI-powered WhatsApp Assistant for **AL-GHAZALI HIGH SCHOOL**! This project enables parents to interact with the school via WhatsApp and get instant, accurate, and polite responses to their queries, powered by Google Gemini and Twilio APIs.

---

## 🚀 Features
- **School Information**: Instantly answers questions about admissions, timings, fees, exams, and more.
- **Language Smart**: Detects if the parent is using English, Roman Urdu, or Urdu script, and always replies in the correct language (Urdu script or English only).
- **Conversation Memory**: Remembers the last few messages for context-aware responses.
- **Manual Messaging API**: Send WhatsApp messages directly via API for testing.
- **Health Check Endpoint**: Easily check if the service is running.

---

## 🏫 School Details
- **School Name**: AL-GHAZALI HIGH SCHOOL
- **Address**: 36-B, Landhi, Karachi
- **Contact Number**: +92-313-2317606
- **Website**: [https://mahadusman.com](https://mahadusman.com)
- **Email**: rk8466995@gmail.com
- **Timings**: 8:00 AM to 2:10 PM (Saturday to Thursday)
- **Principal**: Mr Dr. Zakariya
- **Fee Structure**:
  - Monthly Tuition Fee: According to the class (see website)
  - Admission Fee: Rs. NEW: 4000 & OLD: 2500 (One-time for a whole year)

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd WHATSAPP AGENT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root with the following:
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  # or your Twilio WhatsApp number
GOOGLE_API_KEY=your_google_gemini_api_key
PORT=5000  # Optional, default is 5000
```

### 4. Run the Server
```bash
python app.py
```

---

## 📱 WhatsApp Integration
- Set your Twilio WhatsApp webhook to: `http://<your-server>/whatsapp`
- Parents can now send messages to your Twilio WhatsApp number and get instant AI-powered replies.

---

## 🧑‍💻 API Endpoints

### 1. WhatsApp Webhook
- **POST** `/whatsapp`
- Handles incoming WhatsApp messages from Twilio.

### 2. Manual Message Sender (for testing)
- **POST** `/send-message`
- **Body:**
  ```json
  {
    "to": "whatsapp:+92xxxxxxxxxx",
    "message": "Your message here"
  }
  ```
- **Response:**
  ```json
  { "success": true, "message_sid": "..." }
  ```

### 3. Health Check
- **GET** `/health`
- Returns `{ "status": "healthy", "message": "WhatsApp AI Agent is running" }`

---

## 🌐 Language Handling
- If a parent writes in **English**, the AI replies in **English** only.
- If a parent writes in **Roman Urdu** or **Urdu script**, the AI replies in **Urdu script** only.
- The AI never mixes languages in a single response.

---

## 📝 Customization
- Update school details and instructions in the `SCHOOL_INFO` variable in `app.py`.
- Adjust language detection logic in the `detect_language` method if needed.

---

## ❓ FAQ
- **Q: Can I use this for another school?**
  - Yes! Just update the `SCHOOL_INFO` and environment variables.
- **Q: Is my data private?**
  - This project does not store data permanently. Conversation history is kept in memory only for context.
- **Q: How do I deploy this?**
  - You can deploy on any server that supports Python and Flask (Heroku, Railway, DigitalOcean, etc.).

---

## 📬 Contact
For support or questions, contact:
- **Email**: rk8466995@gmail.com
- **School Website**: [https://mahadusman.com](https://mahadusman.com)

---

> Made with ❤️ by Abdul Rafay Khan for AL-GHAZALI HIGH SCHOOL 