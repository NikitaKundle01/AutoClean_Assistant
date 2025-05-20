
# 🧹 AutoClean - Intelligent Data Cleaning Assistant

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.22.0-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

AutoClean is a web-based platform that automates data cleaning tasks with both rule-based and ML-powered approaches. Upload your messy datasets and download clean, analysis-ready data in seconds!

✨ **Live Demo**:  https://nikitakundle01-autoclean-assistant-app-psqmyi.streamlit.app/

📂 **GitHub**: [github.com/NikitaKundle01/AutoClean_Assitant](https://github.com/NikitaKundle01/AutoClean_Assistant)

## 🚀 Features

- 📤 **Easy Upload**: Supports CSV, Excel files
- 🧼 **Smart Cleaning**:
  - Remove duplicates
  - Handle missing values (mean/median/mode/custom)
  - Drop/rename columns
  - Outlier detection
- 🔍 **Data Profiling**: Automatic analysis of your dataset
- 🔒 **User Authentication**: Secure login/history tracking
- 📊 **ML-Powered Suggestions**: Intelligent cleaning recommendations
- 💾 **History Tracking**: Save and reload previous cleaning sessions

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/autoclean.git
   cd autoclean
   ```
2. **Set up virtual environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```
3. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

## Set up database:

- SQLite: Automatically created on first run
- MySQL: See Database Setup

## 🖥️ Usage

```bash
streamlit run app.py
```
Then open your browser to http://localhost:8501

### 🗃️ Database Setup

**Option 1: SQLite (Default)**
- No setup needed - database created automatically

**Option 2: MySQL**
- Create database:
```bash
sql
CREATE DATABASE autoclean_db;
Update .env file:

ini
DB_HOST=localhost
DB_NAME=autoclean_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=3306
```

## 🧩 Project Structure
```bash
autoclean/
├── app.py                 # Main application
├── modules/
│   ├── cleaner.py         # Data cleaning logic
│   ├── ml_cleaner.py      # ML-based suggestions
│   ├── db_connector.py    # Database handler
│   └── auth_manager.py    # Authentication system
├── data/                  # Processed files storage
├── requirements.txt       # Dependencies
└── README.md              # This file
```


## 🤖 Technologies Used

1. **Frontend**: Streamlit
2. **Backend**: Python
3. **Data Processing**: Pandas, NumPy
4. **Machine Learning**: Scikit-learn
5. **Database**: SQLite/MySQL
6. **Profiling**: ydata-profiling

## 📸 Screenshots
![Screenshot 2025-05-19 231900](https://github.com/user-attachments/assets/8ed3ad02-84b4-47d3-9a1e-c039e26b09ce)

![Screenshot 2025-05-19 231928](https://github.com/user-attachments/assets/88368328-1195-4e83-bb5d-6e172347f895)

![Screenshot 2025-05-19 231944](https://github.com/user-attachments/assets/b729b53c-16bd-4f92-b99a-a296d5410d4b)

## 🔯 Workflow

![deepseek_mermaid_20250519_41c61b](https://github.com/user-attachments/assets/d0784e6d-daa1-4a95-8bc3-ccbca6d0559d)


## 🤝 Contributing
- Fork the project
- Create your feature branch (git checkout -b feature/AmazingFeature)
- Commit your changes (git commit -m 'Add some amazing feature')
- Push to the branch (git push origin feature/AmazingFeature)
- Open a Pull Request

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

## 📧 Contact
Your Name - kundlenikita@gmail.com
Project Link: https://github.com/NikitaKundle01/AutoClean_Assistant/
