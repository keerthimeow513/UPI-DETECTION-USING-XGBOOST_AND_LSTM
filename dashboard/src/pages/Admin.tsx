import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  Divider,
  useTheme,
  alpha,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Devices as DevicesIcon,
  Block as BlockIcon,
  CheckCircle as CheckIcon,
  Edit as EditIcon,
  History as HistoryIcon,
  Notifications as NotificationsIcon,
  Email as EmailIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import GlassCard from '../components/GlassCard';
import { RiskConfiguration, DeviceInfo, AuditLog } from '../types';

// Mock data
const mockDevices: DeviceInfo[] = [
  { id: 'DEV001', name: 'iPhone 14 Pro', trustScore: 0.95, lastUsed: '2024-01-15 10:30', isBlocked: false, transactionCount: 45 },
  { id: 'DEV002', name: 'Samsung S23', trustScore: 0.88, lastUsed: '2024-01-15 09:15', isBlocked: false, transactionCount: 32 },
  { id: 'DEV003', name: 'Unknown Device', trustScore: 0.32, lastUsed: '2024-01-15 08:45', isBlocked: true, transactionCount: 5 },
  { id: 'DEV004', name: 'Xiaomi Mi 13', trustScore: 0.72, lastUsed: '2024-01-14 22:30', isBlocked: false, transactionCount: 18 },
  { id: 'DEV005', name: 'OnePlus 11', trustScore: 0.91, lastUsed: '2024-01-15 11:00', isBlocked: false, transactionCount: 28 },
];

const mockAuditLogs: AuditLog[] = [
  { id: 'LOG001', timestamp: '2024-01-15 10:45:23', action: 'CONFIG_UPDATE', user: 'admin@upi', details: 'Updated high risk threshold', ip_address: '192.168.1.100' },
  { id: 'LOG002', timestamp: '2024-01-15 10:30:15', action: 'DEVICE_BLOCK', user: 'admin@upi', details: 'Blocked device DEV003', ip_address: '192.168.1.100' },
  { id: 'LOG003', timestamp: '2024-01-15 10:15:08', action: 'ALERT_RESOLVE', user: 'analyst@upi', details: 'Resolved alert ALT001', ip_address: '192.168.1.101' },
  { id: 'LOG004', timestamp: '2024-01-15 09:45:32', action: 'LOGIN_SUCCESS', user: 'admin@upi', details: 'Successful login', ip_address: '192.168.1.100' },
  { id: 'LOG005', timestamp: '2024-01-15 09:30:00', action: 'MODEL_RETRAIN', user: 'system', details: 'Model retraining completed', ip_address: '127.0.0.1' },
];

const Admin: React.FC = () => {
  const theme = useTheme();
  const [config, setConfig] = useState<RiskConfiguration>({
    lowThreshold: 30,
    mediumThreshold: 50,
    highThreshold: 70,
    criticalThreshold: 90,
    autoBlockThreshold: 85,
    alertEnabled: true,
    notifyEmail: 'security@upi.com',
  });
  const [devices, setDevices] = useState<DeviceInfo[]>(mockDevices);
  const [auditLogs] = useState<AuditLog[]>(mockAuditLogs);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<RiskConfiguration>(config);

  const handleConfigChange = (field: keyof RiskConfiguration, value: string | number | boolean) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveConfig = () => {
    setConfig(editingConfig);
    setEditDialogOpen(false);
  };

  const toggleDeviceBlock = (deviceId: string) => {
    setDevices((prev) =>
      prev.map((device) =>
        device.id === deviceId ? { ...device, isBlocked: !device.isBlocked } : device
      )
    );
  };

  const getActionColor = (action: string) => {
    if (action.includes('BLOCK') || action.includes('FAIL')) return theme.palette.error.main;
    if (action.includes('UPDATE') || action.includes('RESOLVE')) return theme.palette.warning.main;
    if (action.includes('SUCCESS') || action.includes('LOGIN')) return theme.palette.success.main;
    return theme.palette.info.main;
  };

  const getTrustColor = (score: number) => {
    if (score >= 0.8) return theme.palette.success.main;
    if (score >= 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Admin Panel
        </Typography>
        <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.7)' }}>
          Configure system settings and manage devices
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Risk Configuration */}
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SecurityIcon sx={{ color: theme.palette.primary.main }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Risk Configuration
                </Typography>
              </Box>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => {
                  setEditingConfig(config);
                  setEditDialogOpen(true);
                }}
              >
                Edit Settings
              </Button>
            </Box>

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                    Low Risk Threshold
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Slider
                      value={config.lowThreshold}
                      onChange={(_, value) => handleConfigChange('lowThreshold', value as number)}
                      disabled
                      sx={{
                        flex: 1,
                        color: theme.palette.success.main,
                      }}
                    />
                    <Chip label={`${config.lowThreshold}%`} color="success" size="small" />
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                    Medium Risk Threshold
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Slider
                      value={config.mediumThreshold}
                      onChange={(_, value) => handleConfigChange('mediumThreshold', value as number)}
                      disabled
                      sx={{
                        flex: 1,
                        color: theme.palette.warning.main,
                      }}
                    />
                    <Chip label={`${config.mediumThreshold}%`} color="warning" size="small" />
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                    High Risk Threshold
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Slider
                      value={config.highThreshold}
                      onChange={(_, value) => handleConfigChange('highThreshold', value as number)}
                      disabled
                      sx={{
                        flex: 1,
                        color: theme.palette.error.main,
                      }}
                    />
                    <Chip label={`${config.highThreshold}%`} color="error" size="small" />
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
                    Critical Risk Threshold
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Slider
                      value={config.criticalThreshold}
                      onChange={(_, value) => handleConfigChange('criticalThreshold', value as number)}
                      disabled
                      sx={{
                        flex: 1,
                        color: theme.palette.error.dark,
                      }}
                    />
                    <Chip label={`${config.criticalThreshold}%`} sx={{ backgroundColor: alpha(theme.palette.error.dark, 0.2), color: theme.palette.error.dark }} size="small" />
                  </Box>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.alertEnabled}
                      onChange={(e) => handleConfigChange('alertEnabled', e.target.checked)}
                      color="primary"
                    />
                  }
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <NotificationsIcon sx={{ fontSize: 20 }} />
                      <Typography>Enable Real-time Alerts</Typography>
                    </Box>
                  }
                  sx={{ color: 'white' }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Notification Email"
                  value={config.notifyEmail}
                  onChange={(e) => handleConfigChange('notifyEmail', e.target.value)}
                  size="small"
                  InputProps={{
                    startAdornment: <EmailIcon sx={{ color: 'rgba(255,255,255,0.4)', mr: 1 }} />,
                  }}
                />
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button variant="contained" startIcon={<SaveIcon />}>
                Save Changes
              </Button>
              <Button variant="outlined" startIcon={<RefreshIcon />}>
                Reset to Default
              </Button>
            </Box>
          </GlassCard>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} lg={4}>
          <GlassCard>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              System Status
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Alert
                severity="success"
                icon={<CheckIcon />}
                sx={{ borderRadius: 2 }}
              >
                System Operational
              </Alert>
              <Alert
                severity="info"
                icon={<RefreshIcon />}
                sx={{ borderRadius: 2 }}
              >
                Last Model Update: 2 hours ago
              </Alert>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: 'rgba(255,255,255,0.03)',
                }}
              >
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>
                  Active Devices
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {devices.filter((d) => !d.isBlocked).length}
                </Typography>
              </Box>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: 'rgba(255,255,255,0.03)',
                }}
              >
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>
                  Blocked Devices
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.error.main }}>
                  {devices.filter((d) => d.isBlocked).length}
                </Typography>
              </Box>
            </Box>
          </GlassCard>
        </Grid>

        {/* Device Management */}
        <Grid item xs={12} lg={8}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <DevicesIcon sx={{ color: theme.palette.primary.main }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Device Management
                </Typography>
              </Box>
              <Button variant="outlined" startIcon={<RefreshIcon />}>
                Refresh
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Device ID</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Device Name</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Trust Score</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Transactions</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Last Used</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Status</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {devices.map((device) => (
                    <TableRow
                      key={device.id}
                      sx={{
                        '&:hover': {
                          backgroundColor: 'rgba(255,255,255,0.05)',
                        },
                      }}
                    >
                      <TableCell sx={{ color: 'white', fontFamily: 'monospace' }}>{device.id}</TableCell>
                      <TableCell sx={{ color: 'white' }}>{device.name}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box
                            sx={{
                              width: 60,
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: alpha(getTrustColor(device.trustScore), 0.2),
                              overflow: 'hidden',
                            }}
                          >
                            <Box
                              sx={{
                                width: `${device.trustScore * 100}%`,
                                height: '100%',
                                backgroundColor: getTrustColor(device.trustScore),
                                borderRadius: 3,
                              }}
                            />
                          </Box>
                          <Typography variant="body2" sx={{ color: getTrustColor(device.trustScore), fontWeight: 600 }}>
                            {(device.trustScore * 100).toFixed(0)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell sx={{ color: 'white' }}>{device.transactionCount}</TableCell>
                      <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>{device.lastUsed}</TableCell>
                      <TableCell>
                        <Chip
                          label={device.isBlocked ? 'Blocked' : 'Active'}
                          size="small"
                          sx={{
                            backgroundColor: alpha(
                              device.isBlocked ? theme.palette.error.main : theme.palette.success.main,
                              0.2
                            ),
                            color: device.isBlocked ? theme.palette.error.main : theme.palette.success.main,
                            fontWeight: 600,
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title={device.isBlocked ? 'Unblock Device' : 'Block Device'}>
                          <IconButton
                            size="small"
                            onClick={() => toggleDeviceBlock(device.id)}
                            sx={{
                              color: device.isBlocked ? theme.palette.success.main : theme.palette.error.main,
                            }}
                          >
                            <BlockIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </GlassCard>
        </Grid>

        {/* Audit Logs */}
        <Grid item xs={12} lg={4}>
          <GlassCard>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <HistoryIcon sx={{ color: theme.palette.primary.main }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Audit Logs
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {auditLogs.slice(0, 5).map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255,255,255,0.03)',
                      borderLeft: `3px solid ${getActionColor(log.action)}`,
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Chip
                        label={log.action}
                        size="small"
                        sx={{
                          backgroundColor: alpha(getActionColor(log.action), 0.2),
                          color: getActionColor(log.action),
                          fontWeight: 600,
                          fontSize: '0.7rem',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        {log.timestamp.split(' ')[1]}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                      {log.details}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                      {log.user}
                    </Typography>
                  </Box>
                </motion.div>
              ))}
            </Box>
          </GlassCard>
        </Grid>
      </Grid>

      {/* Edit Configuration Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' }}>
          Edit Risk Configuration
        </DialogTitle>
        <DialogContent sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)' }}>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              fullWidth
              label="Low Risk Threshold (%)"
              type="number"
              value={editingConfig.lowThreshold}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, lowThreshold: parseInt(e.target.value) || 0 }))}
            />
            <TextField
              fullWidth
              label="Medium Risk Threshold (%)"
              type="number"
              value={editingConfig.mediumThreshold}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, mediumThreshold: parseInt(e.target.value) || 0 }))}
            />
            <TextField
              fullWidth
              label="High Risk Threshold (%)"
              type="number"
              value={editingConfig.highThreshold}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, highThreshold: parseInt(e.target.value) || 0 }))}
            />
            <TextField
              fullWidth
              label="Critical Risk Threshold (%)"
              type="number"
              value={editingConfig.criticalThreshold}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, criticalThreshold: parseInt(e.target.value) || 0 }))}
            />
            <TextField
              fullWidth
              label="Auto-Block Threshold (%)"
              type="number"
              value={editingConfig.autoBlockThreshold}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, autoBlockThreshold: parseInt(e.target.value) || 0 }))}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editingConfig.alertEnabled}
                  onChange={(e) => setEditingConfig((prev) => ({ ...prev, alertEnabled: e.target.checked }))}
                />
              }
              label="Enable Real-time Alerts"
            />
            <TextField
              fullWidth
              label="Notification Email"
              value={editingConfig.notifyEmail}
              onChange={(e) => setEditingConfig((prev) => ({ ...prev, notifyEmail: e.target.value }))}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)', p: 2 }}>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveConfig}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Admin;
