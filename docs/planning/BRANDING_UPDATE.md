# Frontend Branding Update

## Changes Made

### 1. Logos Added ✓
- **Main Logo**: `praval_agentic_analytics.png` (left side, next to title)
- **Praval Logo**: `praval-logo.png` (right side of header)
- Both logos copied to `frontend/public/` directory

### 2. Title Updated ✓
- Changed from "Manufacturing Analytics"
- To: **"Praval Agentic Analytics"**
- Updated in:
  - Header title
  - Welcome message
  - Browser tab title (metadata)

### 3. Header Layout Redesigned ✓
**New structure**:
```
┌────────────────────────────────────────────────────────┐
│ [Main Logo] Praval Agentic Analytics     [Praval Logo] │
│             Ask questions about...                      │
└────────────────────────────────────────────────────────┘
```

**Layout details**:
- Left side: Main logo + title + subtitle
- Right side: Praval logo
- Flexbox layout for responsive alignment
- Gradient purple background maintained

### 4. Files Modified

| File | Changes |
|------|---------|
| `frontend/src/components/ChatInterface.tsx` | Added logo images, updated title |
| `frontend/src/app/globals.css` | New header layout styles, logo sizing |
| `frontend/src/app/layout.tsx` | Updated page title metadata |
| `frontend/public/praval-logo.png` | Copied from ~/Github/praval/docs/logo.png |
| `frontend/public/praval_agentic_analytics.png` | Copied from img/ directory |

### 5. Styling Details

```css
.main-logo {
  height: 50px;        /* Main branding logo */
  width: auto;
}

.praval-logo {
  height: 45px;        /* Praval logo (right side) */
  width: auto;
}

.header-content {
  display: flex;
  justify-content: space-between;  /* Space between left and right */
  align-items: center;
}

.header-left {
  display: flex;
  gap: 15px;           /* Space between logo and text */
  align-items: center;
}
```

## Visual Layout

```
╔═══════════════════════════════════════════════════════════╗
║  [📊]  Praval Agentic Analytics               [🔷]        ║
║        Ask questions about production quality...          ║
╚═══════════════════════════════════════════════════════════╝
```

**Elements**:
- 📊 = praval_agentic_analytics.png (main logo)
- 🔷 = praval-logo.png (brand mark)

## Access the Updated UI

1. **Open browser**: http://localhost:3000
2. **Hard refresh**: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

You should see:
- Main "Praval Agentic Analytics" logo on the left
- Title next to the main logo
- Praval brand logo on the right side
- All with purple gradient background

## Logo Specifications

| Logo | Size | Location | Purpose |
|------|------|----------|---------|
| praval_agentic_analytics.png | 50px height | Left side | Main product branding |
| praval-logo.png | 45px height | Right side | Praval brand identity |

## Files Structure

```
frontend/
├── public/
│   ├── praval-logo.png              (1.4MB)
│   └── praval_agentic_analytics.png (888KB)
├── src/
│   ├── components/
│   │   └── ChatInterface.tsx        (Updated header)
│   └── app/
│       ├── layout.tsx               (Updated title)
│       └── globals.css              (New header styles)
```

## Next Steps (Optional)

1. **Favicon**: Add Praval favicon to `frontend/public/favicon.ico`
2. **Mobile responsive**: Adjust logo sizes for smaller screens
3. **Loading state**: Show logo while app initializes
4. **Dark mode**: Add dark mode variant of logos if needed

## Testing

Verify the following:
- ✓ Both logos visible in header
- ✓ Title reads "Praval Agentic Analytics"
- ✓ Browser tab shows "Praval Agentic Analytics"
- ✓ Welcome message updated
- ✓ Logos don't overlap on smaller screens
- ✓ Purple gradient background maintained

## Troubleshooting

### Issue: Logos not showing
**Check**:
```bash
ls /Users/rajesh/Github/praval_mds_analytics/frontend/public/
# Should show both PNG files
```

**Solution**: Rebuild frontend
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### Issue: Old title still showing
**Solution**: Hard refresh browser (Cmd+Shift+R)

### Issue: Layout broken on mobile
**Add to globals.css**:
```css
@media (max-width: 768px) {
  .main-logo { height: 40px; }
  .praval-logo { height: 35px; }
  .chat-header h1 { font-size: 18px; }
}
```

## Summary

✓ "Praval Agentic Analytics" branding applied
✓ Main logo displayed on left side of header
✓ Praval brand logo displayed on right side
✓ All titles and metadata updated
✓ Clean, professional header layout
✓ Frontend rebuilt and running

Access at: http://localhost:3000
