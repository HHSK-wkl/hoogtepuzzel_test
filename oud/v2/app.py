# app.py
import streamlit as st
import model

st.set_page_config(page_title="Hoogte- en Ruimtepuzzel", layout="wide")

st.title("Hoogte- en Ruimtepuzzel Bleizo")

# --- 1. Neerslagscenario & afvoer ---
st.header("Neerslagscenario en afvoer")

scenario_opties = {
    "KNMI'24 - 2100H (48 uur)": {"mm": 142.6, "uren": 48},
    "KNMI'24 - 2100H (24 uur)": {"mm": 133.0, "uren": 24},
    "Limburgbui (48 uur)": {"mm": 200.0, "uren": 48},
    "KNMI'24 - 2150H (48 uur)": {"mm": 153.0, "uren": 48},
}

scenario_naam = st.selectbox("Neerslagscenario", list(scenario_opties.keys()))
neerslag_mm = scenario_opties[scenario_naam]["mm"]
scenario_uren = scenario_opties[scenario_naam]["uren"]

afvoeren_ja_nee = st.selectbox("Afvoeren", ["nee", "ja"])
afvoeren = afvoeren_ja_nee == "ja"

# Correctie: 18 mm per 24 uur
correctie_mm = 18 * (scenario_uren / 24) if afvoeren else 0

neerslag_mm_corr = neerslag_mm - correctie_mm

if afvoeren:
    st.info(f"Gemaalcapaciteit: {correctie_mm:.1f} mm Resterend volume: {neerslag_mm_corr:.1f} mm")
else:
    st.info(f"Neerslagvolume: {neerslag_mm_corr:.1f} mm")

# --- 2. Inrichting / hoogtes ---
st.header("Inrichting en hoogtes")

col1, col2, col3 = st.columns(3)

with col1:
    flex_boven = st.number_input("Flexibel peil bovenkant (m NAP)", value=-5.8, step=0.1)
    flex_onder = st.number_input("Flexibel peil onderkant (m NAP)", value=-6.2, step=0.1)

with col2:
    vloerpeil = st.number_input("Vloerpeil (m NAP)", value=-4.5, step=0.1)
    hoogte_weg = st.number_input("Hoogte as weg (m NAP)", value=-5.3, step=0.1)
    hoogte_groen = st.number_input("Hoogte groen (m NAP)", value=-5.3, step=0.1)

with col3:
    hoogte_droge_berging = st.number_input("Hoogte droge berging (m NAP, leeg = geen)", value=-5.3, step=0.1)
    max_peilstijging = st.number_input("Maximale peilstijging (m)", value=0.8, step=0.05)
    peilstijging_droge_berging = st.number_input("Peilstijging droge berging (m)", value=0.0, step=0.05)

# eenvoudige validaties
if vloerpeil < flex_boven or hoogte_weg < flex_boven or hoogte_groen < flex_boven:
    st.warning("Let op: vloerpeil, weg en groen mogen niet lager zijn dan de bovenkant bandbreedte.")

# --- 3. Oppervlakken en percentages ---
st.header("Oppervlak en gebruik")

col4, col5 = st.columns(2)

with col4:
    opp_ha = st.number_input("Oppervlak plangebied (ha)", value=36.4, step=0.1)
    open_water_pct = st.number_input("Open water (%)", value=5.0, step=0.5) / 100
    verhard_pct = st.number_input("Verhard (%)", value=57.0, step=0.5) / 100
    droge_berging_pct = st.number_input("Droge berging (onverhard) (%)", value=15.0, step=0.5) / 100
    
    # Automatisch berekend onverhard
    onverhard_rest_pct = 1 - (open_water_pct + verhard_pct + droge_berging_pct)
    onverhard_rest_pct = max(0, onverhard_rest_pct)

    st.text_input(
        "Overig onverhard (%)",
        value=f"{onverhard_rest_pct * 100:.1f}",
        disabled=True)

    # Waarschuwing bij overschrijding
    totaal_pct = open_water_pct + verhard_pct + droge_berging_pct
    if totaal_pct > 1:
        st.error(
            f"Let op: het totaal van open water, verhard en droge berging is {totaal_pct*100:.1f}%. "
            "Dit mag niet boven 100% uitkomen."
        )

with col5:
    pct_natuurvriendelijk = st.number_input("Percentage natuurvriendelijk talud (%)", value=50.0, step=5.0) / 100
    talud_nvo = st.number_input("Talud natuurvriendelijk (1:x)", value=3.0, step=0.5)
    talud_normaal = st.number_input("Talud normaal (1:x)", value=2.0, step=0.5)
    beheer_vanaf_kant_pct = st.number_input("Beheer vanaf kant (%)", value=100.0, step=5.0) / 100
    breedte_onderhoud = st.number_input("Breedte onderhoudsstrook (m)", value=5.0, step=0.5)
    breedte_waterloop = st.number_input("Aanname breedte waterloop (m)", value=8.0, step=0.5)
    porien_volume = st.number_input("Poriënvolume (-)", value=0.28, step=0.01)


# --- 4. Berekeningen ---
if st.button("Bereken en visualiseer"):
    resultaten = model.bereken_ruimtepuzzel(
        neerslag_mm=neerslag_mm_corr,
        afvoeren=afvoeren,
        flex_boven=flex_boven,
        flex_onder=flex_onder,
        vloerpeil=vloerpeil,
        hoogte_weg=hoogte_weg,
        hoogte_groen=hoogte_groen,
        hoogte_droge_berging=hoogte_droge_berging,
        max_peilstijging=max_peilstijging,
        peilstijging_droge_berging=peilstijging_droge_berging,
        opp_ha=opp_ha,
        open_water_pct=open_water_pct,
        verhard_pct=verhard_pct,
        droge_berging_pct=droge_berging_pct,
        pct_natuurvriendelijk=pct_natuurvriendelijk,
        talud_nvo=talud_nvo,
        talud_normaal=talud_normaal,
        beheer_vanaf_kant_pct=beheer_vanaf_kant_pct,
        breedte_onderhoud=breedte_onderhoud,
        breedte_waterloop=breedte_waterloop,
        porien_volume=porien_volume,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Dwarsprofiel")
        fig_profiel = model.plot_profiel(resultaten["profiel_params"])
        st.pyplot(fig_profiel)

    with col_b:
        st.subheader("Ruimtebeslag")
        fig_ruimte = model.plot_ruimtebeslag(resultaten["ruimte"])
        st.pyplot(fig_ruimte)

    st.subheader("Kerncijfers")
    st.write({
    	"Berging oppervlaktewater (m³)": round(resultaten["berging_oppervlaktewater_m3"], 1),
    	"Berging taluds (m³ per m)": round(resultaten["berging_taluds_m3_per_m"], 1),
    	"Berging onverhard (m³)": round(resultaten["berging_onverhard_m3"], 1),
        "Berging bodem (mm)": round(resultaten["R3"], 1),
	"Tekort bodemberging (m3)": round(resultaten["S3"], 1),
    	"Totale berging (m³)": round(resultaten["totale_berging_m3"], 1),
    	"Benodigde berging (m³)": round(resultaten["benodigde_berging_m3"], 1),
        "Benodigde berging (mm)": round(resultaten["benodigde_berging_mm"], 1),
    	"Tekort / Overschot (m³)": round(resultaten["tekort_overschot_m3"], 1),
        "Tekort / Overschot (mm)": round(resultaten["tekort_overschot_mm"], 1),
    })

