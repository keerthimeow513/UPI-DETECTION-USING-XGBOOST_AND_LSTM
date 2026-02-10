# UPI Fraud Detection Dashboard

A modern React + TypeScript dashboard for UPI (Unified Payments Interface) fraud detection with Google Design 3 and Glassmorphism styling.

## Features

- **Glassmorphism Design**: Modern UI with blur effects and gradient backgrounds
- **Google Design 3 Theme**: Material You color system and typography
- **Real-time Analytics**: Interactive charts and fraud pattern analysis
- **Prediction System**: AI-powered fraud detection for transactions
- **Admin Panel**: Device management and risk configuration
- **Model Performance**: Monitor accuracy, precision, recall metrics

## Tech Stack

- React 18 with TypeScript
- Material UI (MUI) v6
- Framer Motion for animations
- Recharts for data visualization
- Vite for development

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
dashboard/
├── src/
│   ├── App.tsx                    # Main application component
│   ├── index.tsx                   # Entry point
│   ├── theme/
│   │   └── theme.ts               # Google Design 3 theme configuration
│   ├── components/
│   │   ├── Layout.tsx             # Main layout with sidebar navigation
│   │   ├── GlassCard.tsx          # Glassmorphism card component
│   │   └── KPICard.tsx            # KPI metrics display card
│   ├── pages/
│   │   ├── Dashboard.tsx          # Overview with KPIs and charts
│   │   ├── Prediction.tsx         # Real-time fraud prediction
│   │   ├── Analytics.tsx         # Fraud patterns and analytics
│   │   ├── Admin.tsx             # Admin panel and device management
│   │   └── Performance.tsx       # Model performance metrics
│   ├── services/
│   │   └── api.ts                # API client and service functions
│   └── types/
│       └── index.ts               # TypeScript type definitions
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## API Integration

The dashboard connects to a FastAPI backend. Configure the API URL in environment variables:

```env
VITE_API_URL=http://localhost:8000
```

### Available API Endpoints

- `POST /predict` - Fraud prediction
- `GET /dashboard/stats` - Dashboard statistics
- `GET /transactions/recent` - Recent transactions
- `GET /analytics/*` - Analytics data
- `GET /admin/*` - Admin configuration
- `GET /model/*` - Model metrics

## Pages

### Dashboard
- Real-time transaction monitoring
- KPI cards with trends
- Transaction volume charts
- Active fraud alerts

### Prediction
- Interactive fraud prediction form
- Real-time risk analysis
- Factor breakdown
- Recommendations

### Analytics
- Fraud trends over time
- Category-based analysis
- Geographic distribution
- Risk factor analysis

### Admin
- Risk threshold configuration
- Device management
- Audit logs
- Alert settings

### Performance
- Model accuracy metrics
- Confusion matrix
- Performance over time
- System resources

## Customization

### Theme
Edit `src/theme/theme.ts` to customize:
- Color palette
- Typography
- Component styles
- Glassmorphism effects

### Components
- GlassCard: Main glassmorphism container
- KPICard: Metric display cards
- Layout: Navigation and structure

## License

MIT License
