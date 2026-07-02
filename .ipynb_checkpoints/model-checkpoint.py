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
):
    # 1. Basisoppervlakken
    opp_m2 = opp_ha * 10_000
    open_water = open_water_pct * opp_m2
    verhard = verhard_pct * opp_m2
    droge_berging = droge_berging_pct * opp_m2
    onverhard = opp_m2 - open_water - verhard  # kan je nog verfijnen

    # 2. Berging in oppervlaktewater (vereenvoudigd)
    neerslag_m = neerslag_mm / 1000
    berging_oppervlaktewater = open_water * neerslag_m  # m3

    # 3. Taluds (normaal + natuurvriendelijk) – sterk geschematiseerd
    # hier kun je later exact de Excel-logica inbouwen
    breedte_profiel = breedte_waterloop
    diepte_bandbreedte = flex_boven - flex_onder  # m (negatieve NAP-waarden → let op teken)
    diepte_bandbreedte = abs(diepte_bandbreedte)

    # aanname: taludlengte = diepte * helling
    taludlengte_normaal = diepte_bandbreedte * talud_normaal
    taludlengte_nvo = diepte_bandbreedte * talud_nvo

    # oppervlak talud (per meter lengte watergang)
    talud_oppervlak_normaal = taludlengte_normaal  # m2 per m
    talud_oppervlak_nvo = taludlengte_nvo          # m2 per m

    # verhouding natuurvriendelijk
    frac_nvo = pct_natuurvriendelijk
    frac_normaal = 1 - frac_nvo

    talud_oppervlak_totaal = (
        talud_oppervlak_normaal * frac_normaal
        + talud_oppervlak_nvo * frac_nvo
    )

    # berging in taluds (vereenvoudigd: talud-oppervlak * peilstijging)
    peilstijging_m = max_peilstijging  # hier ga je nog koppelen aan scenario
    berging_taluds = talud_oppervlak_totaal * peilstijging_m * 1  # per meter lengte

    # 4. Bodemberging / droge berging (sterk geschematiseerd)
    # hier kun je poriënvolume, diepte etc. uit Excel overnemen
    porienvolume = 0.28  # placeholder
    bodemberging_m = porienvolume * 0.5  # bijv. 0.5 m effectieve diepte
    berging_onverhard = onverhard * bodemberging_m

    # 5. Ruimtebeslag (voor grafiek)
    ruimte = {
        "open_water_m2": open_water,
        "verhard_m2": verhard,
        "droge_berging_m2": droge_berging,
        "onverhard_overig_m2": max(onverhard - droge_berging, 0),
    }

    # 6. Resultaten bundelen
    resultaten = {
        "berging_oppervlaktewater_m3": berging_oppervlaktewater,
        "berging_taluds_m3_per_m": berging_taluds,
        "berging_onverhard_m3": berging_onverhard,
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
        },
    }

    return resultaten


def plot_profiel(profiel_params):
    """
    Maakt een dwarsprofiel-plot:
    - watergang met bandbreedte
    - taluds (schematisch)
    - maaiveld/groen
    - as-weg
    - vloerpeil
    """
    flex_boven = profiel_params["flex_boven"]
    flex_onder = profiel_params["flex_onder"]
    vloerpeil = profiel_params["vloerpeil"]
    hoogte_weg = profiel_params["hoogte_weg"]
    hoogte_groen = profiel_params["hoogte_groen"]
    hoogte_droge_berging = profiel_params["hoogte_droge_berging"]
    b_water = profiel_params["breedte_waterloop"]
    b_onderhoud = profiel_params["breedte_onderhoud"]

    fig, ax = plt.subplots(figsize=(8, 4))

    # x-as: simpel profiel
    x = [0, b_water]
    y_boven = [flex_boven, flex_boven]
    y_onder = [flex_onder, flex_onder]

    # watergang
    ax.fill_between(x, y_onder, y_boven, color="#a6cee3", alpha=0.7, label="Watergang bandbreedte")

    # maaiveld/groen (schematisch links en rechts)
    ax.hlines(hoogte_groen, -b_onderhoud, 0, colors="green", linewidth=3, label="Groen")
    ax.hlines(hoogte_groen, b_water, b_water + b_onderhoud, colors="green", linewidth=3)

    # as-weg (bijv. rechts)
    ax.hlines(hoogte_weg, b_water + b_onderhoud, b_water + b_onderhoud + 5, colors="gray", linewidth=4, label="As weg")

    # vloerpeil (bijv. ergens rechts)
    ax.hlines(vloerpeil, b_water + b_onderhoud + 5, b_water + b_onderhoud + 10, colors="orange", linewidth=3, label="Vloerpeil")

    # droge berging (optioneel)
    if hoogte_droge_berging is not None:
        ax.hlines(hoogte_droge_berging, -b_onderhoud - 5, -b_onderhoud, colors="brown", linewidth=3, label="Droge berging")

    ax.invert_yaxis()  # omdat NAP vaak negatief is
    ax.set_xlabel("Dwarsrichting (m)")
    ax.set_ylabel("Hoogte (m NAP)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def plot_ruimtebeslag(ruimte_dict):
    labels = list(ruimte_dict.keys())
    waarden = [v / 10_000 for v in ruimte_dict.values()]  # m2 → ha

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, waarden, color=["#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6"])
    ax.set_ylabel("Oppervlak (ha)")
    ax.set_title("Ruimtebeslag")
    plt.xticks(rotation=20, ha="right")

    return fig
