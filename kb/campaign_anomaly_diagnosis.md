# Campaign Anomaly Diagnosis

## Definition
Campaign anomalies are unexpected performance patterns requiring immediate investigation: sudden metric spikes, drops, or unusual correlations.

## Frequent Symptoms
- CTR drops >30% in one day
- CPC spikes without bid changes
- Conversion rate halves overnight
- Spend doubles with no performance improvement  
- Impressions collapse by 50%+
- CPA triples on a single day

## Probable Causes

### Technical Issues
- Tracking pixel failure
- Landing page downtime
- Platform outage or bug
- Attribution window change
- Conversion tracking duplication

### Market Changes  
- New competitor entering auction
- Seasonal demand shift
- Pricing or promotion changes
- Negative press or reviews
- Platform policy update

### Internal Factors
- Creative fatigue or disapproval
- Budget pacing changes
- Audience overlap or saturation
- Bid strategy adjustment
- Geo-targeting modification

## Data Diagnostics (from CSV)
Check these patterns:
- Compare metrics day-over-day and week-over-week
- Check for data gaps or zeros in `impressions`
- Calculate rolling 7-day averages for baselines
- Correlate anomalies across metrics: Does `spend` drop explain `conversions` drop?
- Check if anomaly coincides with `date` boundaries

## Actionable Recommendations

### Immediate Response (First 2 hours)
1. Verify tracking pixels are firing
2. Check landing page uptime and load speed
3. Review platform status pages
4. Check for disapproved ads or keywords
5. Pull auction insights for new competitors

### Short-Term Fixes (24 hours)
1. Pause underperforming ad groups
2. Launch backup creative if fatigue suspected
3. Adjust bids or budgets back to baseline
4. Implement temporary CPA caps
5. Exclude problematic placements or audiences

### Long-Term Prevention (1 week)
1. Set up automated rules for anomaly detection
2. Create performance alert thresholds
3. Document diagnostic runbook
4. Implement backup tracking system
5. Build performance baseline models

## Heuristic Rules
- If impressions drop >50% in one day: Check ad approval status
- If CTR halves with same impressions: Creative fatigue or disapproval
- If CPC triples with same CTR: Check auction for new competitor
- If conversions drop to zero: Tracking failure until proven otherwise

## Concrete Examples

**Example 1: Sudden Zero Conversions**
- Data: Yesterday 50 conversions, today 0, same spend
- Diagnosis: Conversion pixel not firing
- Action: Check Google Tag Manager, found tracking code removed during site update

**Example 2: CPC Spike on Monday**
- Data: Weekend CPC $1.50, Monday CPC $4.50
- Diagnosis: New competitor launched aggressive campaign
- Action: Reduce bids, launch competitor conquesting campaign

**Example 3: Impression Collapse**
- Data: 100k daily impressions dropped to 15k overnight
- Diagnosis: Ad disapproved for policy violation
- Action: Appeal or modify creative, launch backup campaign

## LLM Response Templates
- "I detected an anomaly: [metric] changed by [X]% between [date1] and [date2]. The most likely cause based on your data is..."
- "The pattern of [metric1] dropping while [metric2] remains stable suggests [technical/market/internal] issue..."
- "Comparing your data to typical patterns, the [date] anomaly correlates with [event/factor]. I recommend..."
- "This performance pattern is classic [creative fatigue / tracking issue / competitive pressure]. Action plan:..."