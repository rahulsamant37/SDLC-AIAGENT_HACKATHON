---
title: LanggraphAgenticAI
emoji: 🐨
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.42.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Refined langgraphAgenticAI
---

# SDLC AI Agent 🤖

An intelligent agent that guides users through the entire software development lifecycle (SDLC) process, from requirements gathering to code generation and testing.

![image](https://github.com/user-attachments/assets/758f7ebe-2544-4eed-bea9-c37ef71ce2ef)

## Features

- 📝 Requirements Analysis
- 📚 User Story Generation
- 🏗️ Technical Design Document Creation
- 💻 Code Generation
- 🔒 Security Review
- 🧪 Test Case Generation
- 🔄 Real-time Feedback Integration
- 📦 Artifact Management
- 🚀 GitHub Integration

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- LLM Integration: Google Generative AI (Gemini)
- API: FastAPI
- Storage: Local Session State

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SDLC-AIAGENT_HACKATHON.git
cd SDLC-AIAGENT_HACKATHON
```

2. Set up virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file and add required environment variables:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Navigate to http://localhost:8501 in your browser

3. Follow the guided SDLC process:
   - Enter project requirements
   - Review and approve generated artifacts
   - Provide feedback at each stage
   - Download or export final deliverables

## Project Structure

```
SDLC-AIAGENT_HACKATHON/
├── app.py              # Main Streamlit application
├── api.py             # FastAPI backend
├── src/
│   ├── LLMS/         # LLM integration
│   ├── nodes/        # SDLC process nodes
│   └── utils/        # Helper functions
├── requirements.txt   # Project dependencies
└── .env              # Environment variables
```

## Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```
3. Commit your changes:
```bash
git commit -am 'Add some feature'
```
4. Push to the branch:
```bash
git push origin feature/your-feature-name
```
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Generative AI](https://ai.google.dev/)
- Part of the AI Agent Hackathon
