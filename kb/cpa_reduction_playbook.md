# CPA Reduction Playbook

## Definition
CPA (Cost Per Acquisition) measures cost per conversion. Formula: Spend / Conversions. Lower CPA indicates more efficient customer acquisition.

## Frequent Symptoms
- CPA exceeding target by 25%+
- CPA increasing while conversion rate drops
- High CPA variance between audience segments
- CPA higher on mobile than desktop
- New campaign CPA > established campaign CPA by 100%+

## Probable Causes
- Poor conversion funnel optimization
- High bounce rate on landing pages
- Mismatched audience to offer
- Form friction (too many fields)
- Slow page load speed on conversion pages
- Weak value proposition post-click
- Incorrect conversion tracking or attribution

## Data Diagnostics (from CSV)
Check these patterns:
- Group by `audience_segment`: Identify high-CPA segments to exclude
- Group by `country`: Find geographic cost inefficiencies
- Compare `cpa` vs `ctr`: Low CTR often precedes high CPA
- Analyze `conversions` relative to `clicks`: Calculate conversion rate drop-offs
- Cross-reference with `ad_format`: Some formats naturally have lower CPA

## Actionable Recommendations

### Pre-Conversion Optimization
1. Simplify forms to 3 fields maximum
2. Add trust signals (testimonials, security badges)
3. Implement exit-intent popups with offers
4. Add progress indicators for multi-step forms
5. Test one-click checkout or signup

### Audience Refinement
1. Create exclusion lists for high-CPA segments
2. Build lookalikes from converting users only
3. Implement frequency capping at 3 impressions/day
4. Use suppression lists for converted users

### Funnel Improvements
1. Reduce landing page load time to under 2 seconds
2. Match ad copy to landing page headline exactly
3. Add social proof near conversion buttons
4. Test pricing page layout and options

## Heuristic Rules
- If CPA > target by 50% for 5 days: Pause campaign
- If mobile CPA > desktop CPA by 40%: Reduce mobile bids by 30%
- If CPA increases with budget: Implement automated rules to pause at CPA cap
- If CPA drops on weekends: Increase weekend budget by 50%

## Concrete Examples

**Example 1: High CPA on Form Submits**
- Data: CPA $45, target $30, conversion rate 2%
- Diagnosis: 12-field form causing drop-off
- Action: Reduce to 4 fields, CPA dropped to $28

**Example 2: Audience Segment Inefficiency**
- Data: 18-24 segment CPA $60, 25-34 segment CPA $25
- Diagnosis: Younger audience less ready to purchase
- Action: Exclude 18-24, allocate budget to 25-34

## LLM Response Templates
- "Your CPA of $[X] exceeds target by [Y]%, with conversion rate only [Z]%. The primary issue appears to be..."
- "The [segment_name] audience segment has the highest CPA at $[X], recommend excluding or re-evaluating..."
- "Based on the data, your conversion funnel is losing [X]% of users between click and conversion, suggesting..."