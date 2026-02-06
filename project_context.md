# Project Context: Junior Print Scout

This document provides context for AI assistants working on the "Junior Print Scout" project.

## 1. Project Goal

The primary goal is to build a Streamlit application that acts as a kid-friendly interface for finding and requesting 3D models to be printed. It includes a separate interface for a "parent" to view and manage these requests.

## 2. Key Architecture & Features

*   **Frontend:** A Streamlit app with two main pages.
*   **"Kid" Interface (Search Page):**
    *   A search bar for finding 3D models.
    *   A "Search Assistant" (powered by the Google Gemini API) to help refine user queries.
    *   Search results are fetched from a Google Custom Search Engine (CSE).
    *   The CSE is configured to search only `makerworld.com`, `printables.com`, and `thingiverse.com`.
    *   Results are displayed in a grid with a title, thumbnail, source, and a "Request This" button.
*   **"Parent" Interface (Admin Page):**
    *   Named "Dad's Queue".
    *   Displays a list of requested models from a database, including thumbnails.
    *   Allows the parent to mark items as "Printed", which removes them from the active queue.
*   **Backend/Database:** A simple SQLite database (`requests.db`) to store the print requests.
*   **API Keys:** The user has confirmed that API keys for Google Custom Search and Google Gemini are available via Streamlit's secrets (`st.secrets`).

## 3. Tech Stack

*   **Language:** Python
*   **Framework:** Streamlit
*   **APIs:**
    *   `google-api-python-client` for Google Custom Search.
    *   `google-generativeai` for the Gemini-powered search assistant.
*   **Database:** `sqlite3` (standard library)

## 4. Development Log

### 2024-05-21 (Session 1)

*   **Action:** Created `requirements.txt`.
*   **Reason:** To define the necessary Python libraries for the project: `streamlit`, `google-api-python-client`, and `google-generativeai`.

*   **Action:** Created the main application file, `JuniorPrintScout.py`.
*   **Reason:** To establish the basic structure of the Streamlit app. This includes:
    *   A function `init_db()` to create and initialize the `requests.db` SQLite database.
    *   A sidebar radio button to navigate between the "Search" and "Dad's Queue" pages.
    *   Placeholder sections for the search functionality and the request queue display.

*   **Action:** Created this `project_context.md` file.
*   **Reason:** Per user request, to maintain a running log of project decisions, context, and actions to aid future development sessions.

### 2024-05-21 (Session 2)

*   **Action:** Implemented Google Custom Search in `JuniorPrintScout.py`.
*   **Reason:** To fetch and display 3D model search results based on user input.
*   **Details:**
    *   Added `googleapiclient.discovery` to imports.
    *   Created a `google_search` function to encapsulate the API call.
    *   Added logic to access API keys from `st.secrets` with a fallback for local development.
    *   The search results are now displayed in a 2-column grid.
    *   Updated the `requests` database table schema to include `thumbnail_url` and `source`.

### 2024-05-21 (Session 3)

*   **Action:** Implemented the "Request This" button functionality and updated the "Dad's Queue" page.
*   **Reason:** To allow users to save requests to the database and for the parent to see the full details.
*   **Details:**
    *   Created an `add_request` function to handle inserting new requests into the SQLite database.
    *   Added a `UNIQUE` constraint to the `url` column in the `requests` table to prevent duplicate entries.
    *   The "Dad's Queue" page was updated to display the thumbnail image alongside the title and link.

### 2024-05-21 (Session 4)

*   **Action:** Implemented the Gemini-powered "Search Assistant".
*   **Reason:** To help the user refine their search query for better results.
*   **Details:**
    *   Added `google.generativeai` to imports and configured the API key.
    *   Created a `get_refined_query` function that sends the user's input to the Gemini API with a carefully crafted prompt.
    *   Integrated Streamlit's `st.session_state` to hold the search query. This allows the assistant to update the query, which is then used by the search function.
    *   The UI flow is now: User enters an idea -> Clicks "Ask Assistant" -> Gemini refines the query -> The refined query is displayed and used for the search. A "Search Now!" button was also added for more explicit control.