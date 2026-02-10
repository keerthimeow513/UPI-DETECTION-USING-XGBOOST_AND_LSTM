// Transaction Types
export interface Transaction {
  id: string;
  sender_upi: string;
  receiver_upi: string;
  amount: number;
  timestamp: string;
  merchant_category: string;
  location: string;
  device_id: string;
  is_fraud: boolean;
  fraud_probability?: number;
  risk_score?: number;
}

// API Response Types
export interface FraudPredictionRequest {
  transaction_id: string;
  sender_upi: string;
  receiver_upi: string;
  amount: number;
  timestamp: string;
  merchant_category: string;
  device_id: string;
  location: string;
  transaction_type: string;
  previous_transaction_count: number;
  previous_fraud_count: number;
  device_trust_score: number;
  location_risk_score: number;
  amount_deviation: number;
  time_since_last_transaction: number;
}

export interface FraudPredictionResponse {
  transaction_id: string;
  prediction: 'fraud' | 'legitimate';
  fraud_probability: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  confidence_score: number;
  factors: RiskFactor[];
  recommendations: string[];
}

export interface RiskFactor {
  name: string;
  impact: 'positive' | 'negative' | 'neutral';
  value: number;
  description: string;
}

// Dashboard Types
export interface DashboardStats {
  totalTransactions: number;
  fraudDetected: number;
  legitimateTransactions: number;
  fraudRate: number;
  averageRiskScore: number;
  recentAlerts: number;
  blockedAmount: number;
  savingsAmount: number;
}

// Analytics Types
export interface TimeSeriesData {
  timestamp: string;
  value: number;
  category?: string;
}

export interface FraudPattern {
  category: string;
  count: number;
  percentage: number;
  trend: 'up' | 'down' | 'stable';
}

export interface GeographicData {
  location: string;
  fraudCount: number;
  transactionCount: number;
  riskLevel: 'low' | 'medium' | 'high';
}

// Admin Types
export interface RiskConfiguration {
  lowThreshold: number;
  mediumThreshold: number;
  highThreshold: number;
  criticalThreshold: number;
  autoBlockThreshold: number;
  alertEnabled: boolean;
  notifyEmail: string;
}

export interface DeviceInfo {
  id: string;
  name: string;
  trustScore: number;
  lastUsed: string;
  isBlocked: boolean;
  transactionCount: number;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  details: string;
  ip_address: string;
}

// Performance Types
export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  auc_roc: number;
  confusionMatrix: ConfusionMatrix;
}

export interface ConfusionMatrix {
  true_positive: number;
  true_negative: number;
  false_positive: number;
  false_negative: number;
}

export interface ModelVersion {
  version: string;
  trainingDate: string;
  accuracy: number;
  isActive: boolean;
}

export interface PerformanceOverTime {
  date: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
}

// User Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'analyst' | 'viewer';
  lastLogin: string;
}

// Alert Types
export interface FraudAlert {
  id: string;
  transaction_id: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  status: 'pending' | 'reviewed' | 'resolved' | 'dismissed';
  assigned_to?: string;
}
