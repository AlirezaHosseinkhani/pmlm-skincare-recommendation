# Skincare Recommendation API

AI-powered skincare recommendation system that analyzes facial images and recommends suitable cream products.

## Features

- 🤖 Facial image analysis using advanced AI models
- 💊 Personalized product recommendations based on skin type and concerns
- 📊 Analytics tracking for recommendation patterns
- 🔄 Fallback support between OpenAI and custom LLM providers
- 🎯 Detailed skin analysis including type, concerns, and age range

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure your API keys

## Running the Application

```bash
uvicorn app.main:app --reload