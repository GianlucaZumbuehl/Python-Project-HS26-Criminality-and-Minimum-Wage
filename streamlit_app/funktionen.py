# Alle Rechnungen und Grafiken an einem Ort.
# Die Seiten (app.py und pages/) rufen nur diese Funktionen auf.

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


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
    "Neuenburg": ["Aargau", "Freiburg", "St. Gallen"],
    "Genf": ["Aargau", "Luzern", "St. Gallen", "Wallis"],
    "Basel-Stadt": ["Aargau", "Bern", "Solothurn", "St. Gallen", "Thurgau", "Wallis"],
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
# 1. PARALLEL TRENDS (normalisiert)
# ============================================================
# Jeder Kanton wird durch seinen Durchschnitt vor dem Mindestlohn geteilt.
# So starten alle bei 100 und man kann die Linien übereinander legen.

def grafik_trends(df, kanton, kontrollen):
    jahr = EINFUEHRUNG[kanton]
    fig, ax = plt.subplots(figsize=(8, 4))

    linien = ["--", ":", "-."]  # verschiedene Linien für die Kontrollen

    for i, k in enumerate(kontrollen + [kanton]):
        daten = df[df["Canton"] == k]
        vorher = daten[daten["Year"] < jahr]["rate"].mean()
        index = daten["rate"] / vorher * 100

        if k == kanton:
            ax.plot(daten["Year"], index, color=HAUPTKANTON_FARBE, linewidth=3, label=k)
        else:
            ax.plot(daten["Year"], index, color="grey", linestyle=linien[i % 3], label=k)

    ax.axvline(jahr, color="black", linestyle=":")  # Linie bei der Einführung
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Index (vorher = 100)")
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")  # Legende rechts neben der Grafik
    return fig


# ============================================================
# 2. EVENT STUDY (Code von Caner)
# ============================================================
# Pro Jahr: log_rate Mindestlohn-Kanton minus Durchschnitt der Kontrollen.
# Davon wird die Differenz im Jahr vor der Einführung abgezogen (Referenzjahr = 0)
# und das Ergebnis in % umgerechnet.

def event_study(df, kanton, kontrollen):
    jahr = EINFUEHRUNG[kanton]

    treat = df[df["Canton"] == kanton].groupby("Year")["log_rate"].mean()
    kontrolle = df[df["Canton"].isin(kontrollen)].groupby("Year")["log_rate"].mean()

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

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(punkte.index, punkte.values, "o", color=HAUPTKANTON_FARBE)
    ax.plot(referenz.index, referenz.values, "o", color="#eb6834",
            label=f"Reference year ({jahr - 1})")
    ax.axhline(0, color="grey", linewidth=1)
    ax.axvline(jahr, color="black", linestyle=":",
               label=f"Minimum wage introduction ({jahr})")
    ax.set_xticks(effekt.index)
    ax.tick_params(axis="x", rotation=45)
    ax.set_xlabel("Year")
    ax.set_ylabel("Effect relative to reference year (%)")
    ax.set_title(f"Event study: {kanton} vs. {', '.join(kontrollen)}")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), frameon=False, ncol=2)
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot(x, kontrafakt, color=HAUPTKANTON_FARBE, linestyle="--",
            label=f"{kanton} without minimum wage (counterfactual)")
    ax.plot(x, treat, color=HAUPTKANTON_FARBE, label=f"{kanton} (minimum wage)")
    ax.plot(x, kontrolle, color="#eb6834", label=f"Control cantons (average of {len(kontrollen)})")

    # log-skalierte Achse, beschriftet in %
    ax.set_yscale("log")
    werte = np.concatenate([treat, kontrolle, kontrafakt])
    ticks = np.geomspace(werte.min(), werte.max(), 6)
    ax.set_yticks(ticks, [f"{t:.2f} %" for t in ticks])
    ax.minorticks_off()

    beschriftung = [f"{jahr}\n(first full year)"] + [str(j) for j in jahre[1:]]
    ax.set_xticks(jahre, beschriftung)
    ax.set_xlim(jahre[0], jahre[-1])
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of accused persons (log scale)")
    ax.set_title(f"Difference-in-Differences: {kanton} vs. {', '.join(kontrollen)}")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
    fig.tight_layout()
    return fig