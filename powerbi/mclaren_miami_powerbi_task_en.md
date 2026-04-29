# Project Brief for a Power BI Dashboard

## Analysis Topic

**McLaren: race-pace stability in Miami as a potential competitive advantage over rivals**

---

## 1. Fundamental Question

**Can McLaren gain a competitive advantage at the Miami Grand Prix through more stable long-run race pace compared with its main rivals?**

In other words:  
Does McLaren necessarily need to be the fastest team over a single lap to be strong in the race, or can the team be competitive because its pace drops off less over the race distance?

---

## 2. Testable Hypothesis

**Hypothesis:**  
In modern races comparable to the Miami Grand Prix, McLaren demonstrates more stable race pace than Ferrari, Mercedes, and Red Bull: its relative lap time deteriorates less from the beginning to the end of the race, and its lap-time variability is lower than that of its main competitors.

**What “confirmed” means:**  
The hypothesis is considered confirmed if McLaren simultaneously:

1. shows a smaller pace drop-off between the first and last parts of the race;
2. has lower lap-time variability;
3. reduces the gap to competitors or increases its advantage over them in the second half of the race.

**What “rejected” means:**  
The hypothesis is considered rejected if McLaren does not differ from its competitors in terms of pace stability, or if its pace drops off more than Ferrari, Mercedes, and Red Bull.

---

## 3. Metrics for Testing the Hypothesis

### Core Metrics

| Metric | Description | Purpose |
|---|---|---|
| **Average Lap Time** | Team average `lap_time_ms` | Shows overall race pace |
| **Median Lap Time** | Team median `lap_time_ms` | More robust to outliers than the average |
| **Relative Pace Delta** | Difference between a driver's lap time and the median lap time of the top teams on the same lap | Allows pace comparison within the same race and lap |
| **Pace Drift** | Difference between median pace in the final part and the first part of the race | Main metric for pace drop-off |
| **Lap Time Variability** | Standard deviation or IQR of `lap_time_ms` | Measures race-pace consistency |
| **Late Race Pace** | Average or median pace in the final third of the race | Shows team strength closer to the finish |
| **Position Change by Race Phase** | Position change by race phase based on `position` from `lap_times` | Helps connect pace to on-track result |

---

### Recommended Calculated Metrics

#### 1. Relative Pace Delta

```text
Relative Pace Delta =
Team / Driver Lap Time - Competitor Median Lap Time on the same lap
```

Interpretation:

- negative value — the team is faster than the benchmark;
- positive value — the team is slower than the benchmark;
- value close to zero — pace is approximately in line with competitors.

---

#### 2. Pace Drift

```text
Pace Drift =
Median Lap Time in the final third of the race
-
Median Lap Time in the first third of the race
```

The lower the value, the more stable the team's race pace.

---

#### 3. Team Consistency Index

```text
Team Consistency Index =
IQR or Standard Deviation of lap_time_ms on clean racing laps
```

The lower the value, the more consistent the team's pace.

---

#### 4. Late Race Advantage

```text
Late Race Advantage =
Relative Pace Delta in the final third of the race
-
Relative Pace Delta in the first third of the race
```

If the value improves toward the end of the race, the team becomes relatively stronger over the race distance.

---

## 4. Analysis Period

Recommended period:

**2022–2026, up to the latest completed race before the 2026 Miami Grand Prix.**

Rationale:

- The Miami Grand Prix only appeared in modern Formula 1 history in 2022.
- Older seasons starting from 1950 are not suitable for direct comparison because of different cars, regulations, race formats, tyre rules, and team lineups.
- For an applied team-focused analysis, the modern period is more relevant than the entire historical database.

Primary analysis focus:

1. **Miami Grand Prix 2022–2025** — direct historical context for the circuit.
2. **Modern races from 2022–2026** — additional context on current team strength.
3. **Similar circuits** — to expand the sample if Miami alone provides too few observations.

---

## 5. Comparison with Other Teams

### Main Team for the Analysis

**McLaren**

The project brief is written as if the analyst works inside McLaren and is preparing a dashboard for the Miami race weekend.

---

### Main Competitors for Comparison

| Team | Why compare against them |
|---|---|
| **Red Bull** | Benchmark for strong race pace |
| **Ferrari** | Direct rival for podiums / high points finishes |
| **Mercedes** | Team with potentially strong race pace and strategic execution |
| **Aston Martin** | Additional reference point if broader comparison is needed |
| **Williams / Alpine / Haas** | Not McLaren's primary rivals, but useful for wider midfield context |

---

### Comparison Logic

The comparison should not rely only on absolute lap time. It should be evaluated across three levels:

1. **Absolute pace**  
   Which team is faster by average and median lap time.

2. **Pace stability**  
   Which team has lower lap-time variability.

3. **Pace evolution during the race**  
   Which team loses less speed from the beginning to the end of the race distance.

Main analytical angle:  
**McLaren may not be the fastest team at the beginning of the race, but it may become stronger relative to its competitors in the second half of the race.**

---

## 6. Power BI Dashboard Structure

For a 5-minute story, the optimal structure is **4 pages**.

---

## Page 1 — Executive Summary

**Page objective:**  
Immediately answer whether the hypothesis is supported.

### Main Elements

- KPI card: `McLaren Pace Drift`
- KPI card: `McLaren Consistency Index`
- KPI card: `McLaren Late Race Pace Rank`
- Hypothesis status indicator:  
  **Confirmed / Partially Confirmed / Rejected**
- Bar chart: `Pace Drift` comparison by team
- Bar chart: `Lap Time Variability` comparison by team

### Main Question on the Page

**Is McLaren actually more stable than its competitors over a long run?**

---

## Page 2 — Race Pace Evolution

**Page objective:**  
Show how team pace changes over the race distance.

### Main Elements

- Line chart: `Relative Pace Delta` by `lap_num`
- Filters:
  - season;
  - circuit;
  - team;
  - driver;
  - race.
- McLaren highlighted with a distinct color.
- 3-lap or 5-lap rolling average to smooth noise.

### Main Question on the Page

**At what point in the race does McLaren become stronger or weaker relative to its competitors?**

---

## Page 3 — Race Phases Comparison

**Page objective:**  
Break the race into clear phases.

### Race Phases

- Early Race: first 25% of the distance
- Mid Race: 25–75% of the distance
- Late Race: final 25% of the distance

### Main Elements

- Clustered bar chart: average `Relative Pace Delta` by race phase
- Matrix: teams × race phases
- Line / slope chart: pace change from Early Race to Late Race
- Tooltip with McLaren drivers

### Main Question on the Page

**Does McLaren's pace drop off less than its competitors' pace from the beginning to the end of the race?**

---

## Page 4 — Miami vs Similar Circuits

**Page objective:**  
Understand whether Miami is a unique case or part of a broader pattern.

### Main Elements

- Scatter plot:
  - X-axis: `Average Relative Pace`
  - Y-axis: `Lap Time Variability`
  - points: teams / circuits
- Bar chart: McLaren `Pace Drift` by circuit
- Table: ranking of circuits where McLaren is most stable
- Circuit filter: Miami, Jeddah, Baku, Singapore, Las Vegas, Monaco, and other street / semi-street circuits

### Main Question on the Page

**Is Miami similar to circuits where McLaren has already shown stable race pace?**

---

## 7. Example Conclusion

### If the Hypothesis Is Confirmed

**Conclusion:**  
The analysis confirms that McLaren has a competitive advantage over a long race distance. In races comparable to Miami, the team shows a smaller pace drop-off between the first and final parts of the race than Ferrari, Mercedes, and Red Bull. McLaren's key strength is its stability in the second half of the race: the team has fewer sharp lap-time losses and more often reduces the gap to competitors toward the finish.

**Practical interpretation for the team:**  
McLaren can build its Miami strategy not only around qualifying position, but also around strong race pace. If the team maintains stable pace after the midpoint of the race, it may be able to attack competitors in the second half or defend its position more effectively over a long stint.

---

### If the Hypothesis Is Rejected

**Conclusion:**  
The analysis does not confirm McLaren's advantage in race-pace stability. In Miami and on comparable circuits, McLaren does not show a smaller pace drop-off than Ferrari, Mercedes, and Red Bull. Moreover, in the second half of the race the team either loses relative pace or does not gain a meaningful advantage over its competitors.

**Practical interpretation for the team:**  
McLaren should not rely only on race-pace stability as its key competitive advantage. To achieve a strong result in Miami, the team should place greater emphasis on qualifying, starting position, track-position defense, and minimizing losses on individual laps.

---

## 8. Example Story for a 5-Minute Video

### Working Title

**“Can McLaren win in Miami through pace stability rather than single-lap speed?”**

---

### Storyline

**0:00–0:30 — Context**

“Before the Miami Grand Prix, McLaren needs to understand where its real competitive advantage lies. Being fast over one lap is not enough: the race is not always won by the team with the best individual lap time, but by the team that can maintain strong pace over the full distance.”

---

**0:30–1:10 — Hypothesis**

“My hypothesis is that McLaren has an advantage over Ferrari, Mercedes, and Red Bull specifically in race-pace stability. In other words, the team does not have to be faster on every lap, but its pace deteriorates less from the beginning to the end of the race.”

---

**1:10–2:00 — Overall Picture**

“On the first dashboard page, we can see a comparison of teams across two key metrics: pace drop-off and lap-time variability. If McLaren ranks below its competitors in Pace Drift and Variability, it means the team is more stable over the race distance.”

---

**2:00–3:00 — Lap-by-Lap Dynamics**

“Now we move beyond averages and look at race development lap by lap. The key line here is Relative Pace Delta. If McLaren's line improves in the second half of the race, the team is not just maintaining its pace — it is becoming stronger relative to its competitors.”

---

**3:00–4:00 — Race Phase Analysis**

“Let's split the race into three phases: early, middle, and late race. The most important part is the final third of the distance. This is where tyres, fuel load, strategy, and car stability start to matter most. If McLaren loses less in this phase, that can become a strategic advantage in Miami.”

---

**4:00–4:40 — Miami vs Similar Circuits**

“Because Miami has a short history, we expand the analysis to similar circuits. This helps us understand whether McLaren's stability is just a one-race coincidence or a repeatable pattern on circuits of a similar type.”

---

**4:40–5:00 — Final Conclusion**

“The final question for the team is simple: can McLaren build its race around stable race pace? If the hypothesis is confirmed, the team can focus on a strong second half of the race. If not, the key factors become qualifying, starting position, and track-position defense.”

---

## Final Project Formulation

**Dashboard objective:**  
Evaluate whether McLaren's race-pace stability is a potential competitive advantage over Ferrari, Mercedes, and Red Bull at the Miami Grand Prix.

**Fundamental question:**  
Can McLaren achieve a strong result in Miami through more stable long-run race pace?

**Hypothesis:**  
McLaren demonstrates a smaller pace drop-off and lower lap-time variability over the race distance than its main competitors, making the team especially competitive in the second half of the Miami Grand Prix.
