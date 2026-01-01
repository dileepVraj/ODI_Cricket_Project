# ODI Cricket Analysis & Trading Engine

A comprehensive Data Science project designed to analyze historical One Day International (ODI) cricket data. This engine processes match statistics to identify trends, team performance metrics, and potential trading edges.

## 🚀 Project Overview
This tool parses over 1.3 million lines of historical ball-by-ball data to calculate:
- **Match Odds & Probabilities:** Analyzing historical win rates based on current match states.
- **Team Performance:** Aggregating stats for specific matchups (e.g., India vs. Australia).
- **Venue Analysis:** Understanding how specific grounds behave (1st innings vs. 2nd innings scores).

## 📂 Repository Structure
* **`engine.py`**: The core processing logic. Contains functions to clean data, calculate strike rates, and compute team averages.
* **`dashboard.ipynb`**: A Jupyter Notebook interface for visualizing the data. Used for generating charts and interactive analysis.
* **`smart_merge.py`**: Utility script for merging new match data with the master historical database.
* **`interface.py`**: The command-line interface (CLI) for interacting with the engine.
* **`data/`**: Storage for raw and processed CSV files (Note: The master dataset is excluded from the repo due to size).

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Libraries:**
    * `Pandas` (Data manipulation & Aggregation)
    * `Matplotlib` / `Seaborn` (Visualization)
    * `Jupyter` (Interactive Analysis)

## ⚙️ How to Run
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/dileepVraj/ODI_Cricket_Project.git](https://github.com/dileepVraj/ODI_Cricket_Project.git)
    ```
2.  **Install dependencies:**
    (Ensure you have Python and Pandas installed)
    ```bash
    pip install pandas matplotlib jupyter
    ```
3.  **Run the Dashboard:**
    ```bash
    jupyter notebook dashboard.ipynb
    ```

## 📈 Future Roadmap
* Implement machine learning models to predict match outcomes.
* Add a real-time data scraper for live match analysis.
* Develop a web-based frontend using Streamlit.

---
*Created by Dileep Vraj - Aspiring Professional Cricket Trader & Data Analyst*