# Multi-Agent System Implementation Plan

## Objective
Transform the current 2-agent system into a sophisticated 5-agent architecture with clear identities and specialized responsibilities.

## Current State Analysis

### Existing Agents
1. **ChatAgent** → Will become **Manufacturing Advisor**
   - Currently: Generic router (should_query_data, generate_conversational_response)
   - Needs: Manufacturing domain expertise, clarification capabilities

2. **DataAnalystAgent** → Will split into 2 agents:
   - **Analytics Specialist** (query design)
   - **Visualization Specialist** (chart selection)

### New Agents Needed
3. **Visualization Specialist** - NEW
4. **Quality Inspector** - NEW
5. **Report Writer** - Enhance existing insight generation

## Implementation Phases

### Phase 1: Agent Scaffolding (Foundation)
**Goal:** Create the 5 agent classes with clear interfaces

**Tasks:**
1. Create `manufacturing_advisor.py`
   - Port relevant logic from `chat_agent.py`
   - Add manufacturing terminology mapping
   - Add clarification question logic
   - Add context enrichment capabilities

2. Refactor `data_analyst_agent.py` → `analytics_specialist.py`
   - Focus only on query design
   - Remove chart formatting logic
   - Add query validation
   - Enhance schema knowledge with automotive context

3. Create `visualization_specialist.py`
   - Port chart formatting from old data_analyst_agent
   - Add chart type decision matrix
   - Add slicing/dicing logic
   - Add data transformation capabilities

4. Create `quality_inspector.py`
   - Anomaly detection logic
   - Pattern analysis
   - Root cause reasoning
   - Manufacturing domain knowledge base

5. Create `report_writer.py`
   - Port insight generation from old data_analyst_agent
   - Enhance with narrative structure
   - Add actionable recommendations
   - Add follow-up question generation

**Deliverable:** 5 agent classes with clear interfaces

### Phase 2: Agent Communication Protocol
**Goal:** Define how agents communicate and pass data

**Design Decisions:**
- **Option A:** Sequential pipeline (Agent1 → Agent2 → Agent3 → Agent4 → Agent5)
  - Pros: Simple, predictable flow
  - Cons: Rigid, can't handle clarifications mid-flow

- **Option B:** Orchestrator pattern (Central coordinator calls agents as needed)
  - Pros: Flexible, can handle clarifications
  - Cons: More complex orchestration logic

- **Option C:** Reef/Spores framework (Structured multi-agent system)
  - Pros: Built-in state management, agent discovery, observability
  - Cons: New dependency, learning curve

**Recommendation:** Start with Option B (Orchestrator), migrate to Option C (Reef) later

**Tasks:**
1. Create `agent_orchestrator.py`
   - Manages agent invocation sequence
   - Handles inter-agent communication
   - Manages conversation state
   - Error handling and fallbacks

2. Define agent output schemas (Pydantic models)
   ```python
   class ManufacturingAdvisorOutput:
       decision: str  # "needs_data", "conversational", "clarification"
       enriched_query: str
       entities: dict
       clarification_question: Optional[str]

   class AnalyticsSpecialistOutput:
       cube_query: CubeQuery
       rationale: str
       confidence: float

   class VisualizationSpecialistOutput:
       chart_type: str
       chart_config: dict
       data_transformations: list

   class QualityInspectorOutput:
       insights: list[str]
       anomalies: list[dict]
       root_causes: list[str]

   class ReportWriterOutput:
       narrative: str
       recommendations: list[str]
       follow_up_questions: list[str]
   ```

**Deliverable:** Agent communication framework

### Phase 3: Manufacturing Advisor (Agent 1)
**Goal:** Build the first line of user interaction

**Key Capabilities:**
1. **Manufacturing Terminology Mapping**
   ```python
   TERMINOLOGY_MAP = {
       "doors": ["Door_Outer_Left", "Door_Outer_Right"],
       "doors parts": ["Door_Outer_Left", "Door_Outer_Right"],
       "bonnet": ["Bonnet_Outer"],
       "failure modes": "defect_type dimension",
       "quality issues": "defect_type dimension",
       "efficiency": "avgOee measure",
       "Line A": "LINE_A",
       "800T press": "LINE_A",
       # ... more mappings
   }
   ```

2. **Context Awareness**
   - Track what data was shown in previous messages
   - Resolve references like "these failure modes"
   - Maintain entity salience (what's currently being discussed)

3. **Clarification Logic**
   ```python
   def needs_clarification(self, query: str, entities: dict) -> bool:
       if not entities.get("part_family") and "quality" in query:
           return True  # Which part?
       if "compare" in query and len(entities.get("part_families", [])) < 2:
           return True  # Compare what to what?
       return False
   ```

**Deliverable:** Manufacturing Advisor that understands domain language

### Phase 4: Analytics Specialist (Agent 2)
**Goal:** Expert query designer

**Key Capabilities:**
1. **Schema Knowledge Base**
   ```python
   CUBE_SELECTOR = {
       "detailed_defects": "PressOperations",  # Has defect_type
       "part_comparison": "PartFamilyPerformance",  # Aggregated
       "shift_analysis": "PressLineUtilization",  # Shift metrics
       "oee_breakdown": "PressLineUtilization",  # Has OEE components
   }
   ```

2. **Query Templates**
   ```python
   QUERY_PATTERNS = {
       "compare_parts_by_defects": {
           "cube": "PressOperations",
           "measures": ["defectCount", "reworkCount"],
           "dimensions": ["partFamily", "defectType"],
           "filters": lambda parts: {"partFamily": {"in": parts}}
       },
       # ... more patterns
   }
   ```

3. **Query Validation**
   - Check if measures exist in selected cube
   - Verify dimension compatibility
   - Validate filter values against data

**Deliverable:** Robust query generation with validation

### Phase 5: Visualization Specialist (Agent 3)
**Goal:** Smart chart selection and data presentation

**Key Capabilities:**
1. **Chart Decision Matrix**
   ```python
   def select_chart_type(self, data_shape: dict, query_intent: str) -> str:
       num_categories = data_shape["num_categories"]
       num_metrics = data_shape["num_metrics"]
       has_time = data_shape["has_time_dimension"]

       if has_time:
           return "line"
       if num_categories > 10:
           return "table"  # Too many for chart
       if num_metrics == 1 and num_categories <= 5:
           return "bar"
       if num_metrics > 1 and num_categories <= 5:
           return "grouped_bar"
       # ... more logic
   ```

2. **Data Slicing**
   ```python
   def slice_for_visualization(self, data: list, chart_type: str) -> list:
       if chart_type == "bar" and len(data) > 10:
           # Show top 10, aggregate rest as "Other"
           sorted_data = sorted(data, key=lambda x: x["value"], reverse=True)
           top_10 = sorted_data[:10]
           other_sum = sum(x["value"] for x in sorted_data[10:])
           return top_10 + [{"category": "Other", "value": other_sum}]
       return data
   ```

3. **Chart Configuration**
   - Automatic axis labels
   - Color schemes (categorical, sequential, diverging)
   - Sorting (alphabetical, by value, by date)
   - Legends and annotations

**Deliverable:** Intelligent visualization engine

### Phase 6: Quality Inspector (Agent 4)
**Goal:** Analytical insights and root cause reasoning

**Key Capabilities:**
1. **Anomaly Detection**
   ```python
   def detect_anomalies(self, data: list, metric: str) -> list:
       values = [d[metric] for d in data]
       mean = statistics.mean(values)
       std = statistics.stdev(values)

       anomalies = []
       for d in data:
           z_score = abs((d[metric] - mean) / std)
           if z_score > 2:  # More than 2 std deviations
               anomalies.append({
                   "entity": d["category"],
                   "value": d[metric],
                   "expected_range": f"{mean-2*std:.1f} to {mean+2*std:.1f}",
                   "significance": "high" if z_score > 3 else "medium"
               })
       return anomalies
   ```

2. **Root Cause Knowledge Base**
   ```python
   ROOT_CAUSE_RULES = {
       "high_springback": [
           "Check die draw bead condition",
           "Verify material yield strength is within spec",
           "Review blank holder force settings"
       ],
       "left_right_asymmetry": [
           "Compare die calibration dates",
           "Check for operator variation by shift",
           "Review tonnage consistency"
       ],
       # ... more rules
   }
   ```

3. **Pattern Analysis**
   - Trend detection (increasing, decreasing, cyclical)
   - Correlation analysis (does X relate to Y?)
   - Segmentation (which groups behave differently?)

**Deliverable:** Insightful analysis engine

### Phase 7: Report Writer (Agent 5)
**Goal:** Clear, actionable communication

**Key Capabilities:**
1. **Insight Structuring**
   ```python
   def structure_insights(self, raw_insights: list) -> dict:
       return {
           "key_findings": [i for i in raw_insights if i["type"] == "finding"],
           "root_causes": [i for i in raw_insights if i["type"] == "cause"],
           "recommendations": [i for i in raw_insights if i["type"] == "action"],
       }
   ```

2. **Natural Language Generation**
   - Use comparatives ("28% fewer" not "0.72x")
   - Add context ("vs previous period", "compared to target")
   - Manufacturing terminology (not generic data terms)

3. **Follow-up Generation**
   ```python
   def generate_followups(self, current_query: str, results: dict) -> list:
       followups = []

       # If comparing parts, suggest drill-down
       if "part_family" in results["dimensions"]:
           parts = results["data"][0]["partFamily"]
           followups.append(f"Show me defect trends over time for {parts}")

       # If anomaly found, suggest root cause analysis
       if results.get("anomalies"):
           anomaly = results["anomalies"][0]
           followups.append(f"What factors contributed to {anomaly}?")

       return followups[:3]  # Max 3 suggestions
   ```

**Deliverable:** Professional reporting capability

### Phase 8: Integration & Testing
**Goal:** Wire everything together and validate

**Tasks:**
1. Update `app.py` to use orchestrator
2. Create integration tests for multi-agent flow
3. Test with various query types:
   - Simple queries ("What's the OEE?")
   - Complex comparisons ("Compare doors by failure modes")
   - Ambiguous queries ("Show me quality")
   - Follow-up queries ("What about the other part?")
4. Performance testing (latency with 5 agents)
5. Error handling for agent failures

**Deliverable:** Production-ready multi-agent system

## Implementation Timeline

**Week 1:** Phase 1-2 (Scaffolding + Communication)
**Week 2:** Phase 3-4 (Advisor + Analytics Specialist)
**Week 3:** Phase 5-6 (Viz Specialist + Quality Inspector)
**Week 4:** Phase 7-8 (Report Writer + Integration)

## Success Metrics

1. **Query Understanding:** Handle "doors parts" → Door_Outer_Left + Door_Outer_Right mapping (90%+ accuracy)
2. **Visualization Quality:** Choose appropriate chart type (95%+ alignment with best practices)
3. **Insight Depth:** Generate actionable root cause insights (measured by user follow-up rate)
4. **Response Time:** End-to-end latency <5 seconds for complex queries
5. **Clarification Rate:** Ask clarifying questions when needed (20-30% of ambiguous queries)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Latency from 5 sequential LLM calls | High | Run some agents in parallel, cache frequent patterns |
| Agents disagree (e.g., viz choice) | Medium | Clear priority hierarchy, orchestrator makes final call |
| Context loss across agents | High | Use structured output schemas, comprehensive state |
| Cost of multiple LLM calls | Medium | Use smaller models for simpler agents, cache results |
| Complexity makes debugging hard | High | Add logging at each agent transition, observability dashboard |

## Next Steps

**Immediate:**
1. Review and approve agent architecture
2. Decide on communication pattern (Orchestrator vs Reef)
3. Set up development branch for multi-agent work

**Questions for Decision:**
1. Should we implement Phase 1-8 sequentially or in parallel?
2. Do you want to see a prototype with 2-3 agents first before full implementation?
3. Should we use Reef/Spores or build custom orchestration?
4. What's the priority: query understanding, visualization quality, or insight depth?
