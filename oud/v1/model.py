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


    # 5. Totale berging
    totale_berging = (
    	berging_oppervlaktewater +
    	berging_taluds +
    	berging_onverhard
     )

    # 6. Benodigde berging (m3)
    benodigde_berging = opp_m2 * neerslag_m

    # 7. Tekort of overschot
    tekort_overschot = totale_berging - benodigde_berging


    # 8. Ruimtebeslag (voor grafiek)
    ruimte = {
        "open_water_m2": open_water,
        "verhard_m2": verhard,
        "droge_berging_m2": droge_berging,
        "onverhard_overig_m2": max(onverhard - droge_berging, 0),
    }

    # 9. Resultaten bundelen
    resultaten = {
        "berging_oppervlaktewater_m3": berging_oppervlaktewater,
        "berging_taluds_m3_per_m": berging_taluds,
        "berging_onverhard_m3": berging_onverhard,
        "totale_berging_m3": totale_berging,
        "benodigde_berging_m3": benodigde_berging,
        "tekort_overschot_m3": tekort_overschot,
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


def plot_profiel(params):
    import numpy as np
    import matplotlib.pyplot as plt

    # Invoerparameters
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

    # Hoogteverschil
    dh = flex_boven - flex_onder

    # Taludbreedtes
    talud_normaal_breedte = abs(dh) * talud_normaal
    talud_nvo_breedte = abs(dh) * talud_nvo

    # ---------------------------------------------------------
    # 1. Boven- en onderkant bandbreedte (horizontaal)
    # ---------------------------------------------------------
    ax.hlines(flex_boven, 0, b_water, colors="navy", linestyles="dashed", label="Bovenkant bandbreedte")
    ax.hlines(flex_onder, 0, b_water, colors="skyblue", linestyles="dashed", label="Onderkant bandbreedte")

    # ---------------------------------------------------------
    # 2. Taluds (normaal = vaste lijn, nvo = stippellijn)
    # ---------------------------------------------------------

    # Talud normaal: boven breed → onder smal
    ax.plot(
        [-talud_normaal_breedte, 0],     # breed boven → smal onder
        [flex_boven, flex_onder],
        color="black",
        linewidth=2,
        label="Talud normaal"
    )
    ax.plot(
        [b_water + talud_normaal_breedte, b_water],
        [flex_boven, flex_onder],
        color="black",
        linewidth=2
    )

    # Talud natuurvriendelijk (stippellijn): boven breed → onder smal
    ax.plot(
        [-talud_nvo_breedte, 0],
        [flex_boven, flex_onder],
        color="black",
        linestyle="dashed",
        linewidth=2,
        label="Talud natuurvriendelijk"
    )
    ax.plot(
        [b_water + talud_nvo_breedte, b_water],
        [flex_boven, flex_onder],
        color="black",
        linestyle="dashed",
        linewidth=2
    )

    # ---------------------------------------------------------
    # 3. Watergang (blauw, binnen horizontale lijnen)
    # ---------------------------------------------------------
    #ax.fill_between(
    #    [0, b_water],
    #    [flex_onder, flex_onder],
    #    [flex_boven, flex_boven],
    #    color="#6baed6",
    #    alpha=0.8,
    #    label="Watergang"
    #)

    # ---------------------------------------------------------
    # 4. Droge berging (stippellijn rechts)
    # ---------------------------------------------------------
    x0 = b_water + talud_normaal_breedte
    if hoogte_droge_berging is not None:
        ax.hlines(
            hoogte_droge_berging,
            x0,
            x0 + 4,
            colors="black",
            linestyles="dashed",
            linewidth=2,
            label="Droge berging"
        )

    # ---------------------------------------------------------
    # 5. Groen (rechts)
    # ---------------------------------------------------------
    ax.hlines(
        hoogte_groen,
        x0 + 4,
        x0 + 8,
        colors="green",
        linewidth=4,
        label="Groen"
    )

    # ---------------------------------------------------------
    # 6. Weg (rechts naast groen)
    # ---------------------------------------------------------
    ax.hlines(
        hoogte_weg,
        x0 + 8,
        x0 + 13,
        colors="gray",
        linewidth=5,
        label="Weg"
    )

    # ---------------------------------------------------------
    # 7. Vloerpeil (rechts naast weg)
    # ---------------------------------------------------------
    ax.hlines(
        vloerpeil,
        x0 + 13,
        x0 + 18,
        colors="orange",
        linewidth=4,
        label="Vloerpeil"
    )

    # ---------------------------------------------------------
    # 8. Annotaties
    # ---------------------------------------------------------
    ax.text(b_water/2, flex_boven + 0.1, "Bovenkant bandbreedte", ha="center")
    ax.text(b_water/2, flex_onder - 0.1, "Onderkant bandbreedte", ha="center")

    ax.text(x0 + 16, vloerpeil + 0.05, "Vloerpeil", color="orange")
    ax.text(x0 + 10.5, hoogte_weg + 0.05, "Weg", color="gray")
    ax.text(x0 + 6, hoogte_groen + 0.05, "Groen", color="green")

    if hoogte_droge_berging is not None:
        ax.text(x0 + 2, hoogte_droge_berging + 0.05, "Droge berging")

    # ---------------------------------------------------------
    # 9. As-instellingen
    # ---------------------------------------------------------
    ymin = min(flex_onder, hoogte_groen, hoogte_weg, vloerpeil) - 0.5
    ymax = max(flex_boven, hoogte_groen, hoogte_weg, vloerpeil) + 0.5

    ax.set_ylim(ymin, ymax)
    ax.set_xlim(-talud_normaal_breedte - 2, x0 + 20)

    ax.set_xlabel("Dwarsrichting (m)")
    ax.set_ylabel("Hoogte (m NAP)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    return fig

def plot_ruimtebeslag(ruimte):
    labels = list(ruimte.keys())
    waarden = [v for v in ruimte.values()]  # m2

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        waarden,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=["#1f78b4", "#b2df8a", "#fb9a99", "#cab2d6"]
    )
    ax.set_title("Ruimtebeslag (verdeling m²)")
    ax.axis('equal')  # cirkelvormig

    return fig

