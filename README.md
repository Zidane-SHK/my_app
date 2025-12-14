



## Overview

This application is the culmination project for **Weeks 7–11**, integrating authentication, database management, and AI into a Streamlit dashboard.

  * **Cybersecurity:** Logging and analysis.
  * **Data Science:** Tracking and dataset management.
  * **IT Operations:** Ticket management and system status.

Each role is equipped with a **Context-Aware AI Assistant** that can answer questions based on live data from the database.

-----

## Features

  * **OOP Classes:** The webapp uses a specialized classes (`DatabaseManager`, `AuthManager`, `SecurityIncident`, `ITTicket`) to ensure scaling and less verbosity in code.
  * **Secure Authentication:** User login system secured by **BCrypt** password hashing.
  * **AI Chatbot:** Custom Chatbots (powered by OpenAI GPT 3.5 Turbo) for each page.
  * **Visualizations:** Interactive charts and metrics using **Altair** and **Pandas** to visualize.
  * **CRUD Operations:** Insert, Read, Update, Delete records across all three modules for Admins and/or users.

-----

## Timeline (Weeks 7–11)

This project represents a cumulative effort, building complexity week over week:

  * **Week 7: Security**

      * Using `bcrypt` for secure password hashing and verification.
      * Created the user authentication.

  * **Week 8: Database Architecture**

      * Introduced **SQLite** for data storage.
      * Designed the schema for Users, IT Tickets, and Security Incidents.

  * **Week 9: User Interface (Streamlit)**

      * Developed the frontend using **Streamlit**.
      * Implemented data dashboards with charts and metrics.
      * Created the multi-page navigation.

  * **Week 10: AI & API Integration**

      * Integrated the **OpenAI API**.
      * Developed role-specific personas.
      * Implemented chat streaming and history appending.

  * **Week 11: OOP Refactoring & Final Integration**

      * **Refactoring:** Converte code into Classes and Methods to reduce code verbosity.
      * **Data-AI Connection:** Connected the AI to the SQLite database, allowing it to view live data.
      * **Misc:** Added chat features (Clear History) and secure secrets management.

-----

## Setup

1.  **Clone the repository:**

    git clone https://github.com/Zidane-SHK/my_app.git
    cd my_app

2.  **Dependencies:**

    pip install -r requirements/requirements.txt

3.  **Configure:**
    Create a folder named `.streamlit` in the project root and add a the file `secrets.toml`:

    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY = "sk-proj-..."
    ```

4.  **Database:**
    Generate sample data for testing:
    By either using Kaggle or any opensource datasets in the CSV format

6.  **Run:**

    streamlit run main.py

-----

## Structure

```text
├── .streamlit/          # Ignored by Git(API KEY)
├── Assets/              # CSV Data (IT, Cyber, DataSci)
├── database/            # SQLite DB and connection
├── models/              # OOP Classes (User, GPT, Ticket, in Models)
├── pages/               # Streamlit Pages (1_Cybsec, 2_Datasci, 3_IT)
├── services/            # Services (Auth, DatabaseManager, ITTicket)
├── main.py              # Log-in Page (Main)
```
