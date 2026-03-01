# Project Sentinel - Implementation Plan

## Overview
A Nuxt v4 dashboard application for SHIELD to forecast and analyze economic data concerning Avengers/supply chain actions. Theme: Tony Stark/Iron Man styled tech interface.

---

## Tech Stack
- **Framework**: Nuxt 4.3.1 (Vite)
- **UI**: shadcn-vue, TailwindCSS, @nuxt/ui
- **Auth**: better-auth with JWT plugin
- **Charts**: vue-chartjs + Chart.js
- **Globe**: globe.gl
- **Forms**: @tanstack/vue-form + zod
- **State**: Pinia
- **Database**: PostgreSQL (via node-postgres/pg)
- **Real-time**: RabbitMQ (amqplib)
- **API**: Nitro server routes

---

## Nuxt 4 Project Structure (app/ directory)
```
app/
├── components/          # Auto-imported Vue components
├── pages/               # File-based routing
├── layouts/              # Layouts
├── composables/          # Auto-imported composables
├── stores/               # Pinia stores
├── server/
│   └── api/             # API endpoints
├── app.vue              # Root app
└── nuxt.config.ts       # Nuxt configuration
```

---

## Component List (Modular)

### Layout Components
- `AppSidebar.vue` - Navigation sidebar
- `AppHeader.vue` - Header with user + Jarvis toggle
- `AppToast.vue` - Toast notification system
- `JarvisButton.vue` - Floating toggle button
- `JarvisChat.vue` - Chat interface
- `layouts/default.vue` - Main layout combining above

### Auth Components
- `LoginForm.vue` - Login form with zod validation

### Dashboard Components
- `DashboardWelcome.vue` - "Welcome {Name}" text
- `GlobeDisplay.vue` - Globe visualization (globe.gl)
- `GlobeHoverMiniGraph.vue` - Mini tooltip chart on hover
- `PriorityEventList.vue` - Top-right news-style events
- `HeroReportList.vue` - Bottom-right anonymous reports

### Analytics Components
- `AnalyticsChart.vue` - Reusable real-time chart
- `AnalyticsRealtimeListener.vue` - RabbitMQ consumer
- `SectorInfoPanel.vue` - Sector info description
- `SectorForecastChart.vue` - Sector chart with forecast
- `ResourceInfoPanel.vue` - Resource info description
- `ResourceByCountryMap.vue` - Country allocation map
- `ResourceForecastChart.vue` - Resource forecast per country

### Event & Report Components
- `EventDetail.vue` - Full event display
- `ReportForm.vue` - New report form
- `ReportMetadataSigner.vue` - JWT signing utility

---

## Page Routes

| Route | Description |
|-------|-------------|
| `/` | Redirect to /dashboard if logged in, else /login |
| `/login` | Login page |
| `/dashboard` | Main dashboard |
| `/analytics` | General analytics with real-time charts |
| `/analytics/sector/:sec` | Sector-specific analytics with forecasts |
| `/analytics/resource/:name` | Resource-specific analytics |
| `/event/:name` | Event detail page |
| `/reports/new` | Create new report |

---

## API Endpoints (Mock)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login |
| `/api/auth/session` | GET | Get session |
| `/api/events` | GET | List events |
| `/api/events/:id` | GET | Single event |
| `/api/analytics` | GET | General analytics |
| `/api/analytics/sector/:sec` | GET | Sector analytics |
| `/api/analytics/resource/:name` | GET | Resource analytics |
| `/api/forecast` | GET | Forecast data |
| `/api/reports` | GET/POST | List/create reports |

---

## RabbitMQ Queues
- `analytics` - Real-time analytics data (timestamp, resource, sector)
- `events` - Priority events (id, event, priority, started)

---

## Database Schema (PostgreSQL)

### Tables
- `users` - User accounts (better-auth)
- `reports` - Field intelligence reports
- `events` - Processed events
- `analytics_data` - Historical analytics

---

## Task Breakdown

### Phase 1: Project Foundation
- [ ] Initialize Nuxt 4 project
- [ ] Install dependencies
- [ ] Configure TailwindCSS + shadcn-vue
- [ ] Setup PostgreSQL connection

### Phase 2: Authentication
- [ ] Setup better-auth with JWT
- [ ] Create auth store
- [ ] Build LoginForm component
- [ ] Add route middleware

### Phase 3: Layout & Core UI
- [ ] Build layout components (Sidebar, Header, Toast)
- [ ] Create default layout
- [ ] Implement Jarvis components

### Phase 4: Dashboard
- [ ] Build all dashboard components
- [ ] Create page routes (index, login, dashboard)

### Phase 5: Analytics
- [ ] Build analytics components
- [ ] Create analytics pages with routes

### Phase 6: Events & Reports
- [ ] Build event/report components
- [ ] Create event and reports pages

### Phase 7: Mock API
- [ ] Create server API endpoints
- [ ] Parse field_intel_reports.jsonl

### Phase 8: Real-time Integration
- [ ] Setup RabbitMQ composable
- [ ] Connect charts to RabbitMQ
- [ ] Wire toast notifications

---

## Key Data Points

### Resources
- Vibranium (kg)
- Pym Particles
- Arc Reactor Cores
- Medical Kits
- Clean Water (L)

### Locations
- Avengers Compound
- Wakanda
- Sanctum Sanctorum
- Sokovia
- New Asgard

### Priority Levels
- Routine (blue)
- High (yellow)
- Avengers Level Threat (red)
