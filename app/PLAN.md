Individual Task Breakdown
Phase 1: Project Foundation
| Task | Description |
|------|-------------|
| 1.1 | Initialize Nuxt 4 project with Vite |
| 1.2 | Install dependencies: shadcn-vue, better-auth, zod, tanstack vue forms, vue-chartjs, globe.gl, pinia |
| 1.3 | Configure TailwindCSS and shadcn-vue |
| 1.4 | Setup project structure (components, folder pages, composables, stores, server/api) |
Phase 2: Authentication
| Task | Description |
|------|-------------|
| 2.1 | Setup better-auth with JWT plugin |
| 2.2 | Create auth store (Pinia) for user session |
| 2.3 | Build LoginForm.vue component with zod validation |
| 2.4 | Create auth middleware for protected routes |
Phase 3: Core Layout Components
| Task | Description |
|------|-------------|
| 3.1 | Build AppSidebar.vue - persistent navigation sidebar |
| 3.2 | Build AppHeader.vue - header with user info, Jarvis toggle |
| 3.3 | Build AppToast.vue - toast notification system with priority colors |
| 3.4 | Create default.vue layout combining sidebar/header |
Phase 4: Dashboard Components (Modular)
| Task | Description |
|------|-------------|
| 4.1 | Build GlobeDisplay.vue - main globe visualization (globe.gl wrapper) |
| 4.2 | Build GlobeHoverMiniGraph.vue - mini tooltip graph on hover |
| 4.3 | Build PriorityEventList.vue - top-right news-style event headlines |
| 4.4 | Build HeroReportList.vue - bottom-right anonymous reports |
| 4.5 | Build DashboardWelcome.vue - "Welcome {Name}" text component |
| 4.6 | Assemble pages/dashboard.vue from above components |
Phase 5: Analytics Components (Modular)
| Task | Description |
|------|-------------|
| 5.1 | Build AnalyticsChart.vue - reusable real-time chart component |
| 5.2 | Build SectorInfoPanel.vue - info description for sectors |
| 5.3 | Build SectorForecastChart.vue - chart with regression + forecast area |
| 5.4 | Build ResourceInfoPanel.vue - info description per resource |
| 5.5 | Build ResourceByCountryMap.vue - country resource allocation map |
| 5.6 | Build ResourceForecastChart.vue - forecast per country |
| 5.7 | Build AnalyticsRealtimeListener.vue - RabbitMQ connection handler |
| 5.8 | Create pages/analytics/index.vue, pages/analytics/sector/[sec].vue, pages/analytics/resource/[name].vue |
Phase 6: Event & Report Components
| Task | Description |
|------|-------------|
| 6.1 | Build EventDetail.vue - full event report display |
| 6.2 | Build ReportForm.vue - new report form with zod validation |
| 6.3 | Build ReportMetadataSigner.vue - JWT signing for hero metadata |
| 6.4 | Create pages/event/[name].vue and pages/reports/new.vue |
Phase 7: AI Assistant
| Task | Description |
|------|-------------|
| 7.1 | Build JarvisButton.vue - floating toggle button |
| 7.2 | Build JarvisChat.vue - expanded chat interface |
| 7.3 | Integrate Jarvis into header/layout |
Phase 8: Mock API & Data
| Task | Description |
|------|-------------|
| 8.1 | Create mock API endpoints (server/api/*.ts) |
| 8.2 | Parse field_intel_reports.jsonl into usable mock data |
| 8.3 | Generate time-series analytics mock data |
| 8.4 | Create forecast mock endpoints |
Phase 9: Real-time Integration
| Task | Description |
|------|-------------|
| 9.1 | Setup RabbitMQ consumer composable |
| 9.2 | Connect analytics charts to RabbitMQ stream |
| 9.3 | Wire toast notifications to event stream |
---