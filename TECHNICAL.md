# Technical notes

This is the technical companion to the [README](README.md). It covers the original study, the data, the rules,
the full set of test statistics and how to reproduce everything. Every table is in
[results/FINDINGS.md](results/FINDINGS.md), and a methods review of the original paper is in
[METHODS_REVIEW.md](METHODS_REVIEW.md).

## The original study

Faruk Gul, Hugo Sonnenschein and Robert Wilson, "Foundations of Dynamic Monopoly and the Coase Conjecture,"
*Journal of Economic Theory* 39(1), 1986, pp. 155–190. A seller with zero cost names a price each period to a
continuum of buyers with values $`f(q)`$; everyone discounts by $`\delta`$. Theorem 1 shows that when the lowest
value exceeds cost (the gap case), the equilibrium path is generically unique, prices decline, and the market
clears in finitely many periods. Section 4 shows that without a gap there can be a continuum of stationary
equilibria (Examples 2 and 3), only one of them analytic (Theorem 2). Theorem 3 (the Coase conjecture) says that
for any $`\varepsilon > 0`$ there is a $`\bar\delta < 1`$ such that for $`\delta > \bar\delta`$ every equilibrium
with stationary buyer strategies opens below $`\varepsilon`$ (or below the lowest value plus $`\varepsilon`$ in the
gap case). Note 6.2 states the formal equivalence with a seller making repeated offers to one privately informed
buyer. The paper is theory; its numbers are Example 1's closed form and footnote 13's values for Example 2 at
$`\delta = 0.9`$ (0.8247, 0.3199, 0.1446).

Example 1 (linear demand $`f(q) = 1 - q`$) gives

```math
\alpha = \beta = \frac{\sigma}{1+\sigma}, \qquad \sigma = \sqrt{1-\delta}, \qquad R(0) = \tfrac{1}{2}\beta
```

where $`\alpha`$ is the share of remaining buyers served each period, $`\beta`$ the opening price and $`R(0)`$ the
seller's value. Example 2's ratio $`a`$ of unserved buyers solves

```math
\delta a^3 - a^2 - a + 1 = 0, \qquad p_0 = \frac{(1-\delta)\,a}{1-\delta a}, \qquad R_0 = \frac{p_0\, a}{1+a}
```

which I derived from the paper's three recursions (indifference, value recursion, continuity of the value).

## Headline results

| Test | Estimate | Uncertainty | N |
|---|---|---|---|
| Footnote 13, Example 2 at δ = 0.9 | a = 0.8247, p₀ = 0.3199, R₀ = 0.1446 | exact match | |
| Example 1 closed form vs numerical solution | agree within 10⁻¹² at δ = 0.5, 0.9, 0.99, 0.999 | | |
| Daily settlement rate, days 4–6 vs day 120+ | 7.5% vs 0.8% | 95% CI [6.3, 8.8] vs [0.6, 1.1] | 714 |
| Weibull shape k (flat hazard: k = 1) | 0.652 | [0.617, 0.690]; LR 293.7, p < 0.001 | 714 |
| Gamma-mixture θ (one common rate: θ = 0) | 0.703 | [0.578, 0.854]; LR 311.5, p < 0.001 | 714 |
| AIC, exponential / Weibull / gamma mixture | 6,446.6 / 6,154.8 / 6,137.0 | | 714 |
| Implied loss per day, median dispute | 0.36% (25 × daily interest) | | 714 |
| Cox, first contract (all strikes) | β = 0.184, HR 1.20 | SE 0.066, p = 0.006 | 1,841 |
| Cox, first contract (lasting 4+ days) | β = −0.044, HR 0.96 | SE 0.112, p = 0.69 | 714 |
| Log-rank, first contract (lasting 4+ days) | χ² = 0.003 | p = 0.95 | 714 |

## Data

| File | Source | Content |
|---|---|---|
| `data/raw/labor_action_tracker_strikes.csv` | ILR Labor Action Tracker, `https://striketracker.ilr.cornell.edu/labor_actions.json` | 1,999 strike rows, start dates 2021-01-01 to 2026-10-30, with employer, union, dates, duration, participants, authorization, demands, states |
| `data/raw/fred_baa.csv` | FRED, `fredgraph.csv?id=BAA` | Moody's seasoned Baa corporate bond yield, monthly, 1919–2026 |
| `data/raw/DOWNLOADED.txt` | | Download date (2026-11-01) and URLs |

The tracker's duration is end date minus start date plus one, in calendar days.

## Method

Rules fixed before any model was fit:

- Sample: strikes starting 2021-01-01 to 2026-09-30 (1,984); the month before the download is left for end dates
  to be recorded. Strikes with no end date (143) are dropped from the main runs.
- Hazard tests use strikes still running on day 4 (714), with time $`t = D - 3`$. Short strikes are often
  called for a fixed period (40% of strikes with an end date last exactly one day); a constant hazard is memoryless, so conditioning on survival does not bias the test.
- Durations are whole days, so each likelihood term is interval-censored.

```math
\log L(\vartheta) = \sum_{i:\,\text{ended}} \log\big[S(t_i - 1;\vartheta) - S(t_i;\vartheta)\big] + \sum_{i:\,\text{open}} \log S(t_i;\vartheta)
```

- Survival functions: exponential $`e^{-\lambda t}`$; Weibull $`e^{-(\lambda t)^k}`$; gamma mixture of exponentials
  $`(1 + \theta\lambda t)^{-1/\theta}`$, the marginal survival when each dispute has rate
  $`\lambda_i \sim \text{Gamma}(1/\theta,\ \theta\lambda)`$. Parameters are estimated in logs; standard errors come
  from the inverse numerical Hessian; confidence intervals for $`k`$ and $`\theta`$ are exponentiated log-scale
  intervals. LR tests use $`\chi^2_1`$; the $`\theta = 0`$ test is on the boundary and uses half the $`\chi^2_1`$
  tail.
- Implied discounting: a daily settlement share $`\alpha = 1 - e^{-\lambda}`$ maps to Example 1's per-day factor by

```math
\delta = 1 - \Big(\frac{\alpha}{1-\alpha}\Big)^{2}
```

- Interest benchmark: mean Baa yield over 2021–2025 (5.22%), $`\delta = e^{-r\Delta/365}`$ for offer intervals
  from a year to an hour; the commitment benchmark is the static monopoly price 1/2 and profit 1/4.
- Binned hazards: settlements divided by strike-days at risk in each window; exact Poisson intervals.
- Robustness samples: strikes still running on day 8 (time from day 8), union-authorized, pay among the demands,
  1,000+ participants, and 2026 strikes with no end date treated as censored on 2026-10-30.
- Extension: first contract or recognition = tracker demand "First contract" or "Union recognition". Kaplan–Meier
  curves, log-rank test, and a Cox model with log participants (counts of 0 treated as missing; missing counts
  median-filled plus a missing dummy),
  authorization, and start-year effects; standard errors clustered by employer (lower-cased name).

## Full test statistics

| Sample | N | Weibull k [95% CI] | LR vs exp. | Gamma θ [95% CI] | AIC Weibull | AIC gamma |
|---|---|---|---|---|---|---|
| All strikes, day 4+ | 714 | 0.652 [0.617, 0.690] | 293.7 | 0.703 [0.578, 0.854] | 6,154.8 | 6,137.0 |
| Day 8+ | 513 | 0.707 [0.663, 0.755] | 134.4 | 0.523 [0.401, 0.682] | 4,729.0 | 4,712.3 |
| Union-authorized | 606 | 0.670 [0.631, 0.711] | 219.4 | 0.646 [0.518, 0.805] | 5,336.5 | 5,317.4 |
| Pay among demands | 542 | 0.662 [0.621, 0.705] | 211.0 | 0.651 [0.518, 0.820] | 4,700.0 | 4,680.7 |
| 1,000+ participants | 103 | 0.670 [0.577, 0.777] | 35.0 | 0.702 [0.420, 1.173] | 890.0 | 888.3 |
| 2026 open strikes censored | 753 | 0.620 [0.586, 0.657] | 349.4 | 0.954 [0.802, 1.133] | 6,355.0 | 6,327.4 |

All p-values for the exponential restriction are below 0.001. In the Cox model on strikes lasting 4+ days,
authorization has a hazard ratio of 0.640 (SE of β 0.121, p < 0.001); log participants 1.020 (p = 0.40).

## Reproducing the results

```bash
pip install -r requirements.txt
python src/fetch_data.py          # optional: refreshes data/raw/ (the committed copies are used otherwise)
python src/coase_bargaining.py    # model replication, hazard tests, implied discounting, two figures
python src/gap_test.py            # extension: first contract vs existing relationship
```

Python 3.12 or later. Refreshing the data will add strikes recorded after 2026-11-01 and change the numbers.

## Repository layout

| Path | What it is |
|---|---|
| `src/fetch_data.py` | Downloads and trims the tracker and FRED files |
| `src/coase_bargaining.py` | Examples 1 and 2, Coase limit, duration models, implied discounting, named-strike tables |
| `src/gap_test.py` | Gap / no-gap extension |
| `results/*.csv`, `results/*.png` | Every number and figure in the README |

## References

- Ausubel, L. M. & Deneckere, R. J. (1989). Reputation in bargaining and durable goods monopoly. *Econometrica* 57(3), 511–531.
- Coase, R. H. (1972). Durability and monopoly. *Journal of Law and Economics* 15(1), 143–149.
- Gul, F., Sonnenschein, H. & Wilson, R. (1986). Foundations of dynamic monopoly and the Coase conjecture. *Journal of Economic Theory* 39(1), 155–190.
- Kennan, J. & Wilson, R. (1993). Bargaining with private information. *Journal of Economic Literature* 31(1), 45–104.
- ILR Labor Action Tracker, Cornell University ILR School and University of Illinois LER, striketracker.ilr.cornell.edu.
- Moody's seasoned Baa corporate bond yield (BAA), Federal Reserve Bank of St. Louis, FRED.
