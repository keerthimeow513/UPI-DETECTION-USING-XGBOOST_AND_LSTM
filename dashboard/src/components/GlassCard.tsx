import React from 'react';
import { Box, Card, CardProps, useTheme, alpha } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface GlassCardProps extends CardProps {
  children: React.ReactNode;
  hoverEffect?: boolean;
  glowEffect?: boolean;
  intensity?: 'low' | 'medium' | 'high';
}

const GlassCard: React.FC<GlassCardProps> = ({
  children,
  hoverEffect = true,
  glowEffect = false,
  intensity = 'medium',
  sx,
  ...props
}) => {
  const theme = useTheme();

  const getBackgroundOpacity = () => {
    switch (intensity) {
      case 'low':
        return 0.08;
      case 'high':
        return 0.2;
      default:
        return 0.12;
    }
  };

  const getBorderOpacity = () => {
    switch (intensity) {
      case 'low':
        return 0.08;
      case 'high':
        return 0.3;
      default:
        return 0.15;
    }
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <Card
          sx={{
            background: `linear-gradient(135deg,
              ${alpha('#ffffff', getBackgroundOpacity())} 0%,
              ${alpha(theme.palette.primary.main, getBackgroundOpacity() * 0.5)} 50%,
              ${alpha(theme.palette.secondary.main, getBackgroundOpacity() * 0.3)} 100%)`,
            backdropFilter: 'blur(20px)',
            border: `1px solid ${alpha('#ffffff', getBorderOpacity())}`,
            borderRadius: 4,
            boxShadow: `
              0 8px 32px rgba(0, 0, 0, 0.2),
              0 4px 16px rgba(0, 0, 0, 0.1),
              inset 0 1px 0 ${alpha('#ffffff', 0.1)}
            `,
            overflow: 'hidden',
            position: 'relative',
            transition: hoverEffect
              ? 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              : 'none',
            '&::before': glowEffect
              ? {
                  content: '""',
                  position: 'absolute',
                  top: '-50%',
                  left: '-50%',
                  width: '200%',
                  height: '200%',
                  background: `conic-gradient(
                    transparent,
                    ${alpha(theme.palette.primary.main, 0.1)},
                    transparent,
                    ${alpha(theme.palette.secondary.main, 0.1)},
                    transparent
                  )`,
                  animation: 'rotate 4s linear infinite',
                  zIndex: 0,
                }
              : {},
            '&::after': glowEffect
              ? {
                  content: '""',
                  position: 'absolute',
                  inset: 0,
                  background: 'inherit',
                  zIndex: 1,
                  borderRadius: 4,
                }
              : {},
            '& > *': {
              position: 'relative',
              zIndex: 2,
            },
            ...(hoverEffect && {
              '&:hover': {
                transform: 'translateY(-4px) scale(1.01)',
                boxShadow: `
                  0 16px 48px rgba(0, 0, 0, 0.3),
                  0 8px 24px rgba(0, 0, 0, 0.2),
                  inset 0 1px 0 ${alpha('#ffffff', 0.15)},
                  0 0 40px ${alpha(theme.palette.primary.main, 0.15)}
                `,
                borderColor: alpha('#ffffff', 0.25),
              },
            }),
            ...sx,
          }}
          {...props}
        >
          {children}
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};

// Inner glow effect component
export const GlassCardInner: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Box
    sx={{
      p: 3,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    }}
  >
    {children}
  </Box>
);

// Animated border variant
interface GlowingBorderCardProps extends CardProps {
  children: React.ReactNode;
  glowColor?: string;
}

export const GlowingBorderCard: React.FC<GlowingBorderCardProps> = ({
  children,
  glowColor,
  sx,
  ...props
}) => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        position: 'relative',
        borderRadius: 4,
        padding: '2px',
        background: `linear-gradient(135deg,
          ${glowColor || theme.palette.primary.main} 0%,
          ${glowColor || theme.palette.secondary.main} 100%)`,
        ...sx,
      }}
    >
      <Box
        sx={{
          background: `linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)`,
          borderRadius: 'calc(4px - 1px)',
          height: '100%',
        }}
      >
        <Box sx={{ p: 3 }}>{children}</Box>
      </Box>
    </Box>
  );
};

export default GlassCard;
