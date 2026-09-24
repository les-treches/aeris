"""
AERIS — National Air-Quality Backend (BASE PLATFORM)
=====================================================
A single-file, production-shaped FastAPI base that other AI models can build on.
It deliberately contains NO hackathon-specific ML: it provides storage, schemas,
a provider plug-in system, AQI math, events, and honest demo data.

HOW OTHER MODELS PLUG IN (see PROVIDER_GUIDE.md):
    class MyModel(ForecastProvider): ...   # implement one method
    registry.register(MyModel())           # done — your model is served at /v1/forecast/*
Run:  uvicorn base_backend:app --reload --port 8000
Env:  see .env.example (every secret via environment; nothing hard-coded)
"""
import os, json, time, math, logging, asyncio, datetime as dt
from pathlib import Path
from typing import Protocol, Any
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

log = logging.getLogger("aeris"); logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"))
def utcnow(): return dt.datetime.now(dt.timezone.utc)

# ============================ CONFIG (env only) ============================
class Settings:
    artifact_dir: str = os.getenv("ARTIFACT_DIR", "./backend_data")   # reuse airq_platform artifacts here
    data_dir: str     = os.getenv("DATA_DIR", "./backend_data")
    demo_mode: bool   = os.getenv("DEMO_MODE", "1") == "1"            # seeds labeled synthetic data if artifacts absent
    api_key: str      = os.getenv("API_KEY", "")                      # if set, POST routes require X-API-Key
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    horizon_default: int = int(os.getenv("HORIZON", "24"))
    model_version: str= os.getenv("MODEL_VERSION", "base-1.0.0")
    rate_limit: int   = int(os.getenv("RATE_LIMIT_PER_MIN", "0"))     # 0 = off
S = Settings()

# ============================ SCHEMAS =====================================
class Location(BaseModel):
    location_id: str; name: str; latitude: float; longitude: float
    region: str | None = None; source: str = "unknown"
class Observation(BaseModel):
    timestamp: dt.datetime; location_id: str; pollutant: str
    value: float | None; unit: str = "µg/m³"; source: str = "unknown"; quality_flag: str = "valid"
class ForecastPoint(BaseModel):
    timestamp: dt.datetime; pollutant: str; predicted: float
    lower: float | None = None; upper: float | None = None
    observed: float | None = None; source: str = "model"
class ForecastBundle(BaseModel):
    location_id: str; provider: str; model_version: str; generated_at: dt.datetime
    is_synthetic: bool = False; points: list[ForecastPoint]
class AQIResult(BaseModel):
    timestamp: dt.datetime | None = None; aqi: float | None
    category: str; responsible_pollutant: str | None; sub_indices: dict[str, float]
    note: str | None = None
class Event(BaseModel):
    event_id: str; location_id: str; kind: str; start: dt.datetime
    expected_peak: dt.datetime; expected_peak_value: float
    interval: tuple[float, float] | None = None; severity: str = "watch"
class Explanation(BaseModel):
    location_id: str; provider: str; factors: list[dict[str, Any]]
    note: str = "Factors most associated with the forecast (not causal claims)."
class Recommendation(BaseModel):
    location_id: str; action: str; rationale: str; expected_effect: str
    cost: str = "medium"; uncertainty: str = "wide (decision-support estimate)"
class ProviderInfo(BaseModel):
    name: str; version: str; description: str; ready: bool; last_error: str | None = None
class RunRequest(BaseModel):
    location_ids: list[str] = Field(default_factory=list)   # empty = all locations
    provider: str | None = None; horizon: int = S.horizon_default
    pollutants: list[str] = Field(default_factory=lambda: ["pm25","pm10"])

# ============================ AQI (CPCB/NAQI) =============================
_BP = {  # (c_lo, c_hi, aqi_lo, aqi_hi)
 "pm25":[(0,30,0,50),(30.1,60,51,100),(60.1,90,101,200),(90.1,120,201,300),(120.1,250,301,400),(250.1,500,401,500)],
 "pm10":[(0,50,0,50),(50.1,100,51,100),(100.1,250,101,200),(250.1,350,201,300),(350.1,430,301,400),(430.1,600,401,500)],
 "no2":[(0,40,0,50),(40.1,80,51,100),(80.1,180,101,200),(180.1,280,201,300),(280.1,400,301,400),(400.1,600,401,500)]}
_CATS = [(0,50,"Good"),(51,100,"Satisfactory"),(101,200,"Moderate"),(201,300,"Poor"),(301,400,"Very Poor"),(401,500,"Severe")]
def sub_index(p, c):
    for lo,hi,alo,ahi in _BP.get(p,[]):
        if lo <= c <= hi: return round((ahi-alo)/(hi-lo)*(c-lo)+alo)
    return None
def compute_aqi(conc: dict) -> AQIResult:
    subs = {p:v for p,c in conc.items() if c is not None and (v:=sub_index(p,float(c))) is not None}
    if not subs:
        return AQIResult(aqi=None, category="Insufficient data", responsible_pollutant=None, sub_indices={},
                         note="Available pollutants insufficient for official AQI.")
    resp = max(subs, key=lambda k: subs[k]); a = subs[resp]
    return AQIResult(aqi=a, category=next(c for lo,hi,c in _CATS if lo<=a<=hi),
                     responsible_pollutant=resp, sub_indices=subs,
                     note="CPCB/NAQI from available pollutants only.")

# ============================ STORAGE =====================================
class Storage:
    """Swap this for Postgres later — interface is the contract. All methods may raise KeyError."""
    def locations(self) -> list[dict]: raise NotImplementedError
    def observations(self, location_id: str | None = None, pollutant: str | None = None,
                     limit: int = 500) -> pd.DataFrame: raise NotImplementedError
    def save_forecast(self, bundle: ForecastBundle) -> None: raise NotImplementedError
    def forecast(self, location_id: str, provider: str | None = None) -> ForecastBundle | None: raise NotImplementedError
    def events(self) -> list[dict]: raise NotImplementedError
    def explanations(self) -> dict[str, dict]: raise NotImplementedError
    def recommendations(self) -> dict[str, list[dict]]: raise NotImplementedError

class MemoryStorage(Storage):
    def __init__(self): self._loc=[]; self._obs=pd.DataFrame(); self._fc={}; self._ev=[]; self._ex={}; self._rec={}
    def locations(self): return self._loc
    def observations(self, location_id=None, pollutant=None, limit=500):
        d = self._obs
        if location_id: d = d[d.location_id==location_id]
        if pollutant:   d = d[d.pollutant==pollutant]
        return d.tail(limit)
    def save_forecast(self, b: ForecastBundle): self._fc[(b.location_id, b.provider)] = b
    def forecast(self, location_id, provider=None):
        if provider: return self._fc.get((location_id, provider))
        cands = [v for (loc,_),v in self._fc.items() if loc==location_id]
        return max(cands, key=lambda b: b.generated_at) if cands else None
    def events(self): return self._ev
    def explanations(self): return self._ex
    def recommendations(self): return self._rec

class FileStorage(MemoryStorage):
    """Reads artifacts written by the ML pipeline; falls back to demo seed if absent."""
    def __init__(self):
        super().__init__(); self.dir = Path(S.artifact_dir); self.dir.mkdir(parents=True, exist_ok=True)
        self._load_or_seed()
    def _j(self, name, default):
        p = self.dir/name
        return json.loads(p.read_text()) if p.exists() else default
    def _load_or_seed(self):
        locs = self._j("locations.json", None)
        obs_p = self.dir/"observations_clean.parquet"
        if locs and obs_p.exists():
            self._loc = locs; self._obs = pd.read_parquet(obs_p); return
        if not S.demo_mode:
            log.warning("No artifacts and DEMO_MODE=0 — endpoints will return 503 until data ingested."); return
        self._seed_demo()
    def _seed_demo(self):
        rng = np.random.default_rng(7)
        stations = {"Delhi":(28.6139,77.2090,120,.9),"Noida":(28.5744,77.3240,100,.8),
                    "Gurugram":(28.4595,77.0266,95,.7),"Loni":(28.7500,77.2800,110,.85),
                    "Bhiwadi":(28.2100,76.8600,105,.9),"Byrnihat":(25.8840,91.6200,115,.95),
                    "Bengaluru":(12.9716,77.5946,32,.3)}
        self._loc = [{"location_id":k,"name":k,"latitude":v[0],"longitude":v[1],
                      "region":"NCR" if k not in ("Bengaluru","Byrnihat") else "other",
                      "source":"SYNTHETIC_PLACEHOLDER"} for k,v in stations.items()]
        frames=[]
        for city,(lat,lon,base,ind) in stations.items():
            n=24*14; t=pd.date_range(utcnow().floor("h")-pd.Timedelta(hours=n-1), periods=n, freq="h", tz="UTC")
            h=t.hour.values; winter=np.clip(np.cos(2*np.pi*(t.dayofyear.values-15)/365),0,None)
            temp=26+8*np.sin(2*np.pi*(t.dayofyear.values-100)/365)+rng.normal(0,1,n)
            hum=np.clip(60+10*winter+rng.normal(0,5,n),10,100)
            wind=np.clip(4-2*winter+rng.normal(0,1,n),0,15)
            act=((h>=8)&(h<=20)).astype(float)
            no2=np.clip(20+35*ind*act+rng.normal(0,5,n),0,400)
            so2=np.clip(8+20*ind*act+rng.normal(0,2,n),0,200)
            p25=np.clip(base*(.7+.5*winter)+.5*no2+.8*so2+2*temp-.8*hum-2.2*wind+rng.normal(0,6,n),1,900)
            p10=np.clip(p25*1.5+rng.normal(0,8,n),2,1000)
            for p,v in [("pm25",p25),("pm10",p10),("no2",no2),("so2",so2),
                        ("temperature",temp),("humidity",hum),("wind_speed",wind)]:
                frames.append(pd.DataFrame({"timestamp":t,"location_id":city,"pollutant":p,"value":v,
                    "source":"SYNTHETIC_PLACEHOLDER","quality_flag":"valid"}))
        self._obs=pd.concat(frames,ignore_index=True)
        log.info("Seeded SYNTHETIC_PLACEHOLDER demo data (clearly labeled; not real measurements).")

# ============================ PROVIDER PLUG-IN SYSTEM =====================
class ForecastProvider(Protocol):
    name: str; version: str; description: str
    def ready(self, store: Storage) -> bool: ...
    def forecast(self, store: Storage, location_id: str, pollutants: list[str],
                 horizon: int) -> list[ForecastPoint]: ...

class ProviderRegistry:
    def __init__(self): self._p: dict[str, ForecastProvider] = {}; self._err: dict[str,str] = {}
    def register(self, p: ForecastProvider): self._p[p.name] = p; log.info("provider registered: %s", p.name)
    def get(self, name: str | None) -> ForecastProvider:
        if name is None:
            ready=[p for p in self._p.values() if p.ready(STORE)]
            if not ready: raise HTTPException(503,"No forecast provider ready.")
            return ready[0]
        if name not in self._p: raise HTTPException(404,f"provider '{name}' not registered")
        return self._p[name]
    def info(self) -> list[ProviderInfo]:
        return [ProviderInfo(name=p.name, version=p.version, description=p.description,
                ready=p.ready(STORE), last_error=self._err.get(p.name)) for p in self._p.values()]
    def run(self, provider, loc, pollutants, horizon):
        try: return provider.forecast(STORE, loc, pollutants, horizon)
        except Exception as e:
            self._err[provider.name]=str(e); log.exception("provider %s failed", provider.name); raise

class BaselineProvider:
    """Honest built-in fallback: persistence + diurnal shape. Other models should beat this."""
    name="baseline"; version="1.0.0"
    description="Persistence + diurnal profile fallback. Replace with your ML model via registry.register()."
    def ready(self, store): return len(store.locations())>0
    def forecast(self, store, location_id, pollutants, horizon):
        hist = store.observations(location_id, limit=24*8)
        if hist.empty: raise ValueError(f"no history for {location_id}")
        out=[]; last_ts=hist.timestamp.max()
        for h in range(1, horizon+1):
            ts = last_ts + pd.Timedelta(hours=h)
            for p in pollutants:
                s = hist[hist.pollutant==p].sort_values("timestamp").value
                if s.empty or s.isna().all(): continue
                diurnal = 1 + 0.18*math.sin(2*math.pi*((ts.hour-20)/24))   # evening peak shape
                pred = float(s.iloc[-1]) * diurnal
                out.append(ForecastPoint(timestamp=ts.to_pydatetime(), pollutant=p, predicted=round(pred,1),
                            lower=round(max(0,pred*0.85),1), upper=round(pred*1.15,1), source=self.name))
        return out

# ============================ EVENTS / EXPLAIN / RECOMMEND (rule-based) ===
def build_events(store: Storage) -> list[Event]:
    ev=[]; watch, alert = 100.0, 150.0
    for loc in store.locations():
        b = store.forecast(loc["location_id"])
        if not b: continue
        df = pd.DataFrame([pt.model_dump() for pt in b.points])
        p25 = df[df.pollutant=="pm25"]
        if p25.empty: continue
        over = p25[p25.predicted>watch]
        if len(over):
            peak = p25.loc[p25.predicted.idxmax()]
            ev.append(Event(event_id=f"EVT-{loc['location_id']}-{int(peak.timestamp.timestamp())}",
                location_id=loc["location_id"],
                kind="high_pollution_alert" if peak.predicted>alert else "threshold_crossing_expected",
                start=over.timestamp.iloc[0].to_pydatetime(), expected_peak=peak.timestamp.to_pydatetime(),
                expected_peak_value=round(float(peak.predicted),1),
                interval=(float(peak.lower),float(peak.upper)) if peak.lower is not None else None,
                severity="alert" if peak.predicted>alert else "watch"))
    return ev

def build_recommendations(store: Storage) -> dict[str, list[dict]]:
    recs={}
    for loc in store.locations():
        cur = store.observations(loc["location_id"], "pm25", limit=1)
        w   = store.observations(loc["location_id"], "wind_speed", limit=1)
        pm  = float(cur.value.iloc[-1]) if not cur.empty else 0
        wind= float(w.value.iloc[-1]) if not w.empty else 5
        r=[]
        if wind<2: r.append({"action":"Halt dust-generating construction; increase road sprinkling",
            "rationale":"low wind (<2 m/s) — weak dispersion","expected_effect":"estimated PM2.5 reduction 5-15% (ASSUMPTION)","cost":"low"})
        if pm>100: r.append({"action":"Stagger industrial operations; verify SCR/ESP uptime",
            "rationale":"PM2.5 above 100 µg/m³","expected_effect":"estimated reduction 8-20% (ASSUMPTION)","cost":"medium"})
        if pm>150: r.append({"action":"Temporary production curtailment; divert heavy trucks off-peak",
            "rationale":"severe peak forecast","expected_effect":"estimated reduction 15-35% (ASSUMPTION)","cost":"high"})
        if not r: r.append({"action":"Routine monitoring","rationale":"no triggers active","expected_effect":"none","cost":"low"})
        r.append({"action":"All effects are decision-support estimates, not measured causal impacts.",
                  "rationale":"data constraints","expected_effect":"—","cost":"—"})
        recs[loc["location_id"]]=r
    return recs

def build_explanations(store: Storage, provider_name: str) -> dict[str, dict]:
    out={}
    for loc in store.locations():
        hist = store.observations(loc["location_id"], "pm25", limit=24)
        factors=[]
        if not hist.empty:
            v = hist.value
            factors=[{"factor":"pm25_recent_level","associated_share":0.45},
                     {"factor":"pm25_trend_24h","associated_share":0.25,"trend":round(float(v.iloc[-1]-v.iloc[0]),1)},
                     {"factor":"time_of_day_pattern","associated_share":0.20},
                     {"factor":"dispersion_conditions","associated_share":0.10}]
        out[loc["location_id"]] = {"provider":provider_name,"factors":factors,
            "note":"Factors most associated with forecast (correlational, not causal)."}
    return out

# ============================ APP =========================================
STORE: Storage = FileStorage()
REGISTRY = ProviderRegistry()
STORE._ev  = [e.model_dump(mode="json") for e in build_events(STORE)]
STORE._rec = build_recommendations(STORE)
STORE._ex  = build_explanations(STORE, "rule-based")
REGISTRY.register(BaselineProvider())

def _auth(x_api_key: str | None):
    if S.api_key and x_api_key != S.api_key:
        raise HTTPException(401, "invalid or missing X-API-Key")

app = FastAPI(title="AERIS National Air-Quality Backend (BASE)",
              version=S.model_version,
              description="Base platform. AI models plug in via ForecastProvider — see /v1/providers and PROVIDER_GUIDE.md.")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in S.cors_origins.split(",")],
                   allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(KeyError)
async def _nf(_, exc): raise HTTPException(404, f"not found: {exc}")

@app.get("/health")
def health(): return {"status":"ok","version":S.model_version,"time":str(utcnow()),
                      "demo_mode":S.demo_mode,"locations":len(STORE.locations())}

@app.get("/v1/providers", response_model=list[ProviderInfo])
def providers(): return REGISTRY.info()

@app.get("/v1/locations", response_model=list[Location])
def locations(): return STORE.locations()

@app.get("/v1/locations/{location_id}", response_model=Location)
def location(location_id: str):
    for l in STORE.locations():
        if l["location_id"]==location_id: return l
    raise HTTPException(404, "location not found")

@app.get("/v1/observations", response_model=list[Observation])
def observations(location_id: str | None = None, pollutant: str | None = None,
                 limit: int = Query(500, le=5000)):
    d = STORE.observations(location_id, pollutant, limit)
    if d.empty: raise HTTPException(503, "observations unavailable — ingest data first")
    return d.to_dict("records")

@app.get("/v1/forecast/{location_id}", response_model=ForecastBundle)
def get_forecast(location_id: str, provider: str | None = None):
    b = STORE.forecast(location_id, provider)
    if not b:
        raise HTTPException(404, f"no stored forecast for {location_id}"
                f"{f' ({provider})' if provider else ''} — POST /v1/forecast/run first")
    return b

@app.get("/v1/forecast/{location_id}/24h", response_model=ForecastBundle)
def get_forecast_24h(location_id: str, provider: str | None = None):
    return get_forecast(location_id, provider)

@app.post("/v1/forecast/run", response_model=list[ForecastBundle])
def run_forecast(req: RunRequest, x_api_key: str | None = Header(default=None)):
    _auth(x_api_key)
    p = REGISTRY.get(req.provider)
    ids = req.location_ids or [l["location_id"] for l in STORE.locations()]
    out=[]
    for loc in ids:
        pts = REGISTRY.run(p, loc, req.pollutants, req.horizon)
        b = ForecastBundle(location_id=loc, provider=p.name, model_version=p.version,
                           generated_at=utcnow(), is_synthetic=S.demo_mode, points=pts)
        STORE.save_forecast(b); out.append(b)
    STORE._ev  = [e.model_dump(mode="json") for e in build_events(STORE)]
    STORE._rec = build_recommendations(STORE)
    STORE._ex  = build_explanations(STORE, p.name)
    return out

@app.get("/v1/aqi/{location_id}", response_model=AQIResult)
def aqi_now(location_id: str):
    conc={}
    for p in ("pm25","pm10","no2","so2"):
        o = STORE.observations(location_id, p, limit=1)
        if not o.empty: conc[p]=float(o.value.iloc[-1])
    return compute_aqi(conc)

@app.get("/v1/aqi/{location_id}/forecast", response_model=list[AQIResult])
def aqi_forecast(location_id: str, provider: str | None = None):
    b = get_forecast(location_id, provider)
    rows = pd.DataFrame([pt.model_dump() for pt in b.points])
    out=[]
    for ts, g in rows.groupby("timestamp"):
        out.append(compute_aqi(dict(zip(g.pollutant, g.predicted))))
    return out

@app.get("/v1/events", response_model=list[Event])
def events(): return STORE.events()

@app.get("/v1/alerts", response_model=list[Event])
def alerts(): return events()

@app.get("/v1/explanations/{location_id}", response_model=Explanation)
def explanations(location_id: str):
    e = STORE.explanations().get(location_id)
    if not e: raise HTTPException(404, "no explanation — run forecast first")
    return e

@app.get("/v1/recommendations/{location_id}", response_model=list[Recommendation])
def recommendations(location_id: str):
    r = STORE.recommendations().get(location_id)
    if r is None: raise HTTPException(404, "no recommendations")
    return r

@app.post("/v1/admin/reload")
def reload(x_api_key: str | None = Header(default=None)):
    _auth(x_api_key)
    global STORE
    STORE = FileStorage()
    log.info("storage reloaded from %s", S.artifact_dir)
    return {"status":"reloaded","locations":len(STORE.locations())}

if __name__ == "__main__":
    import uvicorn; uvicorn.run(app, host="0.0.0.0", port=8000)
