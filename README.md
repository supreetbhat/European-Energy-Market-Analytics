# Automated Energy-Market ETL Pipeline ⚡📊

## 📖 Overview

This project is an end-to-end, automated Data Engineering pipeline designed to handle European energy market data. It extracts live day-ahead energy prices and corresponding weather data, processes it for anomalies using distributed computing, and loads it into a cloud data warehouse to power a live strategic dashboard.

This project demonstrates production-ready data engineering practices, shifting from manual data science scripts to fully automated, cloud-hosted architectures.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Extraction** | Python, REST APIs (ENTSO-E, Open-Meteo) |
| **Transformation** | PySpark, Databricks (Community Edition) |
| **Orchestration** | Apache Airflow, Docker |
| **Cloud Storage** | Google Cloud Platform — Cloud Storage & BigQuery |
| **Visualization** | Power BI / DAX |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed and configured:

- Python 3.9+
- Docker Desktop (for running Apache Airflow locally)
- A free [ENTSO-E API Key](https://transparency.entsoe.eu/)
- A free [Databricks Community Edition](https://community.cloud.databricks.com/) account
- A Google Cloud Platform (GCP) account with BigQuery enabled
- Power BI Desktop

---

## 🚀 Development & Execution Guide

### Phase 1 — Local Setup & Data Extraction

**Goal:** Prove you can reliably connect to external systems and extract data.

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/energy-market-etl.git
cd energy-market-etl
```

**2. Create a virtual environment and install dependencies:**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Create a `.env` file in the root directory and add your credentials:**
```env
ENTSOE_API_KEY=your_api_key_here
GCP_PROJECT_ID=your_gcp_project_id
```

**4. Run the extraction script to test the API connection:**
```bash
python src/extract/fetch_energy_data.py
```

✅ **Expected output:** A raw JSON/CSV file saved in the `data/raw/` folder.

---

### Phase 2 — Big Data Transformation (PySpark)

**Goal:** Prove you can handle massive datasets and ensure data quality.

1. Upload the raw data to your Databricks Community Edition workspace.
2. Open the notebook at `src/transform/clean_energy_data.ipynb`.
3. Execute the PySpark cells to:
   - Drop null values and handle missing timestamps
   - Merge ENTSO-E pricing data with Open-Meteo weather data
   - Enforce schema rules (e.g., ensuring prices are floats, not strings)
4. Export the cleaned dataset as a **Parquet file**.

---

### Phase 3 — Orchestration (Apache Airflow)

**Goal:** Prove you can automate the entire workflow without manual intervention.

**1. Initialise the Airflow environment using Docker:**
```bash
docker-compose up -d
```

**2. Access the Airflow UI:**

Navigate to [http://localhost:8080](http://localhost:8080) in your browser.

> Default credentials: `airflow` / `airflow`

**3. Activate the pipeline:**

- Place `energy_pipeline_dag.py` into your `dags/` folder.
- Turn on the DAG in the Airflow UI.

The DAG is scheduled to run **automatically every day at 08:00 AM**.

---

### Phase 4 — Cloud Deployment (GCP BigQuery)

**Goal:** Prove you understand enterprise cloud environments.

**1. Authenticate your local machine with GCP:**
```bash
gcloud auth application-default login
```

**2. Push data to BigQuery:**

Update the final step of your Airflow DAG to load the cleaned PySpark DataFrame directly into a BigQuery table using the `pandas-gbq` library or native GCP Airflow hooks.

**3. Verify the data has landed in your BigQuery console.**

---

### Phase 5 — Enterprise Visualization (Power BI)

**Goal:** Prove you can deliver business value to stakeholders.

1. Open **Power BI Desktop**.
2. Go to **Get Data → Google BigQuery** and connect using **DirectQuery** mode.
3. Build the following KPIs using DAX:
   - Average Daily Energy Price
   - Price Volatility Index
   - Correlation between wind/solar generation and price drops
4. **Publish** the dashboard to Power BI Service for automatic daily refresh.

---

## 🤝 Contributing

Contributions are welcome. Fork the repository and submit a pull request with your proposed changes.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).