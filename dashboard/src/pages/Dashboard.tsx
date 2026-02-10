import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  useTheme,
  alpha,
  Tooltip,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  AccountBalance as AccountIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import GlassCard from '../components/GlassCard';
import KPICard from '../components/KPICard';
import { Transaction, FraudAlert, DashboardStats } from '../types';

// Mock data for demonstration
const mockStats: DashboardStats = {
  totalTransactions: 45892,
  fraudDetected: 234,
  legitimateTransactions: 45658,
  fraudRate: 0.51,
  averageRiskScore: 23.5,
  recentAlerts: 12,
  blockedAmount: 1250000,
  savingsAmount: 3200000,
};

const mockTransactions: Transaction[] = [
  {
    id: 'TXN001',
    sender_upi: 'user@upi',
    receiver_upi: 'merchant@upi',
    amount: 2500,
    timestamp: '2024-01-15T10:30:00',
    merchant_category: 'Shopping',
    location: 'Mumbai',
    device_id: 'DEV001',
    is_fraud: false,
    fraud_probability: 12,
  },
  {
    id: 'TXN002',
    sender_upi: 'user2@upi',
    receiver_upi: 'unknown@upi',
    amount: 15000,
    timestamp: '2024-01-15T10:35:00',
    merchant_category: 'Transfer',
    location: 'Delhi',
    device_id: 'DEV002',
    is_fraud: true,
    fraud_probability: 89,
  },
  {
    id: 'TXN003',
    sender_upi: 'user3@upi',
    receiver_upi: 'retail@upi',
    amount: 850,
    timestamp: '2024-01-15T10:40:00',
    merchant_category: 'Grocery',
    location: 'Bangalore',
    device_id: 'DEV003',
    is_fraud: false,
    fraud_probability: 8,
  },
  {
    id: 'TXN004',
    sender_upi: 'user4@upi',
    receiver_upi: 'suspicious@upi',
    amount: 50000,
    timestamp: '2024-01-15T10:45:00',
    merchant_category: 'Transfer',
    location: 'Unknown',
    device_id: 'DEV004',
    is_fraud: true,
    fraud_probability: 95,
  },
  {
    id: 'TXN005',
    sender_upi: 'user5@upi',
    receiver_upi: 'restaurant@upi',
    amount: 1200,
    timestamp: '2024-01-15T10:50:00',
    merchant_category: 'Food',
    location: 'Chennai',
    device_id: 'DEV005',
    is_fraud: false,
    fraud_probability: 15,
  },
];

const mockAlerts: FraudAlert[] = [
  {
    id: 'ALT001',
    transaction_id: 'TXN002',
    timestamp: '2024-01-15T10:35:00',
    severity: 'high',
    message: 'Suspicious high-value transfer detected',
    status: 'pending',
  },
  {
    id: 'ALT002',
    transaction_id: 'TXN004',
    timestamp: '2024-01-15T10:45:00',
    severity: 'critical',
    message: 'Known fraudulent pattern - immediate action required',
    status: 'pending',
  },
];

const mockChartData = [
  { time: '00:00', legitimate: 120, fraud: 3 },
  { time: '04:00', legitimate: 80, fraud: 2 },
  { time: '08:00', legitimate: 350, fraud: 8 },
  { time: '12:00', legitimate: 520, fraud: 12 },
  { time: '16:00', legitimate: 480, fraud: 15 },
  { time: '20:00', legitimate: 320, fraud: 9 },
  { time: '23:59', legitimate: 180, fraud: 5 },
];

const mockPieData = [
  { name: 'Shopping', value: 35 },
  { name: 'Transfer', value: 25 },
  { name: 'Bills', value: 20 },
  { name: 'Food', value: 15 },
  { name: 'Other', value: 5 },
];

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'];

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const [stats, setStats] = useState<DashboardStats>(mockStats);
  const [transactions] = useState<Transaction[]>(mockTransactions);
  const [alerts] = useState<FraudAlert[]>(mockAlerts);

  const getRiskColor = (probability: number) => {
    if (probability < 30) return theme.palette.success.main;
    if (probability < 60) return theme.palette.warning.main;
    if (probability < 80) return theme.palette.error.main;
    return theme.palette.error.dark;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return theme.palette.error.dark;
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      default:
        return theme.palette.info.main;
    }
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Fraud Detection Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Real-time monitoring and analysis of UPI transactions
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Transactions"
            value={stats.totalTransactions.toLocaleString()}
            trend="up"
            trendValue="+12.5%"
            icon={<AccountIcon />}
            color={theme.palette.primary.main}
            delay={0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Fraud Detected"
            value={stats.fraudDetected}
            trend="down"
            trendValue="-8.3%"
            icon={<SecurityIcon />}
            color={theme.palette.error.main}
            delay={0.1}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Amount Blocked"
            value={`₹${(stats.blockedAmount / 100000).toFixed(1)}L`}
            trend="up"
            trendValue="+15.2%"
            icon={<BlockIcon />}
            color={theme.palette.warning.main}
            delay={0.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Savings Protected"
            value={`₹${(stats.savingsAmount / 100000).toFixed(1)}L`}
            trend="up"
            trendValue="+22.8%"
            icon={<TrendingUpIcon />}
            color={theme.palette.success.main}
            delay={0.3}
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Transaction Volume Chart */}
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Transaction Volume & Fraud Detection
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={mockChartData}>
                <defs>
                  <linearGradient id="colorLegitimate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.error.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.error.main} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" />
                <RechartsTooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="legitimate"
                  stroke={theme.palette.success.main}
                  fillOpacity={1}
                  fill="url(#colorLegitimate)"
                  name="Legitimate"
                />
                <Area
                  type="monotone"
                  dataKey="fraud"
                  stroke={theme.palette.error.main}
                  fillOpacity={1}
                  fill="url(#colorFraud)"
                  name="Fraud"
                />
              </AreaChart>
            </ResponsiveContainer>
          </GlassCard>
        </Grid>

        {/* Transaction Categories */}
        <Grid item xs={12} lg={4}>
          <GlassCard>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Transaction Categories
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={mockPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mockPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip
                  contentStyle={{
                    background: 'rgba(26, 26, 46, 0.9)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 8,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center', mt: 2 }}>
              {mockPieData.map((item, index) => (
                <Chip
                  key={item.name}
                  label={`${item.name}: ${item.value}%`}
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

      {/* Tables Row */}
      <Grid container spacing={3}>
        {/* Recent Transactions */}
        <Grid item xs={12} lg={7}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Recent Transactions
              </Typography>
              <Chip label="Live" color="success" size="small" />
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>ID</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Amount</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Category</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Risk Score</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Status</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((txn) => (
                    <motion.div
                      key={txn.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TableRow
                        sx={{
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.05)',
                          },
                        }}
                      >
                        <TableCell sx={{ color: 'white' }}>{txn.id}</TableCell>
                        <TableCell sx={{ color: 'white' }}>₹{txn.amount.toLocaleString()}</TableCell>
                        <TableCell sx={{ color: 'rgba(255,255,255,0.8)' }}>{txn.merchant_category}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box
                              sx={{
                                width: 40,
                                height: 6,
                                borderRadius: 3,
                                backgroundColor: alpha(getRiskColor(txn.fraud_probability || 0), 0.2),
                                overflow: 'hidden',
                              }}
                            >
                              <Box
                                sx={{
                                  width: `${txn.fraud_probability || 0}%`,
                                  height: '100%',
                                  backgroundColor: getRiskColor(txn.fraud_probability || 0),
                                  borderRadius: 3,
                                }}
                              />
                            </Box>
                            <Typography
                              variant="body2"
                              sx={{ color: getRiskColor(txn.fraud_probability || 0), fontWeight: 600 }}
                            >
                              {txn.fraud_probability || 0}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={txn.is_fraud ? <ErrorIcon /> : <CheckIcon />}
                            label={txn.is_fraud ? 'Fraud' : 'Clean'}
                            size="small"
                            sx={{
                              backgroundColor: alpha(
                                txn.is_fraud ? theme.palette.error.main : theme.palette.success.main,
                                0.2
                              ),
                              color: txn.is_fraud ? theme.palette.error.main : theme.palette.success.main,
                              fontWeight: 600,
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton size="small" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                              <ViewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    </motion.div>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </GlassCard>
        </Grid>

        {/* Active Alerts */}
        <Grid item xs={12} lg={5}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Active Alerts
              </Typography>
              <Chip
                icon={<WarningIcon />}
                label={`${alerts.length} Active`}
                size="small"
                color="warning"
              />
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {alerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${alpha(getSeverityColor(alert.severity), 0.15)} 0%, ${alpha(
                        getSeverityColor(alert.severity),
                        0.05
                      )} 100%)`,
                      border: `1px solid ${alpha(getSeverityColor(alert.severity), 0.3)}`,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Chip
                        label={alert.severity.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: alpha(getSeverityColor(alert.severity), 0.3),
                          color: getSeverityColor(alert.severity),
                          fontWeight: 700,
                          fontSize: '0.7rem',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
                      {alert.message}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                      Transaction: {alert.transaction_id}
                    </Typography>
                  </Box>
                </motion.div>
              ))}
            </Box>
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
