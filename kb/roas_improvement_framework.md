# ROAS Improvement Framework

## Definition
ROAS (Return on Ad Spend) measures revenue generated per dollar spent. Formula: Revenue / Spend. ROAS of 4.0 means $4 revenue for every $1 spent.

## Frequent Symptoms
- ROAS below target (typically 3.0-5.0x for ecommerce)
- ROAS declining while spend increases
- High variance in ROAS by country or segment
- ROAS lower on new customer campaigns than retention
- Weekend ROAS lower than weekday ROAS

## Probable Causes
- Low average order value (AOV)
- High percentage of return customers
- Poor product-market fit for audience
- Seasonal demand fluctuations
- Competitive pressure on pricing
- Inefficient upselling/cross-selling
- Long conversion cycles misattributed

## Data Diagnostics (from CSV)
Check these patterns:
- Group by `country`: Identify most profitable markets
- Group by `audience_segment`: Calculate ROAS by segment
- Group by `ad_format`: Compare ROAS efficiency
- Time series: Track ROAS trends over `date`
- Correlation: ROAS vs `spend` - diminishing returns?

## Actionable Recommendations

### Revenue Optimization
1. Implement post-purchase upsells (increase AOV by 15-25%)
2. Create bundled offers (product + accessory)
3. Add subscription or loyalty programs
4. Implement cart abandon recovery emails
5. Test pricing strategies (anchoring, decoy effects)

### Spend Allocation
1. Shift 70% budget to top 3 ROAS segments
2. Cap spending on campaigns below target ROAS
3. Test incrementality to find true ROAS
4. Implement dayparting based on ROAS by hour

### Customer Segmentation
1. Separate acquisition vs retention campaigns
2. Create VIP segments with higher lifetime value
3. Implement win-back for high-value lapsed customers
4. Test different offers by segment profitability

## Heuristic Rules
- If ROAS < 2.0 for 7 days: Pause campaign immediately
- If ROAS drops 30% week-over-week: Check for new competitors
- If ROAS > 8.0: Increase budget by 50% (likely under-spending)
- If spend > $10,000 with ROAS < 1.5: Full campaign audit required

## Concrete Examples

**Example 1: Declining ROAS with Scale**
- Data: At $5k spend ROAS 5.0, at $10k spend ROAS 2.5
- Diagnosis: Audience saturation, diminishing returns
- Action: Cap spend at $6k, find new audiences

**Example 2: Low ROAS on Display**
- Data: Display ROAS 1.8 vs target 4.0
- Diagnosis: Brand awareness not driving immediate purchase
- Action: Add retargeting to display, measure assisted conversions

## LLM Response Templates
- "Your overall ROAS of [X]x is below the [Y]x target. The [segment] segment is most efficient at [Z]x, while [segment2] is dragging performance at [W]x..."
- "ROAS is declining as spend increases past $[X], indicating saturation. The optimal spend level appears to be $[Y]..."
- "Based on geographic analysis, [country] has ROAS of [X]x compared to [Y]x average, suggesting opportunity to reallocate budget from..."