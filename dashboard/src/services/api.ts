import axios from 'axios';
import {
  FraudPredictionRequest,
  FraudPredictionResponse,
  DashboardStats,
  Transaction,
  ModelMetrics,
  RiskConfiguration,
  DeviceInfo,
  AuditLog,
  FraudAlert,
  PerformanceOverTime,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service Functions
export const fraudApi = {
  // Predict fraud for a transaction
  predictFraud: async (data: FraudPredictionRequest): Promise<FraudPredictionResponse> => {
    const response = await api.post<FraudPredictionResponse>('/predict', data);
    return response.data;
  },

  // Get dashboard statistics
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/dashboard/stats');
    return response.data;
  },

  // Get recent transactions
  getRecentTransactions: async (limit: number = 10): Promise<Transaction[]> => {
    const response = await api.get<Transaction[]>(`/transactions/recent?limit=${limit}`);
    return response.data;
  },

  // Get fraud alerts
  getFraudAlerts: async (status?: string): Promise<FraudAlert[]> => {
    const url = status ? `/alerts?status=${status}` : '/alerts';
    const response = await api.get<FraudAlert[]>(url);
    return response.data;
  },

  // Update alert status
  updateAlertStatus: async (alertId: string, status: string): Promise<void> => {
    await api.put(`/alerts/${alertId}/status`, { status });
  },
};

export const analyticsApi = {
  // Get fraud trends over time
  getFraudTrends: async (days: number = 30): Promise<{ labels: string[]; data: number[] }> => {
    const response = await api.get<{ labels: string[]; data: number[] }>(
      `/analytics/fraud-trends?days=${days}`
    );
    return response.data;
  },

  // Get fraud by category
  getFraudByCategory: async (): Promise<{ category: string; count: number }[]> => {
    const response = await api.get<{ category: string; count: number }[]>(
      '/analytics/fraud-by-category'
    );
    return response.data;
  },

  // Get transaction volume
  getTransactionVolume: async (days: number = 7): Promise<{ labels: string[]; legitimate: number[]; fraud: number[] }> => {
    const response = await api.get<{ labels: string[]; legitimate: number[]; fraud: number[] }>(
      `/analytics/transaction-volume?days=${days}`
    );
    return response.data;
  },

  // Get performance over time
  getPerformanceOverTime: async (days: number = 30): Promise<PerformanceOverTime[]> => {
    const response = await api.get<PerformanceOverTime[]>(
      `/analytics/performance?days=${days}`
    );
    return response.data;
  },
};

export const adminApi = {
  // Get risk configuration
  getRiskConfiguration: async (): Promise<RiskConfiguration> => {
    const response = await api.get<RiskConfiguration>('/admin/risk-config');
    return response.data;
  },

  // Update risk configuration
  updateRiskConfiguration: async (config: RiskConfiguration): Promise<RiskConfiguration> => {
    const response = await api.put<RiskConfiguration>('/admin/risk-config', config);
    return response.data;
  },

  // Get registered devices
  getDevices: async (): Promise<DeviceInfo[]> => {
    const response = await api.get<DeviceInfo[]>('/admin/devices');
    return response.data;
  },

  // Block/unblock device
  toggleDeviceBlock: async (deviceId: string, blocked: boolean): Promise<void> => {
    await api.put(`/admin/devices/${deviceId}/block`, { blocked });
  },

  // Get audit logs
  getAuditLogs: async (limit: number = 100): Promise<AuditLog[]> => {
    const response = await api.get<AuditLog[]>(`/admin/audit-logs?limit=${limit}`);
    return response.data;
  },
};

export const modelApi = {
  // Get model metrics
  getModelMetrics: async (): Promise<ModelMetrics> => {
    const response = await api.get<ModelMetrics>('/model/metrics');
    return response.data;
  },

  // Get model versions
  getModelVersions: async (): Promise<{ version: string; trainingDate: string; accuracy: number; isActive: boolean }[]> => {
    const response = await api.get<{ version: string; trainingDate: string; accuracy: number; isActive: boolean }[]>('/model/versions');
    return response.data;
  },

  // Get confusion matrix
  getConfusionMatrix: async (): Promise<{ true_positive: number; true_negative: number; false_positive: number; false_negative: number }> => {
    const response = await api.get<{ true_positive: number; true_negative: number; false_positive: number; false_negative: number }>('/model/confusion-matrix');
    return response.data;
  },

  // Retrain model
  retrainModel: async (): Promise<{ message: string; newVersion: string }> => {
    const response = await api.post<{ message: string; newVersion: string }>('/model/retrain');
    return response.data;
  },
};

export default api;
