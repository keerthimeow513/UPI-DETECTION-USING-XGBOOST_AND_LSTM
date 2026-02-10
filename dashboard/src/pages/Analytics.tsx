import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Chip,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShowChart as ChartIcon,
  BarChart as BarIcon,
  PieChart as PieIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ComposedChart,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';
import GlassCard from '../components/GlassCard';
import KPICard from '../components/KPICard';

const Analytics: React.FC = () => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [chartType, setChartType] = useState<'area' | 'bar' | 'line'>('area');

  const handleTimeRangeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newTimeRange: '7d' | '30d' | '90d' | null
  ) => {
    if (newTimeRange !== null) {
      setTimeRange(newTimeRange);
    }
  };

  const mockTrendData = [
    { date: 'Week 1', fraud: 45, legitimate: 3200, detected: 42 },
    { date: 'Week 2', fraud: 52, legitimate: 3450, detected: 48 },
    { date: 'Week 3', fraud: 38, legitimate: 3800, detected: 36 },
    { date: 'Week 4', fraud: 65, legitimate: 4100, detected: 62 },
    { date: 'Week 5', fraud: 48, legitimate: 4350, detected: 45 },
    { date: 'Week 6', fraud: 55, legitimate: 4500, detected: 52 },
  ];

  const mockCategoryData = [
    { category: 'Shopping', fraud: 120, legitimate: 4500 },
    { category: 'Transfer', fraud: 280, legitimate: 3200 },
    { category: 'Bills', fraud: 45, legitimate: 5600 },
    { category: 'Food', fraud: 35, legitimate: 2800 },
    { category: 'Travel', fraud: 65, legitimate: 1800 },
    { category: 'Entertainment', fraud: 25, legitimate: 1200 },
  ];

  const mockLocationData = [
    { location: 'Mumbai', fraud: 180, risk: 'high' },
    { location: 'Delhi', fraud: 145, risk: 'high' },
    { location: 'Bangalore', fraud: 95, risk: 'medium' },
    { location: 'Chennai', fraud: 65, risk: 'medium' },
    { location: 'Kolkata', fraud: 55, risk: 'low' },
    { location: 'Hyderabad', fraud: 45, risk: 'low' },
  ];

  const mockHourlyData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${i.toString().padStart(2, '0')}:00`,
    fraud: Math.floor(Math.random() * 20) + 5,
    legitimate: Math.floor(Math.random() * 200) + 50,
  }));

  const mockRadarData = [
    { metric: 'Transaction Amount', value: 85 },
    { metric: 'Device Trust', value: 72 },
    { metric: 'Location Risk', value: 68 },
    { metric: 'Time Pattern', value: 90 },
    { metric: 'Historical', value: 78 },
    { metric: 'Merchant', value: 65 },
  ];

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      default:
        return theme.palette.success.main;
    }
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Fraud Analytics
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Comprehensive analysis of fraud patterns and trends
        </Typography>
      </Box>

      {/* Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <ToggleButtonGroup
          value={timeRange}
          exclusive
          onChange={handleTimeRangeChange}
          size="small"
          sx={{
            '& .MuiToggleButton-root': {
              color: 'rgba(255,255,255,0.6)',
              borderColor: 'rgba(255,255,255,0.2)',
              '&.Mui-selected': {
                backgroundColor: alpha(theme.palette.primary.main, 0.2),
                color: theme.palette.primary.main,
              },
            },
          }}
        >
          <ToggleButton value="7d">7 Days</ToggleButton>
          <ToggleButton value="30d">30 Days</ToggleButton>
          <ToggleButton value="90d">90 Days</ToggleButton>
        </ToggleButtonGroup>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            icon={<ChartIcon />}
            label="Area"
            onClick={() => setChartType('area')}
            sx={{
              backgroundColor: chartType === 'area' ? alpha(theme.palette.primary.main, 0.2) : 'transparent',
              color: chartType === 'area' ? theme.palette.primary.main : 'rgba(255,255,255,0.6)',
            }}
          />
          <Chip
            icon={<BarIcon />}
            label="Bar"
            onClick={() => setChartType('bar')}
            sx={{
              backgroundColor: chartType === 'bar' ? alpha(theme.palette.primary.main, 0.2) : 'transparent',
              color: chartType === 'bar' ? theme.palette.primary.main : 'rgba(255,255,255,0.6)',
            }}
          />
          <Chip
            icon={<TrendingUpIcon />}
            label="Line"
            onClick={() => setChartType('line')}
            sx={{
              backgroundColor: chartType === 'line' ? alpha(theme.palette.primary.main, 0.2) : 'transparent',
              color: chartType === 'line' ? theme.palette.primary.main : 'rgba(255,255,255,0.6)',
            }}
          />
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Fraud"
            value="570"
            trend="down"
            trendValue="-12.3%"
            color={theme.palette.error.main}
            delay={0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Fraud Rate"
            value="1.2%"
            trend="down"
            trendValue="-0.3%"
            color={theme.palette.warning.main}
            delay={0.1}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Avg. Fraud Amount"
            value="₹24,500"
            trend="down"
            trendValue="-8.5%"
            color={theme.palette.info.main}
            delay={0.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Detection Rate"
            value="94.2%"
            trend="up"
            trendValue="+2.1%"
            color={theme.palette.success.main}
            delay={0.3}
          />
        </Grid>
      </Grid>

      {/* Main Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Fraud Trends */}
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Fraud Detection Trends
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              {chartType === 'area' ? (
                <AreaChart data={mockTrendData}>
                  <defs>
                    <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.error.main} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={theme.palette.error.main} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorLegitimate" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(26, 26, 46, 0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: 8,
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="fraud"
                    stroke={theme.palette.error.main}
                    fillOpacity={1}
                    fill="url(#colorFraud)"
                    name="Fraud Cases"
                  />
                  <Area
                    type="monotone"
                    dataKey="legitimate"
                    stroke={theme.palette.success.main}
                    fillOpacity={1}
                    fill="url(#colorLegitimate)"
                    name="Legitimate"
                  />
                </AreaChart>
              ) : chartType === 'bar' ? (
                <BarChart data={mockTrendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(26, 26, 46, 0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: 8,
                    }}
                  />
                  <Legend />
                  <Bar dataKey="fraud" fill={theme.palette.error.main} name="Fraud Cases" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="detected" fill={theme.palette.warning.main} name="Detected" radius={[4, 4, 0, 0]} />
                </BarChart>
              ) : (
                <LineChart data={mockTrendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <Tooltip
                    contentStyle={{
                      background: 'rgba(26, 26, 46, 0.9)',
                      border: '1px solid rgba(255,255,255,0.2)',
                      borderRadius: 8,
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="fraud"
                    stroke={theme.palette.error.main}
                    strokeWidth={2}
                    dot={{ fill: theme.palette.error.main }}
                    name="Fraud Cases"
                  />
                  <Line
                    type="monotone"
                    dataKey="detected"
                    stroke={theme.palette.success.main}
                    strokeWidth={2}
                    dot={{ fill: theme.palette.success.main }}
                    name="Detected"
                  />
                </LineChart>
              )}
            </ResponsiveContainer>
          </GlassCard>
        </Grid>

        {/* Fraud by Category */}
        <Grid item xs={12} lg={4}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Fraud by Category
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={mockCategoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={3}
                  dataKey="fraud"
                  nameKey="category"
                >
                  {mockCategoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
              {mockCategoryData.map((item, index) => (
                <Chip
                  key={item.category}
                  label={`${item.category}: ${item.fraud}`}
                  size="small"
                  sx={{
                    backgroundColor: alpha(COLORS[index], 0.2),
                    color: COLORS[index],
                    fontWeight: 500,
                  }}
                />
              ))}
            </Box>
          </GlassCard>
        </Grid>
      </Grid>

      {/* Secondary Charts */}
      <Grid container spacing={3}>
        {/* Hourly Distribution */}
        <Grid item xs={12} lg={6}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Fraud by Hour of Day
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockHourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="hour" stroke="rgba(255,255,255,0.5)" fontSize={10} />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="fraud" fill={theme.palette.error.main} radius={[4, 4, 0, 0]} name="Fraud" />
              </BarChart>
            </ResponsiveContainer>
          </GlassCard>
        </Grid>

        {/* Geographic Distribution */}
        <Grid item xs={12} lg={6}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Geographic Risk Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={mockLocationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="location" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                />
                <Bar dataKey="fraud" fill={theme.palette.primary.main} radius={[4, 4, 0, 0]} name="Fraud Cases" />
                <Line
                  type="monotone"
                  dataKey="fraud"
                  stroke={theme.palette.error.main}
                  strokeWidth={2}
                  dot={{ fill: theme.palette.error.main }}
                />
              </ComposedChart>
            </ResponsiveContainer>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
              {mockLocationData.map((item) => (
                <Box key={item.location} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: getRiskColor(item.risk),
                    }}
                  />
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                    {item.location}
                  </Typography>
                </Box>
              ))}
            </Box>
          </GlassCard>
        </Grid>

        {/* Risk Factor Analysis */}
        <Grid item xs={12}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Risk Factor Analysis
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
                  Feature Importance
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={mockRadarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="metric" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                    <PolarRadiusAxis stroke="rgba(255,255,255,0.5)" />
                    <Radar
                      name="Importance"
                      dataKey="value"
                      stroke={theme.palette.primary.main}
                      fill={alpha(theme.palette.primary.main, 0.3)}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
                  Top Risk Indicators
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {[
                    { name: 'Unusual Transaction Amount', score: 95, trend: 'up' },
                    { name: 'New Device Login', score: 88, trend: 'up' },
                    { name: 'Multiple Failed Attempts', score: 82, trend: 'stable' },
                    { name: 'Location Anomaly', score: 75, trend: 'down' },
                    { name: 'Time of Transaction', score: 68, trend: 'stable' },
                  ].map((indicator, index) => (
                    <motion.div
                      key={indicator.name}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          p: 2,
                          borderRadius: 2,
                          backgroundColor: 'rgba(255,255,255,0.03)',
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {indicator.name}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                              Score: {indicator.score}
                            </Typography>
                            {indicator.trend === 'up' ? (
                              <TrendingUpIcon sx={{ fontSize: 14, color: theme.palette.error.main }} />
                            ) : indicator.trend === 'down' ? (
                              <TrendingDownIcon sx={{ fontSize: 14, color: theme.palette.success.main }} />
                            ) : null}
                          </Box>
                        </Box>
                        <Box
                          sx={{
                            width: 60,
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: alpha(theme.palette.warning.main, 0.2),
                            overflow: 'hidden',
                          }}
                        >
                          <Box
                            sx={{
                              width: `${indicator.score}%`,
                              height: '100%',
                              backgroundColor: indicator.score > 80 ? theme.palette.error.main : theme.palette.warning.main,
                              borderRadius: 3,
                            }}
                          />
                        </Box>
                      </Box>
                    </motion.div>
                  ))}
                </Box>
              </Grid>
            </Grid>
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;
