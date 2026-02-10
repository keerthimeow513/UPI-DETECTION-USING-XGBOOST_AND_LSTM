import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Chip,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  alpha,
  Paper,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from '../components/GlassCard';
import { FraudPredictionRequest, FraudPredictionResponse, RiskFactor } from '../types';

const Prediction: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FraudPredictionResponse | null>(null);
  const [formData, setFormData] = useState<FraudPredictionRequest>({
    transaction_id: '',
    sender_upi: '',
    receiver_upi: '',
    amount: 0,
    timestamp: new Date().toISOString(),
    merchant_category: '',
    device_id: '',
    location: '',
    transaction_type: '',
    previous_transaction_count: 0,
    previous_fraud_count: 0,
    device_trust_score: 0,
    location_risk_score: 0,
    amount_deviation: 0,
    time_since_last_transaction: 0,
  });

  const handleInputChange = (field: keyof FraudPredictionRequest, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock response
    const mockResponse: FraudPredictionResponse = {
      transaction_id: formData.transaction_id || 'TXN-MOCK-001',
      prediction: formData.amount > 50000 ? 'fraud' : 'legitimate',
      fraud_probability: Math.random() * 100,
      risk_level: formData.amount > 50000 ? 'high' : 'low',
      confidence_score: 0.92,
      factors: [
        { name: 'Transaction Amount', impact: formData.amount > 50000 ? 'positive' : 'negative', value: 0.75, description: 'High value transaction' },
        { name: 'Device Trust Score', impact: 'negative', value: 0.65, description: 'Previously used device' },
        { name: 'Location Risk', impact: formData.location === 'Unknown' ? 'positive' : 'neutral', value: 0.45, description: 'Location verification status' },
        { name: 'Transaction Pattern', impact: 'negative', value: 0.32, description: 'Historical transaction behavior' },
      ],
      recommendations: [
        'Enable 2FA for transactions above ₹10,000',
        'Verify recipient UPI ID before transfer',
        'Set up transaction alerts for real-time monitoring',
      ],
    };

    setResult(mockResponse);
    setLoading(false);
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical':
        return theme.palette.error.dark;
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      default:
        return theme.palette.success.main;
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'positive':
        return <WarningIcon sx={{ color: theme.palette.error.main }} />;
      case 'negative':
        return <CheckIcon sx={{ color: theme.palette.success.main }} />;
      default:
        return <InfoIcon sx={{ color: theme.palette.info.main }} />;
    }
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Real-Time Fraud Prediction
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Analyze transaction risk using our AI-powered fraud detection model
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input Form */}
        <Grid item xs={12} lg={7}>
          <GlassCard>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <PsychologyIcon sx={{ color: theme.palette.primary.main, fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Transaction Details
              </Typography>
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Transaction ID"
                  value={formData.transaction_id}
                  onChange={(e) => handleInputChange('transaction_id', e.target.value)}
                  placeholder="TXN-XXXX-XXXX"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Amount (₹)"
                  type="number"
                  value={formData.amount || ''}
                  onChange={(e) => handleInputChange('amount', parseFloat(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Sender UPI ID"
                  value={formData.sender_upi}
                  onChange={(e) => handleInputChange('sender_upi', e.target.value)}
                  placeholder="user@upi"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Receiver UPI ID"
                  value={formData.receiver_upi}
                  onChange={(e) => handleInputChange('receiver_upi', e.target.value)}
                  placeholder="merchant@upi"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Merchant Category</InputLabel>
                  <Select
                    value={formData.merchant_category}
                    label="Merchant Category"
                    onChange={(e) => handleInputChange('merchant_category', e.target.value)}
                  >
                    <MenuItem value="Shopping">Shopping</MenuItem>
                    <MenuItem value="Food">Food & Dining</MenuItem>
                    <MenuItem value="Transfer">Money Transfer</MenuItem>
                    <MenuItem value="Bills">Bill Payments</MenuItem>
                    <MenuItem value="Travel">Travel</MenuItem>
                    <MenuItem value="Entertainment">Entertainment</MenuItem>
                    <MenuItem value="Other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Transaction Type</InputLabel>
                  <Select
                    value={formData.transaction_type}
                    label="Transaction Type"
                    onChange={(e) => handleInputChange('transaction_type', e.target.value)}
                  >
                    <MenuItem value="P2P">P2P Transfer</MenuItem>
                    <MenuItem value="P2M">Payment to Merchant</MenuItem>
                    <MenuItem value="Bill">Bill Payment</MenuItem>
                    <MenuItem value="QR">QR Code Payment</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="City Name"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Device ID"
                  value={formData.device_id}
                  onChange={(e) => handleInputChange('device_id', e.target.value)}
                  placeholder="Device Identifier"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 2 }}>
              Additional Risk Factors
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Previous Transactions"
                  type="number"
                  value={formData.previous_transaction_count || ''}
                  onChange={(e) => handleInputChange('previous_transaction_count', parseInt(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Previous Fraud Count"
                  type="number"
                  value={formData.previous_fraud_count || ''}
                  onChange={(e) => handleInputChange('previous_fraud_count', parseInt(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Device Trust Score (0-1)"
                  type="number"
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                  value={formData.device_trust_score || ''}
                  onChange={(e) => handleInputChange('device_trust_score', parseFloat(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Location Risk Score (0-1)"
                  type="number"
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                  value={formData.location_risk_score || ''}
                  onChange={(e) => handleInputChange('location_risk_score', parseFloat(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Amount Deviation (%)"
                  type="number"
                  value={formData.amount_deviation || ''}
                  onChange={(e) => handleInputChange('amount_deviation', parseFloat(e.target.value) || 0)}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Time Since Last Transaction (min)"
                  type="number"
                  value={formData.time_since_last_transaction || ''}
                  onChange={(e) => handleInputChange('time_since_last_transaction', parseFloat(e.target.value) || 0)}
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleSubmit}
                disabled={loading}
                startIcon={<SecurityIcon />}
                sx={{ flex: 1 }}
              >
                {loading ? 'Analyzing...' : 'Analyze Transaction'}
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => {
                  setFormData({
                    transaction_id: '',
                    sender_upi: '',
                    receiver_upi: '',
                    amount: 0,
                    timestamp: new Date().toISOString(),
                    merchant_category: '',
                    device_id: '',
                    location: '',
                    transaction_type: '',
                    previous_transaction_count: 0,
                    previous_fraud_count: 0,
                    device_trust_score: 0,
                    location_risk_score: 0,
                    amount_deviation: 0,
                    time_since_last_transaction: 0,
                  });
                  setResult(null);
                }}
              >
                Reset
              </Button>
            </Box>
          </GlassCard>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={5}>
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <GlassCard>
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <AnalyticsIcon sx={{ fontSize: 64, color: theme.palette.primary.main, mb: 2 }} />
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      Analyzing Transaction...
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 3 }}>
                      Our AI model is evaluating multiple risk factors
                    </Typography>
                    <LinearProgress
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                        },
                      }}
                    />
                  </Box>
                </GlassCard>
              </motion.div>
            ) : result ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <GlassCard>
                  {/* Prediction Result */}
                  <Box
                    sx={{
                      textAlign: 'center',
                      p: 3,
                      borderRadius: 3,
                      background: `linear-gradient(135deg, ${alpha(
                        result.prediction === 'fraud' ? theme.palette.error.main : theme.palette.success.main,
                        0.2
                      )} 0%, ${alpha(
                        result.prediction === 'fraud' ? theme.palette.error.main : theme.palette.success.main,
                        0.05
                      )} 100%)`,
                      border: `1px solid ${alpha(
                        result.prediction === 'fraud' ? theme.palette.error.main : theme.palette.success.main,
                        0.3
                      )}`,
                      mb: 3,
                    }}
                  >
                    {result.prediction === 'fraud' ? (
                      <ErrorIcon sx={{ fontSize: 64, color: theme.palette.error.main, mb: 2 }} />
                    ) : (
                      <CheckIcon sx={{ fontSize: 64, color: theme.palette.success.main, mb: 2 }} />
                    )}
                    <Typography
                      variant="h5"
                      sx={{
                        fontWeight: 700,
                        color: result.prediction === 'fraud' ? theme.palette.error.main : theme.palette.success.main,
                        mb: 1,
                      }}
                    >
                      {result.prediction === 'fraud' ? 'FRAUD DETECTED' : 'TRANSACTION SAFE'}
                    </Typography>
                    <Chip
                      label={result.risk_level.toUpperCase()}
                      sx={{
                        backgroundColor: alpha(getRiskColor(result.risk_level), 0.2),
                        color: getRiskColor(result.risk_level),
                        fontWeight: 700,
                      }}
                    />
                  </Box>

                  {/* Fraud Probability */}
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        Fraud Probability
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, color: getRiskColor(result.risk_level) }}
                      >
                        {result.fraud_probability.toFixed(1)}%
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        height: 12,
                        borderRadius: 6,
                        backgroundColor: alpha(getRiskColor(result.risk_level), 0.1),
                        overflow: 'hidden',
                      }}
                    >
                      <Box
                        sx={{
                          width: `${result.fraud_probability}%`,
                          height: '100%',
                          background: `linear-gradient(90deg, ${theme.palette.warning.main} 0%, ${getRiskColor(result.risk_level)} 100%)`,
                          borderRadius: 6,
                          transition: 'width 0.5s ease-in-out',
                        }}
                      />
                    </Box>
                  </Box>

                  {/* Confidence Score */}
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        Confidence Score
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                        {(result.confidence_score * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={result.confidence_score * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
                        },
                      }}
                    />
                  </Box>

                  <Divider sx={{ my: 3 }} />

                  {/* Risk Factors */}
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    Risk Factors Analysis
                  </Typography>
                  <List dense>
                    {result.factors.map((factor: RiskFactor, index: number) => (
                      <ListItem
                        key={index}
                        sx={{
                          borderRadius: 2,
                          mb: 1,
                          backgroundColor: 'rgba(255,255,255,0.03)',
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>{getImpactIcon(factor.impact)}</ListItemIcon>
                        <ListItemText
                          primary={factor.name}
                          secondary={`${factor.description} (${(factor.value * 100).toFixed(0)}%)`}
                          primaryTypographyProps={{ fontWeight: 500, color: 'white' }}
                          secondaryTypographyProps={{ color: 'rgba(255,255,255,0.6)' }}
                        />
                      </ListItem>
                    ))}
                  </List>

                  <Divider sx={{ my: 3 }} />

                  {/* Recommendations */}
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    Recommendations
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {result.recommendations.map((rec: string, index: number) => (
                      <Alert
                        key={index}
                        severity="info"
                        icon={<InfoIcon />}
                        sx={{
                          borderRadius: 2,
                          backgroundColor: alpha(theme.palette.info.main, 0.1),
                          '& .MuiAlert-message': { color: 'rgba(255,255,255,0.8)' },
                        }}
                      >
                        {rec}
                      </Alert>
                    ))}
                  </Box>
                </GlassCard>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <GlassCard>
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <PsychologyIcon sx={{ fontSize: 80, color: 'rgba(255,255,255,0.2)', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>
                      Ready to Analyze
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.4)' }}>
                      Fill in the transaction details and click "Analyze Transaction" to get fraud prediction
                    </Typography>
                  </Box>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Prediction;
