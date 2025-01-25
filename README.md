# SEO Analyzer Application

The **SEO Analyzer Application** is a web-based tool built using Streamlit to evaluate and improve the SEO (Search Engine Optimization) performance of web pages. It fetches and analyzes key SEO aspects such as meta tags, content quality, links, images, and more. The app also calculates an SEO score based on multiple factors and provides visual insights for optimization.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Project Structure](#project-structure)

---

## Project Overview

This application simplifies SEO analysis by automating the process of extracting key information from a webpage. Users can enter a URL and a focus keyword to receive an in-depth report on the SEO aspects of the page. It provides actionable insights, such as keyword density, meta information, headings analysis, and an overall SEO score.

---

## Features

- **SEO Score Calculation:**
  - Calculates a weighted SEO score based on various on-page and off-page factors.

- **Meta Information Analysis:**
  - Extracts and evaluates the title, meta description, and other metadata.

- **Keyword Analysis:**
  - Analyzes the density and placement of focus keywords.

- **Content and Links Analysis:**
  - Checks the quality of headings, word count, internal and external links, and broken links.

- **Images Analysis:**
  - Evaluates the presence of alt text and image optimization.

- **Performance Metrics:**
  - Measures bounce rate, time on page, and pages per session.

- **Interactive Visuals:**
  - Displays an SEO score gauge chart using Plotly.

---

## Technologies Used

- **Frontend Framework:**
  - Streamlit (for web-based user interface)

- **Backend Libraries:**
  - `requests` (for fetching webpage content)
  - `beautifulsoup4` (for parsing HTML content)

- **Data Visualization:**
  - Plotly (for interactive gauge charts)

---

## Installation

### Prerequisites

Ensure the following are installed on your system:
- Python 3.8 or later
- Virtual environment tool (`venv` or `virtualenv`)

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Anshuman-Jha-01/SEO-analyzer.git
   cd SEO-analyzer

2. **Create a Virtual Environment:**
    ```bash
    python -m venv venv

3. **Activate the Virtual Environment:**
    - On Windows:
        ```bash
        venv/Scripts/activate

    - On macOS/Linux:
        ```bash
        source venv/bin/activate

4. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt

5. **Run the Application:**
    ```bash
      streamlit run Main-App.py

---

## Usage
1. Launch the application by running the ```streamlit``` command:

2. Enter the following inputs in the Streamlit interface:
    - URL of the webpage to analyze
    - Focus keyword for SEO analysis
    - Bounce rate, time on page, and pages per session metrics.

3. Click on **Analyze** to generate the report.

4. View the following results:
    - **SEO Score:** Visualized as a gauge chart.
    - **HTTP Details:** Status codes, HTTPS usage, response time, etc.
    - **Meta Information:** Title and description analysis.
    - **Keyword Analysis:** Density, frequency, and positions of the focus keyword.
    - **Headings Analysis:** Counts and content of headings (H1-H6).
    - **Word Count:** Total word count, anchor text word count, and percentage.
    - **Links Summary:** Internal and external links, broken links, and nofollow links.
    - **Images Analysis:** Alt text and optimization details.

---

## Components
1. ```Main-App.py```:
    - The main Python file containing the SEO analysis logic and Streamlit interface.

2. ```requirements.txt```:
    - Lists all Python dependencies required to run the application.

---

## Project Structure

```bash
    /src
    ├── Main-App.py          # Main Python file containing the SEO analyzer
    └── requirements.txt     # File listing dependencies
  ```

