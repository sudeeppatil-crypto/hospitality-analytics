# Hospitality Analytics – Inference Document

## 1. Executive Summary
This report evaluates five hospitality KPIs across five hotels over the five-year period 2021–2025:
- Occupancy rate
- Average Daily Rate (ADR)
- Revenue per Available Room (RevPAR)
- Guest satisfaction score
- Employee turnover rate

Populate this report using the dashboard's downloadable inference report and the observations below.

## 2. Data and Methodology
The project uses synthetic data generated with Python and Pandas. Entity identifiers use UUIDs and sample names are realistic. The warehouse contains hotel, room, guest, employee and date dimensions, along with booking, daily room, guest feedback and employee event facts.

### KPI definitions
- Occupancy = occupied room nights / available room nights × 100.
- ADR = room revenue / occupied room nights.
- RevPAR = room revenue / available room nights.
- Guest satisfaction = average submitted feedback rating.
- Employee turnover = employee terminations / average headcount × 100.

Out-of-order rooms are excluded from the available-room denominator. Check-in dates are included as occupied nights and checkout dates are excluded.

## 3. Seasonal Analysis
Use the hotel-specific Peak, Shoulder and Off-season labels in the seasonal dashboard.

For each hotel, document:
1. Which season has the highest occupancy?
2. Does ADR rise during the high-demand season?
3. Does higher ADR translate into higher RevPAR?
4. Does guest satisfaction fall during high occupancy, potentially due to crowding or longer wait times?
5. Does employee turnover change during peak workload or seasonal staffing periods?

Do not assume that Peak season must always have the best satisfaction or turnover. Use the observed values.

## 4. Hotel-wise Findings
For each hotel, write:
- Strongest KPI and weakest KPI.
- Best-performing season.
- Lowest-performing season.
- One plausible operational explanation supported by the data.

## 5. KPI Stories
### Occupancy Rate
Discuss tourism demand, holidays, festivals, conferences and local events. Explain the months/seasons where occupancy rises or falls.

### ADR
Discuss peak-season pricing, off-season discounts and the hotel's ability to maintain room rates.

### RevPAR
Explain how occupancy and ADR combine. A high ADR alone does not guarantee high RevPAR if occupancy falls substantially.

### Guest Satisfaction
Compare ratings with occupancy and feedback volume. Discuss service quality, staffing capacity, crowding and wait times as possible explanations, not proven causes.

### Employee Turnover
Compare hires, terminations and average headcount by month and season. Discuss seasonal hiring, workload and employee retention.

## 6. Recommendations
Base recommendations on the actual dashboard results. Examples:
- Adjust pricing and promotions by season.
- Increase staffing and housekeeping capacity before peak periods.
- Monitor guest feedback categories with lower ratings.
- Plan seasonal hiring and retention activities.
- Investigate hotels with persistently low RevPAR or high turnover.

## 7. Limitations
- The dataset is synthetic and demonstrates analytical methods rather than actual hotel performance.
- Seasonal associations do not establish causation.
- Feedback is based only on submitted responses and may have response bias.
- Turnover rates depend on the event-based headcount reconstruction and the selected reporting period.
