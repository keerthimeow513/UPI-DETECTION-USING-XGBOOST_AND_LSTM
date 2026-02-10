import React from 'react';
import { Box, Typography, useTheme, alpha, LinearProgress } from '@mui/material';
import { motion } from 'framer-motion';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'flat';
  trendValue?: string;
  icon?: React.ReactNode;
  color?: string;
  progress?: number;
  delay?: number;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendValue,
  icon,
  color,
  progress,
  delay = 0,
}) => {
  const theme = useTheme();
  const defaultColor = color || theme.palette.primary.main;

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon sx={{ color: theme.palette.success.main, fontSize: 18 }} />;
      case 'down':
        return <TrendingDownIcon sx={{ color: theme.palette.error.main, fontSize: 18 }} />;
      default:
        return <TrendingFlatIcon sx={{ color: theme.palette.warning.main, fontSize: 18 }} />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return theme.palette.success.main;
      case 'down':
        return theme.palette.error.main;
      default:
        return theme.palette.warning.main;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Box
        sx={{
          p: 3,
          borderRadius: 3,
          background: `linear-gradient(135deg,
            ${alpha(defaultColor, 0.15)} 0%,
            ${alpha(defaultColor, 0.05)} 50%,
            ${alpha(theme.palette.secondary.main, 0.05)} 100%)`,
          backdropFilter: 'blur(20px)',
          border: `1px solid ${alpha(defaultColor, 0.2)}`,
          boxShadow: `
            0 4px 20px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 ${alpha('#ffffff', 0.1)}
          `,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: `
              0 8px 32px rgba(0, 0, 0, 0.2),
              inset 0 1px 0 ${alpha('#ffffff', 0.15)},
              0 0 30px ${alpha(defaultColor, 0.1)}
            `,
          },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography
              variant="body2"
              sx={{
                color: 'rgba(255,255,255,0.6)',
                fontWeight: 500,
                mb: 0.5,
              }}
            >
              {title}
            </Typography>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                background: `linear-gradient(135deg, ${defaultColor} 0%, ${alpha(defaultColor, 0.7)} 100%)`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {value}
            </Typography>
          </Box>
          {icon && (
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${alpha(defaultColor, 0.2)} 0%, ${alpha(defaultColor, 0.1)} 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: defaultColor,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        {subtitle && (
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)', mb: 1 }}>
            {subtitle}
          </Typography>
        )}

        {(trend || trendValue) && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {trend && getTrendIcon()}
            {trendValue && (
              <Typography
                variant="body2"
                sx={{
                  color: getTrendColor(),
                  fontWeight: 600,
                }}
              >
                {trendValue}
              </Typography>
            )}
          </Box>
        )}

        {progress !== undefined && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                Progress
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 600 }}>
                {progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: alpha(defaultColor, 0.1),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  background: `linear-gradient(90deg, ${defaultColor} 0%, ${alpha(defaultColor, 0.7)} 100%)`,
                },
              }}
            />
          </Box>
        )}
      </Box>
    </motion.div>
  );
};

export default KPICard;
