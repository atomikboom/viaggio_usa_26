import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import json
import os
import pydeck as pdk
import math
import requests


MAPBOX_API_KEY = st.secrets.get("MAPBOX_API_KEY", os.getenv("MAPBOX_API_KEY"))
ICON_URLS_BY_TYPE = {
    "Hotel": "https://cdn-icons-png.flaticon.com/512/727/727606.png",
    "Parco": "https://cdn-icons-png.flaticon.com/512/9101/9101314.png",
    "Città": "https://cdn-icons-png.flaticon.com/512/9131/9131493.png",
    "Viewpoint": "https://cdn-icons-png.flaticon.com/512/18183/18183776.png",
    "Altro": "https://cdn-icons-png.flaticon.com/512/18432/18432784.png",
}

def initialize_database(db_path="travel_hub_usa_ovest.db"):

    # -----------------------------
    # 1) TABELLA ITINERARY
    # -----------------------------
    itinerary_rows = [
        {
            "Giorno": 1,
            "Data": "2026-08-10",
            "Tipo giorno": "On the road",
            "Tappa principale": "Milano → Los Angeles, Santa Monica",
            "Distanza prevista (km)": None,
            "Pernottamento": "Rest Haven Motel",
            "Attività principali / note": "Arrivo + visita Santa Monica",
        },
        {
            "Giorno": 2,
            "Data": "2026-08-11",
            "Tipo giorno": "Città",
            "Tappa principale": "Los Angeles -> Palm Springs -> Indio",
            "Distanza prevista (km)": None,
            "Pernottamento": "Best Western Date Tree Hotel",
            "Attività principali / note": "Beverly Hills, Hollywood, Griffith",
        },
        {
            "Giorno": 3,
            "Data": "2026-08-12",
            "Tipo giorno": "Parco / On the road",
            "Tappa principale": "Joshua Tree → Route 66 → Sedona → Flagstaff",
            "Distanza prevista (km)": None,
            "Pernottamento": "Holiday Inn Express",
            "Attività principali / note": "Visita Joshua Tree, Route 66",
        },
        {
            "Giorno": 4,
            "Data": "2026-08-13",
            "Tipo giorno": "Parco",
            "Tappa principale": "Sedona → Grand Canyon",
            "Distanza prevista (km)": None,
            "Pernottamento": "Yavapai Lodge",
            "Attività principali / note": "South Rim, Hopi Point",
        },
        {
            "Giorno": 5,
            "Data": "2026-08-14",
            "Tipo giorno": "Parco",
            "Tappa principale": "Grand Canyon → Monument Valley",
            "Distanza prevista (km)": None,
            "Pernottamento": "The View Hotel",
            "Attività principali / note": "Alba a Mather Point, tramonto MV",
        },
        {
            "Giorno": 6,
            "Data": "2026-08-15",
            "Tipo giorno": "Parco / On the road",
            "Tappa principale": "Monument Valley → Page",
            "Distanza prevista (km)": None,
            "Pernottamento": "Super 8 by Wyndham Page",
            "Attività principali / note": "Scenic Drive Monument Valley",
        },
        {
            "Giorno": 7,
            "Data": "2026-08-16",
            "Tipo giorno": "Parco",
            "Tappa principale": "Page → Antelope Canyon → Bryce Canyon",
            "Distanza prevista (km)": None,
            "Pernottamento": "Ruby’s Inn",
            "Attività principali / note": "Tour Antelope + Lake Powell",
        },
        {
            "Giorno": 8,
            "Data": "2026-08-17",
            "Tipo giorno": "Parco / Città",
            "Tappa principale": "Bryce → Zion → Las Vegas",
            "Distanza prevista (km)": None,
            "Pernottamento": "Flamingo Las Vegas",
            "Attività principali / note": "Scenic drive Zion + arrivo Vegas",
        },
        {
            "Giorno": 9,
            "Data": "2026-08-18",
            "Tipo giorno": "Parco / On the road",
            "Tappa principale": "Valley of Fire → Death Valley",
            "Distanza prevista (km)": None,
            "Pernottamento": "The Ranch at Death Valley",
            "Attività principali / note": "Fire Wave, Badwater Basin",
        },
        {
            "Giorno": 10,
            "Data": "2026-08-19",
            "Tipo giorno": "On the road",
            "Tappa principale": "Death Valley → Three Rivers",
            "Distanza prevista (km)": None,
            "Pernottamento": "Lazy J Ranch Motel",
            "Attività principali / note": "Trasferimento lungo verso Sequoia",
        },
        {
            "Giorno": 11,
            "Data": "2026-08-20",
            "Tipo giorno": "Parco / On the road",
            "Tappa principale": "Sequoia → Kings Canyon → Yosemite area",
            "Distanza prevista (km)": None,
            "Pernottamento": "Curry Village",
            "Attività principali / note": "General Sherman, General Grant",
        },
        {
            "Giorno": 12,
            "Data": "2026-08-21",
            "Tipo giorno": "Parco / Città",
            "Tappa principale": "Yosemite → San Francisco",
            "Distanza prevista (km)": None,
            "Pernottamento": "Hotel Zephyr",
            "Attività principali / note": "Tunnel View + arrivo SF",
        },
        {
            "Giorno": 13,
            "Data": "2026-08-22",
            "Tipo giorno": "Città",
            "Tappa principale": "San Francisco — Golden Gate + bici",
            "Distanza prevista (km)": None,
            "Pernottamento": "Hotel Zephyr",
            "Attività principali / note": "Golden Gate Park, Sausalito",
        },
        {
            "Giorno": 14,
            "Data": "2026-08-23",
            "Tipo giorno": "Città",
            "Tappa principale": "San Francisco — quartieri & ferry",
            "Distanza prevista (km)": None,
            "Pernottamento": "Hotel Zephyr",
            "Attività principali / note": "Chinatown, Lombard, Alcatraz (opz.)",
        },
        {
            "Giorno": 15,
            "Data": "2026-08-24",
            "Tipo giorno": "On the road",
            "Tappa principale": "Rientro in Italia",
            "Distanza prevista (km)": None,
            "Pernottamento": "—",
            "Attività principali / note": "Consegna auto, volo",
        },
    ]

    itinerary_df = pd.DataFrame(itinerary_rows, columns=[
        "Giorno",
        "Data",
        "Tipo giorno",
        "Tappa principale",
        "Distanza prevista (km)",
        "Pernottamento",
        "Attività principali / note",
    ])

    # -----------------------------
    # 2) TABELLA BOOKINGS
    # -----------------------------
    bookings_data = [

        ["Hotel", "Rest Haven Motel – Santa Monica", "2026-08-10", "2026-08-11", "25653230", 226.45, "https://www.resthavenmotel.com", "Colazione esclusa"],
        ["Hotel", "Best Western Date Tree – Indio", "2026-08-11", "2026-08-12", "", None, "", "Colazione inclusa"],
        ["Hotel", "Holiday Inn Express Sedona", "2026-08-12", "2026-08-13", "", None, "", ""],
        ["Hotel", "Yavapai Lodge – Grand Canyon", "2026-08-13", "2026-08-14", "73066067899416", None, "", ""],
        ["Hotel", "The View Hotel – Monument Valley", "2026-08-14", "2026-08-15", "TVHUT04755008", None, "", "Vista iconica"],
        ["Hotel", "Super 8 by Wyndham Page", "2026-08-15", "2026-08-16", "4720068931", 164.13, "", "Colazione inclusa"],
        ["Hotel", "Ruby’s Inn – Bryce Canyon", "2026-08-16", "2026-08-17", "4309748448", None, "", ""],
        ["Hotel", "Flamingo Las Vegas", "2026-08-17", "2026-08-19", "VCWS-003S7EWZ", 186.55, "", "56,63$ da pagare in loco"],
        ["Hotel", "The Ranch at Death Valley", "2026-08-19", "2026-08-20", "6344122925", None, "", ""],
        ["Hotel", "Lazy J Ranch Motel – Three Rivers", "2026-08-20", "2026-08-21", "6683620206", None, "", ""],
        ["Hotel", "Curry Village – Yosemite", "2026-08-21", "2026-08-22", "1656LV", 237.20, "", ""],
        ["Hotel", "Hotel Zephyr – San Francisco", "2026-08-22", "2026-08-25", "6458596951", 633.00, "", ""],

    ]

    bookings_df = pd.DataFrame(bookings_data, columns=[
        "Tipo", "Nome", "Check_in", "Check_out", "Codice", "Importo", "Link", "Note"
    ])

    # -----------------------------
    # 3) TABELLA LOCATIONS
    # -----------------------------
    locations_rows = []
    for name, tipo, day_note in [
        ("Los Angeles", "Città", "Giorno 1-2"),
        ("Santa Monica Pier", "Cityspot", "Giorno 1"),
        ("Venice Beach", "Cityspot", "Giorno 1"),
        ("Beverly Hills", "Cityspot", "Giorno 2"),
        ("Hollywood Blvd", "Cityspot", "Giorno 2"),
        ("Griffith Observatory", "Viewpoint", "Giorno 2"),
        ("Palm Springs", "Città", "Giorno 2"),
        ("Indio", "Città", "Giorno 2"),
        ("Joshua Tree National Park", "Parco", "Giorno 3"),
        ("Route 66", "Strada", "Giorno 3"),
        ("Sedona", "Città", "Giorno 3-4"),
        ("Grand Canyon South Rim", "Parco", "Giorno 4-5"),
        ("Monument Valley", "Parco", "Giorno 5-6"),
        ("Page", "Città", "Giorno 6-7"),
        ("Antelope Canyon", "Tour", "Giorno 7"),
        ("Lake Powell", "Lago", "Giorno 7"),
        ("Bryce Canyon", "Parco", "Giorno 7-8"),
        ("Zion National Park", "Parco", "Giorno 8"),
        ("Las Vegas", "Città", "Giorno 8-9"),
        ("Valley of Fire", "Parco", "Giorno 9"),
        ("Death Valley National Park", "Parco", "Giorno 9-10"),
        ("Sequoia National Park", "Parco", "Giorno 11"),
        ("Kings Canyon", "Parco", "Giorno 11"),
        ("Yosemite National Park", "Parco", "Giorno 11-12"),
        ("San Francisco", "Città", "Giorno 12-15"),
    ]:
        locations_rows.append(
            {
                "Nome luogo": name,
                "Data": None,
                "Latitudine": None,
                "Longitudine": None,
                "Tipo": "Altro" if tipo == "Cityspot" else tipo,
                "Note": day_note,
                "Maps URL": "",
            }
        )

    locations_df = pd.DataFrame(
        locations_rows,
        columns=[
            "Nome luogo",
            "Data",
            "Latitudine",
            "Longitudine",
            "Tipo",
            "Note",
            "Maps URL",
        ],
    )

    # -----------------------------
    # 4) SALVATAGGIO SU SQLITE
    # -----------------------------
    conn = sqlite3.connect(db_path)

    itinerary_df.to_sql("itinerary", conn, if_exists="replace", index=False)
    bookings_df.to_sql("bookings", conn, if_exists="replace", index=False)
    locations_df.to_sql("locations", conn, if_exists="replace", index=False)

    conn.close()

    return True


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Distanza approssimata in km tra due coordinate (lat/lon in gradi)
    usando la formula di Haversine.
    """
    if None in (lat1, lon1, lat2, lon2):
        return None

    R = 6371.0  # raggio medio della Terra in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def get_mapbox_route(lon1, lat1, lon2, lat2):
    """
    Usa Mapbox Directions API per ottenere il percorso stradale tra due punti.
    Restituisce:
    - lista di coordinate [ [lon, lat], ... ]
    - distanza in km
    - durata in ore
    Se qualcosa va storto, restituisce (None, None, None)
    """
    if MAPBOX_API_KEY is None:
        return None, None, None

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}"
    params = {
        "geometries": "geojson",
        "overview": "full",
        "access_token": MAPBOX_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("routes"):
            return None, None, None

        route = data["routes"][0]
        coords = route["geometry"]["coordinates"]  # lista [lon, lat]
        distance_km = route["distance"] / 1000.0   # metri -> km
        duration_h = route["duration"] / 3600.0    # secondi -> ore

        return coords, distance_km, duration_h

    except Exception:
        # Possiamo loggare se vuoi, per ora facciamo fallback
        return None, None, None


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rimuove le righe completamente vuote:
    - tutte NaN
    - oppure solo stringhe vuote/spazi
    """
    if df is None or df.empty:
        return df

    tmp = df.copy()

    # Trasforma stringhe vuote o solo spazi in NaN
    # (vale per tutte le colonne, anche Maps URL, Nome luogo, ecc.)
    tmp = tmp.replace(r'^\s*$', pd.NA, regex=True)

    # Elimina le righe dove TUTTE le celle sono NaN
    tmp = tmp.dropna(how="all")

    return tmp

def extract_lat_lon_from_maps_url(url: str):
    """
    Prova a estrarre latitudine e longitudine da un URL di Google Maps.
    Supporta formati tipo:
    - .../@37.4219,-122.0840,15z/...
    - ...?q=37.4219,-122.0840...
    Restituisce (lat, lon) oppure (None, None) se non riesce.
    """
    if not isinstance(url, str):
        return None, None

    url = url.strip()
    if url == "":
        return None, None

    # Caso 1: URL con @lat,lon,zoom
    try:
        if "@" in url:
            part = url.split("@", 1)[1]
            pieces = part.split(",")
            if len(pieces) >= 2:
                lat = float(pieces[0])
                lon = float(pieces[1])
                return lat, lon
    except Exception:
        pass

    # Caso 2: URL con ?q=lat,lon
    try:
        if "q=" in url:
            part = url.split("q=", 1)[1]
            part = part.split("&", 1)[0]
            pieces = part.split(",")
            if len(pieces) >= 2:
                lat = float(pieces[0])
                lon = float(pieces[1])
                return lat, lon
    except Exception:
        pass

    return None, None

def render_countdown():
    """Mostra un countdown alla partenza e lo stato del viaggio."""
    today = date.today()
    start_date = date(2026, 8, 10)
    end_date = date(2026, 8, 25)

    # Prima della partenza: countdown
    if today < start_date:
        days_to_start = (start_date - today).days
        # piccolo extra: settimane + giorni
        weeks = days_to_start // 7
        rest_days = days_to_start % 7

        if days_to_start == 1:
            text = "⏳ Manca **1 giorno** alla partenza (10 agosto 2026)."
        else:
            text = f"⏳ Mancano **{days_to_start} giorni** alla partenza (10 agosto 2026)."

        if weeks > 0:
            text += f" (≈ {weeks} settimane"
            if rest_days:
                text += f" e {rest_days} giorni"
            text += ")"

        st.info(text)

    # Durante il viaggio
    elif start_date <= today <= end_date:
        total_days = (end_date - start_date).days + 1
        current_day = (today - start_date).days + 1
        days_left = (end_date - today).days

        if days_left == 0:
            extra = "🎉 Ultimo giorno di viaggio!"
        else:
            extra = f"Ti restano ancora **{days_left} giorni**."

        st.success(
            f"✈️ Siete in viaggio! Giorno **{current_day}/{total_days}**. {extra}"
        )

    # Dopo il viaggio: non mostra nulla (sparisce)
    else:
        # Se vuoi, potresti mettere un piccolo messaggio tipo:
        # st.caption("Viaggio concluso. Puoi usare l'app per i ricordi e il consuntivo delle spese.")
        pass

def ensure_columns(df: pd.DataFrame, columns) -> pd.DataFrame:
    """
    Garantisce che il DataFrame abbia tutte le colonne elencate in 'columns'.
    Aggiunge quelle mancanti come NaN e le ordina.
    """
    if df is None:
        df = pd.DataFrame()
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[columns]


# ------------------------
# CONFIGURAZIONE APP
# ------------------------
st.set_page_config(
    page_title="Travel Hub USA Ovest 2026",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 Travel Hub USA Ovest 2026")
st.caption("Itinerario • Info utili • Spese & Budget • Dashboard")

render_countdown()

# CSS per aumentare l'altezza delle mappe pydeck
st.markdown(
    """
    <style>
    /* Contenitore del grafico deck.gl */
    [data-testid="stDeckGlJson"] {
        height: 800px !important;
    }
    /* Div interno che contiene il canvas */
    [data-testid="stDeckGlJson"] > div {
        height: 800px !important;
    }
    /* Canvas vero e proprio */
    [data-testid="stDeckGlJson"] canvas {
        height: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DB_PATH = "travel_hub_usa_ovest.db"

# ------------------------
# FUNZIONI DB
# ------------------------
TABLE_COLUMN_ALIASES = {
    "itinerary": {
        "Tipo": "Tipo giorno",
        "Tappa": "Tappa principale",
        "Note": "Attività principali / note",
        "Distance_km": "Distanza prevista (km)",
    },
    "locations": {
        "Nome": "Nome luogo",
        "Categoria": "Tipo",
        "Giorno": "Note",
    },
    "packing": {
        "Per chi?": "Per chi",
    },
    "todo": {
        "Assegnato": "Assegnato a",
    },
}

def get_conn():
    return sqlite3.connect(DB_PATH)

def load_table(table_name, columns):
    """Carica una tabella dal DB in un DataFrame. Se non esiste, restituisce un DF vuoto."""
    with get_conn() as conn:
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            aliases = TABLE_COLUMN_ALIASES.get(table_name)
            if aliases:
                df = df.rename(columns=aliases)
            # Se c'è la colonna id, lasciamola: può essere utile, ma non obbligatoria
            return df
        except Exception:
            return pd.DataFrame(columns=columns)

def save_table(df, table_name):
    """Salva un DataFrame nel DB (sostituendo la tabella)."""
    with get_conn() as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

def init_info_table():
    """Crea la tabella info se non esiste."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS info (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.commit()

def set_info(key, value):
    """Salva una coppia chiave/valore (stringa) nella tabella info."""
    init_info_table()
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO info(key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (key, value),
        )
        conn.commit()

def get_info(key, default=None):
    """Recupera una stringa dalla tabella info; se non esiste, restituisce default."""
    init_info_table()
    with get_conn() as conn:
        cur = conn.execute("SELECT value FROM info WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            return row[0]
        return default

def load_travellers_from_db():
    """Carica i nomi dei viaggiatori da info come JSON."""
    raw = get_info("travellers", None)
    if raw is None:
        # Default: Daniele e Alessandra, Andrea e Paola
        default_travellers = ["Daniele", "Alessandra", "Andrea", "Paola"]
        set_info("travellers", json.dumps(default_travellers))
        return default_travellers
    try:
        return json.loads(raw)
    except Exception:
        # fallback
        return ["Daniele", "Alessandra", "Andrea", "Paola"]

def save_travellers_to_db(travellers_list):
    set_info("travellers", json.dumps(travellers_list))

# ------------------------
# INIZIALIZZAZIONE STATO
# ------------------------
def init_state():
    # Viaggiatori
    if "travellers" not in st.session_state:
        st.session_state.travellers = load_travellers_from_db()

    # Itinerary
    itinerary_columns = [
        "Data",
        "Giorno",
        "Tipo giorno",
        "Tappa principale",
        "Distanza prevista (km)",
        "Pernottamento",
        "Attività principali / note",
    ]
    if "itinerary" not in st.session_state:
        df_it = load_table("itinerary", itinerary_columns)
        df_it = ensure_columns(df_it, itinerary_columns)
        st.session_state.itinerary = drop_empty_rows(df_it)

    # Schedule (ora per ora) - opzionale
    schedule_columns = ["Data", "Ora", "Descrizione"]
    if "schedule" not in st.session_state:
        df_sc = load_table("schedule", schedule_columns)
        df_sc = ensure_columns(df_sc, schedule_columns)
        st.session_state.schedule = drop_empty_rows(df_sc)

    # Spese
    expenses_columns = [
        "Data",
        "Categoria",
        "Descrizione",
        "Pagato da",
        "Partecipanti",
        "Importo",
        "Valuta",
        "Tasso -> EUR",
        "Importo in EUR",
    ]
    if "expenses" not in st.session_state:
        df_ex = load_table("expenses", expenses_columns)
        df_ex = ensure_columns(df_ex, expenses_columns)
        st.session_state.expenses = drop_empty_rows(df_ex)
        
        # Locations per la mappa
    locations_columns = [
        "Nome luogo",
        "Data",
        "Latitudine",
        "Longitudine",
        "Tipo",   # es. Hotel, Parco, Città, Altro
        "Note",
        "Maps URL",
    ]
    if "locations" not in st.session_state:
        df_loc = load_table("locations", locations_columns)
        df_loc = ensure_columns(df_loc, locations_columns)
        st.session_state.locations = drop_empty_rows(df_loc)

    # Info luoghi (wiki delle tappe)
    places_info_columns = [
        "Luogo",
        "Descrizione",
        "Cose da vedere",
        "Dove mangiare",
        "Note utili",
        "Link utili",
    ]
    if "places_info" not in st.session_state:
        df_pi = load_table("places_info", places_info_columns)
        st.session_state.places_info = drop_empty_rows(df_pi)
    
        # To-do pre-viaggio
    todo_columns = [
        "Task",
        "Scadenza",
        "Assegnato a",
        "Stato",  # Da fare / In corso / Fatto
        "Note",
    ]
    if "todo" not in st.session_state:
        df_td = load_table("todo", todo_columns)
        df_td = ensure_columns(df_td, todo_columns)
        st.session_state.todo = drop_empty_rows(df_td)

    # Packing list
    packing_columns = [
        "Oggetto",
        "Categoria",  # Documenti, Tech, Vestiti, Medicine, Altro
        "Per chi",    # Daniele & Alessandra, Andrea & Paola, Tutti
        "Stato",      # Da comprare, Da preparare, In valigia, Già sul posto
        "Note",
    ]
    if "packing" not in st.session_state:
        df_pack = load_table("packing", packing_columns)
        df_pack = ensure_columns(df_pack, packing_columns)
        st.session_state.packing = drop_empty_rows(df_pack)




init_state()


# ------------------------
# FUNZIONI DI SUPPORTO
# ------------------------
def parse_participants(str_participants):
    """Converte la stringa 'P1;P2' in lista ['P1', 'P2']."""
    if pd.isna(str_participants) or str_participants == "":
        return []
    return [p.strip() for p in str_participants.split(";") if p.strip()]


def compute_balances(expenses_df, travellers):
    """
    Calcola quanto ha pagato ciascuno, quanto dovrebbe pagare
    e il saldo finale (positivo = deve ricevere, negativo = deve dare).
    """
    paid = {t: 0.0 for t in travellers}
    should = {t: 0.0 for t in travellers}

    for _, row in expenses_df.iterrows():
        payer = row.get("Pagato da")
        amount_eur = row.get("Importo in EUR")
        participants = parse_participants(row.get("Partecipanti"))

        if not participants or pd.isna(amount_eur):
            continue

        share = amount_eur / len(participants)

        if payer in paid:
            paid[payer] += amount_eur

        for p in participants:
            if p in should:
                should[p] += share

    data = []
    for t in travellers:
        saldo = paid[t] - should[t]
        data.append(
            {
                "Persona": t,
                "Totale pagato (EUR)": round(paid[t], 2),
                "Dovuto teorico (EUR)": round(should[t], 2),
                "Saldo (EUR)": round(saldo, 2),
            }
        )

    return pd.DataFrame(data)


def compute_couples_summary(balance_df):
    """
    Assume coppia 1: Persona 1 & Persona 2
           coppia 2: Persona 3 & Persona 4
    (si basa sull'ordine dei viaggiatori)
    """
    if len(balance_df) < 4:
        return None

    coppia_A = balance_df.iloc[0:2]
    coppia_B = balance_df.iloc[2:4]

    total_A = coppia_A["Saldo (EUR)"].sum()
    total_B = coppia_B["Saldo (EUR)"].sum()

    return pd.DataFrame(
        [
            {"Coppia": f"Coppia A ({balance_df.iloc[0]['Persona']} + {balance_df.iloc[1]['Persona']})",
             "Saldo (EUR)": round(total_A, 2)},
            {"Coppia": f"Coppia B ({balance_df.iloc[2]['Persona']} + {balance_df.iloc[3]['Persona']})",
             "Saldo (EUR)": round(total_B, 2)},
        ]
    )

def compute_itinerary_stats(itinerary_df: pd.DataFrame):
    """Calcola km totali, km/giorno, cambi hotel, distribuzione per tipo di giorno."""
    if itinerary_df is None or itinerary_df.empty:
        return None, None, None, None

    df = itinerary_df.copy()

    # Data in formato datetime per ordinare
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Distanza numerica
    if "Distanza prevista (km)" in df.columns:
        df["Distanza prevista (km)"] = pd.to_numeric(
            df["Distanza prevista (km)"], errors="coerce"
        )
        total_km = df["Distanza prevista (km)"].sum(skipna=True)
    else:
        total_km = 0

    # Numero di giorni (righe con almeno Data o Tappa principale)
    valid_rows = df[
        df["Data"].notna()
        | df.get("Tappa principale", pd.Series(dtype=str)).astype(str).str.strip().ne("")
    ]
    num_days = len(valid_rows)
    avg_km = total_km / num_days if num_days > 0 else 0

    # Cambi hotel: quante volte il pernottamento cambia rispetto al giorno precedente
    hotel_changes = 0
    if "Pernottamento" in df.columns:
        df_sorted = df.sort_values("Data")
        pern = df_sorted["Pernottamento"].fillna("").astype(str).str.strip().tolist()
        prev = ""
        for p in pern:
            if p and p != prev:
                if prev != "":
                    hotel_changes += 1
                prev = p

    # Distribuzione per tipo giorno
    type_counts = None
    if "Tipo giorno" in df.columns:
        type_counts = (
            df["Tipo giorno"]
            .fillna("Non specificato")
            .astype(str)
            .value_counts()
            .reset_index()
        )
        type_counts.columns = ["Tipo giorno", "Numero giorni"]

    return total_km, avg_km, hotel_changes, type_counts


# ------------------------
# SIDEBAR: IMPOSTAZIONI
# ------------------------
st.sidebar.header("⚙️ Impostazioni")

read_only = st.sidebar.checkbox(
    "Modalità sola lettura (blocca modifiche)",
    value=False,
    help="Quando attiva, nessuno può modificare i dati: si può solo consultare.",
)

st.sidebar.title("⚙️ Amministrazione database")

if st.sidebar.button("Inizializza viaggio (popola DB)"):
    initialize_database()
    st.success("Database inizializzato con successo! 🎉")


st.sidebar.subheader("Viaggiatori")
for i in range(4):
    new_name = st.sidebar.text_input(
        f"Nome persona {i+1}",
        value=st.session_state.travellers[i],
        key=f"traveller_{i}",
    )
    st.session_state.travellers[i] = new_name

if st.sidebar.button("💾 Salva nomi viaggiatori"):
    save_travellers_to_db(st.session_state.travellers)
    st.sidebar.success("Nomi salvati!")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Sezioni",
    ("Itinerario", "Mappa", "Info luoghi", "Info utili", "Packing list", "To-do pre-viaggio", "Spese & Budget", "Dashboard"),
)


# ------------------------
# PAGINA: ITINERARIO
# ------------------------
if page == "Itinerario":
    st.header("📅 Itinerario")

    st.markdown("### Riepilogo giorno per giorno")

    itinerary_df = st.session_state.itinerary.copy()
    
    if "Data" in itinerary_df.columns:
        itinerary_df["Data"] = pd.to_datetime(itinerary_df["Data"], errors="coerce")

    if read_only:
        st.info("Modalità sola lettura attiva.")
        st.dataframe(itinerary_df, use_container_width=True)

    else:
        edited_itinerary = st.data_editor(
            itinerary_df,
            num_rows="dynamic",
            use_container_width=True,
            key="itinerary_editor",
            column_config={
                "Data": st.column_config.DateColumn(
                    "Data",
                    format="DD/MM/YYYY",
                    help="Data dell'attività"
                ),
                "Giorno": st.column_config.NumberColumn(
                    "Giorno",
                    format="%d",
                    help="Numero progressivo del giorno di viaggio",
                ),
                "Tipo giorno": st.column_config.SelectboxColumn(
                    "Tipo giorno",
                    options=[
                        "Città",
                        "Parco",
                        "On the road",
                        "Parco / On the road",
                        "Parco / Città",
                        "Parco / Città / On the road",
                        "Misto",
                    ],
                    help="Classificazione del giorno",
                ),
                "Tappa principale": st.column_config.TextColumn(
                    "Tappa principale",
                    help="Località o tratto principale della giornata",
                ),
                "Distanza prevista (km)": st.column_config.NumberColumn(
                    "Distanza prevista (km)",
                    help="Distanza pianificata per la giornata (facoltativa)",
                    step=10,
                    format="%.0f",
                ),
                "Pernottamento": st.column_config.TextColumn("Pernottamento"),
                "Attività principali / note": st.column_config.TextColumn(
                    "Attività principali / note"
                ),
            },
        )

        col_save_it1, col_save_it2 = st.columns([1, 4])
        with col_save_it1:
            if st.button("💾 Salva itinerario", key="save_itinerary_btn"):
                cleaned_itinerary = drop_empty_rows(edited_itinerary)

                if "Data" in cleaned_itinerary.columns:
                    converted_dates = pd.to_datetime(
                        cleaned_itinerary["Data"], errors="coerce"
                    )
                    formatted_dates = converted_dates.dt.strftime("%Y-%m-%d")
                    cleaned_itinerary["Data"] = formatted_dates.where(
                        ~converted_dates.isna(), pd.NA
                    )

                st.session_state.itinerary = cleaned_itinerary
                save_table(cleaned_itinerary, "itinerary")
                st.success("Itinerario salvato nel database!")

    st.markdown("### (Opzionale) Dettaglio ora per ora")

    schedule_df = st.session_state.schedule.copy()

    if read_only:
        st.dataframe(schedule_df, use_container_width=True)
    else:
        edited_schedule = st.data_editor(
            schedule_df,
            num_rows="dynamic",
            use_container_width=True,
            key="schedule_editor",
        )

        col_save_sc1, col_save_sc2 = st.columns([1, 4])
        with col_save_sc1:
            if st.button("💾 Salva dettaglio orario"):
                cleaned_schedule = drop_empty_rows(edited_schedule)
                st.session_state.schedule = cleaned_schedule
                save_table(cleaned_schedule, "schedule")
                st.success("Dettaglio orario salvato nel database!")

# ------------------------
# PAGINA: MAPPA
# ------------------------
elif page == "Mappa":
    st.header("🗺️ Mappa del viaggio")

    st.markdown(
        "Gestisci qui i punti principali del viaggio (città, parchi, hotel, viewpoint). "
        "La tabella è modificabile e la mappa si aggiorna di conseguenza."
    )

    locations_df = st.session_state.locations.copy()

    st.subheader("Punti sulla mappa")

    # --- PARTE TABELLA / EDITOR ---
    if read_only:
        st.info("Modalità sola lettura attiva: non puoi modificare i punti, ma puoi consultarli.")
        st.dataframe(locations_df, use_container_width=True)
        map_source_df = locations_df  # la mappa userà questi dati
    else:
        edited_locations = st.data_editor(
            locations_df,
            num_rows="dynamic",
            use_container_width=True,
            key="locations_editor",
            column_config={
                "Nome luogo": st.column_config.TextColumn("Nome luogo"),
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Latitudine": st.column_config.NumberColumn("Latitudine", step=0.000001),
                "Longitudine": st.column_config.NumberColumn("Longitudine", step=0.000001),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["Hotel", "Parco", "Città", "Viewpoint", "Altro"],
                    help="Serve per differenziare i marker sulla mappa",
                ),
                "Note": st.column_config.TextColumn("Note"),
                "Maps URL": st.column_config.TextColumn(
                    "Google Maps URL",
                    help="Incolla qui il link di Google Maps del luogo; puoi poi estrarre automaticamente le coordinate.",
                ),
            },
        )

        # Bottone per estrarre coordinate dai link Google Maps
        if st.button("📍 Estrai coordinate dai link Google Maps"):
            loc = edited_locations.copy()
            loc = drop_empty_rows(loc)

            debug_rows = []
            updated = False

            for idx, row in loc.iterrows():
                nome = row.get("Nome luogo", "")
                url = row.get("Maps URL", None)
                url = str(url).strip() if url is not None else ""

                # Se non c'è URL, saltiamo ma logghiamo
                if not url:
                    debug_rows.append(
                        {
                            "idx": idx,
                            "Nome luogo": nome,
                            "URL presente?": False,
                            "URL (inizio)": "",
                            "Lat estratta": None,
                            "Lon estratta": None,
                        }
                    )
                    continue

                # Proviamo SEMPRE a estrarre lat/lon, anche se ci sono valori già esistenti
                new_lat, new_lon = extract_lat_lon_from_maps_url(url)

                debug_rows.append(
                    {
                        "idx": idx,
                        "Nome luogo": nome,
                        "URL presente?": True,
                        "URL (inizio)": url[:60] + ("..." if len(url) > 60 else ""),
                        "Lat estratta": new_lat,
                        "Lon estratta": new_lon,
                    }
                )

                if new_lat is not None and new_lon is not None:
                    loc.at[idx, "Latitudine"] = new_lat
                    loc.at[idx, "Longitudine"] = new_lon
                    updated = True

            # Mostriamo cosa è successo dentro il ciclo
            if debug_rows:
                st.markdown("#### Debug estrazione coordinate")
                st.dataframe(pd.DataFrame(debug_rows), use_container_width=True)

            if updated:
                st.session_state.locations = loc
                save_table(loc, "locations")
                st.success("Coordinate aggiornate dai link Google Maps e salvate nel database!")
                edited_locations = loc  # aggiorniamo l'editor
            else:
                st.info("Nessuna coordinata trovata. Controlla che gli URL siano link completi di Google Maps.")

        col_save_map1, col_save_map2 = st.columns([1, 4])
        with col_save_map1:
            if st.button("💾 Salva punti mappa"):
                cleaned_locations = drop_empty_rows(edited_locations)
                st.session_state.locations = cleaned_locations
                save_table(cleaned_locations, "locations")
                st.success("Punti mappa salvati nel database!")

        # Per la mappa usiamo sempre ciò che c'è nell'editor
        map_source_df = edited_locations

    # --- PARTE MAPPA ---
    st.markdown("---")
    st.subheader("Mappa interattiva")

    # Usiamo i dati attuali (readonly o editor) per mostrare la mappa live
    map_df = drop_empty_rows(map_source_df)

    if map_df.empty:
        st.info("Aggiungi qualche punto nella tabella sopra per vedere la mappa.")
    else:
        # Rimuove righe senza coordinate
        map_df = map_df.dropna(subset=["Latitudine", "Longitudine"])

        if map_df.empty:
            st.warning("I punti esistono ma mancano le coordinate (Latitudine/Longitudine).")
        else:
            # Colori diversi in base al tipo (li teniamo per eventuali usi futuri)
            def tipo_to_color(tipo):
                if not isinstance(tipo, str):
                    return [128, 128, 128]
                t = tipo.lower()
                if "hotel" in t:
                    return [0, 102, 255]      # blu
                if "parco" in t:
                    return [0, 153, 0]        # verde
                if "citt" in t:               # città
                    return [255, 165, 0]      # arancio
                if "view" in t:
                    return [186, 85, 211]     # viola
                return [200, 200, 200]        # grigio

            map_df["color"] = map_df["Tipo"].apply(tipo_to_color)

            # Ordiniamo i punti in base a Data (se presente) per costruire il "percorso"
            ordered = map_df.copy()
            if "Data" in ordered.columns:
                ordered = ordered.sort_values("Data", kind="mergesort")
            ordered = ordered.reset_index(drop=True)

            # Costruiamo i segmenti usando Mapbox Directions (se possibile)
            segments = []
            route_paths = []  # per PathLayer

            for i in range(len(ordered) - 1):
                r_from = ordered.iloc[i]
                r_to = ordered.iloc[i + 1]

                lat1, lon1 = r_from["Latitudine"], r_from["Longitudine"]
                lat2, lon2 = r_to["Latitudine"], r_to["Longitudine"]

                # Prima proviamo con Mapbox Directions
                coords, dist_km, time_h = get_mapbox_route(lon1, lat1, lon2, lat2)

                # Se Directions fallisce, fallback a Haversine
                if coords is None or dist_km is None or time_h is None:
                    dist_km = haversine_km(lat1, lon1, lat2, lon2)
                    if dist_km is None:
                        continue
                    speed_kmh = 80.0
                    time_h = dist_km / speed_kmh
                    coords = [[lon1, lat1], [lon2, lat2]]  # linea dritta

                route_paths.append(
                    {
                        "path": coords,
                        "width": 5000,
                    }
                )

                segments.append(
                    {
                        "Da": r_from.get("Nome luogo", f"Punto {i+1}"),
                        "A": r_to.get("Nome luogo", f"Punto {i+2}"),
                        "Distanza (km)": round(dist_km, 1),
                        "Tempo (h)": round(time_h, 2),
                    }
                )

            segments_df = pd.DataFrame(segments)

            # Stato iniziale della vista: centro sui punti
            view_state = pdk.ViewState(
                latitude=float(map_df["Latitudine"].mean()),
                longitude=float(map_df["Longitudine"].mean()),
                zoom=5,
                pitch=30,
            )

            # Prepara i dati icona (pin) per ogni punto
            def build_icon_data(row):
                tipo = str(row.get("Tipo", "Altro")).strip()
                icon_url = ICON_URLS_BY_TYPE.get(tipo, ICON_URLS_BY_TYPE["Altro"])
                return {
                    "url": icon_url,  # URL dell'immagine del pin
                    "width": 128,
                    "height": 128,
                    "anchorY": 128,  # punta in basso
                }

            map_df["icon_data"] = map_df.apply(build_icon_data, axis=1)

            # Layer dei segnalini (IconLayer)
            icon_layer = pdk.Layer(
                "IconLayer",
                data=map_df,
                get_icon="icon_data",
                get_position="[Longitudine, Latitudine]",
                get_size=4,      # grandezza base del pin
                size_scale=10,   # scala globale (puoi giocare con 8–12)
                pickable=True,
            )

            # Path tra le tappe (usando le route_paths)
            path_layer = pdk.Layer(
                "PathLayer",
                data=route_paths,
                get_path="path",
                get_width="width",
                get_color=[255, 140, 0],
            )

            tooltip = {
                "html": "<b>{Nome luogo}</b><br/>Tipo: {Tipo}<br/>Data: {Data}<br/>{Note}",
                "style": {"backgroundColor": "white", "color": "black"},
            }

            if MAPBOX_API_KEY:
                deck = pdk.Deck(
                    layers=[icon_layer, path_layer],
                    initial_view_state=view_state,
                    map_provider="mapbox",
                    map_style="mapbox://styles/mapbox/satellite-streets-v11",
                    api_keys={"mapbox": MAPBOX_API_KEY},
                    tooltip=tooltip,
                    height=800,
                )
            else:
                deck = pdk.Deck(
                    layers=[icon_layer, path_layer],
                    initial_view_state=view_state,
                    tooltip=tooltip,
                    height=800,
                )
                st.warning(
                    "MAPBOX_API_KEY non è configurato: sto usando la mappa di default."
                )

            st.pydeck_chart(
                deck,
                use_container_width=True,
            )
            
            # Collegamento Mappa -> Info Luoghi
            st.markdown("---")
            st.subheader("🔗 Info luogo selezionato")

            selected_loc = st.selectbox(
                "Seleziona un luogo per visualizzare le info",
                map_df["Nome luogo"].unique()
            )

            info_df = st.session_state.places_info.copy()
            row = info_df[info_df["Luogo"] == selected_loc]

            if row.empty:
                st.info("Non ci sono ancora informazioni per questo luogo.")
            else:
                r = row.iloc[0]
                st.markdown(f"### {selected_loc}")
                st.markdown(f"**Descrizione:**\n{r['Descrizione'] or '—'}")
                st.markdown(f"**Cose da vedere:**\n{r['Cose da vedere'] or '—'}")
                st.markdown(f"**Dove mangiare:**\n{r['Dove mangiare'] or '—'}")
                st.markdown(f"**Note utili:**\n{r['Note utili'] or '—'}")
                st.markdown(f"**Link utili:**\n{r['Link utili'] or '—'}")


            # Tabella con le distanze/tempi tra una tappa e la successiva
            st.markdown("#### Segmenti del viaggio (distanze e tempi)")
            if segments_df.empty:
                st.info("Aggiungi almeno due punti con coordinate per vedere le distanze.")
            else:
                st.dataframe(segments_df, use_container_width=True)
          

# ------------------------
# PAGINA: INFO LUOGHI
# ------------------------
elif page == "Info luoghi":
    st.header("📍 Info luoghi")

    st.markdown(
        "Qui puoi raccogliere informazioni dettagliate su ogni tappa: cosa vedere, dove mangiare, link utili, "
        "note pratiche, ecc."
    )

    itinerary_df = st.session_state.itinerary.copy()
    locations_df = st.session_state.locations.copy()
    places_info_df = st.session_state.places_info.copy()

    # Costruiamo la lista dei luoghi disponibili
    luoghi_it = []
    if "Tappa principale" in itinerary_df.columns:
        luoghi_it = (
            itinerary_df["Tappa principale"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    luoghi_loc = []
    if "Nome luogo" in locations_df.columns:
        luoghi_loc = (
            locations_df["Nome luogo"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    all_places = sorted(set(luoghi_it + luoghi_loc))

    if not all_places:
        st.info(
            "Non ci sono ancora luoghi definiti. Aggiungi tappe in **Itinerario** "
            "o punti in **Mappa** per poter inserire le info."
        )
    else:
        selected_place = st.selectbox("Seleziona il luogo", all_places)

        # Cerchiamo se esistono già info per questo luogo
        existing_row = places_info_df[places_info_df["Luogo"] == selected_place]

        if not existing_row.empty:
            row = existing_row.iloc[0]
            desc_default = row.get("Descrizione", "")
            cose_default = row.get("Cose da vedere", "")
            food_default = row.get("Dove mangiare", "")
            note_default = row.get("Note utili", "")
            link_default = row.get("Link utili", "")
        else:
            desc_default = ""
            cose_default = ""
            food_default = ""
            note_default = ""
            link_default = ""

        st.subheader(f"Dettagli per: {selected_place}")
        
        if read_only:
            st.info("Modalità sola lettura attiva: non puoi modificare le info dei luoghi.")
            st.markdown(f"**Descrizione generale**\n\n{desc_default or '_(vuoto)_'}")
            st.markdown(f"**Cose da vedere**\n\n{cose_default or '_(vuoto)_'}")
            st.markdown(f"**Dove mangiare**\n\n{food_default or '_(vuoto)_'}")
            st.markdown(f"**Note utili**\n\n{note_default or '_(vuoto)_'}")
            st.markdown(f"**Link utili**\n\n{link_default or '_(vuoto)_'}")
        else:

            desc = st.text_area(
                "Descrizione generale",
                value=desc_default,
                height=120,
            )
            cose = st.text_area(
                "Cose da vedere (must see)",
                value=cose_default,
                height=120,
                placeholder="- Punto panoramico X\n- Passeggiata Y\n- Vista Z",
            )
            food = st.text_area(
                "Dove mangiare / consigli food",
                value=food_default,
                height=120,
                placeholder="- Ristorante A\n- Diner B\n- Consigli generali",
            )
            note = st.text_area(
                "Note utili / pratiche",
                value=note_default,
                height=120,
                placeholder="Parcheggi, orari, meteo, regole del parco, ecc.",
            )
            links = st.text_area(
                "Link utili",
                value=link_default,
                height=100,
                placeholder="Sito parco, mappe, blog, video, ecc.",
            )

        if st.button("💾 Salva info luogo"):
            new_row = {
                "Luogo": selected_place,
                "Descrizione": desc,
                "Cose da vedere": cose,
                "Dove mangiare": food,
                "Note utili": note,
                "Link utili": links,
            }

            if not existing_row.empty:
                # Aggiorniamo la riga esistente
                mask = places_info_df["Luogo"] == selected_place
                for k, v in new_row.items():
                    places_info_df.loc[mask, k] = v
            else:
                # Aggiungiamo una nuova riga
                places_info_df = pd.concat(
                    [places_info_df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )

            places_info_df = drop_empty_rows(places_info_df)
            st.session_state.places_info = places_info_df
            save_table(places_info_df, "places_info")
            st.success("Info luogo salvate nel database!")

        st.markdown("---")
        st.subheader("Riepilogo rapido di tutte le info luoghi")
        if places_info_df.empty:
            st.info("Non hai ancora salvato info per nessun luogo.")
        else:
            st.dataframe(places_info_df, use_container_width=True)

# ------------------------
# PAGINA: INFO UTILI
# ------------------------
elif page == "Info utili":
    st.header("ℹ️ Info utili viaggio")

    # Carichiamo le eventuali info salvate
    doc_info_default = get_info("doc_info", "")
    car_rental_info_default = get_info("car_rental_info", "")
    emergency_info_default = get_info("emergency_info", "")
    checklist_info_default = get_info("checklist_info", "")
    links_info_default = get_info("links_info", "")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Documenti & burocrazia")
        doc_info = st.text_area(
            "Documenti (passaporti, ESTA, assicurazione, ecc.)",
            height=150,
            key="doc_info",
            value=doc_info_default,
        )

        st.subheader("Noleggio auto")
        car_rental_info = st.text_area(
            "Dati noleggio auto",
            height=150,
            key="car_rental_info",
            value=car_rental_info_default,
        )

    with col2:
        st.subheader("Contatti di emergenza")
        emergency_info = st.text_area(
            "Contatti importanti",
            height=150,
            key="emergency_info",
            value=emergency_info_default,
        )

        st.subheader("Checklist bagaglio")
        checklist_info = st.text_area(
            "Da non dimenticare",
            height=150,
            key="checklist_info",
            value=checklist_info_default,
        )

    st.markdown("---")
    st.subheader("Link utili")
    links_info = st.text_area(
        "Link (mappe, parchi, hotel, ecc.)",
        height=150,
        key="links_info",
        value=links_info_default,
    )

    if st.button("💾 Salva info utili"):
        set_info("doc_info", doc_info)
        set_info("car_rental_info", car_rental_info)
        set_info("emergency_info", emergency_info)
        set_info("checklist_info", checklist_info)
        set_info("links_info", links_info)
        st.success("Info utili salvate nel database!")

# ------------------------
# PAGINA: PACKING LIST
# ------------------------
elif page == "Packing list":
    st.header("🎒 Packing list")

    st.markdown("Organizza tutto ciò che va portato in viaggio.")

    pack_df = st.session_state.packing.copy()

    if read_only:
        st.info("Modalità sola lettura attiva.")
        st.dataframe(pack_df, use_container_width=True)
    else:
        edited_pack = st.data_editor(
            pack_df,
            num_rows="dynamic",
            use_container_width=True,
            key="packing_editor",
            column_config={
                "Oggetto": st.column_config.TextColumn("Oggetto"),
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=["Documenti", "Tech", "Vestiti", "Igiene", "Medicine", "Altro"]
                ),
                "Per chi": st.column_config.SelectboxColumn(
                    "Per chi",
                    options=[
                        "Tutti",
                        "Daniele & Alessandra",
                        "Andrea & Paola",
                    ],
                ),
                "Stato": st.column_config.SelectboxColumn(
                    "Stato",
                    options=["Da comprare", "Da preparare", "In valigia", "Già sul posto"],
                ),
                "Note": st.column_config.TextColumn("Note"),
            },
        )

        if st.button("💾 Salva packing list"):
            cleaned = drop_empty_rows(edited_pack)
            st.session_state.packing = cleaned
            save_table(cleaned, "packing")
            st.success("Packing list salvata!")


# ------------------------
# PAGINA: TO-DO
# ------------------------

elif page == "To-do pre-viaggio":
    st.header("✅ To-do pre-viaggio")

    st.markdown(
        "Usa questa lista per tenere traccia di tutto quello che va fatto prima della partenza: "
        "documenti, prenotazioni, assicurazioni, SIM, ecc."
    )

    todo_df = st.session_state.todo.copy()

    if read_only:
        st.info("Modalità sola lettura attiva: non puoi modificare la lista to-do.")
        st.dataframe(todo_df, use_container_width=True)
    else:
        edited_todo = st.data_editor(
            todo_df,
            num_rows="dynamic",
            use_container_width=True,
            key="todo_editor",
            column_config={
                "Task": st.column_config.TextColumn("Task"),
                "Scadenza": st.column_config.DateColumn("Scadenza", format="DD/MM/YYYY"),
                "Assegnato a": st.column_config.SelectboxColumn(
                    "Assegnato a",
                    options=st.session_state.travellers,
                    help="Chi si occupa di questo task.",
                ),
                "Stato": st.column_config.SelectboxColumn(
                    "Stato",
                    options=["Da fare", "In corso", "Fatto"],
                ),
                "Note": st.column_config.TextColumn("Note"),
            },
        )

        c_save_todo1, c_save_todo2 = st.columns([1, 4])
        with c_save_todo1:
            if st.button("💾 Salva To-do"):
                cleaned_todo = drop_empty_rows(edited_todo)
                st.session_state.todo = cleaned_todo
                save_table(cleaned_todo, "todo")
                st.success("Lista to-do salvata nel database!")

# ------------------------
# PAGINA: SPESE & BUDGET
# ------------------------
elif page == "Spese & Budget":
    st.header("💸 Spese & Budget")

    travellers = st.session_state.travellers
    expenses_df = st.session_state.expenses.copy()
    
    if read_only:
        st.info("Modalità sola lettura attiva: non puoi aggiungere o modificare spese.")
    else:

        st.subheader("Aggiungi una spesa")

        with st.form("add_expense_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                expense_date = st.date_input("Data", value=date(2026, 8, 10))
            with c2:
                category = st.selectbox(
                    "Categoria",
                    [
                        "Alloggio",
                        "Trasporti",
                        "Carburante",
                        "Pasti",
                        "Spesa supermercato",
                        "Parchi / Attrazioni",
                        "Assicurazione",
                        "Telefonia / SIM",
                        "Shopping / Souvenir",
                        "Altro",
                    ],
                )
            with c3:
                description = st.text_input("Descrizione", placeholder="Es. benzina, cena, ingresso parco...")

            c4, c5, c6, c7 = st.columns(4)
            with c4:
                payer = st.selectbox("Pagato da", travellers)
            with c5:
                participants = st.multiselect(
                    "Per chi è la spesa",
                    travellers,
                    default=travellers,
                )
            with c6:
                amount = st.number_input("Importo", min_value=0.0, step=1.0)
            with c7:
                currency = st.selectbox("Valuta", ["EUR", "USD", "Altro"])

            fx = st.number_input(
                "Tasso di cambio verso EUR (quanto vale 1 unità di valuta in EUR)",
                min_value=0.0,
                value=1.0,
                step=0.01,
            )

            submitted = st.form_submit_button("➕ Aggiungi spesa")

        if submitted:
            if amount <= 0 or not participants:
                st.error("Inserisci un importo valido e almeno un partecipante.")
            else:
                amount_eur = amount * fx
                participants_str = ";".join(participants)

                new_row = {
                    "Data": expense_date,
                    "Categoria": category,
                    "Descrizione": description,
                    "Pagato da": payer,
                    "Partecipanti": participants_str,
                    "Importo": amount,
                    "Valuta": currency,
                    "Tasso -> EUR": fx,
                    "Importo in EUR": amount_eur,
                }

                expenses_df = pd.concat(
                    [expenses_df, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                st.session_state.expenses = expenses_df
                save_table(expenses_df, "expenses")
                st.success("Spesa aggiunta e salvata!")

    st.markdown("### Elenco spese (modificabile)")

    if expenses_df.empty:
        st.info("Non hai ancora inserito spese.")
    else:
        if read_only:
            st.dataframe(expenses_df, use_container_width=True)
        else:
                edited_expenses = st.data_editor(
                expenses_df,
                num_rows="dynamic",  # permette anche cancellazione righe
                use_container_width=True,
                key="expenses_editor",
            )

        c_save_exp1, c_save_exp2 = st.columns([1, 4])
        with c_save_exp1:
            if st.button("💾 Salva modifiche spese"):
                cleaned_expenses = drop_empty_rows(edited_expenses)
                st.session_state.expenses = cleaned_expenses
                save_table(cleaned_expenses, "expenses")
                st.success("Spese aggiornate nel database!")

        st.markdown("### Esporta / backup")

        csv = edited_expenses.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Scarica spese in CSV",
            data=csv,
            file_name="spese_viaggio_usa_ovest_2026.csv",
            mime="text/csv",
        )


# ------------------------
# PAGINA: DASHBOARD
# ------------------------
elif page == "Dashboard":
    st.header("📊 Dashboard riepilogativa")

    travellers = st.session_state.travellers
    expenses_df = st.session_state.expenses.copy()

    col_top1, col_top2 = st.columns(2)

    with col_top1:
        st.subheader("Riepilogo per persona")
        if expenses_df.empty:
            st.info("Inserisci qualche spesa per vedere il riepilogo.")
        else:
            balances_df = compute_balances(expenses_df, travellers)
            st.dataframe(balances_df, use_container_width=True)

    with col_top2:
        st.subheader("Riepilogo per coppia")
        if expenses_df.empty:
            st.info("Inserisci qualche spesa per vedere il riepilogo per coppia.")
        else:
            balances_df = compute_balances(expenses_df, travellers)
            couples_df = compute_couples_summary(balances_df)
            if couples_df is not None:
                st.dataframe(couples_df, use_container_width=True)

    st.markdown("---")

    if not expenses_df.empty:
        st.subheader("Spese per categoria")
        cat_group = (
            expenses_df.groupby("Categoria")["Importo in EUR"]
            .sum()
            .reset_index()
            .sort_values("Importo in EUR", ascending=False)
        )
        st.bar_chart(cat_group, x="Categoria", y="Importo in EUR")

        st.subheader("Andamento temporale (spesa in EUR)")
        tmp = expenses_df.copy()
        tmp["Data"] = pd.to_datetime(tmp["Data"])
        daily = tmp.groupby("Data")["Importo in EUR"].sum().reset_index()
        daily = daily.sort_values("Data")
        daily["Spesa cumulativa (EUR)"] = daily["Importo in EUR"].cumsum()
        st.line_chart(daily, x="Data", y="Spesa cumulativa (EUR)")

    st.markdown("---")

    st.subheader("Riepilogo viaggio")
        # Statistiche itinerario (km totali, km/giorno, cambi hotel, tipi giorno)
    itinerary_df = st.session_state.itinerary.copy()
    total_km, avg_km, hotel_changes, type_counts = compute_itinerary_stats(itinerary_df)

    if itinerary_df.empty or total_km is None:
        st.info("Compila la sezione *Itinerario* per vedere le statistiche del viaggio.")
    else:
        c_it_stats1, c_it_stats2, c_it_stats3 = st.columns(3)
        with c_it_stats1:
            st.metric("Km totali previsti", f"{int(total_km):,} km".replace(",", "."))
        with c_it_stats2:
            st.metric("Km medi al giorno", f"{avg_km:.1f} km/giorno")
        with c_it_stats3:
            st.metric("Cambi hotel", str(hotel_changes))

        if type_counts is not None and not type_counts.empty:
            st.subheader("Distribuzione tipi di giorno")
            st.bar_chart(type_counts, x="Tipo giorno", y="Numero giorni")

    st.markdown("---")


    col_it1, col_it2 = st.columns(2)
    with col_it1:
        st.markdown("**Itinerario (tabella sintetica)**")
        if st.session_state.itinerary.empty:
            st.info("Compila la sezione *Itinerario* per vedere un riepilogo qui.")
        else:
            st.dataframe(st.session_state.itinerary, use_container_width=True)

    with col_it2:
        st.markdown("**Note generali**")
        summary_notes_default = get_info("summary_notes", "")
        summary_notes = st.text_area(
            "Riassunto / note del viaggio",
            key="summary_notes",
            value=summary_notes_default,
            height=200,
        )
        if st.button("💾 Salva note riepilogo"):
            set_info("summary_notes", summary_notes)
            st.success("Note riepilogo salvate!")
