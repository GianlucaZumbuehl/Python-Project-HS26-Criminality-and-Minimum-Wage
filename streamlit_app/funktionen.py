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
# 2. EVENT STUDY
# ============================================================
# Pro Jahr: Unterschied Mindestlohn Kanton minus Kontrollen.
# Das Jahr vor der Einführung wird auf 0 gesetzt.

def event_study(df, kanton, kontrollen):
    jahr = EINFUEHRUNG[kanton]

    treat = df[df["Canton"] == kanton].groupby("Year")["log_rate"].mean()
    kontrolle = df[df["Canton"].isin(kontrollen)].groupby("Year")["log_rate"].mean()

    differenz = treat - kontrolle
    effekt = differenz - differenz[jahr - 1]
    return (np.exp(effekt) - 1) * 100  # in Prozent


def grafik_event_study(df, kanton, kontrollen):
    effekt = event_study(df, kanton, kontrollen)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(effekt.index, effekt.values, color=HAUPTKANTON_FARBE, marker="o")
    ax.axhline(0, color="grey")
    ax.axvline(EINFUEHRUNG[kanton], color="black", linestyle=":")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("Effekt in %")
    return fig


# ============================================================
# 3. DIFFERENCE IN DIFFERENCES
# ============================================================

def did_daten(df, kanton, kontrollen):
    d = df[df["Canton"].isin([kanton] + kontrollen)].copy()
    d["Treat"] = (d["Canton"] == kanton).astype(int)
    d["After"] = (d["Year"] >= ERSTES_VOLLES_JAHR[kanton]).astype(int)
    return d


def sterne(p):
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def did_tabelle(df, kanton, kontrollen):
    d = did_daten(df, kanton, kontrollen)

    # Modell A: klassische DiD (wie bei Caner)
    a = smf.ols("log_rate ~ Treat + After + Treat:After", data=d).fit(cov_type="HC1")
    # Modell B: mit Kantons und Jahres Fixed Effects, Fehler nach Kanton geclustert (wie bei Caner)
    b = smf.ols("log_rate ~ Treat:After + C(Canton) + C(Year)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["Canton"]})

    zeilen = []
    for name, m in [("A: DiD", a), ("B: DiD mit Fixed Effects", b)]:
        beta = m.params["Treat:After"]
        p = m.pvalues["Treat:After"]
        zeilen.append({
            "Modell": name,
            "Koeffizient": f"{beta:.3f} {sterne(p)}",
            "Std. Fehler": round(m.bse["Treat:After"], 3),
            "p Wert": round(p, 3),
            "Effekt in %": round((np.exp(beta) - 1) * 100, 1),
            "N": int(m.nobs),
        })
    return pd.DataFrame(zeilen)


def grafik_did(df, kanton, kontrollen):
    d = did_daten(df, kanton, kontrollen)
    treat = d[d["Treat"] == 1].groupby("Year")["log_rate"].mean()
    kontrolle = d[d["Treat"] == 0].groupby("Year")["log_rate"].mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(treat.index, treat.values, color=HAUPTKANTON_FARBE, linewidth=3, label=kanton)
    ax.plot(kontrolle.index, kontrolle.values, color="grey", linestyle="--",
            label="Kontrollen (Durchschnitt)")
    ax.axvline(ERSTES_VOLLES_JAHR[kanton] - 0.5, color="black", linestyle=":")
    ax.set_xlabel("Jahr")
    ax.set_ylabel("log Beschuldigtenrate")
    ax.legend()
    return fig
