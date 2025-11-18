import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import json
import os
import pydeck as pdk
import math
import requests
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

MAPBOX_API_KEY = st.secrets.get("MAPBOX_API_KEY", os.getenv("MAPBOX_API_KEY"))
ICON_URLS_BY_TYPE = {
    "Hotel": "https://cdn-icons-png.flaticon.com/512/727/727606.png",
    "Parco": "https://cdn-icons-png.flaticon.com/512/9101/9101314.png",
    "Città": "https://cdn-icons-png.flaticon.com/512/9131/9131493.png",
    "Viewpoint": "https://cdn-icons-png.flaticon.com/512/18183/18183776.png",
    "Altro": "https://cdn-icons-png.flaticon.com/512/18432/18432784.png",
}
MAX_TRAVELLERS = 4
PACKING_CHECKBOX_COLUMNS = [f"Checked_{i+1}" for i in range(MAX_TRAVELLERS)]

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
    for name, tipo, day_note, maps_url in [
        ("Los Angeles", "Città", "Giorno 1-2", "https://www.google.com/maps/place/Los+Angeles,+CA/@34.052235,-118.243683,12z/"),
        ("Santa Monica Pier", "Cityspot", "Giorno 1", "https://www.google.com/maps/place/Santa+Monica+Pier/@34.009919,-118.496475,17z/"),
        ("Venice Beach", "Cityspot", "Giorno 1", "https://www.google.com/maps/place/Venice+Beach/@33.985047,-118.469483,15z/"),
        ("Beverly Hills", "Cityspot", "Giorno 2", "https://www.google.com/maps/place/Beverly+Hills,+CA/@34.073620,-118.400356,14z/"),
        ("Hollywood Blvd", "Cityspot", "Giorno 2", "https://www.google.com/maps/place/Hollywood+Boulevard/@34.101558,-118.326951,15z/"),
        ("Griffith Observatory", "Viewpoint", "Giorno 2", "https://www.google.com/maps/place/Griffith+Observatory/@34.118434,-118.300393,17z/"),
        ("Palm Springs", "Città", "Giorno 2", "https://www.google.com/maps/place/Palm+Springs,+CA/@33.830296,-116.545292,12z/"),
        ("Indio", "Città", "Giorno 2", "https://www.google.com/maps/place/Indio,+CA/@33.720577,-116.215561,12z/"),
        ("Joshua Tree National Park", "Parco", "Giorno 3", "https://www.google.com/maps/place/Joshua+Tree+National+Park/@33.873415,-115.901008,9z/"),
        ("Route 66", "Strada", "Giorno 3", "https://www.google.com/maps/place/Route+66/@35.325900,-112.874200,8z/"),
        ("Sedona", "Città", "Giorno 3-4", "https://www.google.com/maps/place/Sedona,+AZ/@34.869740,-111.760990,12z/"),
        ("Grand Canyon South Rim", "Parco", "Giorno 4-5", "https://www.google.com/maps/place/Grand+Canyon+Village,+AZ/@36.106965,-112.112997,12z/"),
        ("Monument Valley", "Parco", "Giorno 5-6", "https://www.google.com/maps/place/Monument+Valley/@36.998979,-110.098749,11z/"),
        ("Page", "Città", "Giorno 6-7", "https://www.google.com/maps/place/Page,+AZ/@36.914722,-111.455833,13z/"),
        ("Antelope Canyon", "Tour", "Giorno 7", "https://www.google.com/maps/place/Antelope+Canyon/@36.861900,-111.374300,14z/"),
        ("Lake Powell", "Lago", "Giorno 7", "https://www.google.com/maps/place/Lake+Powell/@36.998000,-111.485000,9z/"),
        ("Bryce Canyon", "Parco", "Giorno 7-8", "https://www.google.com/maps/place/Bryce+Canyon+National+Park/@37.593038,-112.187090,12z/"),
        ("Zion National Park", "Parco", "Giorno 8", "https://www.google.com/maps/place/Zion+National+Park/@37.298202,-113.026300,12z/"),
        ("Las Vegas", "Città", "Giorno 8-9", "https://www.google.com/maps/place/Las+Vegas,+NV/@36.169941,-115.139832,12z/"),
        ("Valley of Fire", "Parco", "Giorno 9", "https://www.google.com/maps/place/Valley+of+Fire+State+Park/@36.422999,-114.514247,12z/"),
        ("Death Valley National Park", "Parco", "Giorno 9-10", "https://www.google.com/maps/place/Death+Valley+National+Park/@36.505389,-117.079407,9z/"),
        ("Sequoia National Park", "Parco", "Giorno 11", "https://www.google.com/maps/place/Sequoia+National+Park/@36.486367,-118.565752,10z/"),
        ("Kings Canyon", "Parco", "Giorno 11", "https://www.google.com/maps/place/Kings+Canyon+National+Park/@36.887900,-118.555100,11z/"),
        ("Yosemite National Park", "Parco", "Giorno 11-12", "https://www.google.com/maps/place/Yosemite+National+Park/@37.865101,-119.538330,10z/"),
        ("San Francisco", "Città", "Giorno 12-15", "https://www.google.com/maps/place/San+Francisco,+CA/@37.774929,-122.419418,12z/"),
    ]:
        locations_rows.append(
            {
                "Nome luogo": name,
                "Data": None,
                "Latitudine": None,
                "Longitudine": None,
                "Tipo": "Altro" if tipo == "Cityspot" else tipo,
                "Note": day_note,
                "Maps URL": maps_url,
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
    # 3b) TABELLA PACKING LIST
    # -----------------------------
    packing_rows = []

    def add_packing_items(category, note, items):
        for item in items:
            packing_rows.append(
                {
                    "Oggetto": item,
                    "Categoria": category,
                    "Per chi": "Tutti",
                    "Stato": "Da preparare",
                    "Note": note,
                    **{col: False for col in PACKING_CHECKBOX_COLUMNS},
                }
            )

    add_packing_items(
        "Documenti",
        "Documenti personali",
        [
            "Passaporto valido",
            "Carta d’identità (per sicurezza)",
            "Patente italiana",
            "Permesso internazionale di guida (IDP)",
            "Fotocopie dei documenti (stampa + foto su telefono)",
        ],
    )
    add_packing_items(
        "Documenti",
        "Viaggio & burocrazia",
        [
            "Biglietti aerei / app compagnia",
            "Prenotazioni hotel/motel/appartamenti",
            "Conferma prenotazione auto a noleggio",
            "Numero polizza assicurazione viaggio",
            "ESTA o visto + ricevuta",
        ],
    )
    add_packing_items(
        "Documenti",
        "Soldi & pagamenti",
        [
            "Carte di credito/debito (almeno 2 circuiti)",
            "Contanti in USD",
            "Bancomat abilitato all’estero",
            "Portafoglio da viaggio con RFID",
        ],
    )

    add_packing_items(
        "Tech",
        "Elettronica & accessori",
        [
            "Smartphone + caricabatterie",
            "Power bank capiente (20.000 mAh)",
            "Adattatore prese USA (tipo A/B, 110V)",
            "Cavi di ricarica extra",
            "Supporto smartphone per auto",
            "Cavo AUX / USB per autoradio",
            "Auricolari / cuffie",
            "E-book reader o tablet",
            "Laptop + caricatore",
            "Action cam / GoPro + accessori + SD",
            "Macchina fotografica + obiettivi + SD",
            "Hard disk o SSD portatile",
            "Ciabatta/multipresa da viaggio",
        ],
    )

    add_packing_items(
        "Vestiti",
        "Parte superiore",
        [
            "T-shirt leggere (cotone o tecnico)",
            "Maglie tecniche a maniche lunghe",
            "Felpa o pile leggero",
            "Giacca/piumino leggero o softshell",
            "Giacca antivento/antipioggia",
        ],
    )
    add_packing_items(
        "Vestiti",
        "Parte inferiore",
        [
            "Pantaloni lunghi leggeri/tecnici",
            "Pantaloncini / shorts",
            "Leggings o strati termici",
        ],
    )
    add_packing_items(
        "Vestiti",
        "Intimo & notte",
        [
            "Intimo sufficiente o per lavatrici",
            "Calze tecniche per trekking",
            "Pigiama / abbigliamento notte",
        ],
    )
    add_packing_items(
        "Vestiti",
        "Scarpe",
        [
            "Scarponcini trekking o trail",
            "Sneakers comode per città",
            "Sandali / ciabatte",
        ],
    )
    add_packing_items(
        "Vestiti",
        "Accessori",
        [
            "Cappello con visiera",
            "Bandana / buff",
            "Occhiali da sole polarizzati",
            "Cintura",
            "Costume da bagno",
            "Outfit carino per la sera",
        ],
    )

    add_packing_items(
        "Igiene",
        "Igiene personale & bagno",
        [
            "Spazzolino + dentifricio",
            "Filo interdentale",
            "Deodorante",
            "Shampoo + bagnoschiuma",
            "Rasoio / lamette / schiuma",
            "Spazzola / pettine / elastici",
            "Crema idratante viso/corpo",
            "Burrocacao",
            "Salviette umidificate",
            "Salviettine disinfettanti mani",
            "Fazzoletti di carta",
            "Forbicine / pinzetta (solo bagaglio stiva)",
            "Prodotti per ciclo (se necessario)",
        ],
    )

    add_packing_items(
        "Medicine",
        "Salute & farmacia",
        [
            "Farmaci personali + prescrizioni",
            "Antidolorifici / antipiretici",
            "Antinfiammatori",
            "Cerotti normali + anti-vesciche",
            "Disinfettante gel/spray",
            "Garze sterili + benda elastica",
            "Antidiarroico + fermenti lattici",
            "Antistaminico",
            "Spray/crema punture insetti",
            "Collirio idratante",
            "Crema solare SPF 30/50",
            "Gel aloe vera / doposole",
            "Farmaci per mal d’auto / aereo",
        ],
    )

    add_packing_items(
        "Altro",
        "Road trip: documenti & auto",
        [
            "Patente + IDP + carta credito per noleggio",
            "Contratto noleggio + assicurazione",
            "Numeri utili: assistenza, noleggio, assicurazione",
            "Numeri del gruppo su carta",
        ],
    )
    add_packing_items(
        "Altro",
        "Road trip: accessori auto",
        [
            "Occhiali da sole a portata",
            "Caricabatterie auto USB",
            "Cavo lungo per sedile posteriore",
            "Sacchetti immondizia per auto",
            "Salviette / carta assorbente",
            "Mappa cartacea della zona",
        ],
    )
    add_packing_items(
        "Altro",
        "Road trip: comfort",
        [
            "Cuscino da viaggio per il collo",
            "Mascherina per dormire",
            "Tappi per orecchie",
            "Copertina leggera / felpa extra in auto",
        ],
    )

    add_packing_items(
        "Altro",
        "Trekking & outdoor",
        [
            "Zainetto giornaliero 20-30L",
            "Borraccia grande (1–2L) o camelbak",
            "Bastoncini da trekking",
            "Snack energetici (barrette, frutta secca)",
            "Sacchetti ziplock per rifiuti/snack",
            "Torcia frontale o torcia piccola",
            "Coltellino multiuso (solo stiva)",
            "Sacchetti impermeabili / dry bag",
            "Coprizaino antipioggia",
            "Mini telo / asciugamano microfibra",
        ],
    )

    add_packing_items(
        "Altro",
        "Mare, lago & piscina",
        [
            "Costume/i extra",
            "Asciugamano microfibra",
            "Infradito / sandali",
            "Borsetta mare",
            "Custodia impermeabile smartphone",
            "Occhialini da nuoto",
            "Pareo o maglia UV",
        ],
    )

    add_packing_items(
        "Altro",
        "Cibo & bevande",
        [
            "Borracce riutilizzabili",
            "Snack dall’Italia",
            "Gomme da masticare / mentine",
            "Bustine sali minerali / elettroliti",
            "Caffè solubile o snack di casa",
        ],
    )

    add_packing_items(
        "Altro",
        "Organizzazione valigia",
        [
            "Cubi / organizer per valigia",
            "Sacchetti biancheria sporca",
            "Lucchetto per bagagli",
            "Bilancia pesa-valigia",
            "Borsa pieghevole per shopping",
        ],
    )

    add_packing_items(
        "Altro",
        "Varie utili",
        [
            "Penna + blocco appunti",
            "Copia cartacea itinerario e indirizzi hotel",
            "Riepilogo prenotazioni stampato",
            "Kit da cucito (ago, filo, bottone)",
            "Nastro adesivo / duct tape",
            "Elastici, fascette, moschettoni",
            "Occhiali da vista di scorta",
            "Lenti a contatto + liquido + portalenti",
        ],
    )

    add_packing_items(
        "Altro",
        "App & digitale",
        [
            "Google Maps con mappe offline",
            "App Booking / Airbnb / compagnie",
            "App noleggio auto",
            "Revolut / Wise / altre app pagamento",
            "App meteo aggiornata",
            "Google Translate o app traduzione",
            "Cartella condivisa con documenti",
            "Lista numeri emergenza digitale",
        ],
    )

    packing_df = pd.DataFrame(
        packing_rows,
        columns=[
            "Oggetto",
            "Categoria",
            "Per chi",
            "Stato",
            "Note",
            *PACKING_CHECKBOX_COLUMNS,
        ],
    )

    # -----------------------------
    # 4) SALVATAGGIO SU SQLITE (MERGE INTELLIGENTE)
    # -----------------------------

    # ITINERARY: merge su "Giorno" o "Data"
    itinerary_columns = list(itinerary_df.columns)
    existing_itinerary = load_table("itinerary", itinerary_columns)
    
    # ✅ INVERTI LA LOGICA: se la tabella ESISTE, fai il merge
    if not existing_itinerary.empty:
        merged_itinerary = itinerary_df.copy()
        for _, row in existing_itinerary.iterrows():
            giorno = row.get("Giorno")
            data = row.get("Data")
            mask = (merged_itinerary["Giorno"] == giorno) | (merged_itinerary["Data"] == data)
            if mask.any():
                existing_idx = mask.idxmax()
                for col in merged_itinerary.columns:
                    if pd.isna(merged_itinerary.at[existing_idx, col]) and pd.notna(row.get(col)):
                        merged_itinerary.at[existing_idx, col] = row[col]
            else:
                merged_itinerary = pd.concat(
                    [merged_itinerary, row.to_frame().T],
                    ignore_index=True,
                )
        itinerary_df = merged_itinerary
    # ✅ Se existing_itinerary.empty == True, itinerary_df rimane con i dati iniziali

    # BOOKINGS: stessa logica
    bookings_columns = list(bookings_df.columns)
    existing_bookings = load_table("bookings", bookings_columns)
    
    if not existing_bookings.empty:
        merged_bookings = bookings_df.copy()
        for _, row in existing_bookings.iterrows():
            nome = row.get("Nome")
            check_in = row.get("Check_in")
            mask = (merged_bookings["Nome"] == nome) & (merged_bookings["Check_in"] == check_in)
            if mask.any():
                existing_idx = mask.idxmax()
                for col in merged_bookings.columns:
                    if pd.isna(merged_bookings.at[existing_idx, col]) and pd.notna(row.get(col)):
                        merged_bookings.at[existing_idx, col] = row[col]
            else:
                merged_bookings = pd.concat(
                    [merged_bookings, row.to_frame().T],
                    ignore_index=True,
                )
        bookings_df = merged_bookings

    # LOCATIONS: stessa logica
    locations_columns = [
        "Nome luogo", "Data", "Latitudine", "Longitudine", "Tipo", "Note", "Maps URL"
    ]
    existing_locations = load_table("locations", locations_columns)
    
    if not existing_locations.empty:
        existing_locations = ensure_columns(existing_locations, locations_columns)
        locations_df = ensure_columns(locations_df, locations_columns)
        
        merged_locations = existing_locations.copy()
        for _, new_row in locations_df.iterrows():
            nome_luogo = new_row.get("Nome luogo")
            if pd.isna(nome_luogo) or nome_luogo == "":
                continue
            mask = merged_locations["Nome luogo"] == nome_luogo
            if mask.any():
                existing_idx = mask.idxmax()
                # PRESERVA coordinate esistenti
                if pd.isna(merged_locations.at[existing_idx, "Maps URL"]) or str(merged_locations.at[existing_idx, "Maps URL"]).strip() == "":
                    if pd.notna(new_row.get("Maps URL")) and str(new_row["Maps URL"]).strip() != "":
                        merged_locations.at[existing_idx, "Maps URL"] = new_row["Maps URL"]
                if pd.isna(merged_locations.at[existing_idx, "Tipo"]) or str(merged_locations.at[existing_idx, "Tipo"]).strip() == "":
                    if pd.notna(new_row.get("Tipo")) and str(new_row["Tipo"]).strip() != "":
                        merged_locations.at[existing_idx, "Tipo"] = new_row["Tipo"]
                if pd.isna(merged_locations.at[existing_idx, "Note"]) or str(merged_locations.at[existing_idx, "Note"]).strip() == "":
                    if pd.notna(new_row.get("Note")) and str(new_row["Note"]).strip() != "":
                        merged_locations.at[existing_idx, "Note"] = new_row["Note"]
                if pd.isna(merged_locations.at[existing_idx, "Data"]):
                    if pd.notna(new_row.get("Data")):
                        merged_locations.at[existing_idx, "Data"] = new_row["Data"]
            else:
                merged_locations = pd.concat(
                    [merged_locations, new_row.to_frame().T],
                    ignore_index=True,
                )
        locations_df = merged_locations

    # PACKING: stessa logica
    packing_columns = [
        "Oggetto", "Categoria", "Per chi", "Stato", "Note", *PACKING_CHECKBOX_COLUMNS
    ]
    existing_packing = load_table("packing", packing_columns)
    
    if not existing_packing.empty:
        existing_packing = ensure_columns(existing_packing, packing_columns)
        packing_df = ensure_columns(packing_df, packing_columns)
        
        merged_packing = existing_packing.copy()
        for _, new_row in packing_df.iterrows():
            oggetto = new_row.get("Oggetto")
            categoria = new_row.get("Categoria")
            if pd.isna(oggetto) or oggetto == "":
                continue
            mask = (merged_packing["Oggetto"] == oggetto) & (merged_packing["Categoria"] == categoria)
            if mask.any():
                existing_idx = mask.idxmax()
                # PRESERVA stato e checkbox esistenti
                for col in ["Per chi", "Note"]:
                    if pd.isna(merged_packing.at[existing_idx, col]) or str(merged_packing.at[existing_idx, col]).strip() == "":
                        if pd.notna(new_row.get(col)) and str(new_row[col]).strip() != "":
                            merged_packing.at[existing_idx, col] = new_row[col]
            else:
                merged_packing = pd.concat(
                    [merged_packing, new_row.to_frame().T],
                    ignore_index=True,
                )
        packing_df = merged_packing

    # Salva tutto
    save_table(itinerary_df, "itinerary")
    save_table(bookings_df, "bookings")
    save_table(locations_df, "locations")
    save_table(packing_df, "packing")
    
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

def get_reminders(todo_df: pd.DataFrame, expenses_df: pd.DataFrame, days_ahead=7):
    """
    Restituisce una lista di reminder gratuiti (notifiche in-app) per:
    - To-do in scadenza
    - Spese da registrare
    Nessuna API esterna richiesta, tutto gratuito!
    """
    reminders = []
    today = date.today()
    
    # Reminder per To-do in scadenza
    if todo_df is not None and not todo_df.empty and "Scadenza" in todo_df.columns:
        todo_df_copy = todo_df.copy()
        todo_df_copy["Scadenza"] = pd.to_datetime(todo_df_copy["Scadenza"], errors="coerce")
        todo_df_copy = todo_df_copy[todo_df_copy["Scadenza"].notna()]
        
        # To-do non completati con scadenza nei prossimi N giorni
        upcoming = todo_df_copy[
            (todo_df_copy["Scadenza"].dt.date >= today) &
            (todo_df_copy["Scadenza"].dt.date <= (today + pd.Timedelta(days=days_ahead))) &
            (todo_df_copy.get("Stato", "").astype(str).str.lower().isin(["da fare", "in corso", ""]))
        ]
        
        for idx, row in upcoming.iterrows():
            scadenza = row["Scadenza"].date()
            giorni_rimasti = (scadenza - today).days
            task = row.get("Task", "Task senza nome")
            assegnato = row.get("Assegnato a", "Nessuno")
            
            if giorni_rimasti == 0:
                reminders.append({
                    "type": "urgent",
                    "icon": "🔴",
                    "title": f"SCADENZA OGGI: {task}",
                    "message": f"Assigned to: {assegnato}",
                    "action": "Vai a To-do pre-viaggio"
                })
            elif giorni_rimasti <= 2:
                reminders.append({
                    "type": "warning",
                    "icon": "⚠️",
                    "title": f"Scade tra {giorni_rimasti} giorni: {task}",
                    "message": f"Scadenza: {scadenza.strftime('%d/%m/%Y')} - Assigned to: {assegnato}",
                    "action": "Vai a To-do pre-viaggio"
                })
            else:
                reminders.append({
                    "type": "info",
                    "icon": "📅",
                    "title": f"Scade tra {giorni_rimasti} giorni: {task}",
                    "message": f"Scadenza: {scadenza.strftime('%d/%m/%Y')} - Assigned to: {assegnato}",
                    "action": "Vai a To-do pre-viaggio"
                })
    
    # Reminder per packing list (oggetti da preparare)
    # Questo lo aggiungiamo se necessario
    
    return reminders

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


@st.cache_resource
def get_engine():
    """
    Restituisce un engine SQLAlchemy.
    - Se esiste st.secrets["DB_URL"] -> usa Postgres Neon (cloud).
    - Altrimenti fallback su SQLite locale (utile per test in locale).
    """
    db_url = st.secrets.get("DB_URL", None)
    if db_url:
        # Esempio: postgresql+psycopg2://user:pass@host:5432/dbname?sslmode=require
        return sqlalchemy.create_engine(db_url, pool_pre_ping=True)
    else:
        # Fallback: file SQLite locale
        return sqlalchemy.create_engine(f"sqlite:///{DB_PATH}")

def get_conn():
    """
    Restituisce una connessione SQLAlchemy.
    Compatibile con:
    - pd.read_sql(..., conn)
    - df.to_sql(..., conn, ...)
    - conn.execute("...")
    """
    return get_engine().connect()

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

def _save_df_to_db(conn, table_name, df):
    """
    Salva un DataFrame in una tabella del DB usando solo SQLAlchemy Core,
    evitando pandas.to_sql (compatibile con Postgres/Neon e SQLite).
    Tutte le colonne vengono create come TEXT; i valori vengono convertiti in stringa.
    """
    if df is None:
        return

    # Copia per sicurezza, così non modifichiamo il DF originale
    df = df.copy()

    # Anche se vuoto, usiamo comunque le colonne per definire la tabella
    cols = list(df.columns)
    if not cols:
        # Nessuna colonna -> niente da salvare
        return

    # Droppa e ricrea la tabella
    col_defs = ", ".join(f'"{c}" TEXT' for c in cols)
    conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    conn.execute(text(f"CREATE TABLE {table_name} ({col_defs})"))

    if df.empty:
        # Tabella vuota ma struttura pronta
        return

    # Costruisci la INSERT parametrizzata
    col_list = ", ".join(f'"{c}"' for c in cols)
    placeholders = ", ".join(f":c{i}" for i in range(len(cols)))
    insert_sql = text(f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})")

    # Prepara i parametri per ogni riga
    rows = []
    for _, row in df.iterrows():
        params = {}
        for i, value in enumerate(row):
            if pd.isna(value):
                params[f"c{i}"] = None
            else:
                params[f"c{i}"] = str(value)
        rows.append(params)

    # Esegui in modalità "executemany"
    conn.execute(insert_sql, rows)


def save_table(df, table_name):
    """Salva un DataFrame nel DB (sostituendo la tabella)."""
    engine = get_engine()
    with engine.begin() as conn:
        _save_df_to_db(conn, table_name, df)

def init_info_table():
    """Crea la tabella info se non esiste (compatibile con SQLite e Postgres/Neon)."""
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS info (
                        key   TEXT PRIMARY KEY,
                        value TEXT
                    )
                    """
                )
            )
            # Il context manager gestisce commit/rollback in modo automatico
    except SQLAlchemyError as e:
        # Se il DB non è raggiungibile o la CREATE fallisce, non blocchiamo l'app.
        # Puoi loggare se vuoi:
        # st.write("Errore init_info_table:", e)
        pass


def set_info(key, value):
    """Salva una coppia chiave/valore (stringa) nella tabella info."""
    init_info_table()
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO info (key, value)
                    VALUES (:key, :value)
                    ON CONFLICT (key) DO UPDATE
                    SET value = EXCLUDED.value
                    """
                ),
                {"key": key, "value": value},
            )
    except SQLAlchemyError as e:
        # st.write("Errore set_info:", e)
        pass


def get_info(key, default=None):
    """
    Recupera una stringa dalla tabella info; se non esiste o
    c'è un errore di DB, restituisce default.
    """
    init_info_table()
    try:
        with get_conn() as conn:
            result = conn.execute(
                text("SELECT value FROM info WHERE key = :key"),
                {"key": key},
            )
            value = result.scalar()
            if value is None:
                return default
            return value
    except SQLAlchemyError as e:
        # st.write("Errore get_info:", e)
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
    """Salva la lista dei viaggiatori nella tabella info."""
    set_info("travellers", json.dumps(travellers_list))


# ------------------------
# INIZIALIZZAZIONE STATO
# ------------------------
def init_state(force_reload=False):
    # Viaggiatori
    if force_reload or "travellers" not in st.session_state:
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
    if force_reload or "itinerary" not in st.session_state:
        df_it = load_table("itinerary", itinerary_columns)
        df_it = ensure_columns(df_it, itinerary_columns)
        st.session_state.itinerary = drop_empty_rows(df_it)

    # Schedule (ora per ora) - opzionale
    schedule_columns = ["Data", "Ora", "Descrizione"]
    if force_reload or "schedule" not in st.session_state:
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
    if force_reload or "expenses" not in st.session_state:
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
    if force_reload or "locations" not in st.session_state:
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
    if force_reload or "places_info" not in st.session_state:
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
    if force_reload or "todo" not in st.session_state:
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
        *PACKING_CHECKBOX_COLUMNS,
    ]
    if force_reload or "packing" not in st.session_state:
        df_pack = load_table("packing", packing_columns)
        df_pack = ensure_columns(df_pack, packing_columns)
        for col in PACKING_CHECKBOX_COLUMNS:
            df_pack[col] = df_pack[col].fillna(False).astype(bool)
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


def format_euro(amount: float, default="€ 0") -> str:
    """Formatta un importo in EUR in modo compatto."""
    try:
        if amount is None or pd.isna(amount):
            return default
        formatted = f"{amount:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"€ {formatted}"
    except Exception:
        return default


def format_km(value, default="—"):
    try:
        if value is None or pd.isna(value):
            return default
        return f"{int(round(value)):,} km".replace(",", ".")
    except Exception:
        return default


def get_next_itinerary_entry(itinerary_df: pd.DataFrame):
    """Restituisce la prossima tappa futura (o l'ultima disponibile) con i dettagli principali."""
    if itinerary_df is None or itinerary_df.empty:
        return None

    df = itinerary_df.copy()
    df["__date"] = pd.to_datetime(df.get("Data"), errors="coerce")
    df = df[df["__date"].notna()]
    if df.empty:
        return None

    today_ts = pd.Timestamp(date.today())
    upcoming = df[df["__date"] >= today_ts].sort_values("__date", kind="mergesort")
    if upcoming.empty:
        upcoming = df.sort_values("__date", kind="mergesort")

    row = upcoming.iloc[0]
    distance = pd.to_numeric(row.get("Distanza prevista (km)"), errors="coerce")

    return {
        "giorno": row.get("Giorno"),
        "data": row["__date"].date(),
        "data_label": row["__date"].strftime("%d/%m/%Y"),
        "tipo": row.get("Tipo giorno") or row.get("Tipo"),
        "tappa": row.get("Tappa principale") or row.get("Tappa"),
        "pernottamento": row.get("Pernottamento"),
        "note": row.get("Attività principali / note") or row.get("Note"),
        "distanza_label": f"{int(distance):,} km".replace(",", ".") if pd.notna(distance) else None,
    }


def get_top_todo_items(todo_df: pd.DataFrame, limit: int = 3):
    """Restituisce i prossimi task (Da fare / In corso) ordinati per scadenza."""
    if todo_df is None or todo_df.empty or "Stato" not in todo_df.columns:
        return []

    df = todo_df.copy()
    df["__deadline"] = pd.to_datetime(df.get("Scadenza"), errors="coerce")
    mask = df["Stato"].astype(str).isin(["Da fare", "In corso"])
    df = df[mask]
    if df.empty:
        return []

    df = df.sort_values(["__deadline", "Task"], ascending=[True, True], kind="mergesort").head(limit)
    tasks = []
    for _, row in df.iterrows():
        deadline = row["__deadline"]
        tasks.append(
            {
                "Task": row.get("Task", "Task"),
                "Scadenza": deadline.strftime("%d/%m") if pd.notna(deadline) else "Senza data",
                "Assegnato a": row.get("Assegnato a", "—"),
                "Stato": row.get("Stato", ""),
                "Note": row.get("Note", ""),
            }
        )
    return tasks


def get_recent_expenses(expenses_df: pd.DataFrame, limit: int = 3):
    """Ritorna le ultime spese registrate ordinate per data."""
    if expenses_df is None or expenses_df.empty or "Importo in EUR" not in expenses_df.columns:
        return []

    df = expenses_df.copy()
    df["__date"] = pd.to_datetime(df.get("Data"), errors="coerce")
    df = df.sort_values(["__date"], ascending=[False], kind="mergesort").head(limit)

    items = []
    for _, row in df.iterrows():
        items.append(
            {
                "Categoria": row.get("Categoria", "Spesa"),
                "Descrizione": row.get("Descrizione", ""),
                "Data": row["__date"].strftime("%d/%m") if pd.notna(row["__date"]) else "—",
                "Importo": row.get("Importo in EUR"),
                "Pagato da": row.get("Pagato da", "—"),
            }
        )
    return items


# ------------------------
# SIDEBAR: IMPOSTAZIONI
# ------------------------
page = st.sidebar.radio(
    "Sezioni",
    (
        "Home",
        "Itinerario",
        "Mappa",
        "Info luoghi",
        "Info utili",
        "Packing list",
        "To-do pre-viaggio",
        "Spese & Budget",
        "Dashboard",
    ),
)

st.sidebar.header("⚙️ Impostazioni")

read_only = st.sidebar.checkbox(
    "Modalità sola lettura (blocca modifiche)",
    value=False,
    help="Quando attiva, nessuno può modificare i dati: si può solo consultare.",
)

st.sidebar.title("⚙️ Amministrazione database")

if st.sidebar.button("Inizializza viaggio (popola DB)"):
    initialize_database(DB_PATH)
    init_state(force_reload=True)
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


# ------------------------
# PAGINA: HOME MOBILE
# ------------------------
if page == "Home":
    st.header("📱 Dashboard veloce")
    st.caption("Panoramica pensata per la visualizzazione su smartphone.")

    travellers = st.session_state.travellers
    itinerary_df = st.session_state.itinerary.copy()
    expenses_df = st.session_state.expenses.copy()
    todo_df = st.session_state.todo.copy()

    total_km, avg_km, hotel_changes, _ = compute_itinerary_stats(itinerary_df)

    total_expenses = (
        expenses_df["Importo in EUR"].fillna(0).sum()
        if "Importo in EUR" in expenses_df.columns
        else 0.0
    )
    open_tasks_df = (
        todo_df[todo_df["Stato"].isin(["Da fare", "In corso"])]
        if "Stato" in todo_df.columns and not todo_df.empty
        else pd.DataFrame(columns=todo_df.columns)
    )
    open_tasks_count = len(open_tasks_df)

    # Reminder gratuiti (notifiche in-app)
    reminders = get_reminders(todo_df, expenses_df, days_ahead=7)
    if reminders:
        st.markdown("---")
        st.subheader("🔔 Reminder e notifiche")
        for rem in reminders:
            if rem["type"] == "urgent":
                st.error(f"{rem['icon']} **{rem['title']}**\n\n{rem['message']}")
            elif rem["type"] == "warning":
                st.warning(f"{rem['icon']} **{rem['title']}**\n\n{rem['message']}")
            else:
                st.info(f"{rem['icon']} **{rem['title']}**\n\n{rem['message']}")
        st.divider()

    col_home1, col_home2, col_home3 = st.columns(3)
    with col_home1:
        st.metric("Giorni pianificati", len(itinerary_df) or 0)
    with col_home2:
        st.metric("Spese registrate", format_euro(total_expenses))
    with col_home3:
        st.metric("Task aperti", open_tasks_count)

    st.divider()

    next_leg = get_next_itinerary_entry(itinerary_df)
    st.subheader("🎯 Prossima tappa")
    if next_leg:
        giorno_value = next_leg.get("giorno")
        if pd.notna(giorno_value):
            header = f"Giorno {int(giorno_value)} • {next_leg['data_label']}"
        else:
            header = next_leg["data_label"]

        st.markdown(f"**{header}**")
        st.write(next_leg.get("tappa", "—"))

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.caption(f"Tipo giorno: {next_leg.get('tipo', '—')}")
            if next_leg.get("distanza_label"):
                st.caption(f"Distanza prevista: {next_leg['distanza_label']}")
        with info_col2:
            pern = next_leg.get("pernottamento")
            st.caption(f"Pernotto: {pern or '—'}")

        if next_leg.get("note"):
            st.write(next_leg["note"])
    else:
        st.info("Compila l'itinerario per vedere la prossima tappa.")

    st.divider()

    col_cards1, col_cards2 = st.columns(2)

    with col_cards1:
        st.subheader("✅ Task prioritari")
        top_tasks = get_top_todo_items(todo_df)
        if not top_tasks:
            st.caption("Nessun task urgente. Buon lavoro!")
        else:
            for task in top_tasks:
                st.markdown(
                    f"**{task['Task']}** · {task['Scadenza']} ({task['Assegnato a']})"
                )
                if task["Note"]:
                    st.caption(task["Note"])

    with col_cards2:
        st.subheader("💳 Spese recenti")
        recent_expenses = get_recent_expenses(expenses_df)
        if not recent_expenses:
            st.caption("Aggiungi la prima spesa per popolare questo box.")
        else:
            for exp in recent_expenses:
                st.markdown(
                    f"**{format_euro(exp['Importo'])}** · {exp['Categoria']} • {exp['Data']}"
                )
                desc = exp.get("Descrizione") or "—"
                st.caption(f"{desc} — pagato da {exp.get('Pagato da', '—')}")

    st.divider()

    st.subheader("📌 Statistiche lampo")
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric("Km totali", format_km(total_km))
    with stat_col2:
        st.metric("Km medi/giorno", format_km(avg_km))
    with stat_col3:
        st.metric("Cambi hotel", hotel_changes if hotel_changes is not None else "—")

    st.caption("Apri le sezioni dettagliate dal menu laterale per modificare i dati.")

# ------------------------
# PAGINA: ITINERARIO
# ------------------------
elif page == "Itinerario":
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

            # Filtri per tipo di luogo
            st.markdown("#### Filtri mappa")
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                filter_types = st.multiselect(
                    "Filtra per tipo",
                    options=["Hotel", "Parco", "Città", "Viewpoint", "Altro"],
                    default=["Hotel", "Parco", "Città", "Viewpoint", "Altro"],
                    key="map_type_filter",
                )
            with col_filter2:
                show_current_only = st.checkbox(
                    "Mostra solo tappa corrente (oggi)",
                    value=False,
                    key="map_current_filter",
                )
            
            # Applica filtri
            if filter_types:
                map_df = map_df[map_df["Tipo"].isin(filter_types)]
            
            # Filtro tappa corrente (se richiesto)
            if show_current_only:
                today = date.today()
                if "Data" in map_df.columns:
                    # Converti Data in date per il confronto
                    map_df["Data_parsed"] = pd.to_datetime(map_df["Data"], errors="coerce").dt.date
                    map_df = map_df[map_df["Data_parsed"] == today]
                    map_df = map_df.drop(columns=["Data_parsed"])
            
            if map_df.empty:
                st.info("Nessun punto corrisponde ai filtri selezionati.")
                st.stop()

            # Evidenzia tappa corrente (oggi)
            today = date.today()
            today_str = today.strftime("%Y-%m-%d")
            if "Data" in map_df.columns:
                map_df["is_current"] = map_df["Data"].astype(str) == today_str
            else:
                map_df["is_current"] = False
            
            # Ordiniamo i punti in base a Data (se presente) per costruire il "percorso"
            ordered = map_df.copy()
            if "Data" in ordered.columns:
                ordered = ordered.sort_values("Data", kind="mergesort")
            ordered = ordered.reset_index(drop=True)

            # Costruiamo i segmenti usando Mapbox Directions (se possibile)
            segments = []
            route_paths = []  # per PathLayer
            total_distance = 0.0
            total_time = 0.0

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

                total_distance += dist_km
                total_time += time_h

                route_paths.append(
                    {
                        "path": coords,
                        "width": 1500,
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
            
            # Statistiche totali
            if len(segments) > 0:
                st.markdown("#### 📊 Statistiche viaggio")
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Distanza totale", f"{round(total_distance, 1)} km")
                with col_stat2:
                    st.metric("Tempo totale stimato", f"{round(total_time, 1)} ore")
                with col_stat3:
                    st.metric("Numero tappe", len(map_df))

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
                # Evidenzia tappa corrente con pin più grande
                is_current = row.get("is_current", False)
                size_multiplier = 1.5 if is_current else 1.0
                return {
                    "url": icon_url,  # URL dell'immagine del pin
                    "width": int(128 * size_multiplier),
                    "height": int(128 * size_multiplier),
                    "anchorY": int(128 * size_multiplier),  # punta in basso
                }

            map_df["icon_data"] = map_df.apply(build_icon_data, axis=1)

            # Layer dei segnalini (IconLayer)
            # Evidenzia tappa corrente con dimensione maggiore
            def get_size(row):
                return 6 if row.get("is_current", False) else 4
            
            map_df["icon_size"] = map_df.apply(get_size, axis=1)
            
            icon_layer = pdk.Layer(
                "IconLayer",
                data=map_df,
                get_icon="icon_data",
                get_position="[Longitudine, Latitudine]",
                get_size="icon_size",
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

            # Prepara tooltip ricchi con link Maps URL
            def build_tooltip_html(row):
                nome = str(row.get("Nome luogo", "—"))
                tipo = str(row.get("Tipo", "—"))
                data = str(row.get("Data", "—")) if pd.notna(row.get("Data")) else "—"
                note = str(row.get("Note", "—")) if pd.notna(row.get("Note")) else "—"
                maps_url = str(row.get("Maps URL", "")) if pd.notna(row.get("Maps URL")) else ""
                is_current = row.get("is_current", False)
                
                html = f"<div style='padding: 8px;'>"
                if is_current:
                    html += f"<b style='color: #ff4444; font-size: 14px;'>📍 {nome} (OGGI)</b><br/>"
                else:
                    html += f"<b style='font-size: 14px;'>{nome}</b><br/>"
                html += f"<span style='color: #666;'>Tipo:</span> {tipo}<br/>"
                if data != "—":
                    html += f"<span style='color: #666;'>Data:</span> {data}<br/>"
                if note != "—" and note.strip():
                    html += f"<span style='color: #666;'>Note:</span> {note[:50]}{'...' if len(note) > 50 else ''}<br/>"
                if maps_url and maps_url.strip():
                    html += f"<a href='{maps_url}' target='_blank' style='color: #0066cc; text-decoration: none;'>🗺️ Apri in Google Maps</a>"
                html += "</div>"
                return html
            
            # pydeck richiede una colonna con HTML per il tooltip personalizzato
            # Usiamo un approccio più semplice: tooltip base con info essenziali
            tooltip = {
                "html": "<b>{Nome luogo}</b><br/>Tipo: {Tipo}<br/>Data: {Data}<br/>{Note}",
                "style": {"backgroundColor": "white", "color": "black", "fontSize": "12px"},
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
            
            # Mostra link Maps URL in modo più visibile
            st.markdown("---")
            st.subheader("🔗 Link rapidi Google Maps")
            maps_links_df = map_df[["Nome luogo", "Maps URL", "Tipo", "Data"]].copy()
            maps_links_df = maps_links_df[maps_links_df["Maps URL"].notna()]
            maps_links_df = maps_links_df[maps_links_df["Maps URL"].astype(str).str.strip() != ""]
            
            if not maps_links_df.empty:
                for idx, row in maps_links_df.iterrows():
                    nome = row["Nome luogo"]
                    url = row["Maps URL"]
                    tipo = row.get("Tipo", "—")
                    data = row.get("Data", "—")
                    is_current = row.get("is_current", False)
                    
                    col_link1, col_link2 = st.columns([3, 1])
                    with col_link1:
                        current_badge = " 🔴 **OGGI**" if is_current else ""
                        st.markdown(f"**{nome}** ({tipo}){current_badge}")
                    with col_link2:
                        st.markdown(f"[🗺️ Apri Maps]({url})")
                st.caption("Clicca sui link per aprire la posizione in Google Maps.")
            else:
                st.info("Aggiungi Maps URL ai luoghi per vedere i link rapidi qui.")
            
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
        traveller_names = st.session_state.travellers[:MAX_TRAVELLERS]
        checkbox_columns_config = {}
        for idx, traveller in enumerate(traveller_names):
            col_name = PACKING_CHECKBOX_COLUMNS[idx]
            checkbox_columns_config[col_name] = st.column_config.CheckboxColumn(
                f"{traveller} ha preso?",
                help=f"Segna se {traveller} ha già questo oggetto in valigia.",
                default=False,
            )

        per_chi_options = ["Tutti"] + traveller_names

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
                    options=per_chi_options,
                ),
                "Stato": st.column_config.SelectboxColumn(
                    "Stato",
                    options=["Da comprare", "Da preparare", "In valigia", "Già sul posto"],
                ),
                "Note": st.column_config.TextColumn("Note"),
                **checkbox_columns_config,
            },
        )

        if st.button("💾 Salva packing list"):
            for col in PACKING_CHECKBOX_COLUMNS:
                if col not in edited_pack.columns:
                    edited_pack[col] = False
            edited_pack[PACKING_CHECKBOX_COLUMNS] = edited_pack[PACKING_CHECKBOX_COLUMNS].fillna(False).astype(bool)
            cleaned = drop_empty_rows(edited_pack)
            cleaned = cleaned[cleaned["Oggetto"].notna()]
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
