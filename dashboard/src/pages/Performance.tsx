import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  alpha,
  CircularProgress,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Timer as TimerIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';
import GlassCard from '../components/GlassCard';
import KPICard from '../components/KPICard';
import { ModelMetrics, PerformanceOverTime } from '../types';

// Mock data
const mockMetrics: ModelMetrics = {
  accuracy: 0.952,
  precision: 0.938,
  recall: 0.921,
  f1Score: 0.929,
  auc_roc: 0.968,
  confusionMatrix: {
    true_positive: 892,
    true_negative: 4456,
    false_positive: 58,
    false_negative: 78,
  },
};

const mockPerformanceData: PerformanceOverTime[] = [
  { date: 'Jan 1', accuracy: 0.92, precision: 0.91, recall: 0.89, f1Score: 0.90 },
  { date: 'Jan 3', accuracy: 0.93, precision: 0.92, recall: 0.90, f1Score: 0.91 },
  { date: 'Jan 5', accuracy: 0.94, precision: 0.93, recall: 0.91, f1Score: 0.92 },
  { date: 'Jan 7', accuracy: 0.945, precision: 0.935, recall: 0.915, f1Score: 0.925 },
  { date: 'Jan 9', accuracy: 0.948, precision: 0.936, recall: 0.918, f1Score: 0.927 },
  { date: 'Jan 11', accuracy: 0.95, precision: 0.937, recall: 0.92, f1Score: 0.928 },
  { date: 'Jan 13', accuracy: 0.952, precision: 0.938, recall: 0.921, f1Score: 0.929 },
];

const mockRadarData = [
  { metric: 'Accuracy', value: 95.2, fullMark: 100 },
  { metric: 'Precision', value: 93.8, fullMark: 100 },
  { metric: 'Recall', value: 92.1, fullMark: 100 },
  { metric: 'F1 Score', value: 92.9, fullMark: 100 },
  { metric: 'AUC-ROC', value: 96.8, fullMark: 100 },
];

const mockModelVersions = [
  { version: 'v2.3.1', trainingDate: '2024-01-10', accuracy: 0.952, isActive: true },
  { version: 'v2.3.0', trainingDate: '2023-12-15', accuracy: 0.948, isActive: false },
  { version: 'v2.2.5', trainingDate: '2023-11-20', accuracy: 0.941, isActive: false },
  { version: 'v2.2.0', trainingDate: '2023-10-25', accuracy: 0.935, isActive: false },
];

const Performance: React.FC = () => {
  const theme = useTheme();
  const [metrics] = useState<ModelMetrics>(mockMetrics);
  const [performanceData] = useState<PerformanceOverTime[]>(mockPerformanceData);
  const [modelVersions] = useState(mockModelVersions);

  const getMetricColor = (value: number) => {
    if (value >= 0.95) return theme.palette.success.main;
    if (value >= 0.90) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  const calculateTotal = (tp: number, tn: number, fp: number, fn: number) => tp + tn + fp + fn;
  const calculateAccuracy = (tp: number, tn: number, fp: number, fn: number) =>
    ((tp + tn) / (tp + tn + fp + fn)) * 100;

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Model Performance
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Monitor and analyze fraud detection model metrics
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Accuracy"
            value={`${(metrics.accuracy * 100).toFixed(1)}%`}
            trend="up"
            trendValue="+0.4%"
            icon={<SpeedIcon />}
            color={getMetricColor(metrics.accuracy)}
            progress={metrics.accuracy * 100}
            delay={0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Precision"
            value={`${(metrics.precision * 100).toFixed(1)}%`}
            trend="up"
            trendValue="+0.2%"
            icon={<TrendingUpIcon />}
            color={getMetricColor(metrics.precision)}
            progress={metrics.precision * 100}
            delay={0.1}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Recall"
            value={`${(metrics.recall * 100).toFixed(1)}%`}
            trend="up"
            trendValue="+0.3%"
            icon={<TrendingUpIcon />}
            color={getMetricColor(metrics.recall)}
            progress={metrics.recall * 100}
            delay={0.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="AUC-ROC"
            value={`${(metrics.auc_roc * 100).toFixed(1)}%`}
            trend="up"
            trendValue="+0.1%"
            icon={<TrendingUpIcon />}
            color={getMetricColor(metrics.auc_roc)}
            progress={metrics.auc_roc * 100}
            delay={0.3}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Over Time */}
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Performance Over Time
              </Typography>
              <Button variant="outlined" startIcon={<RefreshIcon />} size="small">
                Refresh
              </Button>
            </Box>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={performanceData}>
                <defs>
                  <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorPrecision" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorRecall" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.warning.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.warning.main} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" domain={[0.85, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                <RechartsTooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                  formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, '']}
                />
                <Area
                  type="monotone"
                  dataKey="accuracy"
                  stroke={theme.palette.primary.main}
                  fillOpacity={1}
                  fill="url(#colorAccuracy)"
                  name="Accuracy"
                />
                <Area
                  type="monotone"
                  dataKey="precision"
                  stroke={theme.palette.success.main}
                  fillOpacity={1}
                  fill="url(#colorPrecision)"
                  name="Precision"
                />
                <Area
                  type="monotone"
                  dataKey="recall"
                  stroke={theme.palette.warning.main}
                  fillOpacity={1}
                  fill="url(#colorRecall)"
                  name="Recall"
                />
                <Line type="monotone" dataKey="f1Score" stroke={theme.palette.error.main} strokeWidth={2} dot={{ fill: theme.palette.error.main }} name="F1 Score" />
              </AreaChart>
            </ResponsiveContainer>
          </GlassCard>
        </Grid>

        {/* Metrics Radar */}
        <Grid item xs={12} lg={4}>
          <GlassCard>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              Performance Radar
            </Typography>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={mockRadarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="metric" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                <PolarRadiusAxis stroke="rgba(255,255,255,0.5)" />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke={theme.palette.primary.main}
                  fill={alpha(theme.palette.primary.main, 0.3)}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </GlassCard>
        </Grid>

        {/* Confusion Matrix */}
        <Grid item xs={12} md={6}>
          <GlassCard>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              Confusion Matrix
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Grid container spacing={2} sx={{ maxWidth: 400 }}>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.2)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main }}>
                      {metrics.confusionMatrix.true_positive}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      True Positive
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.2)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main }}>
                      {metrics.confusionMatrix.true_negative}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      True Negative
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.2)} 0%, ${alpha(theme.palette.error.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.error.main }}>
                      {metrics.confusionMatrix.false_positive}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      False Positive
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(theme.palette.error.main, 0.2)} 0%, ${alpha(theme.palette.error.main, 0.05)} 100%)`,
                      border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.error.main }}>
                      {metrics.confusionMatrix.false_negative}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                      False Negative
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Chip
                label={`Overall Accuracy: ${calculateAccuracy(
                  metrics.confusionMatrix.true_positive,
                  metrics.confusionMatrix.true_negative,
                  metrics.confusionMatrix.false_positive,
                  metrics.confusionMatrix.false_negative
                ).toFixed(1)}%`}
                sx={{
                  backgroundColor: alpha(theme.palette.primary.main, 0.2),
                  color: theme.palette.primary.main,
                  fontWeight: 600,
                }}
              />
            </Box>
          </GlassCard>
        </Grid>

        {/* Model Versions */}
        <Grid item xs={12} md={6}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Model Versions
              </Typography>
              <Button variant="contained" size="small">
                Retrain Model
              </Button>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Version</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Training Date</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Accuracy</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {modelVersions.map((model) => (
                    <TableRow
                      key={model.version}
                      sx={{
                        '&:hover': {
                          backgroundColor: 'rgba(255,255,255,0.05)',
                        },
                      }}
                    >
                      <TableCell sx={{ color: 'white', fontWeight: 500 }}>{model.version}</TableCell>
                      <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>{model.trainingDate}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              width: 60,
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: alpha(getMetricColor(model.accuracy), 0.2),
                              overflow: 'hidden',
                            }}
                          >
                            <Box
                              sx={{
                                width: `${model.accuracy * 100}%`,
                                height: '100%',
                                backgroundColor: getMetricColor(model.accuracy),
                                borderRadius: 3,
                              }}
                            />
                          </Box>
                          <Typography variant="body2" sx={{ color: getMetricColor(model.accuracy), fontWeight: 600 }}>
                            {(model.accuracy * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={model.isActive ? <CheckIcon /> : undefined}
                          label={model.isActive ? 'Active' : 'Inactive'}
                          size="small"
                          sx={{
                            backgroundColor: alpha(
                              model.isActive ? theme.palette.success.main : theme.palette.warning.main,
                              0.2
                            ),
                            color: model.isActive ? theme.palette.success.main : theme.palette.warning.main,
                            fontWeight: 600,
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </GlassCard>
        </Grid>

        {/* System Resources */}
        <Grid item xs={12}>
          <GlassCard>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              System Resources
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.primary.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <MemoryIcon sx={{ color: theme.palette.primary.main }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      CPU Usage
                    </Typography>
                  </Box>
                  <Box sx={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
                    <CircularProgress
                      variant="determinate"
                      value={68}
                      size={120}
                      thickness={4}
                      sx={{
                        color: theme.palette.primary.main,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        borderRadius: '50%',
                      }}
                    />
                    <Box
                      sx={{
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                      }}
                    >
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        68%
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.15)} 0%, ${alpha(theme.palette.success.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <MemoryIcon sx={{ color: theme.palette.success.main }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      Memory Usage
                    </Typography>
                  </Box>
                  <Box sx={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
                    <CircularProgress
                      variant="determinate"
                      value={52}
                      size={120}
                      thickness={4}
                      sx={{
                        color: theme.palette.success.main,
                        backgroundColor: alpha(theme.palette.success.main, 0.1),
                        borderRadius: '50%',
                      }}
                    />
                    <Box
                      sx={{
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                      }}
                    >
                      <Typography variant="h5" sx={{ fontWeight: 700 }}>
                        52%
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.15)} 0%, ${alpha(theme.palette.warning.main, 0.05)} 100%)`,
                    border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <TimerIcon sx={{ color: theme.palette.warning.main }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      Avg Response Time
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h3" sx={{ fontWeight: 700, color: theme.palette.warning.main }}>
                      45ms
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                      Average prediction time
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Performance;
