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

    fig, ax = plt.subplots(figsize=(14, 6))

    # Taludbreedte Normaal
    dh = flex_boven - flex_onder
    talud_normaal_breedte = abs(dh) * talud_normaal
   
    # Taludbreedte NVO
    talud_nvo_breedte = abs(dh) * talud_nvo
    
    ax.plot(
    	[0, - talud_nvo_breedte],
    	[flex_onder, flex_boven],
    	linestyle="--",
    	color="black",
    	linewidth=1.2
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
    draw_icon(ax, x0 + 6.5, hoogte_groen + 0.7, r"C:\Users\Diepenmaat\hoogtepuzzel\afbeeldingen\boom.png", zoom=0.1)

    # Auto
    draw_icon(ax, x0 + 10.5, hoogte_weg + 0.28, r"C:\Users\Diepenmaat\hoogtepuzzel\afbeeldingen\auto_fiets.png", zoom=0.08)

    # Huis
    draw_icon(ax, x0 + 15.5, vloerpeil + 0.5, r"C:\Users\Diepenmaat\hoogtepuzzel\afbeeldingen\huis.png", zoom=0.1)

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
