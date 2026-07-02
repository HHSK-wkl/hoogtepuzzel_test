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
    porien_volume,          # ← HIER TOEGEVOEGD
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

    fig, ax = plt.subplots(figsize=(12, 6))

    dh = flex_boven - flex_onder
    talud_normaal_breedte = abs(dh) * talud_normaal
    talud_nvo_breedte = abs(dh) * talud_nvo

    ax.hlines(flex_boven, 0, b_water, colors="navy", linestyles="dashed")
    ax.hlines(flex_onder, 0, b_water, colors="skyblue", linestyles="dashed")

    ax.plot([-talud_normaal_breedte, 0], [flex_boven, flex_onder], color="black")
    ax.plot([b_water + talud_normaal_breedte, b_water], [flex_boven, flex_onder], color="black")

    ax.plot([-talud_nvo_breedte, 0], [flex_boven, flex_onder], color="black", linestyle="dashed")
    ax.plot([b_water + talud_nvo_breedte, b_water], [flex_boven, flex_onder], color="black", linestyle="dashed")

    x0 = b_water + talud_normaal_breedte
    if hoogte_droge_berging is not None:
        ax.hlines(hoogte_droge_berging, x0, x0 + 4, colors="black", linestyles="dashed")

    ax.hlines(hoogte_groen, x0 + 4, x0 + 8, colors="green", linewidth=4)
    ax.hlines(hoogte_weg, x0 + 8, x0 + 13, colors="gray", linewidth=5)
    ax.hlines(vloerpeil, x0 + 13, x0 + 18, colors="orange", linewidth=4)

    ymin = min(flex_onder, hoogte_groen, hoogte_weg, vloerpeil) - 0.5
    ymax = max(flex_boven, hoogte_groen, hoogte_weg, vloerpeil) + 0.5

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(-talud_normaal_breedte - 2, x0 + 20)
    ax.set_xlabel("Dwarsrichting (m)")
    ax.set_ylabel("Hoogte (m NAP)")
    ax.grid(True, alpha=0.3)

    return fig


def plot_ruimtebeslag(ruimte):
    labels = list(ruimte.keys())
    waarden = [v for v in ruimte.values()]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        waarden,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=["#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6"]
    )
    ax.set_title("Ruimtebeslag (verdeling m²)")
    ax.axis('equal')

    return fig
