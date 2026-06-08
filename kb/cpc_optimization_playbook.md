# CPC Optimization Playbook

## Definition  
CPC (Cost Per Click) measures the average cost paid for each click. Formula: Spend / Clicks. Lower CPC indicates more efficient traffic acquisition.

## Frequent Symptoms
- CPC consistently above industry benchmark
- CPC spikes on specific days or times
- High CPC variance between similar campaigns
- CPC increasing while CTR remains flat
- Mobile CPC higher than desktop by 50%+

## Probable Causes
- Aggressive bidding strategy
- High competition for keywords
- Low Quality Score or Ad Rank
- Poor landing page experience
- Irrelevant ad-to-keyword match
- Broad match keywords wasting spend

## Data Diagnostics (from CSV)
Check these patterns:
- Group by `country`: Identify expensive geographic markets
- Group by `ad_format`: Compare CPC efficiency by format
- Group by `audience_segment`: Find cost differences by segment
- Correlate CPC with `conversions`: Ensure efficiency isn't hurting volume

## Actionable Recommendations

### Bid Management
1. Set bid caps at 20% above average CPC
2. Use dayparting to lower bids during low-conversion hours
3. Implement portfolio bidding across similar campaigns
4. Test automated bidding strategies (Target CPA, Maximize clicks)

### Quality Improvement
1. Improve ad relevance to keywords (use keywords in headline)
2. Optimize landing page load speed (aim for <2 seconds)
3. Add negative keywords weekly
4. Increase expected CTR through better extensions

### Structure Optimization
1. Break high-CPC campaigns into tighter ad groups
2. Pause keywords with CPC > 3x average without conversions
3. Move budget from branded to non-branded terms gradually

## Heuristic Rules
- If CPC > 2x target: Pause keyword/ad group immediately
- If CPC increases 30% in one day: Check auction insights for new competitors
- If mobile CPC > desktop CPC by 40%: Reduce mobile bid adjustment to -20%
- If CPC > $5 with CTR < 1%: Pause and re-evaluate creative

## Concrete Examples

**Example 1: High CPC on Display**
- Data: Display CPC at $1.20, target is $0.60
- Diagnosis: Running on premium placements only
- Action: Enable open network, lower max bid to $0.80

**Example 2: Spiking CPC on Weekends**
- Data: Weekend CPC $3.50 vs weekday $1.80
- Diagnosis: Weekend auction competition higher
- Action: Apply -30% bid adjustment for Saturday-Sunday

## LLM Response Templates
- "Your average CPC of $[X] is [Y]% above the benchmark for [country], consider..."
- "The CPC spike on [date/day] coincides with [event/pattern], suggesting..."
- "Campaign [name] has CPC of $[X] which is inefficient given its conversion rate of [Y]%, recommend..."