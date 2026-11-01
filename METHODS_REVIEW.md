# Methods review: Gul, Sonnenschein & Wilson (1986)

- **Paper:** Faruk Gul, Hugo Sonnenschein and Robert Wilson, "Foundations of Dynamic Monopoly and the Coase
  Conjecture," *Journal of Economic Theory* 39(1), 1986, pp. 155–190.
- **Statistical focus:** Theorem 3 (the Coase conjecture for equilibria with stationary buyer strategies) and the
  closed-form linear-demand equilibria of Section 4 (Example 1's share served per period
  $`\alpha = \sigma/(1+\sigma)`$ with $`\sigma = \sqrt{1-\delta}`$, and Example 2's footnote 13 values at
  $`\delta = 0.9`$), which are the paper's only numerical results.
- **Review standard:** internal consistency of the formal results, explicitness of assumptions, and the
  testability of the predictions.
- **What was read:** the full published article (36 scanned pages) from the copy posted in David K. Levine's
  working paper archive (dklevine.com/archive/refs4232.pdf), read through its text layer. The introduction,
  Sections 1 to 6 and the statements and proofs of Lemmas 1 to 3 in the Appendix were read; the remaining
  Appendix proofs were not checked line by line. Several displayed equations are illegible in the text layer
  (noted below). Secondary sources were the paper's abstract on RePEc and the reading-list summary of Ausubel and
  Deneckere (1989).

## Research design

A game-theoretic model with no data. A monopolist with constant unit cost (normalized to zero) offers a price
each period to a unit measure of non-atomic buyers indexed by $`q \in [0,1]`$ with non-increasing values
$`f(q)`$; each buyer wants one unit; all players share a discount factor $`\delta`$. The solution concept is
subgame-perfect equilibrium, with a maintained hypothesis that players treat histories differing only by the
actions of measure-zero sets of buyers as equivalent (Section 1, and note 6.1 showing this has bite).

## Sampling strategy

Not applicable. There is no sample. The "population" is a continuum of buyer types fixed by $`f`$.

## Sample size

Not applicable. The worked examples use one market each.

## Inclusion and exclusion criteria

Not applicable as sampling criteria. The analogous restrictions are modeling assumptions: condition (B), the
lowest value is positive (gap case); condition (L), $`f`$ is Lipschitz at 1; equal discount factors; zero cost;
no new buyers enter; no resale is modeled. Theorem 2 adds analyticity of the buyers' strategy near $`q = 1`$.

## Independent and dependent variables

The primitives are the demand function $`f`$, the discount factor $`\delta`$ (interpreted as $`e^{-r d}`$ with
period length $`d`$), and cost. The outcomes are the equilibrium price path, the quantities sold per period, the
seller's present value, and the number of periods until the market clears.

## Statistical methods

Not applicable in the statistical sense. The methods are existence and uniqueness proofs (Theorems 1 and 2, with
a dynamic-programming characterization), explicit constructions for linear demand (Examples 1 to 3), and a limit
argument (Theorem 3). An intuitive sketch of the Theorem 3 argument appears in Section 5.

## Reported effect sizes

The formal analogues of effect sizes are the comparative statics: as $`\delta \to 1`$, the opening price, the
initial quantity and the seller's value all go to zero in Example 1, and in every equilibrium with stationary buyer
strategies the opening price goes to zero (or to the lowest value). The numerical values are in the table below.

## Confidence intervals

Not applicable. Results are exact.

## P-values, if applicable

Not applicable.

## Missing data treatment

Not applicable.

## Stated limitations

The authors state that without a gap there can be a continuum of stationary equilibria with different price paths
and profits, which "presents serious difficulties for the theory" (Section 4); that they could not prove their
conjecture of uniqueness for continuous buyer strategies and prove it only for analytic ones (Theorem 2); that the
measure-zero equivalence assumption restricts the equilibrium set (note 6.1); that non-stationary equilibria can be
built from multiple stationary ones (note 6.8); that their methods do not cover buyers with different discount
factors (note 6.7); and that the absence of new demand entering the market is central to the analysis (note 6.7).
Note 6.5 discusses Kahn's result that increasing marginal costs overturn the Coase conclusion.

## Methods summary

The paper characterizes subgame-perfect equilibria of a durable-goods (or one-shot purchase) monopoly in which the
seller cannot commit to future prices. In the gap case it proves generic uniqueness of the equilibrium path,
stationarity of buyer behavior, decreasing prices and finite-time market clearing. In the no-gap case it constructs
multiple equilibria for linear demand and proves uniqueness among analytic strategies. It then proves the Coase
conjecture for all equilibria with stationary buyer strategies and notes the formal equivalence with one-sided
offer bargaining under private information. The statements are explicit about their hypotheses, and the
examples verify the general claims in a tractable case.

## Statistics extraction table

| Statistic | Value and unit | Source location | What it measures | What it does not establish |
|---|---|---|---|---|
| Share of remaining buyers served per period, Example 1 | $`\alpha = \sigma/(1+\sigma)`$, $`\sigma = \sqrt{1-\delta}`$ (fraction) | Section 4, Example 1, pp. 163–164 | Pace of sales in the unique analytic stationary equilibrium with linear demand | The pace under other demand curves or in non-stationary equilibria |
| Opening price, Example 1 | $`\beta = \sigma/(1+\sigma)`$ (share of the top value) | Section 4, Example 1, p. 164 | First price when values are uniform on [0, 1] and cost is zero | Prices when buyers enter over time or costs rise with output |
| Seller's value, Example 1 | $`R(q) = \tfrac{1}{2}(1-q)^2 p(0)`$ (share of top value times measure) | Section 4, Example 1, p. 163 | Present value of remaining profit after serving $`q`$ buyers | Welfare or consumer surplus, which are not reported |
| Example 2 ratio of unserved buyers at $`\delta = 0.9`$ | 0.8247 (fraction) | Footnote 13, p. 166 | Per-period survival of unserved buyers in a non-analytic stationary equilibrium | That this equilibrium is more plausible than Example 1 |
| Example 2 opening price at $`\delta = 0.9`$ | 0.3199 (share of top value) | Footnote 13, p. 166 | First price in that equilibrium, above Example 1's 0.2403 | A general bound on prices across equilibria |
| Example 2 seller's value at $`\delta = 0.9`$ | 0.1446 | Footnote 13, p. 166 | Profit in that equilibrium, showing profits differ across equilibria | The size of the multiplicity for other $`\delta`$ |
| Section 2 example equilibrium path | prices 2 then 1; one unit of mass sold at each (values 3 and 1, $`\delta = 1/2`$) | Section 2, p. 160 | A two-type gap market clearing in two periods with off-path randomization | Anything about continuous type distributions |
| Theorem 3 (Coase conjecture) | For every $`\varepsilon > 0`$ there is $`\bar\delta < 1`$ with opening price below $`\varepsilon`$ for $`\delta > \bar\delta`$ | Section 5, p. 168 | Limit of the opening price as periods shorten, over all equilibria with stationary buyer strategies | How fast the limit is reached in real time, or behavior in non-stationary equilibria |
| Theorem 1 | Generic unique path, decreasing prices, finite number of offers | Section 3, pp. 161–162 | Determinacy in the gap case | Determinacy without a gap |

## Interpretation notes

- The Coase conjecture is a limit statement about the opening price. It says nothing directly about how quickly
  sales happen in calendar time for a given period length. In Example 1 the opening price shrinks like
  $`\sqrt{1-\delta}`$, and the median delay in calendar time also shrinks with the square root of the period
  length but is inversely proportional to the square root of the interest rate, so with realistic interest rates
  and daily price changes the market can still take weeks to clear. This repository's `coase_limit.csv` computes that schedule; the paper itself does not.
- The result depends on buyer strategies being stationary. The paper builds the multiplicity (Examples 2 and 3)
  and the non-stationary constructions (note 6.8) that Ausubel and Deneckere (1989) later used to show that the
  seller can approach monopoly profits in the no-gap case. That is an extension of the paper's own warnings, not
  a correction.
- The bargaining equivalence in note 6.2 holds under the measure-zero equivalence hypothesis; note 6.1 gives an
  equilibrium of the monopoly game that is not an equilibrium of the bargaining game without it.
- The modern rerun in this repository uses the bargaining reading to derive a testable implication (a constant
  settlement hazard under Example 1) and confronts it with strike data. That is a test of an implication under
  added assumptions (uniform private values, one-sided offers, daily rounds), not a reproduction of anything in
  the paper, which reports no data.

## Unanswered questions

- How should the per-period discount factor be calibrated outside the durable-goods setting, where the cost of
  delay is not just interest?
- Which equilibrium is selected when there is no gap, and is there an observable signature that distinguishes the
  analytic stationary equilibrium from the others?
- How robust are the conclusions to new buyers entering each period, a feature the authors flag as central?
- Does the uniqueness conjecture for continuous (not necessarily analytic) buyer strategies hold?

## Items requiring expert verification

- The text layer of the scanned copy garbles the displayed equation that determines Example 2's parameter and the
  condition on $`\delta`$ under which the construction is an equilibrium (p. 166). The cubic used in this
  repository, $`\delta a^3 - a^2 - a + 1 = 0`$, was derived from the paper's three recursions and reproduces
  footnote 13 to four decimals, but it should be checked against a clean copy.
- The present value quoted at the end of the Section 2 example (p. 161) is illegible in the text layer and is not
  reported here.
- The Appendix proofs of Theorems 1 to 3 were not verified line by line.
- No published correction or comment documenting an error in the paper was found in the sources read.
