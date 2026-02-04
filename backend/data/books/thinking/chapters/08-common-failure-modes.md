# Common Failure Modes
## Vague goals; fuzzy definitions
- Example: "Make it better" invites thrash; "reduce p95 latency from 600ms to 300ms" focuses effort.

## Single-customer dependence (concentration risk)
- Example: If one customer drives most revenue, a single renegotiation or demand pause can break forecasts, covenants, and hiring plans.

## Overbuilding on leverage (balance-sheet fragility)
- Example: Financing assets aggressively works while demand is strong; it becomes dangerous if utilization drops and asset values fall.

## Premature optimization; local maxima
- Example: Tuning a query before confirming it's on the critical path is optimizing the wrong thing.

## Overconfidence; poor calibration
- Example: Always saying "90% sure" but being wrong half the time; fix with forecasting + scorekeeping.

## Narrative fallacy; hindsight bias
- Example: After a surprise outcome, we tell a clean story that makes it feel inevitable.
- Failure: Confusing a plausible narrative with the true causal process in a noisy world.
- Fix: Write pre-mortems and forecasts ex ante; compare to what actually happened.
- Tie-in: Use counterfactuals ("what else could have happened?") to stay honest about uncertainty.

## Confirmation bias; motivated reasoning
- Example: Only collecting user quotes that support your favorite feature; force a disconfirming-evidence step.

## Scope creep; uncontrolled constraints
- Example: "Just add export" becomes "export + templates + scheduling" without resetting time/cost constraints.

## Conflating correlation with causation
- Example: Two metrics move together after a redesign; you still need a mechanism or experiment to claim causation.

## Managing to proxies (process/metrics over outcomes)
- Example: Celebrating "OKRs completed" while retention drops; the proxy eclipsed the actual goal.


