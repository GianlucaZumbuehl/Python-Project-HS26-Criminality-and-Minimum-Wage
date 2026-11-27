# Alle Rechnungen und Grafiken an einem Ort.
# Die Seiten (app.py und pages/) rufen nur diese Funktionen auf.

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import textwrap  # lange Beschriftungen auf mehrere Zeilen umbrechen


# ============================================================
# EINSTELLUNGEN (hier anpassen)
# ============================================================

# Pfad zu den Daten: eine Ebene über diesem Ordner, im Ordner von Caner
ORDNER = Path(__file__).parent
DATEN = ORDNER.parent / "Group_project_part_caner" / "Crime_Pop_clean_copy2.csv"

# Mindestlohn Kantone: Einführungsjahr und erstes volles Jahr
EINFUEHRUNG = {"Neuenburg": 2017, "Genf": 2020, "Basel-Stadt": 2022}
ERSTES_VOLLES_JAHR = {"Neuenburg": 2018, "Genf": 2021, "Basel-Stadt": 2023}

# Farbe des Mindestlohn Kantons in allen Grafiken (UZH Blau)
HAUPTKANTON_FARBE = "#0028A5"

# Kontrollkantone mit parallelen Trends
KONTROLLEN = {
    "Neuenburg": ["Aargau", "St. Gallen"],
    "Genf": ["Aargau", "Luzern", "Wallis"],
    "Basel-Stadt": ["Aargau", "Bern", "Solothurn", "St. Gallen", "Thurgau"],
}

# ============================================================
# DATEN LADEN
# ============================================================


def daten_laden():
    df = pd.read_csv(DATEN)
    df["rate"] = df["Number of Accused Persons"] / df["Resident Population"]
    df["log_rate"] = np.log(df["rate"])
    return df


# ============================================================
# 1. PARALLEL TRENDS (Code von Annette)
# ============================================================
# Code aus parallel_trend_vis_final.ipynb (letzte Zelle "WITH LOG ACCUSED RATE", normalisiert).
# Für die App angepasst:
#   - als Funktion mit df, kanton, kontrollen (statt fester Paare) und return statt plt.show()
#   - Formel: (np.exp(log - Basis) - 1) * 100 statt (log - Basis) / Basis * 100
#   - Farbe für Kantone, die nicht in colour_cantons stehen (sonst Fehler auf Seite 2)

def grafik_trends(df, kanton, kontrollen):
    data = df.copy()
    data['AccusedLog'] = (np.log(data['AccusedRate']))

    plt.rcParams['font.family'] = 'sans-serif'
    colour1 = "#ED0101"
    colour2 = "#B4B4B4"
    colour_cantons = {
        "Aargau":           "#E69F00",  # orange
        "Basel-Stadt":      "#0028A5",  # UZH blue (minimum wage)
        "Bern":             "#009E73",  # green
        "Genf":             "#0028A5",  # UZH blue (minimum wage)
        "Luzern":           "#CC79A7",  # pink
        "Neuenburg":        "#0028A5",  # UZH blue (minimum wage)
        "Solothurn":        "#D55E00",  # dark orange
        "St. Gallen":       "#8C6D31",  # brown
        "Thurgau":          "#7F7F7F",  # gray
        "Wallis":           "#56A08E",  # teal
    }

    # 1. Filtering subset for the selected cantons
    subset = data[data['Canton'].isin([kanton] + kontrollen)]

    # 2. Creating canvas
    plt.figure(figsize=(12, 5.5))

    # 3. Ploting all cantons onto same graph
    for canton in [kanton] + kontrollen:
        canton_data = subset[subset['Canton'] == canton]
        base_value = canton_data['AccusedLog'].iloc[0]
        canton_data['NormalizedChange'] = (
            np.exp(canton_data['AccusedLog'] - base_value) - 1) * 100

        plt.plot(
            canton_data['Year'],
            canton_data['NormalizedChange'],
            marker='o',
            color=colour_cantons.get(canton, "#7F7F7F"),
            linewidth=2,
            label=canton)
    # adding dotted line for minimum-wage-introduction
    if 'Basel-Stadt' in [kanton] + kontrollen:
        plt.axvline(
            x=2023,
            color=colour1,
            linestyle='dotted',
            linewidth=1.5,
            label='First full year 2023')
    elif 'Genf' in [kanton] + kontrollen:
        plt.axvline(
            x=2021,
            color=colour1,
            linestyle='dotted',
            linewidth=1.5,
            label='First full year 2021')
    elif 'Neuenburg' in [kanton] + kontrollen:
        plt.axvline(
            x=2018,
            color=colour1,
            linestyle='dotted',
            linewidth=1.5,
            label='First full year 2018')

    # 4. Add titles, labels, and return the plot
    plt.title(f'Crime Rate Development: {kanton}', fontsize=16, pad=20, fontweight="bold")
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Change from baseline in %', fontsize=12)
    plt.axhline(0, color=colour2, linewidth=0.8, linestyle='-',
                alpha=0.5)  # adding line to see baseline
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=5,
               fontsize=13, frameon=False)  # Legende unter der Grafik
    plt.grid(True, linestyle='-', alpha=0.6)
    return plt.gcf()


# Neu (gleicher Stil wie oben): Mindestlohn-Kanton vs. Durchschnitt der Kontrollkantone
def grafik_trends_durchschnitt(df, kanton, kontrollen):
    data = df.copy()
    data['AccusedLog'] = (np.log(data['AccusedRate']))

    plt.rcParams['font.family'] = 'sans-serif'
    colour1 = "#ED0101"
    colour2 = "#B4B4B4"
    colour_treated = "#0028A5"   # blue (wie die Mindestlohn-Kantone oben)
    colour_controls = "#E8732A"  # orange

    # 1. Mindestlohn-Kanton und Durchschnitt der Kontrollkantone pro Jahr
    treated_data = data[data['Canton'] == kanton].groupby('Year', as_index=False)[
        'AccusedLog'].mean()
    control_data = data[data['Canton'].isin(kontrollen)].groupby(
        'Year', as_index=False)['AccusedLog'].mean()

    # 2. Creating canvas
    plt.figure(figsize=(12, 5.5))

    # 3. Ploting both lines onto same graph
    for canton_data, name, colour in [(treated_data, kanton, colour_treated),
                                      (control_data, 'Control cantons (average)', colour_controls)]:
        base_value = canton_data['AccusedLog'].iloc[0]
        canton_data['NormalizedChange'] = (
            np.exp(canton_data['AccusedLog'] - base_value) - 1) * 100

        plt.plot(
            canton_data['Year'],
            canton_data['NormalizedChange'],
            marker='o',
            color=colour,
            linewidth=2,
            label=name)
    if kanton == 'Basel-Stadt':  # adding dotted line for minimum-wage-introduction
        plt.axvline(x=2023, color=colour1, linestyle='dotted',
                    linewidth=1.5, label='First full year 2023')
    elif kanton == 'Genf':
        plt.axvline(x=2021, color=colour1, linestyle='dotted',
                    linewidth=1.5, label='First full year 2021')
    elif kanton == 'Neuenburg':
        plt.axvline(x=2018, color=colour1, linestyle='dotted',
                    linewidth=1.5, label='First full year 2018')

    # 4. Add titles, labels, and return the plot
    plt.title(
        f'Crime Rate Development: {kanton} vs average of control cantons', fontsize=16, pad=20, fontweight="bold")
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Change from baseline in %', fontsize=12)
    plt.axhline(0, color=colour2, linewidth=0.8, linestyle='-',
                alpha=0.5)  # adding line to see baseline
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3,
               fontsize=13, frameon=False)  # Legende unter der Grafik
    plt.text(0.5, -0.24, textwrap.fill('Control cantons: ' + ', '.join(kontrollen), 100), transform=plt.gca().transAxes,
             # Liste der Kontrollkantone unter der Legende
             ha='center', va='top', fontsize=12)
    plt.grid(True, linestyle='-', alpha=0.6)
    return plt.gcf()


# ============================================================
# 2. EVENT STUDY (Code von Caner)
# ============================================================
# Pro Jahr: log_rate Mindestlohn-Kanton minus Durchschnitt der Kontrollen.
# Davon wird die Differenz im Jahr vor der Einführung abgezogen (Referenzjahr = 0)
# und das Ergebnis in % umgerechnet.

def event_study(df, kanton, kontrollen):
    jahr = EINFUEHRUNG[kanton]

    treat = df[df["Canton"] == kanton].groupby("Year")["log_rate"].mean()
    kontrolle = df[df["Canton"].isin(kontrollen)].groupby("Year")[
        "log_rate"].mean()

    differenz = treat - kontrolle
    effekt = differenz - differenz[jahr - 1]
    return (np.exp(effekt) - 1) * 100  # in Prozent


def grafik_event_study(df, kanton, kontrollen):
    jahr = EINFUEHRUNG[kanton]
    effekt = event_study(df, kanton, kontrollen)

    # Einführungsjahr ohne Punkt (Mindestlohn galt nur einen Teil des Jahres),
    # Referenzjahr in eigener Farbe
    punkte = effekt[(effekt.index != jahr) & (effekt.index != jahr - 1)]
    referenz = effekt[effekt.index == jahr - 1]

    # gleiche Schrift wie Parallel Trends
    plt.rcParams['font.family'] = 'sans-serif'
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(referenz.index, referenz.values, "o", color="#E8732A",
            label=f"Reference year ({jahr - 1})")
    ax.axhline(0, color="#B4B4B4", linewidth=0.8, alpha=0.5)
    ax.axvline(jahr, color="#ED0101", linestyle="dotted", linewidth=1.5,
               label=f"Minimum wage introduction ({jahr})")
    # blaue Punkte = Effekt pro Jahr; in der Legende mit der Liste der Kontrollkantone
    ax.plot(punkte.index, punkte.values, "o", color=HAUPTKANTON_FARBE,
            label="Control cantons")
    ax.set_xticks(effekt.index)
    ax.tick_params(axis="x", rotation=45)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Effect relative to reference year (%)", fontsize=12)
    ax.set_title(f"Event study: {kanton}", fontsize=16, pad=20, fontweight="bold")
    ax.grid(True, linestyle="-", alpha=0.6)   # Gitter wie Parallel Trends
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3,
              fontsize=13, frameon=False)  # Legende unter der Grafik
    ax.text(0.5, -0.34, textwrap.fill("Control cantons: " + ", ".join(kontrollen), 100), transform=ax.transAxes,
            # Liste der Kontrollkantone unter der Legende
            ha="center", va="top", fontsize=12)
    return fig


# ============================================================
# 3. DIFFERENCE IN DIFFERENCES (Code von Caner)
# ============================================================
# Modell: log_rate = b0 + b1*Treat + b2*After + b3*Treat*After
# Standardfehler: HC1 (zu wenige Kantone für geclusterte Standardfehler)
# Effekt in % = (exp(b3) - 1) * 100

def did_daten(df, kanton, kontrollen):
    d = df[df["Canton"].isin([kanton] + kontrollen)].copy()
    d["Treat"] = (d["Canton"] == kanton).astype(int)
    d["After"] = (d["Year"] >= ERSTES_VOLLES_JAHR[kanton]).astype(int)
    return d


def did_regression(df, kanton, kontrollen):
    d = did_daten(df, kanton, kontrollen)
    return smf.ols("log_rate ~ Treat + After + Treat:After", data=d).fit(cov_type="HC1")


def did_tabelle(df, kanton, kontrollen):
    m = did_regression(df, kanton, kontrollen)
    beta = m.params["Treat:After"]

    return pd.DataFrame({
        "β3 (log)": [round(beta, 3)],
        "Std. error": [round(m.bse["Treat:After"], 3)],
        "p-value": [round(m.pvalues["Treat:After"], 5)],
        "R²": [round(m.rsquared, 3)],
        "Effect in %": [round((np.exp(beta) - 1) * 100, 1)],
        "N": [int(m.nobs)],
    })


def grafik_did(df, kanton, kontrollen):
    m = did_regression(df, kanton, kontrollen)
    b0, b1, b2, b3 = m.params[["Intercept", "Treat", "After", "Treat:After"]]

    jahr = ERSTES_VOLLES_JAHR[kanton]
    jahre = list(range(jahr, df["Year"].max() + 1))
    x = [jahre[0], jahre[-1]]

    # log-Werte zurück in Prozent umrechnen
    treat = np.exp([b0 + b1, b0 + b1 + b2 + b3]) * 100
    kontrolle = np.exp([b0, b0 + b2]) * 100
    kontrafakt = np.exp([b0 + b1, b0 + b1 + b2]) * 100

    # gleiche Schrift wie Parallel Trends
    plt.rcParams['font.family'] = 'sans-serif'
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(x, kontrafakt, color=HAUPTKANTON_FARBE, linestyle="--",
            label=f"{kanton} without min. wage (counterfactual)")
    ax.plot(x, treat, color=HAUPTKANTON_FARBE,
            label=f"{kanton} (minimum wage)")
    ax.plot(x, kontrolle, color="#E8732A", label="Control cantons (average)")

    # log-skalierte Achse, beschriftet in %
    ax.set_yscale("log")
    werte = np.concatenate([treat, kontrolle, kontrafakt])
    ticks = np.geomspace(werte.min(), werte.max(), 6)
    ax.set_yticks(ticks, [f"{t:.2f} %" for t in ticks])
    ax.minorticks_off()

    beschriftung = [f"{jahr}\n(first full year)"] + [str(j) for j in jahre[1:]]
    ax.set_xticks(jahre, beschriftung)
    ax.set_xlim(jahre[0], jahre[-1])
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Share of accused persons (log scale)", fontsize=12)
    ax.set_title(f"Difference-in-Differences: {kanton}", fontsize=16, pad=20, fontweight="bold")
    ax.grid(True, linestyle="-", alpha=0.6)   # Gitter wie Parallel Trends
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=13, frameon=False,
              columnspacing=1.0, handlelength=1.5)  # Legende unter der Grafik
    ax.text(0.5, -0.32, textwrap.fill("Control cantons: " + ", ".join(kontrollen), 100), transform=ax.transAxes,
            # Liste der Kontrollkantone unter der Legende
            ha="center", va="top", fontsize=12)
    return fig
