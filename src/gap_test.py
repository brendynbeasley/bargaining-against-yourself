"""Extension: the paper's gap / no-gap distinction, first-contract strikes against the rest.

Run from the repository root:

    python src/gap_test.py

Gul, Sonnenschein & Wilson split the problem in two. When every buyer values the good above the
seller's cost (the "gap" case, Section 3), the equilibrium is unique and trade is finished after
a finite number of offers. When some buyers value it at or below cost (the "no gap" case,
Section 4), the market stays open forever and there can be a continuum of equilibria.

In bargaining terms, a strike over the renewal of an existing contract is close to the gap case:
both sides already live under a contract and some new contract is almost certain. A strike for a
first contract or for recognition is closer to the no-gap case: some employers would rather have
no union contract at all. The prediction is longer strikes, a fatter tail, and slower
settlement in the first group. The script compares the two groups with Kaplan-Meier curves, a
log-rank test, a Cox regression with controls, and the same gamma-mixture fit used in
src/coase_bargaining.py.

Writes results/gap_*.csv and results/gap_survival.png.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.duration.hazard_regression import PHReg
from scipy import stats
from statsmodels.duration.survfunc import SurvfuncRight, survdiff

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so the shared helpers import under python -I
from coase_bargaining import (BLUE, GRID, INK, MUTED, ORANGE, MIN_DAYS, delta_from_alpha, fit,
                              load_strikes)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results"
CHECK_DAYS = [7, 30, 60, 120]   # days at which the survival curves are read off


def label_groups(s):
    s = s[~s.censored].copy()   # main sample: strikes with a recorded end date
    s["group"] = np.where(s.first_contract, "first contract or recognition", "existing relationship")
    print(f"Strikes with an end date: {len(s)}; "
          f"{int(s.first_contract.sum())} first contract or recognition, {int((~s.first_contract).sum())} other")
    return s


def km_table(s, sample):
    rows = []
    for g, d in s.groupby("group"):
        sf = SurvfuncRight(d.duration_days.values, np.ones(len(d)))
        row = {"sample": sample, "group": g, "strikes": len(d), "median_days": d.duration_days.median(),
               "mean_days": d.duration_days.mean()}
        for k in CHECK_DAYS:
            idx = np.searchsorted(sf.surv_times, k, side="right") - 1
            row[f"still_running_after_{k}_days"] = 1.0 if idx < 0 else sf.surv_prob[idx]
        rows.append(row)
    stat, p = survdiff(s.duration_days.values, np.ones(len(s)), s.group.values)
    for r in rows:
        r["logrank_chi2"], r["logrank_p"] = stat, p
    return rows


def cox(s, sample):
    d = s.copy()
    n = d.participants.where(d.participants > 0)   # the tracker records some unknown counts as 0
    d["log_participants"] = np.log(n.fillna(n.median()))
    d["participants_missing"] = n.isna().astype(float)
    d["authorized"] = d.authorized_y.astype(float)
    d["first"] = d.first_contract.astype(float)
    years = pd.get_dummies(d.start.dt.year, prefix="y", drop_first=True).astype(float)
    X = pd.concat([d[["first", "log_participants", "participants_missing", "authorized"]], years], axis=1)
    grp = pd.factorize(d.employer.str.lower().str.strip())[0]
    res = PHReg(d.duration_days.values, X.values, status=np.ones(len(d))).fit(groups=grp)
    rows = []
    for i, name in enumerate(X.columns[:4]):
        rows.append({"sample": sample, "variable": name, "coef": res.params[i], "se_clustered": res.bse[i],
                     "hazard_ratio": np.exp(res.params[i]), "p": res.pvalues[i], "n": len(d),
                     "employer_clusters": int(grp.max() + 1)})
    return rows


def gamma_by_group(s):
    rows = []
    for g, d in s.groupby("group"):
        days = d.duration_days.values.astype(float)
        days = days[days >= MIN_DAYS]
        t, c = days - (MIN_DAYS - 1), np.zeros(len(days), bool)
        pg, se, ll = fit(t, c, "gamma")
        mean, th = np.exp(pg[0]), np.exp(pg[1])
        lam50 = stats.gamma.ppf(0.5, 1 / th, scale=mean * th)
        a50 = 1 - np.exp(-lam50)
        rows.append({"group": g, "strikes_lasting_4plus": len(t), "gamma_mean_daily_rate": mean, "gamma_theta": th,
                     "median_dispute_daily_share": a50, "median_dispute_loss_per_day": 1 - delta_from_alpha(a50),
                     "share_over_60_days": (days > 60).mean(), "share_over_120_days": (days > 120).mean()})
    return pd.DataFrame(rows)


def longest_first_contract(s):
    d = s[s.first_contract].sort_values("duration_days", ascending=False).head(10)
    return d[["employer", "labor_organization", "start_date", "end_date", "duration_days", "participants"]]


def short_strikes(s):
    """How many strikes in each group ended within MIN_DAYS - 1 days, and the employer most common among them."""
    rows = []
    for g, d in s.groupby("group"):
        short = d[d.duration_days < MIN_DAYS]
        top = short.employer.value_counts()
        rows.append({"group": g, "strikes": len(d), f"ended_within_{MIN_DAYS - 1}_days": len(short),
                     "most_common_employer_among_them": top.index[0], "its_count": int(top.iloc[0])})
    return pd.DataFrame(rows)


def plot(s, path):
    fig, ax = plt.subplots(figsize=(7.5, 4.4), dpi=150)
    for (g, d), col in zip(s.groupby("group"), [BLUE, ORANGE]):
        sf = SurvfuncRight(d.duration_days.values, np.ones(len(d)))
        ax.step(np.r_[0, sf.surv_times], np.r_[1, sf.surv_prob], where="post", color=col, lw=2,
                label=f"{g[0].upper() + g[1:]} ({len(d)} strikes)")
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlim(0, 1200)
    ax.set_xticks([1, 3, 7, 10, 30, 60, 120, 365, 1000])
    ax.set_xticklabels(["1", "3", "7", "10", "30", "60", "120", "365", "1,000"])
    ax.set_xlabel("Days on strike", color=MUTED)
    ax.set_ylabel("Share of strikes still running", color=MUTED)
    ax.set_title("First-contract strikes do not last longer", color=INK, loc="left", fontsize=12)
    ax.grid(color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    s = label_groups(load_strikes())
    long = s[s.duration_days >= MIN_DAYS]
    print(f"  {len(long)} of them lasted {MIN_DAYS}+ days")
    km = pd.DataFrame(km_table(s, "all strikes") + km_table(long, f"lasting {MIN_DAYS}+ days"))
    km.to_csv(OUT / "gap_survival.csv", index=False)
    print(km[["sample", "group", "strikes", "median_days", "still_running_after_30_days", "logrank_p"]]
          .round(4).to_string(index=False))
    cx = pd.DataFrame(cox(s, "all strikes") + cox(long, f"lasting {MIN_DAYS}+ days"))
    cx.to_csv(OUT / "gap_cox.csv", index=False)
    print(cx.round(4).to_string(index=False))
    gg = gamma_by_group(s)
    gg.to_csv(OUT / "gap_gamma_fits.csv", index=False)
    print(gg.round(4).to_string(index=False))
    longest_first_contract(s).to_csv(OUT / "gap_longest_first_contract.csv", index=False)
    sh = short_strikes(s)
    sh.to_csv(OUT / "gap_short_strikes.csv", index=False)
    print(sh.to_string(index=False))
    plot(s, OUT / "gap_survival.png")
    print("wrote results/gap_survival.csv, gap_cox.csv, gap_gamma_fits.csv, gap_longest_first_contract.csv,")
    print("      gap_short_strikes.csv, gap_survival.png")
