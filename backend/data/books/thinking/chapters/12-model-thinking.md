# Thinking and Problem Solving
## Model Thinking
### Diversity Prediction Theorem
Main Idea: Collective predictions are more accurate when individual predictions are diverse.

Formula:
Crowd Error = Avg. Individual Error – Diversity

Example: A group of people estimating the weight of an ox—averaged estimate is more accurate than most individuals.

Elaboration: Diversity adds value by canceling out individual biases.

### Wisdom of Crowds
Main Idea: Aggregated judgments of a group can outperform experts.

Example: Asking 1,000 people to guess the number of jellybeans in a jar—the average is surprisingly accurate.

Condition: Independence + Diversity + Decentralization.

### Linear Regression
Main Idea: Predict a continuous outcome from weighted input variables.

Formula:
Y = β₀ + β₁X₁ + β₂X₂ + … + ε

Example: Predicting house price from area, number of rooms, and location.

### Logistic Regression
Main Idea: Predict binary outcomes using input variables.

Formula:
P(Y=1) = 1 / (1 + e^-(β₀ + β₁X₁ + …))

Example: Predicting whether a loan applicant will default.

### Decision Trees
Main Idea: Recursive partitioning of data into decisions based on feature splits.

Example: Determining if an email is spam based on the presence of certain keywords.

### Bayesian Updating
Main Idea: Update your belief in a hypothesis as new data becomes available.

Formula:
Posterior ∝ Likelihood × Prior

Example: After a positive COVID test, adjust the probability you have the disease depending on test accuracy and disease prevalence.

### Markov Models
Main Idea: System transitions between states with fixed probabilities.

Formula:
P(Xₜ₊₁ | Xₜ)

Example: Weather model: today’s weather depends only on yesterday’s (sunny → rainy with 0.3 prob).

### Hidden Markov Models
Main Idea: Observed outcomes depend on unobserved (hidden) states.

Example: Speech recognition—actual spoken phonemes are hidden, only sound waves are observed.

### Random Walk
Main Idea: A process where each step is a random movement from the previous position.

Formula:
Xₙ = Xₙ₋₁ + εₙ (εₙ is random noise)

Example: Stock price modeling.

### Path Dependence
Main Idea: History matters; current state depends on past choices.

Example: The QWERTY keyboard layout continues due to early adoption.

### Positive Feedback / Increasing Returns
Main Idea: Success begets more success.

Example: Facebook’s growth—more users attract even more users.

### Power Laws
Main Idea: A few large events, many small ones.

Formula:
P(x) ∝ x^(-α)

Example: Wealth distribution—most people have little, a few have a lot.

### Normal Distribution
Main Idea: Bell-shaped distribution with most values near the mean.

Formula:
f(x) = (1/σ√(2π)) * e^(-(x - μ)² / 2σ²)

Example: Human heights, test scores.

### Tipping Points
Main Idea: Small changes can cause dramatic shifts past a critical threshold.

Example: Viral video—once a few influencers share it, it spreads rapidly.

### Threshold Models
Main Idea: Individuals act only when a critical proportion of others do.

Example: Joining a protest when 30% of your peers already have.

### Game Theory
Main Idea: Study of strategic interactions.

Example: Two companies choosing prices while considering competitor behavior.

### Prisoner’s Dilemma
Main Idea: Individuals acting in self-interest can lead to worse outcomes for all.

Example: Two firms both undercutting price—leads to losses for both.

### Coordination Games
Main Idea: Best outcomes occur when players align strategies.

Example: Driving on the same side of the road.

### Network Models
Main Idea: Nodes (agents) and links (connections) model complex interactions.

Example: Mapping how a disease spreads through a social network.

### Diffusion Models
Main Idea: Track how behaviors or technologies spread.

Example: Adoption of electric vehicles over time.

### Agent-Based Models (ABM)
Main Idea: Simulate individual agents interacting with each other and environment.

Example: Modeling traffic with individual cars responding to rules.

### Cellular Automata
Main Idea: Grid of cells evolving by simple local rules.

Example: Conway’s Game of Life.

### System Dynamics Models
Main Idea: Use stocks, flows, and feedback loops to simulate systems over time.

Example: Modeling population growth or CO₂ in the atmosphere.

### Ecological Models
Main Idea: Simulate interspecies interactions like predation or competition.

Example: Wolf-rabbit population dynamics.

### Fitness Landscapes
Main Idea: Visualize how different configurations lead to different outcomes.

Example: Landscape of business strategies—some peaks (high success), some valleys (failure).

### Replicator Dynamics
Main Idea: Strategies or behaviors spread proportionally to their success.

Formula:
dx/dt = x(f(x) – φ)
where f(x) is fitness and φ is average population fitness.

Example: Evolutionary biology—genes that replicate more survive.

### Simpson’s Paradox
Main Idea: A trend in subgroups reverses when combined.

Example: A treatment works better for both men and women but appears worse overall.

### Central Limit Theorem
Main Idea: Averages of samples from any distribution tend toward normal.

Example: Tossing coins—the sum of results is normally distributed.

### Principal Component Analysis (PCA)
Main Idea: Reduce dimensionality of data while retaining variance.

Example: Summarizing customer behavior from many variables into a few principal ones.

### K-means Clustering
Main Idea: Group data into k clusters by minimizing within-cluster variance.

Example: Segmenting customers into behavioral clusters for marketing.

### Naive Bayes Classifier
Main Idea: Classify based on Bayes' theorem assuming feature independence.

Example: Spam filtering using word presence.

### Multimodel Thinking
Main Idea: No single model fits all; use a variety of models together.

Example: Analyze crime using statistics, networks, and ABMs simultaneously.

### Heuristics
Main Idea: Simple rules-of-thumb for decision-making.

Example: “Choose the highest-rated product under $50.”

## Mindware

### The Law of Large Numbers
Idea: Larger samples yield more reliable averages and proportions.

Example: A hospital with 100 births a day will have a more stable boy-girl ratio than one with 10 births a day. If the smaller hospital reports 80% boys on a day, that’s more likely due to chance.

### Correlation ≠ Causation
Idea: Just because two variables are correlated doesn’t mean one causes the other.

Example: Ice cream sales and drowning deaths are correlated—not because ice cream causes drowning, but because both increase during summer.

### Random Assignment
Idea: The best way to test causation is through experiments with random assignment.

Example: To test whether a new teaching method improves scores, randomly assign students to experimental and control groups. This avoids confounding factors.

### Confirmation Bias
Idea: People tend to seek or interpret evidence in ways that confirm their existing beliefs.

Example: A person who believes in astrology will remember the times horoscopes were accurate, and ignore when they weren’t.

### Availability Heuristic
Idea: We judge how likely something is by how easily examples come to mind.

Example: After hearing about a plane crash on the news, people may overestimate the danger of flying.

### Representativeness Heuristic
Idea: People judge the probability of something by how much it resembles a prototype, often neglecting base rates.

Example: If told someone is quiet and loves books, people may assume they’re a librarian—ignoring that there are far more farmers than librarians.

### Regression to the Mean
Idea: Extreme performances tend to be followed by more average ones.

Example: A student who gets an unusually high test score is likely to score lower next time—not because they got worse, but because of natural variation.

### Sunk Cost Fallacy
Idea: People irrationally continue investing in a losing endeavor because of what they’ve already invested.

Example: Staying in a bad movie just because you paid for the ticket.

### Utility Theory & Expected Value
Idea: Rational decisions should weigh benefits vs. probabilities.

Example: Choosing between a 90% chance to win $10 or a 10% chance to win $100. Expected value helps decide which is better in the long run.

### Framing Effects
Idea: The way a choice is worded affects decisions.

Example: People prefer “90% fat-free” over “10% fat,” even though they mean the same.

### Covariation & Causal Reasoning
Idea: We infer causality from observing co-occurrence and patterns of variation.

Example: If people who exercise regularly are less likely to be depressed, we might infer exercise reduces depression—but an experiment is needed to be sure.

### Controlled Comparisons
Idea: Good analysis compares like with like and controls for confounding variables.

Example: When comparing school performance, adjust for socioeconomic background to avoid biased conclusions about teacher quality.

### Dialectical Thinking (East vs. West)
Idea: Eastern cultures are more comfortable with contradiction and complexity, while Western cultures seek logical consistency.

Example: A Westerner may say someone cannot be both shy and outgoing; an Easterner may believe the person could be shy in public but outgoing with friends.

### Attribution Theory
Idea: We explain others’ behavior as due to their disposition, underestimating situational causes.

Example: If someone cuts you off in traffic, you might think they’re a jerk—rather than considering they might be rushing to an emergency.

### Cognitive Dissonance
Idea: When beliefs and actions conflict, we experience discomfort and often adjust beliefs to reduce that dissonance.

Example: A smoker may say, “the science isn’t settled,” to reduce guilt about smoking.

### System 1 vs. System 2 Thinking
Idea: System 1 is fast, intuitive, and error-prone. System 2 is slow, deliberate, and logical.

Example: Instantly assuming a problem’s answer is obvious (System 1), only to realize it’s a trick question upon reflection (System 2).

### Statistical Reasoning
Idea: Unerstanding distributions, variability, and chance is essential for sound reasoning.

Example: Knowing that a medication “works in 70% of cases” requires understanding sample size, placebo effects, and variance.

### Incentive Structures
Idea: People’s behavior is influenced by the incentives they face—even unintentionally.

Example: Teachers may “teach to the test” if rewards depend on student scores.

### Fundamental Attribution Error
Idea: We over-attribute others’ actions to character rather than context.

Example: Thinking a student fails because they’re lazy, not because they work nights to support their family.

### Culture Shapes Cognition
Idea: Culture deeply influences what and how people think.

Example: Westerners focus more on individual objects; East Asians on relationships and context.

## Critical Thinking
### Daily Critical Thinking Habits
- Daily Questioning: Journal or ask “Why do I believe this?” for 1 thing each day.
- Bias Check: 	Pick a recent belief and try to falsify it.
- Argument Analysis:	Dissect 1 editorial, video, or opinion piece per day.
- Forecasting Practice:	Make predictions with % confidence and review them monthly.
- Read Deeply:	Read 1 complex nonfiction book monthly with active notes.
### Practical Guide to Critical Thinking
#### Slow Down and Reflect (Kahneman)
- Recognize when you're relying on intuition (System 1).
- Pause and apply deliberate thought (System 2), especially for important decisions.

#### Ask Basic Questions (Sagan, Hughes)
- What’s the claim?
- What’s the evidence?
- Are there alternative explanations?
- Who benefits?

#### Spot Common Fallacies (McInerny, Gula)
- Straw man, ad hominem, false dilemma, slippery slope, etc.
- Ask: Is the argument attacking the idea or the person?

#### Use the "Baloney Detection Kit" (Sagan)
Independent confirmation, Occam’s razor, falsifiability, and logic over anecdote.

#### Think in Probabilities (Tetlock)
- Replace certainty with likelihoods.
- Update beliefs when new evidence appears (Bayesian mindset).

#### Challenge Your Biases (Banaji, Dobelli)
- Look for confirmation bias, sunk-cost fallacy, halo effect, etc.
- Ask: “What would disconfirm this view?”

#### Read Actively and Analytically (Adler)
- Ask: What is the author’s main point?
- What assumptions are they making?
- Do I agree? Why or why not?

#### Practice “Steelman” Arguments (Mercier)
- Argue the strongest form of your opponent’s view.
- Helps avoid tribal reasoning and fosters dialogue.

## System Thinking
*Systems thinking* is a way of understanding complex problems or phenomena by seeing how parts of a system interrelate and how systems work over time within the context of larger systems. Instead of analyzing components in isolation, systems thinking looks at wholes, feedback loops, dynamics, and patterns.

### Key Concepts:

- System: A set of interconnected components forming a complex whole.
- Feedback Loops: Circular chains of cause and effect; can be reinforcing (positive) or balancing (negative).
- Stocks and Flows: Stocks are quantities that accumulate; flows are rates of change.
- Delays: Time lags between cause and effect; often make systems behavior non-intuitive.
- Emergence: Whole-system behavior that cannot be predicted by analyzing parts alone.
- Leverage Points: Places in a system where a small shift can produce big changes.

### books on the topic

#### Thinking in Systems – Donella Meadows
Main Ideas:
Introduces systems thinking fundamentals for beginners.
Shows how to identify elements, interconnections, and purpose in systems.
Explains different types of feedback loops.
Discusses system traps (e.g., policy resistance, drift to low performance).
Outlines 12 leverage points to intervene in systems (e.g., information flows, goals, paradigms).

Example:
Traffic congestion is a balancing feedback loop — more traffic causes longer delays, leading people to avoid rush hour — but adding lanes (a structural change) may trigger a reinforcing loop (more people drive), worsening it.

#### The Fifth Discipline – Peter Senge

Main Ideas:
Argues that the key discipline for a learning organization is systems thinking.
Introduces five disciplines:
Personal Mastery
Mental Models
Shared Vision
Team Learning
Systems Thinking (integrative discipline)
Emphasizes seeing “the whole elephant,” not just parts.
Identifies systems archetypes, like “Limits to Growth” and “Shifting the Burden.”

Example:
A company investing only in marketing (quick fix) instead of product quality improvement ("root cause") eventually sees diminishing returns — classic “Shifting the Burden” archetype.

#### Thinking in Systems: A Primer – Deborah Hammond
(Complement to Meadows, more historical/philosophical)
Main Ideas:
Historical roots of systems thinking: cybernetics, ecology, organizational theory.
Reviews major contributors like Ludwig von Bertalanffy, Gregory Bateson, Norbert Wiener.
Discusses tensions between mechanistic and holistic worldviews.

#### Systems Thinking: Managing Chaos and Complexity – Jamshid Gharajedaghi
Main Ideas:
Focuses on design thinking + systems thinking in business and management.
Emphasizes multi-dimensionality: structure, function, process, and purpose.
Introduces interactive design for complex adaptive systems.

Example:
Traditional top-down business control fails in dynamic environments; systems thinking enables redesign based on feedback and adaptation.

#### The Art of Systems Thinking – Joseph O'Connor & Ian McDermott
Main Ideas:
Accessible, practical guide for everyday decision making.
Highlights the limits of linear cause-effect thinking.
Helps readers see multiple perspectives and interconnections.
