# AERIS — Environmental Intelligence Platform

A high-precision environmental intelligence dashboard designed in Google Stitch and powered by React, Tailwind CSS, and Bayesian air quality forecasting models.

## 🚀 Quick Start (Zero Installation Required)

1. **One-Click Launch**:
   - Double-click `Launch_AERIS.bat` on your Desktop (or `start_aeris.bat` in this folder).
   - This starts the local server and automatically opens `http://localhost:3000` in your default browser.

2. **Direct Browser Open**:
   - Simply double-click `index.html` to open directly in Chrome, Edge, or Opera GX.

3. **Vite / NPM (Optional, if Node.js is installed)**:
   ```bash
   npm install
   npm run dev
   ```

---

## 📊 Connected Datasets

The dashboard is directly connected to your hackathon forecasting datasets:
1. `india_forecast.csv` (14 Cities National Scope):
   - Delhi, Mumbai, Kolkata, Chennai, Bengaluru, Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow, Patna, Kanpur, Noida, Gurugram.
2. `region_forecast.csv` (7 Regional Critical Hotspot Zones):
   - Bengaluru, Bhiwadi, Byrnihat, Delhi, Gurugram, Loni, Noida.

### Real Fields Mapped:
- `timestamp`: 24-hour diurnal cycle (00:00 to 23:00 IST).
- `pm25_pred`: PM2.5 concentrations, peak times, and diurnal trajectories.
- `pm10_pred`: PM10 aerosol concentrations.
- `cat`: Status classifications (`Good`, `Moderate`, `Poor`).
- `alert`: Operational triage badges (`OK`, `WATCH`, `ALERT`).
- `suggestions`: Direct policy interventions (e.g. `30% curtailment; divert trucks`, `routine monitoring`).

---

## 🖥️ Screen Features

- **Overview**: 4 KPI cards (Current PM2.5, PM10, 24H Peak, Confidence), interactive SVG dispersion chart with P90 credible envelope, contextual AI risk brief, ranked hotspots, operator alerts, and intervention governance.
- **24H Forecast**: In-depth 24-hour trajectory curve, 6 legislative KPI cards, full 24-hour hourly sequence table, and forecast intelligence drawer.
- **Geo Map**: Spatial mesh visualizing all stations across India with color-coded alerts, downwind Gaussian plume heatmap simulation, and interactive 24-hour time scrubber.
- **Alerts Center**: Severity triage filters (`ALL`, `CRITICAL`, `WATCH`), incident tracking, operator acknowledgment, and dispatch triggers.
- **Interventions**: Decision support protocols (EPS-01, EPS-02, EPS-04) with modeled mitigation impacts (-18.4 µg/m³ peak attenuation).
- **Model Intelligence**: Physics-Informed Neural Network (PINN) loss formulation, WRF-Chem atmospheric assimilation, and Bayesian uncertainty analysis.
