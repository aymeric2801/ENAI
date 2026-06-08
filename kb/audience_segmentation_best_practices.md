# Audience Segmentation Best Practices

## Definition
Audience segmentation divides campaign targets into groups based on shared characteristics to improve relevance, CTR, CPA, and ROAS.

## Frequent Symptoms
- Low CTR across all segments (indicates generic messaging)
- High CPA on certain segments
- ROAS variance > 2x between best and worst segments
- Similar performance across all audience segments
- High spend on inefficient segments

## Probable Causes
- Using platform's "expanded audiences" defaults
- No segment-specific creative or offers
- Overlapping audience segments causing self-competition
- Neglecting segment exclusions
- Poor understanding of segment purchase behavior

## Data Diagnostics (from CSV)
Check these patterns:
- Group all KPIs by `audience_segment`
- Cross-tab `audience_segment` with `country`
- Analyze `audience_segment` by `ad_format`
- Compare conversion rates by segment
- Calculate segment-specific ROAS and CPA

## Actionable Recommendations

### Segment-Specific Strategies

**18-24 (Young Adults)**
- Use mobile-first creative, short-form video
- Highlight social proof, FOMO, trends
- Optimize for engagement, not immediate conversion
- Preferred platforms: TikTok, Instagram, Snapchat

**25-34 (Young Professionals)**
- Focus on convenience, time-saving benefits
- Use testimonials from similar demographics
- Optimize for purchase, higher AOV potential
- Preferred platforms: Instagram, LinkedIn, YouTube

**35-50 (Established Consumers)**
- Emphasize quality, reliability, value
- Use detailed product information
- Higher tolerance for longer copy
- Preferred platforms: Facebook, email, search

### Segmentation Tactics

1. Create segment-specific landing pages
2. Implement dynamic creative for segments
3. Use frequency caps per segment (lower for high-intent)
4. Build suppression lists across segments
5. Test lookalikes from best segments only

## Heuristic Rules
- If segment CPA > 2x best segment: Pause and re-evaluate
- If segment has >20% of spend but <10% of conversions: Pause
- If segment ROAS < 0.5x average: Exclude unless brand awareness
- If segment CTR > 2x average: Increase budget 30%

## Concrete Examples

**Example 1: Underperforming Young Adult Segment**
- Data: 18-24 CPA $50, overall CPA $25
- Diagnosis: Using same creative as 35-50 segment
- Action: Launch TikTok-first creative, add student discount

**Example 2: Geographic Segment Inefficiency**
- Data: France CPA $40, Germany CPA $20 for same segment
- Diagnosis: Different competitive landscape or offer fit
- Action: Localize offer for France or reduce bids by 40%

## LLM Response Templates
- "Your [segment_name] segment is underperforming with CTR [X]% vs [Y]% average. For this demographic, I recommend..."
- "The best performing segment is [name] with ROAS [X]x. Consider creating lookalike audiences from this segment's converters..."
- "Based on the data, [segment_name] and [segment_name] have similar CPAs, they could be consolidated to increase volume..."