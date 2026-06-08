# CTR Optimization Playbook

## Definition
CTR (Click-Through Rate) measures the percentage of impressions that result in clicks. Formula: (Clicks / Impressions) * 100.

## Frequent Symptoms
- CTR below 1% for display campaigns
- CTR below 2% for social media campaigns  
- CTR below 0.5% for native advertising
- Declining CTR trend over consecutive days
- High variance in CTR across similar campaigns

## Probable Causes
- Poor ad creative quality or relevance
- Mismatched audience targeting
- Weak value proposition in headline
- Unclear call-to-action (CTA)
- Ad fatigue from overexposure
- Incorrect ad placement or format
- Low ad relevance score on platform

## Data Diagnostics (from CSV)
Check these patterns in your data:
- Group by `ad_format`: Compare CTR across formats
- Group by `audience_segment`: Identify segments with low CTR
- Group by `country`: Find geographic performance gaps
- Time series analysis: Look for day-over-day CTR drops
- Compare campaigns with high vs low `impressions` for fatigue

## Actionable Recommendations

### Creative Optimization
1. A/B test headlines (emotional vs rational)
2. Use numbers and statistics in ad copy
3. Add urgency triggers (Limited time, While supplies last)
4. Test different CTA buttons (Shop Now, Learn More, Get Started)
5. Include social proof (Join 10,000+ customers)

### Targeting Refinement
1. Narrow audience segments with CTR below 2%
2. Create lookalike audiences from high-CTR segments
3. Daypart targeting for peak engagement hours
4. Device-specific creative optimization

### Placement Strategy
1. Move budget from low-CTR placements to high performers
2. Test different ad sizes and positions
3. Exclude non-performing apps or websites

## Heuristic Rules
- If CTR < 1% for >3 days: Pause and refresh creative
- If impressions > 100,000 and CTR < 0.5%: Change audience
- If weekend CTR > weekday CTR: Increase weekend budget by 30%
- If CTR drops more than 25% week-over-week: Launch new creative

## Concrete Examples

**Example 1: Low Display CTR**
- Symptom: Display CTR at 0.3%, benchmark is 0.7%
- Diagnosis: Generic banner creative with "Click Here" CTA
- Action: Test dynamic product ads with "Shop Women's Sale - 40% Off"

**Example 2: Mobile Gaming Ad Fatigue**
- Data: CTR dropped from 2.5% to 1.2% over 7 days
- Diagnosis: Same creative shown 500,000+ times
- Action: Rotate 3 new creatives, implement frequency cap of 3/day

## LLM Response Templates
- "Based on your CTR of [X]% which is below the [Y]% benchmark for [ad_format], I recommend..."
- "Your CTR is declining by [Z]% over the last [N] days, suggesting creative fatigue..."
- "The audience segment [segment_name] has the lowest CTR at [X]%, consider..."