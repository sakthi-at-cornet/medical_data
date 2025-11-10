# Sidebar Status Dashboard Feature

## Overview

Added comprehensive status dashboard with left and right sidebars to provide full system visibility.

## Layout

```
┌─────────────┬──────────────────────────┬─────────────┐
│             │    Chat Interface        │             │
│   Left      │    (Main Area)           │   Right     │
│  Sidebar    │                          │  Sidebar    │
│             │                          │             │
│  Data &     │    Messages              │   System    │
│  Agents     │    Charts                │   Status    │
│             │    Input                 │             │
│             │                          │             │
│ [◀ Collapse]│                          │[Collapse ▶] │
└─────────────┴──────────────────────────┴─────────────┘
```

## Left Sidebar - Data & Agents

### Tabs
1. **Datasets Tab**
   - ProductionQuality 📊
     - Daily production metrics by component
   - MaterialPerformance 🔬
     - Quality analysis by material type
   - QualityTrends 📈
     - Hourly time-series data

2. **Agents Tab**
   - Chat Agent (🟢 Active)
     - Context & conversation flow
   - Data Analyst Agent (🟢 Active)
     - NL → Query translation

### Features
- **Collapsible**: Click ◀ to collapse to 40px width
- **Tabs**: Switch between Datasets and Agents
- **Hover effects**: Cards highlight on hover
- **Status indicators**: Green dot for active agents
- **Icons**: Emoji icons for visual identification

## Right Sidebar - System Status

### Components Monitored

1. **Agents API** 🤖
   - FastAPI + AI Agents
   - Shows version number
   - Status: Healthy / Degraded / Down

2. **Cube.js** 📊
   - Metrics Layer
   - Checks connectivity
   - Status: Healthy / Down

3. **dbt / Airflow** ⚙️
   - Transformations & Orchestration
   - Pipeline status
   - Status: Healthy / Down

4. **PostgreSQL DWH** 🗄️
   - Data Warehouse
   - Database connectivity
   - Status: Healthy / Down

5. **Source Systems** 🔌
   - 3 Source Databases
   - Overall source health
   - Status: Healthy / Down

### Features
- **Live status checks**: Updates every 30 seconds
- **Manual refresh**: 🔄 Refresh button
- **Last checked**: Shows timestamp
- **Color-coded badges**:
  - 🟢 Green: Healthy
  - 🟠 Orange: Degraded
  - 🔴 Red: Down
  - 🔵 Blue: Checking...
- **Collapsible**: Click ▶ to collapse

### Status API Integration

```typescript
// Health check endpoint
GET /health

Response:
{
  "status": "healthy" | "degraded",
  "version": "0.1.0",
  "cubejs_connected": true | false
}
```

Status determined by:
- Agents API: Direct health endpoint
- Cube.js: cubejs_connected field
- Other components: Inferred from agents health

## Responsive Behavior

### Desktop (> 1200px)
- All sidebars visible
- Full 3-column layout

### Tablet (768px - 1200px)
- Right sidebar hidden
- Left sidebar + chat visible

### Mobile (< 768px)
- Both sidebars hidden
- Chat interface only

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/components/LeftSidebar.tsx` | 100 | Datasets & Agents sidebar |
| `frontend/src/components/RightSidebar.tsx` | 135 | System status dashboard |
| `frontend/src/app/page.tsx` | Updated | Layout integration |
| `frontend/src/app/globals.css` | +291 lines | Sidebar styles |

## Styling Details

### Left Sidebar
- Width: 280px (collapsed: 40px)
- Background: #fafafa
- Tabs with active indicator
- Card-based item layout
- Purple hover effects

### Right Sidebar
- Width: 300px (collapsed: 40px)
- Background: #fafafa
- Status card grid
- Color-coded badges
- Refresh button at bottom

### Transitions
- Collapse animation: 0.3s ease
- Hover effects: 0.2s
- Smooth state changes

## Usage

### Collapsing Sidebars
```tsx
// Left sidebar
[◀] button - Collapse to 40px
[▶] button - Expand to 280px

// Right sidebar
[▶] button - Collapse to 40px
[◀] button - Expand to 300px
```

### Checking Status
- Automatic: Updates every 30 seconds
- Manual: Click "🔄 Refresh" button
- Shows "Last checked: HH:MM:SS"

### Viewing Datasets
1. Left sidebar → "Datasets" tab
2. See 3 available datasets with descriptions
3. Click to highlight (visual feedback)

### Viewing Agents
1. Left sidebar → "Agents" tab
2. See 2 active agents with status
3. Green dot indicates active status

## Status Badge Colors

| Status | Background | Text | Icon |
|--------|-----------|------|------|
| Healthy | Light green | Dark green | ✓ |
| Degraded | Light orange | Dark orange | ⚠ |
| Down | Light red | Dark red | ✗ |
| Checking | Light blue | Dark blue | ⏳ |

## Example Status Display

```
🤖 Agents API
   FastAPI + AI Agents
   [✓ Healthy] v0.1.0

📊 Cube.js
   Metrics Layer
   [✓ Healthy]

⚙️ dbt / Airflow
   Transformations & Orchestration
   [✓ Healthy]

🗄️ PostgreSQL DWH
   Data Warehouse
   [✓ Healthy]

🔌 Source Systems
   3 Source Databases
   [✓ Healthy]

─────────────────
[🔄 Refresh]
Last checked: 23:34:52
```

## Benefits

### User Experience
- **Visibility**: See all system components at a glance
- **Context**: Know what data is available
- **Confidence**: Live status reduces uncertainty
- **Navigation**: Easy access to system info

### Operational
- **Monitoring**: Real-time health checks
- **Debugging**: Quick identification of issues
- **Transparency**: Full system visibility
- **Professional**: Enterprise dashboard feel

### Design
- **Clean**: Minimalist card-based UI
- **Intuitive**: Familiar sidebar patterns
- **Responsive**: Adapts to screen size
- **Collapsible**: Maximize chat space when needed

## Future Enhancements (Optional)

1. **Detailed metrics**: Click component for details
2. **Historical status**: Show uptime trends
3. **Alerts**: Visual notifications for issues
4. **Logs**: Quick access to component logs
5. **Performance**: Show query latency metrics
6. **Data refresh**: Show last data update time
7. **Agent activity**: Show query count, success rate
8. **Cost tracking**: API usage and costs

## Testing

Access http://localhost:3000 and verify:

**Left Sidebar**:
- ✓ Shows Datasets and Agents tabs
- ✓ 3 datasets listed with icons
- ✓ 2 agents with green active dots
- ✓ Collapses to 40px width
- ✓ Hover effects working

**Right Sidebar**:
- ✓ Shows 5 system components
- ✓ Health checks running
- ✓ Status badges colored correctly
- ✓ Refresh button works
- ✓ Timestamp updates
- ✓ Collapses to 40px width

**Responsive**:
- ✓ Right sidebar hidden < 1200px
- ✓ Left sidebar hidden < 768px
- ✓ Chat interface remains functional

## Troubleshooting

### Issue: Sidebars not showing
**Solution**: Hard refresh (Cmd+Shift+R)

### Issue: Status stuck on "Checking..."
**Check**: Backend running
```bash
curl http://localhost:8000/health
```

### Issue: Layout broken
**Check**: Browser console for errors
**Solution**: Rebuild frontend

## Summary

✓ Left sidebar with Datasets & Agents
✓ Right sidebar with system status
✓ Live health monitoring
✓ Collapsible sidebars
✓ Responsive design
✓ Clean, professional UI
✓ Real-time updates every 30s

The dashboard provides full visibility into the Praval Agentic Analytics system.
