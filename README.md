# 🌟 AI Data Analyst for Small Businesses

> A fully agentic, AI-powered internal tool for small business owners to upload messy sales data, automatically clean it, generate real-time metrics, and view action-oriented insights!

## 🔥 Features Currently Implemented

- **Automated Data Cleaning (Pandas Engine):** Instantly purges completely empty rows, drops duplicated order entries, and safely standardizes null data values for clean JSON delivery.
- **Smart Column Heuristics:** Employs rule-based metadata generation to automatically sniff out your data's primary *Date*, *Revenue/Sales*, and *Product/Item* fields without requiring user configuration.
- **Mathematical Metrics Engine:** Calculates hyper-fast KPIs instantly upon clicking Generate Dashboard: Total Revenue, Total Orders, and Average Order Value (AOV).
- **Intelligent Insight Generator:** An automated logic engine that computes the Top 5 Best-Selling and Bottom 5 Underperforming products and turns that data into high-quality, English string insights. 
- **Gorgeous UI:** A hand-crafted React + Vite Dashboard styled with premium TailwindCSS, glassmorphic UI elements, interactive data tables, and dynamic visual KPI Cards.

## 🛠️ Technology Stack
- **Backend**: FastAPI (Python), SQLite, Pydantic, Uvicorn
- **Data Engineering**: Pandas, Numpy
- **Frontend**: React, Vite, TailwindCSS (v4), Axios, Lucide Icons

## 🚀 Setup & Installation (Local Development)

### 1. The Backend API
Open a terminal and build the backend environment:
```bash
cd backend
python -m venv venv
# Activate the environment (Windows)
.\venv\Scripts\Activate
# Alternatively (Mac/Linux)
source venv/bin/activate

# Install the Python requirements
pip install fastapi uvicorn pandas python-multipart sqlalchemy openpyxl

# Start the local server
uvicorn main:app --reload
```
*The API is now tracking requests securely at `http://localhost:8000`.*

### 2. The Frontend UI
In a brand new terminal, start the fast React dev server:
```bash
cd frontend
npm install
npm run dev
```
*Your pristine Dashboard is now live at `http://localhost:5173`.*

## 📈 Roadmap
- **Phase 4:** Expand the Dashboard UI to plot Graphical Bar Charts, Trends, and Sparklines via Recharts.
- **Phase 5:** Integrate the Google Gemini API to enable a floating "Chat with Data" assistant—allowing the user to chat with their metrics live in natural language!
