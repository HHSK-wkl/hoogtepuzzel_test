# model.py
import numpy as np
import matplotlib.pyplot as plt

def bereken_ruimtepuzzel(
    neerslag_mm,
    afvoeren,
    flex_boven,
    flex_onder,
    vloerpeil,
    hoogte_weg,
    hoogte_groen,
    hoogte_droge_berging,
    max_peilstijging,
    peilstijging_droge_berging,
    opp_ha,
    open_water_pct,
    verhard_pct,
    droge_berging_pct,
    pct_natuurvriendelijk,
    talud_nvo,
    talud_normaal,
    beheer_vanaf_kant_pct,
    breedte_onderhoud,
    breedte_waterloop,
    porien_volume,          
):
    # 1. Basisoppervlakken
    opp_m2 = opp_ha * 10000
    opp_water = open_water_pct * opp_m2

    # 2. Correctie neerslag (C4)
    neerslag_corr_mm = neerslag_mm - (18 if afvoeren else 0)

    # 3. Bodemberging (S3)
    # R3 = R8 * C26 * 1000
    R3 = max_peilstijging * porien_volume * 1000
    S3 = max(0, neerslag_corr_mm - R3)

    # 4. Benodigde berging in mm (O3)
    benodigde_berging_mm = (open_water_pct + verhard_pct) * neerslag_corr_mm + S3

    # 5. Benodigde berging in m³
    benodigde_berging_m3 = benodigde_berging_mm / 1000 * opp_m2

    # 6. Beschikbare berging in oppervlaktewater (P3)
    lengte_watergang = (opp_water / breedte_waterloop) * 2

    talud_normaal_berg = lengte_watergang * max_peilstijging * talud_normaal / 2
    talud_nvo_berg = lengte_watergang * max_peilstijging * talud_nvo / 2

    berging_oppervlaktewater = (
        talud_normaal_berg * (1 - pct_natuurvriendelijk)
        + talud_nvo_berg * pct_natuurvriendelijk
        + opp_water * max_peilstijging
    )

    # 7. Beschikbare berging droge berging (Q3)
    berging_droge_berging = droge_berging_pct * 10000 * opp_ha * (max_peilstijging - peilstijging_droge_berging)

    # 8. Totale berging
    totale_berging = berging_oppervlaktewater + berging_droge_berging

    # 9. Tekort / overschot
    tekort_overschot = totale_berging - benodigde_berging_m3

    tekort_overschot_mm = (tekort_overschot * 1000)/ opp_m2

    # 10. Ruimtebeslag
    ruimte = {
        "open_water_m2": opp_water,
        "verhard_m2": verhard_pct * opp_m2,
        "droge_berging_m2": droge_berging_pct * opp_m2,
        "onverhard_overig_m2": max(
            opp_m2 - opp_water - verhard_pct * opp_m2 - droge_berging_pct * opp_m2, 0
        ),
    }

    resultaten = {
        "berging_oppervlaktewater_m3": berging_oppervlaktewater,
        "berging_taluds_m3_per_m": talud_normaal_berg + talud_nvo_berg,
        "berging_onverhard_m3": berging_droge_berging,
	"R3": R3,
        "totale_berging_m3": totale_berging,
        "benodigde_berging_m3": benodigde_berging_m3,
        "benodigde_berging_mm": benodigde_berging_mm,
        "tekort_overschot_m3": tekort_overschot,
        "tekort_overschot_mm": tekort_overschot_mm,
        "S3": S3,
        "ruimte": ruimte,
        "profiel_params": {
            "flex_boven": flex_boven,
            "flex_onder": flex_onder,
            "vloerpeil": vloerpeil,
            "hoogte_weg": hoogte_weg,
            "hoogte_groen": hoogte_groen,
            "hoogte_droge_berging": hoogte_droge_berging,
            "breedte_waterloop": breedte_waterloop,
            "breedte_onderhoud": breedte_onderhoud,
            "talud_normaal": talud_normaal,
            "talud_nvo": talud_nvo,
            "max_peilstijging" : max_peilstijging,
        },
    }

    return resultaten



# -------------------------------------------------------------
# De rest van je bestand (plot_profiel en plot_ruimtebeslag)
# blijft exact zoals je het had.
# -------------------------------------------------------------

def plot_profiel(params):
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    import matplotlib.image as mpimg

    # Helperfunctie voor iconen
    def draw_icon(ax, x, y, path, zoom=0.18):
        img = mpimg.imread(path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    # Parameters
    flex_boven = params["flex_boven"]
    flex_onder = params["flex_onder"]
    vloerpeil = params["vloerpeil"]
    hoogte_weg = params["hoogte_weg"]
    hoogte_groen = params["hoogte_groen"]
    hoogte_droge_berging = params["hoogte_droge_berging"]
    b_water = params["breedte_waterloop"]
    b_onderhoud = params["breedte_onderhoud"]
    talud_normaal = params["talud_normaal"]
    talud_nvo = params["talud_nvo"]
    max_peilstijging = params["max_peilstijging"]

    fig, ax = plt.subplots(figsize=(14, 6))

    # Taludbreedte Normaal
    dh = flex_boven - flex_onder
    talud_normaal_breedte = abs(dh) * talud_normaal
   
    # Taludbreedte NVO
    talud_nvo_breedte = abs(dh) * talud_nvo
    
    ax.plot(
    	[0, - talud_nvo_breedte],
    	[flex_onder, flex_boven,],
    	linestyle="--",
    	color="black",
    	linewidth=1.2
    )

    
    # Maximale peilstijging lijn
    peil_max = flex_boven + max_peilstijging

    ax.hlines(
       y=peil_max,
       xmin=-talud_normaal_breedte,
       xmax=b_water + talud_normaal_breedte,
       linestyles="dotted",
       colors="blue",
       linewidth=1.5
    )

    # Label bij de lijn
    ax.text(
       b_water + talud_normaal_breedte - 7.5,
       peil_max + 0.05,
       "Max. peilstijging",
       ha="left",
       va="bottom",
       fontsize=10,
       color="blue"
    )

    ax.text(
       b_water + talud_normaal_breedte - 4.0,
       peil_max + 0.05,
       f"{peil_max:.2f} mNAP",
       ha="left",
       va="bottom",
       fontsize=10,
       color="blue"
    )

    
    talud_nvo_breedte = abs(dh) * talud_nvo
    
    # label talud NVO toevoegen
    ax.text(
    	b_water + talud_nvo_breedte - 12,
    	(flex_boven + flex_onder) / 2 - 0.35,
    	f"Talud NVO 1:{round(talud_nvo)}",
    	ha="left",
    	va="center",
    	fontsize=10,
    	color="gray"
    )

    # Watergang
    ax.fill_between([0, b_water], flex_onder, flex_boven,
                    color="#9ecae1", alpha=0.8)

    # Taluds
    ax.add_patch(Polygon(
        [[-talud_normaal_breedte, flex_boven],
         [0, flex_onder],
         [0, flex_boven]],
        closed=True, color="#c7c7c7", alpha=0.8))

    # label Talud normaal toevoegen
    ax.text(
    	b_water + talud_normaal_breedte / 2 + 0.5,
    	(flex_boven + flex_onder) / 2 - 0.25,
    	f"Talud 1:{round(talud_normaal)}",
    	ha="center",
    	va="center",
    	fontsize=10,
    	color="black"
    	)

    
    ax.text(
    	b_water + talud_normaal_breedte - 6.5,
    	flex_boven + 0.10,
    	"Flex boven",
   	ha="left",
    	va="bottom",
    	fontsize=10
    )

    ax.text(
    	b_water + talud_normaal_breedte - 4.0,
    	flex_boven + 0.10,
    	f"{flex_boven:.2f} mNAP",
    	ha="left",
    	va="bottom",
    	fontsize=10,
    	
    )

    ax.text(
    	b_water + talud_normaal_breedte - 6.5,
    	flex_onder - 0.25,
    	"Flex onder",
   	ha="left",
    	va="bottom",
    	fontsize=10
    )

    ax.text(
    	b_water + talud_normaal_breedte - 4.0,
    	flex_onder - 0.25,
    	f"{flex_onder:.2f} mNAP",
    	ha="left",
    	va="bottom",
    	fontsize=10,
    	
    )

    ax.add_patch(Polygon(
        [[b_water, flex_boven],
         [b_water, flex_onder],
         [b_water + talud_normaal_breedte, flex_boven]],
        closed=True, color="#c7c7c7", alpha=0.8))

    x0 = b_water + talud_normaal_breedte

    # DROGE BERGING
    ax.add_patch(Rectangle((x0 + 1, hoogte_droge_berging - 0.05), 3, 0.1, color="orange"))
    ax.text(x0 + 2.4, hoogte_droge_berging - 0.15, "Droge Berging",
            ha="center", va="top", fontsize=10)
    ax.text(x0 + 2.4, hoogte_droge_berging - 0.35, f"({hoogte_droge_berging:.2f} mNAP)",
            ha="center", va="top", fontsize=10)

    # GROEN
    ax.add_patch(Rectangle((x0 + 4, hoogte_groen - 0.05), 4, 0.1, color="green"))
    ax.text(x0 + 6, hoogte_groen - 0.15, "Groen",
            ha="center", va="top", fontsize=10)
    ax.text(x0 + 6, hoogte_groen - 0.35, f"({hoogte_groen:.2f} mNAP)",
            ha="center", va="top", fontsize=10)

    # INFRA
    ax.add_patch(Rectangle((x0 + 8, hoogte_weg - 0.05), 5, 0.1, color="gray"))
    ax.text(x0 + 10.5, hoogte_weg - 0.15, "Hoogte as weg",
            ha="center", va="top", fontsize=10)
    ax.text(x0 + 10.5, hoogte_weg - 0.35, f"({hoogte_weg:.2f} mNAP)",
            ha="center", va="top", fontsize=10)

    # WONING
    ax.add_patch(Rectangle((x0 + 13, vloerpeil - 0.05), 5, 0.1, color="gray"))
    ax.text(x0 + 15.5, vloerpeil - 0.15,
    "Vloerpeil",
            ha="center", va="top", fontsize=10)
    ax.text(x0 + 15.5, vloerpeil - 0.35,
    f"({vloerpeil:.2f} mNAP)",
            ha="center", va="top", fontsize=10)


    # ICONEN PLAATSEN
    # Boom
    draw_icon(ax, x0 + 6.5, hoogte_groen + 0.7, r"afbeeldingen\boom.png", zoom=0.1)

    # Auto
    draw_icon(ax, x0 + 10.5, hoogte_weg + 0.28, r"afbeeldingen\auto_fiets.png", zoom=0.08)

    # Huis
    draw_icon(ax, x0 + 15.5, vloerpeil + 0.5, r"afbeeldingen\huis.png", zoom=0.1)

    # As-instellingen
    ymin = min(flex_onder, hoogte_groen, hoogte_weg, vloerpeil) - 1
    ymax = max(flex_boven, hoogte_groen, hoogte_weg, vloerpeil) + 2

    #ax.axis("off")
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(-talud_normaal_breedte - 2, x0 + 20)
    
    # Alleen verticale as behouden
    ax.spines['bottom'].set_visible(False)   # horizontale as weg
    ax.spines['top'].set_visible(False)      # bovenrand weg
    ax.spines['right'].set_visible(False)    # rechter as weg

    ax.xaxis.set_ticks([])                   # geen x‑ticks
    ax.set_xlabel("")                        # geen x‑label

    #ax.set_xlabel("Dwarsrichting (m)")
    ax.set_ylabel("Hoogte (m NAP)")
    #ax.set_title("Profielschets")
    ax.grid(False)

    return fig


import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np

def plot_ruimtebeslag(ruimte):
    import matplotlib.pyplot as plt
    import numpy as np

    # Waarden omrekenen naar hectare
    waarden_ha = [v / 10000 for v in ruimte.values()]
    labels = list(ruimte.keys())

    # Labels voor buiten/binnen de taart
    labels_met_ha = [f"{naam} ({int(ha)} ha)" for naam, ha in zip(labels, waarden_ha)]

    fig, ax = plt.subplots(figsize=(7, 7))

    # Custom autopct-functie die zowel pct als ha toont
    def make_autopct(waarden):
        def autopct(pct):
            totaal = sum(waarden)
            waarde = int(round(pct * totaal / 100))
            return f"{pct:.0f}%\n({waarde} ha)"
        return autopct

    wedges, texts, autotexts = ax.pie(
         waarden_ha,
         labels=None,
         autopct=make_autopct(waarden_ha),
         startangle=90,
         pctdistance=0.7,
         labeldistance=1.05,
         colors=["#9ecae1", "gray", "orange", "green"]
)

    # Maak de percentages + ha‑waarden wit
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    

    #ax.set_title("Ruimtebeslag (in hectare)", fontsize=14, weight='bold')
    
    legenda_labels = ["Open water", "Verharding", "Droge berging", "Onverhard/groen"]

    # Legenda met aangepaste namen (zonder ha)
    ax.legend(
        wedges,
        legenda_labels,
        title="Categorieën",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    ax.axis('equal')
    return fig


# app.py
import streamlit as st
# import model

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
    st.caption(f"Drooglegging panden: {vloerpeil - flex_boven:.2f} m")

    hoogte_weg = st.number_input("Hoogte as weg (m NAP)", value=-4.8, step=0.1)
    st.caption(f"Drooglegging wegen: {hoogte_weg - flex_boven:.2f} m")

    hoogte_groen = st.number_input("Hoogte groen (m NAP)", value=-5.15, step=0.1)
    st.caption(f"Drooglegging groen: {hoogte_groen - flex_boven:.2f} m")


with col3:
    # Nieuw: keuze droge berging ja/nee
    droge_berging_aan = st.checkbox("Droge berging toepassen", value=True)

    # Hoogte invoer (alleen actief als 'ja')
    hoogte_droge_berging = st.number_input(
        "Hoogte droge berging (m NAP)",
        value=-5.3,
        step=0.1,
        disabled=not droge_berging_aan
    )

    # Berekening peilstijging alleen als actief
    if droge_berging_aan:
        peilstijging_droge_berging = max(0.0, hoogte_droge_berging - flex_boven)
    else:
        peilstijging_droge_berging = 0.0

    # Weergave (altijd disabled zoals je had)
    st.text_input(
        "Peilstijging meebergen droge berging (m)",
        value=f"{peilstijging_droge_berging:.2f}",
        disabled=True
    )

    max_peilstijging = st.number_input(
        "Maximale peilstijging (m)",
        min_value=0.0,
        value=0.5,
        step=0.05
    )

    
# eenvoudige validaties
if vloerpeil < flex_boven or hoogte_weg < flex_boven or hoogte_groen < flex_boven:
    st.warning("Let op: vloerpeil, weg en groen mogen niet lager zijn dan de bovenkant bandbreedte.")

# --- 3. Oppervlakken en percentages ---
st.header("Oppervlak en gebruik")

col4, col5 = st.columns(2)

with col4:
    opp_ha = st.number_input("Oppervlak plangebied (ha)", min_value=0.0,value=36.4, step=0.1)
    open_water_pct = st.number_input("Open water (%)", min_value=0.0, value=10.0, step=0.5) / 100
    verhard_pct = st.number_input("Verhard (%)", min_value=0.0, value=57.0, step=0.5) / 100
    
    droge_berging_pct = st.number_input(
       "Droge berging (onverhard) (%)",
       min_value=0.0,
       value=0.0,
       step=0.5,
       disabled=not droge_berging_aan
       ) / 100

    if not droge_berging_aan:
       droge_berging_pct = 0.0
       
    
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
    pct_natuurvriendelijk = st.number_input("Percentage natuurvriendelijk talud (%)", min_value=0.0, value=50.0, step=5.0) / 100
    talud_nvo = st.number_input("Talud natuurvriendelijk (1:x)", min_value=0.0, value=5.0, step=0.5)
    talud_normaal = st.number_input("Talud normaal (1:x)", min_value=0.0, value=3.0, step=0.5)
    beheer_vanaf_kant_pct = st.number_input("Beheer vanaf kant (%)", min_value=0.0, value=100.0, step=5.0) / 100
    breedte_onderhoud = st.number_input("Breedte onderhoudsstrook (m)", min_value=0.0, value=5.0, step=0.5)
    breedte_waterloop = st.number_input("Aanname breedte waterloop (m)", min_value=0.0, value=8.0, step=0.5)
    porien_volume = st.number_input("Poriënvolume (-)", min_value=0.0, value=0.28, step=0.01)


# --- 4. Berekeningen ---

if st.button("Bereken en visualiseer"):

    resultaten = bereken_ruimtepuzzel(
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
        fig_profiel = plot_profiel(resultaten["profiel_params"])
        st.pyplot(fig_profiel)

    with col_b:
        st.subheader("Ruimtebeslag")
        fig_ruimte = plot_ruimtebeslag(resultaten["ruimte"])
        st.pyplot(fig_ruimte)

    # ---- NIEUWE VISUALISATIE ----

    import pandas as pd

    kerncijfers = {
        "Berging oppervlaktewater (m³)": round(resultaten["berging_oppervlaktewater_m3"], 1),
        "Berging taluds (m³ per m)": round(resultaten["berging_taluds_m3_per_m"], 1),
        "Berging onverhard (m³)": round(resultaten["berging_onverhard_m3"], 1),
        "Berging bodem (mm)": round(resultaten["R3"], 1),
        "Tekort bodemberging (m³)": round(resultaten["S3"], 1),
        "Totale berging (m³)": round(resultaten["totale_berging_m3"], 1),
        "Benodigde berging (m³)": round(resultaten["benodigde_berging_m3"], 1),
        "Benodigde berging (mm)": round(resultaten["benodigde_berging_mm"], 1),
        "Tekort / Overschot (m³)": round(resultaten["tekort_overschot_m3"], 1),
        "Tekort / Overschot (mm)": round(resultaten["tekort_overschot_mm"], 1),
    }

    st.subheader("Kerncijfers")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Totale berging",
            f"{kerncijfers['Totale berging (m³)']} m³"
        )

    with col2:
        st.metric(
            "Benodigde berging",
            f"{kerncijfers['Benodigde berging (m³)']} m³"
        )

    with col3:
        verschil = kerncijfers["Tekort / Overschot (m³)"]

        st.metric(
            "Tekort/Overschot",
            f"{verschil} m³",
            delta=verschil
        )

    with col4:
       verschil_mm = kerncijfers["Tekort / Overschot (mm)"]

       st.metric(
           "Tekort / Overschot (mm)",
           f"{verschil_mm} mm",
           delta=verschil_mm
        )

    
    if verschil < 0:
        st.error(
             f"Tekort van {-verschil:.1f} m³ ({-verschil_mm:.1f} mm)"
    )
    else:
        st.success(
             f"Overschchot van {verschil:.1f} m³ ({verschil_mm:.1f} mm)"
    )


    df = pd.DataFrame(
        list(kerncijfers.items()),
        columns=["Parameter", "Waarde"]
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
