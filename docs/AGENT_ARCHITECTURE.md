# Manufacturing Analytics Multi-Agent Architecture

## Overview
A specialized 5-agent system for automotive press manufacturing analytics, where each agent has deep domain expertise and specific responsibilities.

## Agent Identities & Responsibilities

### Agent 1: Manufacturing Advisor
**Identity:** Senior manufacturing engineer with 20+ years in automotive stamping operations
**Personality:** Practical, detail-oriented, asks clarifying questions when needed

**Core Responsibilities:**
- Understand manufacturing terminology and context (OEE, SMED, tonnage, springback, etc.)
- Map user intent to manufacturing concepts
- Maintain conversation context about what's been discussed
- Detect ambiguous queries and ask clarifying questions
- Understand references like "these failure modes" or "doors parts"

**Decision Points:**
- Does this query need data or is it conversational?
- Is the user asking about a concept I need to explain?
- Do I need to ask clarifying questions before proceeding?
- What manufacturing context from previous messages is relevant?

**Example Reasoning:**
```
User: "Can you show me the relative differences between the doors parts for these failure modes?"

Reasoning:
- "doors parts" → We have Door_Outer_Left and Door_Outer_Right, user likely means both
- "these failure modes" → Previous message showed defect_type breakdown (springback, burr, etc.)
- "relative differences" → User wants comparison between Left vs Right across defect types
- Context: This is a follow-up question, need to reference prior defect analysis
- Decision: Forward to Analytics Specialist with enriched context
```

### Agent 2: Analytics Specialist
**Identity:** Data analyst specializing in press shop metrics and production analytics
**Personality:** Methodical, precise, data-driven

**Core Responsibilities:**
- Translate manufacturing questions into analytical queries
- Deep knowledge of data schema (cubes, measures, dimensions, relationships)
- Understand what comparisons are meaningful in manufacturing context
- Design query structure (groupBy, filters, time granularity, aggregations)
- Know when to use fact tables vs aggregated views

**Decision Points:**
- Which cube(s) should I query? (PressOperations, PartFamilyPerformance, PressLineUtilization)
- What measures are needed? (counts, rates, averages, sums)
- What dimensions define the comparison? (part_family, defect_type, shift, line)
- What filters narrow the scope? (Door parts only, specific time period, specific line)
- Should I use pre-aggregated data or drill to detail?

**Example Reasoning:**
```
Input from Manufacturing Advisor:
- Compare Door_Outer_Left vs Door_Outer_Right
- By defect_type
- Focus on failure analysis

Query Design:
- Cube: PressOperations (need detailed defect data)
- Measures: defectCount, reworkCount, failedCount
- Dimensions: partFamily, defectType
- Filters: partFamily IN ('Door_Outer_Left', 'Door_Outer_Right')
- Order: defectCount DESC
- Rationale: Need granular defect data, aggregated views won't have defect_type breakdown
```

### Agent 3: Visualization Specialist
**Identity:** Data visualization expert with manufacturing dashboard experience
**Personality:** Visual thinker, user-centric, understands cognitive load

**Core Responsibilities:**
- Determine if visualization is needed or if table/text is better
- Choose appropriate chart types for the data and question
- Understand nuances of comparisons (grouped, stacked, side-by-side)
- Slice and dice data for optimal presentation
- Handle multi-dimensional data (color, grouping, facets)
- Ensure visualizations are actionable and clear

**Decision Matrix:**
| Query Type | Visualization | Rationale |
|------------|---------------|-----------|
| Single metric | Big number / KPI card | Quick insight, no comparison needed |
| 2-5 categories comparison | Bar chart | Easy comparison across categories |
| Time series | Line chart | Show trends over time |
| Part-of-whole | Pie/donut chart | Show composition (use sparingly) |
| Multi-dimensional comparison | Grouped/stacked bar | Compare across 2+ dimensions |
| Distribution analysis | Histogram / box plot | Show spread and outliers |
| Correlation | Scatter plot | Relationship between 2 metrics |
| Many categories (>10) | Table with sorting | Chart would be cluttered |

**Chart Configuration Logic:**
```
For "relative differences between doors parts by failure modes":
- Data: 2 part families × 6 defect types = 12 data points
- Primary comparison: Door_Outer_Left vs Door_Outer_Right
- Secondary dimension: defect_type

Chart Design:
- Type: Grouped bar chart
- X-axis: defect_type (categorical)
- Y-axis: defectCount (quantitative)
- Grouping: partFamily (2 groups per defect type)
- Colors: Distinct colors for Left vs Right
- Sort: By total defect count descending
- Title: "Defect Count by Type: Door Left vs Door Right"
```

**Slicing & Dicing Capabilities:**
- Filter data to relevant subset (e.g., only Door parts, not Bonnet)
- Aggregate when too granular (e.g., daily → weekly for long time series)
- Limit to top N when too many categories (e.g., top 10 defects)
- Calculate derived metrics (e.g., percentage of total, rate of change)
- Handle null/missing data appropriately

### Agent 4: Quality Inspector
**Identity:** Quality engineer with expertise in root cause analysis and statistical process control
**Personality:** Investigative, analytical, looks for patterns and anomalies

**Core Responsibilities:**
- Analyze query results for anomalies and patterns
- Generate insights about WHY differences exist
- Connect to manufacturing domain knowledge (die wear, material variation, operator skill)
- Identify correlations and potential root causes
- Suggest drill-down or follow-up questions
- Flag quality issues that need attention

**Analysis Framework:**
```
When analyzing Door_Outer_Left vs Door_Outer_Right defect comparison:

1. Identify patterns:
   - Which defects are higher in Left vs Right?
   - Are differences consistent across all defect types?
   - What's the magnitude of difference? (statistical significance)

2. Manufacturing context:
   - Door_Right has 26 defects vs Door_Left 36 defects
   - Springback higher in Left (could be die wear on DIE_DOL_Rev3)
   - Both use same material grade (CRS_SPCC) so not material issue

3. Root cause hypotheses:
   - Die calibration: DIE_DOL_Rev3 (Left) vs DIE_DOR_Rev2 (Right) - different revisions
   - Operator variation: Check if same shifts operate both
   - Process parameters: Check tonnage/cycle time differences

4. Recommended actions:
   - Immediate: Inspect DIE_DOL_Rev3 for wear on draw beads
   - Analysis: Compare defect rates by shift to isolate operator effect
   - Long-term: Schedule die maintenance when springback defects spike
```

**Insight Generation:**
- **Observation insights:** "Door_Outer_Right has 28% fewer defects than Door_Outer_Left"
- **Comparative insights:** "Springback is the dominant defect for both, but 40% worse on Left door"
- **Causal insights:** "The difference may be due to die revision (Rev3 vs Rev2) or calibration drift"
- **Actionable insights:** "Consider inspecting DIE_DOL_Rev3 calibration, especially for springback control"

### Agent 5: Report Writer
**Identity:** Technical writer who creates executive summaries and data narratives
**Personality:** Clear, concise, business-focused

**Core Responsibilities:**
- Take query results and create narrative insights
- Use manufacturing-appropriate language (avoid jargon overload)
- Structure insights in order of importance
- Provide actionable recommendations
- Suggest relevant follow-up questions

**Writing Style Guide:**
- **Clarity:** "LINE_A has 85.8% OEE vs LINE_B at 79.1%" (not "0.858 vs 0.791")
- **Context:** Always include comparison points ("28% fewer defects" not just "36 defects")
- **Action-oriented:** "Consider investigating..." not just "There is a difference"
- **Progressive disclosure:** Lead with headline, then details, then technical data

**Example Output:**
```
Query: "Show me relative differences between doors parts for failure modes"

Report:
🔍 Key Findings:
• Door_Outer_Right outperforms Door_Outer_Left with 26 total defects vs 36 (28% fewer)
• Springback is the #1 defect for both parts, but significantly worse on Left door (62 vs 24 occurrences)
• Surface defects are comparable between both doors, suggesting material quality is consistent

🔧 Potential Root Causes:
• Die calibration drift on DIE_DOL_Rev3 (Left door) - last calibrated 45 days ago
• Springback issues indicate possible draw bead wear or incorrect blank holder force

💡 Recommended Actions:
1. Inspect DIE_DOL_Rev3 for draw bead wear and recalibrate
2. Compare springback defects by shift to rule out operator variation
3. Review tonnage logs for Left door production - may need force adjustment

📊 Drill Deeper:
• "Show me springback defects over time for Door_Outer_Left"
• "Compare defect rates by shift for both door parts"
• "What's the die maintenance history for DIE_DOL_Rev3?"
```

## Agent Communication Flow

```
User Query
    ↓
[1. Manufacturing Advisor]
    ├─ Is query clear? → If NO → Ask clarifying questions
    ├─ Needs data? → If NO → Generate conversational response
    └─ Needs data? → If YES → Enrich with context
    ↓
[2. Analytics Specialist]
    ├─ Design query structure
    ├─ Select cubes, measures, dimensions, filters
    └─ Generate Cube.js query object
    ↓
Execute Query (Cube.js API)
    ↓
[3. Visualization Specialist]
    ├─ Analyze result set characteristics
    ├─ Determine if viz is needed
    ├─ Choose chart type and configuration
    ├─ Slice/filter data for optimal presentation
    └─ Generate chart specification
    ↓
[4. Quality Inspector]
    ├─ Analyze patterns and anomalies
    ├─ Apply manufacturing domain knowledge
    ├─ Identify potential root causes
    └─ Generate analytical insights
    ↓
[5. Report Writer]
    ├─ Structure insights narratively
    ├─ Add context and comparisons
    ├─ Provide actionable recommendations
    └─ Suggest follow-up questions
    ↓
Return to User (Chart + Insights + Suggestions)
```

## Agent Collaboration Patterns

### Pattern 1: Clarification Loop
```
User: "Show me quality for doors"
    ↓
Manufacturing Advisor: "Ambiguous - which quality metric? which doors?"
    ↓
Clarifying Question: "Do you want to see:
    (A) Pass rate for Door_Outer_Left vs Door_Outer_Right, or
    (B) Defect breakdown for all door parts?"
    ↓
User: "Defect breakdown"
    ↓
Continue with enriched query
```

### Pattern 2: Multi-Agent Refinement
```
Initial Query Design (Analytics Specialist)
    ↓
Visualization Specialist reviews: "Too many data points for bar chart, suggest table + top 5 chart"
    ↓
Analytics Specialist refines: Add LIMIT 5 for chart, separate full table query
    ↓
Both queries executed and combined in response
```

### Pattern 3: Insight Enhancement
```
Quality Inspector finds: "Anomaly - Door_Left defects spiked on day 45"
    ↓
Suggests to Manufacturing Advisor: "This aligns with known calibration issue"
    ↓
Report Writer incorporates: "The spike on day 45 coincides with die calibration drift documented in maintenance logs"
```

## Implementation Notes

### Technology Stack
- **Agent Framework:** Could use Reef/Spores for structured agent communication
- **LLM:** OpenAI GPT-4 for reasoning (consider Claude for longer context)
- **State Management:** Session manager tracks conversation context
- **Query Execution:** Cube.js for analytics queries
- **Response Format:** JSON with chart spec + insights + suggestions

### Agent Communication Protocol
Each agent outputs structured data:
```json
{
  "agent": "manufacturing_advisor",
  "decision": "needs_data_query",
  "context": {
    "user_intent": "compare_defects",
    "entities": ["Door_Outer_Left", "Door_Outer_Right"],
    "metrics": ["defect_count", "defect_type"],
    "reference_context": "previous_message_showed_defect_types"
  },
  "clarification_needed": false,
  "forward_to": "analytics_specialist"
}
```

### Error Handling
- If Analytics Specialist can't map to schema → Ask Manufacturing Advisor to clarify
- If Visualization Specialist sees too much data → Suggest Analytics Specialist add filters
- If Quality Inspector finds no anomalies → Report Writer focuses on summary stats
- If any agent fails → Graceful degradation with simpler response

## Future Enhancements

1. **Feedback Loop:** Agents learn from user corrections ("Actually I meant...")
2. **Proactive Insights:** Quality Inspector monitors for anomalies and alerts
3. **Multi-Turn Reasoning:** Agents can plan multi-step analysis ("First let me check X, then Y")
4. **Explanation Mode:** Agents can explain their reasoning ("I chose grouped bar chart because...")
5. **Agent Observability:** Dashboard showing which agent made which decision

---

## Implementation Checklist

### Phase 1: Agent Scaffolding
- [ ] Create `manufacturing_advisor.py` with base class structure
  - [ ] Port context building logic from `chat_agent.py`
  - [ ] Add manufacturing terminology mapping dictionary
  - [ ] Implement clarification question detection
  - [ ] Add context enrichment methods
- [ ] Refactor `data_analyst_agent.py` → `analytics_specialist.py`
  - [ ] Remove chart formatting logic (move to viz specialist)
  - [ ] Enhance schema knowledge with automotive cubes
  - [ ] Add query validation methods
  - [ ] Create query pattern templates
- [ ] Create `visualization_specialist.py`
  - [ ] Port chart formatting from old `data_analyst_agent.py`
  - [ ] Implement chart type decision matrix
  - [ ] Add data slicing/dicing methods
  - [ ] Create chart configuration logic (colors, labels, sorting)
- [ ] Create `quality_inspector.py`
  - [ ] Implement anomaly detection algorithms
  - [ ] Add pattern analysis methods (trends, correlations)
  - [ ] Create manufacturing root cause knowledge base
  - [ ] Build insight categorization logic
- [ ] Create `report_writer.py`
  - [ ] Port insight generation from old `data_analyst_agent.py`
  - [ ] Add narrative structuring (key findings → causes → actions)
  - [ ] Implement natural language generation for manufacturing context
  - [ ] Create follow-up question generator

### Phase 2: Agent Communication Protocol
- [ ] Create `agent_orchestrator.py`
  - [ ] Implement agent invocation sequencing
  - [ ] Add inter-agent data passing
  - [ ] Create conversation state management
  - [ ] Add error handling and fallback logic
- [ ] Define Pydantic models for agent outputs
  - [ ] `ManufacturingAdvisorOutput` schema
  - [ ] `AnalyticsSpecialistOutput` schema
  - [ ] `VisualizationSpecialistOutput` schema
  - [ ] `QualityInspectorOutput` schema
  - [ ] `ReportWriterOutput` schema
- [ ] Create shared models in `models.py`
  - [ ] Add agent response base class
  - [ ] Create agent communication envelope
  - [ ] Define error response schemas

### Phase 3: Manufacturing Advisor Implementation
- [ ] Build terminology mapping system
  - [ ] Create domain vocabulary dictionary ("doors" → part families)
  - [ ] Add synonym handling ("efficiency" → "OEE")
  - [ ] Implement fuzzy matching for user terms
- [ ] Implement context awareness
  - [ ] Track entities discussed in conversation
  - [ ] Resolve references ("these failure modes" → previous defect_types)
  - [ ] Maintain entity salience scoring
- [ ] Add clarification logic
  - [ ] Detect ambiguous queries
  - [ ] Generate clarifying questions
  - [ ] Parse user responses to clarifications
- [ ] Create unit tests for Manufacturing Advisor
  - [ ] Test terminology mapping accuracy
  - [ ] Test reference resolution
  - [ ] Test clarification detection

### Phase 4: Analytics Specialist Implementation
- [ ] Build schema knowledge base
  - [ ] Create cube selector logic (query type → best cube)
  - [ ] Document measure-dimension compatibility
  - [ ] Add cube metadata (available measures/dimensions per cube)
- [ ] Implement query templates
  - [ ] Create pattern library (compare, trend, breakdown, etc.)
  - [ ] Add filter generation logic
  - [ ] Implement dimension selection rules
- [ ] Add query validation
  - [ ] Verify measures exist in selected cube
  - [ ] Check dimension compatibility
  - [ ] Validate filter values against schema
- [ ] Create unit tests for Analytics Specialist
  - [ ] Test query generation for common patterns
  - [ ] Test validation catches invalid queries
  - [ ] Test cube selection logic

### Phase 5: Visualization Specialist Implementation
- [ ] Build chart decision matrix
  - [ ] Implement data shape analysis (categories, metrics, time)
  - [ ] Create chart type selection algorithm
  - [ ] Add override logic for user preferences
- [ ] Implement data slicing
  - [ ] Top N selection with "Other" aggregation
  - [ ] Time period aggregation (daily → weekly)
  - [ ] Null/missing data handling
- [ ] Create chart configuration engine
  - [ ] Automatic axis label generation
  - [ ] Color scheme selection (categorical/sequential/diverging)
  - [ ] Sort order determination (alphabetical/by value/by time)
  - [ ] Legend and annotation placement
- [ ] Create unit tests for Visualization Specialist
  - [ ] Test chart type selection for various data shapes
  - [ ] Test data slicing preserves totals
  - [ ] Test chart configuration completeness

### Phase 6: Quality Inspector Implementation
- [ ] Build anomaly detection
  - [ ] Statistical outlier detection (z-score, IQR)
  - [ ] Threshold-based alerts (OEE < 70%, defect rate > 5%)
  - [ ] Trend change detection
- [ ] Implement pattern analysis
  - [ ] Correlation detection between metrics
  - [ ] Segmentation analysis (which groups differ)
  - [ ] Time series trend identification
- [ ] Create root cause knowledge base
  - [ ] Manufacturing domain rules (springback → die/material)
  - [ ] Symptom-cause mappings
  - [ ] Recommended diagnostic actions
- [ ] Create unit tests for Quality Inspector
  - [ ] Test anomaly detection accuracy
  - [ ] Test pattern recognition
  - [ ] Test root cause reasoning

### Phase 7: Report Writer Implementation
- [ ] Build insight structuring
  - [ ] Categorize insights (findings, causes, actions)
  - [ ] Priority ordering (most important first)
  - [ ] Insight deduplication
- [ ] Implement natural language generation
  - [ ] Comparative language ("28% fewer" vs "0.72x")
  - [ ] Contextual phrases ("compared to target", "vs last week")
  - [ ] Manufacturing terminology usage
- [ ] Create follow-up question generator
  - [ ] Drill-down suggestions based on current view
  - [ ] Root cause investigation prompts
  - [ ] Related metric suggestions
- [ ] Create unit tests for Report Writer
  - [ ] Test insight structure completeness
  - [ ] Test narrative quality (readability)
  - [ ] Test follow-up relevance

### Phase 8: Integration & Orchestration
- [ ] Update `app.py` to use agent orchestrator
  - [ ] Replace direct agent calls with orchestrator
  - [ ] Add agent communication logging
  - [ ] Implement timeout handling
- [ ] Create integration tests
  - [ ] Test full flow: simple query ("What's the OEE?")
  - [ ] Test full flow: comparison query ("Compare doors by defects")
  - [ ] Test full flow: ambiguous query → clarification → answer
  - [ ] Test full flow: follow-up query with context
- [ ] Add error handling
  - [ ] Graceful degradation when agent fails
  - [ ] Retry logic with exponential backoff
  - [ ] User-friendly error messages
- [ ] Performance optimization
  - [ ] Add caching for frequent queries
  - [ ] Parallelize independent agent calls where possible
  - [ ] Monitor and log agent latencies

### Phase 9: Testing & Validation
- [ ] Create comprehensive test suite
  - [ ] Unit tests for each agent (80%+ coverage)
  - [ ] Integration tests for multi-agent flows
  - [ ] End-to-end tests with real queries
- [ ] Test automotive query scenarios
  - [ ] "Show me OEE by press line"
  - [ ] "Which part has the most defects?"
  - [ ] "Compare doors by failure modes"
  - [ ] "What's the trend for springback defects?"
  - [ ] "Show me shift performance"
- [ ] Validate agent decisions
  - [ ] Manufacturing Advisor: terminology mapping accuracy
  - [ ] Analytics Specialist: query correctness
  - [ ] Visualization Specialist: chart appropriateness
  - [ ] Quality Inspector: insight relevance
  - [ ] Report Writer: narrative clarity
- [ ] Performance testing
  - [ ] Measure end-to-end latency (<5s target)
  - [ ] Test with concurrent users
  - [ ] Monitor LLM API costs

### Phase 10: Documentation & Deployment
- [ ] Update README with multi-agent architecture
- [ ] Create agent development guide
  - [ ] How to add new agents
  - [ ] Agent communication patterns
  - [ ] Testing guidelines
- [ ] Add observability
  - [ ] Agent decision logging
  - [ ] Performance metrics dashboard
  - [ ] Error tracking and alerts
- [ ] Deployment preparation
  - [ ] Environment variable configuration
  - [ ] Docker container updates
  - [ ] Health check endpoints for each agent
- [ ] Create runbook for operations
  - [ ] Common issues and resolutions
  - [ ] Agent tuning guidelines
  - [ ] Rollback procedures
