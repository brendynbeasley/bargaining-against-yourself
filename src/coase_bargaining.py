"""Gul, Sonnenschein & Wilson (1986) on American strikes, 2021-2026.

Run from the repository root (after src/fetch_data.py has saved data/raw/):

    python src/coase_bargaining.py

Part 1 reproduces the paper's two worked examples for linear demand (Example 1, the analytic
stationary equilibrium, and the footnote 13 numbers for Example 2) and shows the Coase limit:
how the opening price, the seller's profit and the time to clear the market change as the
interval between offers shrinks.

Part 2 takes the paper's bargaining reading (note 6.2: a seller with known cost makes repeated
offers to one buyer with private information) to strikes. In the stationary linear equilibrium
a constant share of the remaining types settles in every round, so strike durations should have
a flat daily hazard. The script measures the hazard in the Labor Action Tracker, fits three
duration models by maximum likelihood (exponential, Weibull, exponential with gamma-distributed
dispute-specific rates), and translates the fitted settlement rates into the per-day discount
factor the paper's formula requires.

Writes results/*.csv and results/*.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, special, stats
from statsmodels.tools.numdiff import approx_hess

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

DATA_DATE = pd.Timestamp("2026-10-30")   # last start date in the tracker download (data/raw/DOWNLOADED.txt)
FIRST_START = pd.Timestamp("2021-01-01")  # tracker coverage begins here
LAST_START = pd.Timestamp("2026-09-30")   # leave a month for end dates to be recorded
RECENT_OPEN = pd.Timestamp("2026-01-01")  # open strikes starting on or after this date are treated as ongoing
MIN_DAYS = 4          # main sample: strikes still running on day 4; 1-3 day strikes are mostly announced in advance
RATE_YEARS = (2021, 2025)                 # years averaged for the Baa interest-rate benchmark
OFFER_INTERVALS = {"once a year": 365.0, "once a quarter": 91.25, "once a month": 30.4,
                   "once a week": 7.0, "once a day": 1.0, "once an hour": 1 / 24}
EX2_MIN_DELTA = 0.9   # Example 2 needs a large discount factor; the paper's own numbers use 0.9
BIG_STRIKE = 10_000   # participants threshold for the table of named strikes
BLUE, ORANGE, AQUA, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e4e3df"


# ---------------------------------------------------------------- Part 1: the model
def example1(delta):
    """Closed form of Example 1 (linear demand f(q) = 1 - q, zero cost): share of remaining
    buyers served each period alpha, opening price beta, seller's value R(0)."""
    s = np.sqrt(1 - delta)
    alpha = s / (1 + s)
    return alpha, alpha, alpha / 2


def example1_numeric(delta):
    """Solve the same equilibrium from its three conditions without the closed form: the
    marginal buyer's indifference, the seller's first-order condition and the value recursion."""
    def gap(x):  # x = share of remaining buyers who wait
        g = (1 - delta) / (1 - delta * x)
        a = (1 - x) * x * g / (1 - delta * x * x)
        return x - g / (2 * (g - delta * a))
    x = optimize.brentq(gap, 1e-9, 1 - 1e-12)
    g = (1 - delta) / (1 - delta * x)
    return 1 - x, x * g, (1 - x) * x * g / (1 - delta * x * x)


def example2(delta):
    """Example 2 (non-analytic stationary equilibrium): a solves delta a^3 - a^2 - a + 1 = 0,
    p0 = (1 - delta) a / (1 - delta a), R0 = p0 a / (1 + a)."""
    a = optimize.brentq(lambda a: delta * a**3 - a**2 - a + 1, 0.5, 1 - 1e-12)
    p0 = (1 - delta) * a / (1 - delta * a)
    return a, p0, p0 * a / (1 + a)


def delta_from_alpha(alpha):
    """Invert alpha = s / (1 + s), s = sqrt(1 - delta)."""
    s = alpha / (1 - alpha)
    return 1 - s**2


def baa_rate():
    df = pd.read_csv(RAW / "fred_baa.csv")
    df.columns = ["date", "baa"]
    df["year"] = pd.to_datetime(df.date).dt.year
    sel = df[(df.year >= RATE_YEARS[0]) & (df.year <= RATE_YEARS[1])]
    print(f"FRED BAA: {len(df)} months loaded, {len(sel)} used ({RATE_YEARS[0]}-{RATE_YEARS[1]})")
    return sel.baa.mean() / 100


def model_tables(r):
    rows = []
    for d in [0.5, 0.9, 0.99, 0.999]:
        a1, b1, r1 = example1(d)
        a1n, b1n, r1n = example1_numeric(d)
        a2, p2, r2 = example2(d) if d >= EX2_MIN_DELTA else (np.nan, np.nan, np.nan)
        rows.append({"delta": d, "ex1_alpha_closed": a1, "ex1_alpha_numeric": a1n,
                     "ex1_price0": b1, "ex1_value0": r1, "ex1_value0_numeric": r1n,
                     "ex2_a": a2, "ex2_price0": p2, "ex2_value0": r2})
    t1 = pd.DataFrame(rows)
    t1.to_csv(OUT / "model_examples.csv", index=False)
    a, p0, r0 = example2(0.9)
    print(f"Example 2 at delta = 0.9: a = {a:.4f}, p0 = {p0:.4f}, R0 = {r0:.4f} "
          f"(paper, footnote 13: 0.8247, 0.3199, 0.1446)")

    rows = []
    for label, days in OFFER_INTERVALS.items():
        d = np.exp(-r * days / 365)
        alpha, p0, v0 = example1(d)
        rows.append({"offer_interval": label, "days_between_offers": days, "annual_rate": r,
                     "delta_per_offer": d, "share_settling_per_offer": alpha,
                     "opening_price_share_of_top_value": p0,
                     "opening_price_vs_commitment_price": p0 / 0.5,
                     "seller_profit_vs_commitment": v0 / 0.25,
                     "median_days_to_sale": days * np.log(0.5) / np.log(1 - alpha),
                     "mean_days_to_sale": days * (1 - alpha) / alpha})
    t2 = pd.DataFrame(rows)
    t2.to_csv(OUT / "coase_limit.csv", index=False)
    print(t2[["offer_interval", "opening_price_vs_commitment_price", "seller_profit_vs_commitment",
              "median_days_to_sale"]].round(4).to_string(index=False))
    return t2


# ---------------------------------------------------------------- Part 2: strikes
def load_strikes():
    s = pd.read_csv(RAW / "labor_action_tracker_strikes.csv")
    n0 = len(s)
    s["start"] = pd.to_datetime(s.start_date)
    s["end"] = pd.to_datetime(s.end_date)
    s = s[(s.start >= FIRST_START) & (s.start <= LAST_START)].copy()
    print(f"Tracker strikes loaded: {n0}; {len(s)} start between {FIRST_START.date()} and {LAST_START.date()}")
    s["censored"] = s.end.isna()
    # robustness run only: a 2026 strike with no recorded end is treated as still running on DATA_DATE;
    # older strikes with no end date cannot be placed and stay out of every run
    s["recent_open"] = s.censored & (s.start >= RECENT_OPEN)
    s["days_cens"] = np.where(s.censored, (DATA_DATE - s.start).dt.days + 1, s.duration_days)
    s["pay"] = s.demands.fillna("").str.contains("Pay")
    s["first_contract"] = s.demands.fillna("").str.contains("First contract|Union recognition")
    s["authorized_y"] = s.authorized.eq("Y")
    print(f"  {int(s.censored.sum())} have no end date: all dropped in the main sample; "
          f"{int(s.recent_open.sum())} that began in 2026 are censored in a robustness run")
    return s


def interval_loglik(params, t, cens, model):
    """Log likelihood for durations counted in whole days after day MIN_DAYS - 1.
    A strike ending on day t contributes S(t-1) - S(t); a censored one contributes S(t)."""
    lam = np.exp(params[0])
    if model == "exp":
        logS = lambda u: -lam * u
    elif model == "weibull":
        k = np.exp(params[1])
        logS = lambda u: -(lam * u) ** k
    else:  # gamma-mixed exponential, theta = variance of the dispute rate / mean^2
        th = np.exp(params[1])
        logS = lambda u: -np.log1p(th * lam * u) / th
    ls_t, ls_prev = logS(t), logS(t - 1)
    ev = ls_prev + np.log(-np.expm1(np.minimum(ls_t - ls_prev, -1e-300)))
    return np.where(cens, ls_t, ev).sum()


def fit(t, cens, model):
    k = 1 if model == "exp" else 2
    start = np.array([np.log(1 / t.mean())] + [0.0] * (k - 1))
    nll = lambda p: -interval_loglik(p, t, cens, model)
    res = optimize.minimize(nll, start, method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-9, "maxiter": 20000})
    res = optimize.minimize(nll, res.x, method="BFGS")
    cov = np.linalg.inv(approx_hess(res.x, nll))
    return res.x, np.sqrt(np.diag(cov)), -res.fun


def hazard_bins(t, cens):
    edges = [4, 7, 14, 30, 60, 120, 100000]
    labels = ["days 4-6", "days 7-13", "days 14-29", "days 30-59", "days 60-119", "day 120+"]
    rows = []
    for lab, a, b in zip(labels, edges[:-1], edges[1:]):
        at_risk = t >= a
        exposure = (np.minimum(t, b - 1) - a + 1)[at_risk].sum()
        events = ((t >= a) & (t < b) & ~cens).sum()
        lo = stats.chi2.ppf(0.025, 2 * events) / 2 / exposure if events else 0.0
        hi = stats.chi2.ppf(0.975, 2 * events + 2) / 2 / exposure
        rows.append({"interval": lab, "strikes_at_risk": int(at_risk.sum()), "settlements": int(events),
                     "strike_days": int(exposure), "daily_settlement_rate": events / exposure,
                     "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


def run_sample(name, d, use_censored=False):
    if use_censored:
        keep = ~d.censored | d.recent_open
        days, cens = d.days_cens.values[keep].astype(float), d.censored.values[keep]
    else:
        keep = ~d.censored
        days, cens = d.duration_days.values[keep].astype(float), np.zeros(keep.sum(), bool)
    sel = days >= MIN_DAYS if name != "lasting 8+ days" else days >= 8
    shift = (MIN_DAYS - 1) if name != "lasting 8+ days" else 7
    t, c = days[sel] - shift, cens[sel]
    pe, se_e, ll_e = fit(t, c, "exp")
    pw, se_w, ll_w = fit(t, c, "weibull")
    pg, se_g, ll_g = fit(t, c, "gamma")
    lam_e = np.exp(pe[0])
    k, k_lo, k_hi = np.exp(pw[1]), np.exp(pw[1] - 1.96 * se_w[1]), np.exp(pw[1] + 1.96 * se_w[1])
    th = np.exp(pg[1])
    lr_w = 2 * (ll_w - ll_e)
    lr_g = 2 * (ll_g - ll_e)
    row = {"sample": name, "strikes": int(sel.sum()), "censored": int(c.sum()),
           "median_days_after_start": float(np.median(days[sel])),
           "exp_daily_rate": lam_e, "exp_daily_share": 1 - np.exp(-lam_e),
           "exp_rate_se": lam_e * se_e[0], "exp_loglik": ll_e,
           "weibull_shape_k": k, "weibull_k_ci_low": k_lo, "weibull_k_ci_high": k_hi, "weibull_loglik": ll_w,
           "lr_exp_vs_weibull": lr_w, "p_exp_vs_weibull": stats.chi2.sf(lr_w, 1),
           "gamma_mean_rate": np.exp(pg[0]), "gamma_theta": th,
           "gamma_theta_ci_low": np.exp(pg[1] - 1.96 * se_g[1]), "gamma_theta_ci_high": np.exp(pg[1] + 1.96 * se_g[1]),
           "gamma_loglik": ll_g, "lr_exp_vs_gamma": lr_g, "p_exp_vs_gamma": 0.5 * stats.chi2.sf(lr_g, 1),
           "aic_exp": 2 - 2 * ll_e, "aic_weibull": 4 - 2 * ll_w, "aic_gamma": 4 - 2 * ll_g}
    return row, (t, c, pe, pw, pg)


def implied_discounting(row, r):
    """Translate fitted daily settlement rates into Example 1's per-day discount factor."""
    rows = []
    a = row["exp_daily_share"]
    rows.append({"what": "one common rate (exponential fit)", "daily_settlement_share": a,
                 "implied_delta_per_day": delta_from_alpha(a), "implied_loss_per_day": 1 - delta_from_alpha(a)})
    shape, mean = 1 / row["gamma_theta"], row["gamma_mean_rate"]
    for q in [0.10, 0.25, 0.50, 0.75, 0.90]:
        lam = stats.gamma.ppf(q, shape, scale=mean / shape)
        a = 1 - np.exp(-lam)
        rows.append({"what": f"dispute rates, {int(q * 100)}th percentile (gamma fit)", "daily_settlement_share": a,
                     "implied_delta_per_day": delta_from_alpha(a), "implied_loss_per_day": 1 - delta_from_alpha(a)})
    d = np.exp(-r / 365)
    a = example1(d)[0]
    rows.append({"what": f"interest only: Baa yield {r:.2%} a year, daily offers", "daily_settlement_share": a,
                 "implied_delta_per_day": d, "implied_loss_per_day": 1 - d})
    out = pd.DataFrame(rows)
    # half-life: days until half of the disputes settling at this daily share have settled
    out["half_life_days"] = np.log(0.5) / np.log(1 - out.daily_settlement_share)
    out["loss_per_day_vs_interest"] = out.implied_loss_per_day / (1 - d)
    return out


def big_strikes(s):
    b = s[(s.participants >= BIG_STRIKE)].sort_values("participants", ascending=False)
    b = b[["employer", "labor_organization", "start_date", "end_date", "duration_days", "participants"]].copy()
    b["labor_organization"] = b.labor_organization.str.replace(" \u2013 ", ", ", regex=False)  # dash in one union name
    print(f"Strikes with {BIG_STRIKE:,}+ participants: {len(b)}")
    return b


def longest_strikes(s, n=10):
    """The longest strikes with an end date, flagged by whether they were for a first contract or recognition."""
    b = s[~s.censored].sort_values("duration_days", ascending=False).head(n)
    return b[["employer", "labor_organization", "start_date", "end_date", "duration_days", "participants",
              "first_contract"]]


def plot_survival(t, c, pe, pg, path):
    order = np.sort(np.unique(t))
    surv, s = [], 1.0
    for u in order:
        n = (t >= u).sum()
        dd = ((t == u) & ~c).sum()
        s *= 1 - dd / n
        surv.append(s)
    grid = np.arange(0, order.max() + 1)
    fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=150)
    ax.step(np.r_[0, order], np.r_[1, surv], where="post", color=INK, lw=2, label="Strikes still running (data)")
    lam = np.exp(pe[0])
    ax.plot(grid, np.exp(-lam * grid), color=ORANGE, lw=2, ls="--",
            label="One common settlement rate (stationary model)")
    lg, th = np.exp(pg[0]), np.exp(pg[1])
    ax.plot(grid, (1 + th * lg * grid) ** (-1 / th), color=BLUE, lw=2,
            label="Each dispute its own rate (gamma mixture)")
    ax.set_yscale("log")
    ax.set_ylim(0.003, 1.05)
    ax.set_xlim(0, 400)
    ax.set_xlabel("Days since day 3 of the strike", color=MUTED)
    ax.set_ylabel("Share of strikes still running (log scale)", color=MUTED)
    ax.set_title("Strikes that last a week tend to last much longer", color=INK, loc="left", fontsize=12)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.grid(color=GRID, lw=0.8)
    ax.tick_params(colors=MUTED)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_coase(t2, path):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), dpi=150)
    x = np.arange(len(t2))   # evenly spaced categories, longest interval on the left
    axes[0].plot(x, 100 * t2.opening_price_vs_commitment_price, color=BLUE, lw=2, marker="o", ms=6)
    axes[0].set_ylabel("Opening price, % of the commitment price", color=MUTED)
    axes[1].plot(x, t2.median_days_to_sale, color=ORANGE, lw=2, marker="o", ms=6)
    axes[1].set_ylabel("Median days until a buyer purchases", color=MUTED)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(["year", "quarter", "month", "week", "day", "hour"])
        ax.set_xlabel("Time between price offers", color=MUTED)
        ax.grid(color=GRID, lw=0.8)
        ax.tick_params(colors=MUTED)
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
    axes[0].set_title("Prices collapse as offers speed up", color=INK, loc="left", fontsize=11)
    axes[1].set_title("Sales take weeks to years", color=INK, loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    r = baa_rate()
    t2 = model_tables(r)
    plot_coase(t2, OUT / "coase_limit.png")

    s = load_strikes()
    print(f"  {int((s.duration_days < MIN_DAYS).sum())} ended within {MIN_DAYS - 1} days "
          f"(excluded from the hazard tests, kept in the overview)")
    ended = s.loc[~s.censored, "duration_days"]   # duration statistics use strikes with an end date only
    overview = pd.DataFrame([{
        "strikes": len(s), "with_end_date": len(ended),
        "median_days": ended.median(), "mean_days": ended.mean(),
        "share_1_day": (ended == 1).mean(), "share_1_to_3_days": (ended <= 3).mean(),
        "share_over_30_days": (ended > 30).mean(), "share_over_100_days": (ended > 100).mean(),
        "max_days": ended.max()}])
    overview.to_csv(OUT / "strike_overview.csv", index=False)

    samples = [("all strikes", s, False), ("lasting 8+ days", s, False),
               ("union-authorized", s[s.authorized_y], False), ("pay among the demands", s[s.pay], False),
               ("1,000+ participants", s[s.participants >= 1000], False),
               ("2026 strikes with no end date censored", s, True)]
    rows, keep = [], None
    for name, d, cflag in samples:
        row, payload = run_sample(name, d, cflag)
        rows.append(row)
        if name == "all strikes":
            keep = payload
        print(f"  {name}: N = {row['strikes']}, Weibull k = {row['weibull_shape_k']:.3f} "
              f"[{row['weibull_k_ci_low']:.3f}, {row['weibull_k_ci_high']:.3f}], "
              f"LR exp vs gamma = {row['lr_exp_vs_gamma']:.1f}")
    fits = pd.DataFrame(rows)
    fits.to_csv(OUT / "duration_fits.csv", index=False)

    t, c, pe, pw, pg = keep
    hb = hazard_bins(t + MIN_DAYS - 1, c)
    hb.to_csv(OUT / "hazard_by_duration.csv", index=False)
    print(hb.round(4).to_string(index=False))
    imp = implied_discounting(fits.iloc[0], r)
    imp.to_csv(OUT / "implied_discounting.csv", index=False)
    print(imp.round(5).to_string(index=False))
    big_strikes(s).to_csv(OUT / "big_strikes.csv", index=False)
    longest_strikes(s).to_csv(OUT / "longest_strikes.csv", index=False)
    plot_survival(t, c, pe, pg, OUT / "strike_survival.png")
    print("wrote results/model_examples.csv, coase_limit.csv, strike_overview.csv, duration_fits.csv,")
    print("      hazard_by_duration.csv, implied_discounting.csv, big_strikes.csv, longest_strikes.csv")
    print("      and two figures")
