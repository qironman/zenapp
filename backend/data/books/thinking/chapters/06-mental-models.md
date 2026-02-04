# Mental Models (Toolbox)

## First principles vs analogy
- Example: Instead of copying a competitor's pricing, derive value drivers (costs, willingness-to-pay, constraints) from scratch.
- Use analogy when explaining complex or unfamiliar concepts by relating them to something the audience already understands
- Use first principles when you need to strip away assumptions and rebuild understanding from fundamental truths
- Use inductive reasoning when drawing general conclusions from specific observations or patterns in data
- Use deductive reasoning when applying established principles or rules to reach specific, logical conclusions
- Use systems thinking when analyzing interconnected elements and understanding how they influence each other within the larger whole
## Occam's razor (simplicity with adequate explanation)


## Inversion (avoid failure modes)
- Example: For "how do we succeed?", also list "how could we fail?" (e.g., churn, outages, bad positioning) and mitigate.
- Example: For "how do we build trust with customers?", invert to "what would destroy their trust?" (e.g., data breaches, lying, ignoring feedback) and avoid those.
- Example: For "how do we hire great people?", ask "what leads to bad hires?" (e.g., rushing, ignoring red flags, unclear role) and prevent that.
- Example: For "how do we stay healthy?", think "what makes us sick?" (e.g., poor sleep, stress, bad diet) and eliminate those habits.
  
## Opportunity cost and tradeoffs
- Example: Saying yes to a side project is saying no to sleep, health, or your main work; make the trade explicit.

## Middle Way (avoid extremes; find stable balance)
- Example: At work, neither "say yes to everything" nor "refuse all pressure";
  set boundaries while still owning responsibilities.
- Heuristic: Identify the two extremes, then pick a constrained middle path that can be sustained.
- Use: Avoid boom-bust cycles (sprints then burnout); build a pace you can keep.
- Boundary pattern: protect sleep/health basics first, then negotiate scope, then optimize.
- Tie-in: Pairs well with reversibility (test a boundary, learn, adjust).
- Source: Buddhist teaching on the Middle Way (TODO: add a canonical sutta reference).

## Expected value and utility
- Example: Two job offers: one with higher expected comp but higher burnout risk; optimize utility, not just dollars.

## Monte Carlo thinking (simulate distributions)
- Example: Instead of "will this work?", simulate 1,000 plausible paths and look at the probability of ruin and upside.
- Use: Turn uncertainty into a distribution (ranges, probabilities) to avoid single-point overconfidence.
- Practical: When you can't compute, do "mental Monte Carlo" with a few distinct scenarios and weights.
- Model pointers:
  - ### Probabilistic thinking (Bayes; calibration; base rates)
  - ### Counterfactual thinking (alternative histories; decision vs outcome)

## Skewness and fat tails (nonlinear payoffs)
- Example: A strategy can win small amounts frequently and still be bad if it occasionally blows up (ruin).
- Key idea: Average returns hide distribution shape; tails dominate long-run outcomes.
- Use: Avoid hidden short-vol trades (earning pennies, risking dollars) unless you can survive tail events.
- Model pointers:
  - ### Expected value and utility
  - ### Overbuilding on leverage (balance-sheet fragility)

## Marginal thinking (next unit; diminishing returns)
- Example: The first hour of refactoring helps a lot; the 20th hour may be polish with low marginal benefit.

## Compounding (time as a multiplier)
- Example: Reading 20 pages/day compounds into dozens of books/year; so does daily technical debt.

## Flywheel (reinforcing loop; momentum)
- Example: Better product -> more users -> more data/feedback -> better product -> repeat.
- Structure: input -> mechanism -> output -> reinvestment -> stronger input.
- Design steps:
  - Pick a high-frequency input you can do weekly (ship, write, sell, practice).
  - Make output measurable (retention, referrals, skill, cash flow, reach).
  - Reinvest output into the mechanism (tooling, distribution, training, capacity).
  - Reduce friction (time-to-first-value, onboarding, waiting, handoffs).
  - Add feedback loops (instrument, review, adjust).
- Personal flywheel: sleep + exercise -> energy -> better work -> confidence -> consistency -> better sleep.
- Failure mode: confusing motion with momentum; choose inputs that produce real feedback, not vanity activity.
- Model pointers:
  - ### Systems thinking (feedback loops; delays; second-order effects)
  - ### Compounding (time as a multiplier)
  - ### Proxies vs outcomes (process/metrics are tools; don't let them replace the goal)

## Cumulative advantage (path dependence; increasing returns)
- Example: A small early lead (distribution, reputation, capital) can snowball into dominance.
- Mechanism: early luck/skill -> more visibility/resources -> better opportunities -> more skill/resources.
- Use: In careers and markets, early positioning and consistency can matter disproportionately.
- Failure mode: mistaking path-dependent outcomes for pure merit; always ask what the entry conditions were.
- Model pointers:
  - ### Flywheel (reinforcing loop; momentum)
  - ### Compounding (time as a multiplier)
  - ### Selection effects and survivorship bias

## Institutional mortality (organizations drift toward "Day 2"; plan for decline unless actively resisted)
- Example: Bezos has argued that large companies tend not to live forever (often measured in a few decades) and that Amazon could fail someday; the model is "decline is the default unless you fight it."

## Pareto principle (80/20)
- Example: 20% of features often drive 80% of usage; measure and double down on the real drivers.

## Leverage (tools, code, capital, people, media)
- Example: Automate a recurring manual report with a script; one hour now saves ten hours/month later.

## Map vs territory (models are not reality)
- Example: A strategy deck is a map; customer behavior is the territory. Prefer experiments over persuasion.

## Selection effects and survivorship bias
- Example: Studying only profitable companies overweights lucky strategies; include the failed ones in your dataset.
- Silent graveyard: the missing failures can be the majority, and they contain the real risk information.
- Use: Ask "how many tried and failed?" before copying a winner's playbook.

## Luck vs skill (variance; small samples)
- Example: A fund beats the market for 2 years; it may still be luck in a noisy environment.
- Use: Increase sample size, widen the dataset, and look for a mechanism before inferring skill.
- Practical: Track calibration (probabilities vs outcomes) and compare to base rates.
- Model pointers:
  - ### Probabilistic thinking (Bayes; calibration; base rates)
  - ### Selection effects and survivorship bias

## Over-monitoring noise (confusing volatility with information)
- Example: Checking prices hourly makes randomness feel like a story and increases reactive decisions.
- Use: Match your sampling frequency to the decision frequency (long-term plan -> long-term metrics).
- Practice: When the signal is weak, lower the monitoring rate and focus on process inputs you control.
- Model pointers:
  - ### Map vs territory (models are not reality)
  - ### Proxies vs outcomes (process/metrics are tools; don't let them replace the goal)

## Anthropic principle (observer selection effects)
- Example: We observe a universe compatible with observers; correct for that selection effect
  before treating "fine-tuned for life" as neutral evidence.
- Use: Turns some genesis/cosmology arguments into conditional reasoning ("given observers exist...").
- Failure mode: Using anthropic reasoning as a conversation-stopper or as a proof of a favored metaphysics.

## Fitness vs truth (useful delusions)
- Example: Evolution tends to optimize for reproduction/survival, not accurate perception.
  Some intuitions can be adaptive but misleading.
- Use: Treat strong feelings as signals, not evidence; add external checks (data, experiments, disconfirming tests).
- Tie-in: Buddhism treats many mental constructions (self-stories, craving narratives) as sources of suffering.
- Source: Robert Wright, *Why Buddhism is True* (TODO: verify exact framing).

## Hedonic adaptation (desire treadmill)
- Example: Getting what you want often feels good briefly, then the baseline returns and wanting resumes.
- Use: Don't bet your life strategy on repeated consumption wins; invest in skills, relationships, and practice.
- Tie-in: Matches the Buddhist claim that craving does not terminate in lasting satisfaction.
- Source: Robert Wright, *Why Buddhism is True* (TODO: verify exact framing).

## Incentives (people respond to what is rewarded)
- Example: If you reward "tickets closed," expect shallow fixes and reopened bugs.

## Principal-agent problems
- Example: A contractor optimizes billable hours; you optimize outcome. Align incentives and define acceptance tests.

## Game theory (strategies; equilibria; commitment)
- Example: In pricing, competitors respond; a temporary discount can trigger a price war unless you can commit to terms.

## Proxies vs outcomes (process/metrics are tools; don't let them replace the goal)
- Example: Measuring "meetings held" is a proxy; the outcome is "decisions made and shipped." Bezos' "Day 1" framing explicitly warns about becoming satisfied with proxies.

## Goodhart's law (metrics distort behavior)
Example: 
- If a school targets test scores, teachers teach to the test; 
- if a team targets velocity, story points inflate.

## Chesterton's fence (understand before removing)
- Example: Before deleting a "redundant" approval step, learn what failure it was preventing (fraud, outages, regressions).

## Second-order thinking (downstream consequences)
- Example: A generous refund policy reduces friction but may invite abuse and raise costs; design a second-order check.

## Optionality and reversibility (one-way vs two-way doors)
- Example: An API breaking change is one-way; run a parallel version and deprecate slowly to preserve optionality.



