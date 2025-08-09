"use client";

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, TrendingUp, TrendingDown, Minus, AlertTriangle, Heart } from 'lucide-react';

// Define strict types for color values
type ColorKey = 'red' | 'orange' | 'yellow' | 'green';
type TrendKey = 'increasing' | 'decreasing' | 'stable';
type AnimationKey = 'warning-pulse' | 'pulse-stress' | 'heartbeat' | 'none';

interface StressMeterData {
  current: number;
  percentage: number;
  color: ColorKey;
  label: string;
  animation: AnimationKey;
  trend: TrendKey;
}

interface LiveStressMeterProps {
  stressMeter: StressMeterData | null;
  isActive?: boolean;
  showDetails?: boolean;
}

// Strongly typed color configuration
const colorClassesMap: Record<ColorKey, { 
  bg: string; 
  glow: string; 
  border: string; 
  text: string; 
}> = {
  red: {
    bg: 'from-red-600 via-red-500 to-red-700',
    glow: 'shadow-red-500/50',
    border: 'border-red-400/50',
    text: 'text-red-300'
  },
  orange: {
    bg: 'from-orange-500 via-orange-400 to-red-600',
    glow: 'shadow-orange-500/50',
    border: 'border-orange-400/50',
    text: 'text-orange-300'
  },
  yellow: {
    bg: 'from-yellow-500 via-yellow-400 to-orange-500',
    glow: 'shadow-yellow-500/50',
    border: 'border-yellow-400/50',
    text: 'text-yellow-300'
  },
  green: {
    bg: 'from-green-500 via-green-400 to-emerald-500',
    glow: 'shadow-green-500/50',
    border: 'border-green-400/50',
    text: 'text-green-300'
  }
};

// Type-safe color class getter
function getColorClasses(color: ColorKey): typeof colorClassesMap[ColorKey] {
  return colorClassesMap[color];
}

// Helper function to determine color from stress level
function getColorFromLevel(level: number): ColorKey {
  if (level >= 8) return 'red';
  if (level >= 6) return 'orange';
  if (level >= 4) return 'yellow';
  return 'green';
}

export default function LiveStressMeter({ 
  stressMeter, 
  isActive = false, 
  showDetails = true 
}: LiveStressMeterProps) {
  const [currentLevel, setCurrentLevel] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (stressMeter?.current !== undefined) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setCurrentLevel(stressMeter.current);
        setTimeout(() => setIsAnimating(false), 800);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [stressMeter?.current]);

  if (!stressMeter) {
    return (
      <div className="w-full h-16 bg-gray-800/30 rounded-2xl animate-pulse flex items-center justify-center">
        <span className="text-white/50 text-sm">Loading stress meter...</span>
      </div>
    );
  }

  const colorClasses = getColorClasses(stressMeter.color);
  const percentage = (currentLevel / 10) * 100;

  const getTrendIcon = () => {
    switch (stressMeter.trend) {
      case 'increasing': return <TrendingUp className="w-4 h-4 text-red-400" />;
      case 'decreasing': return <TrendingDown className="w-4 h-4 text-green-400" />;
      default: return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getAnimationClass = (): string => {
    switch (stressMeter.animation) {
      case 'warning-pulse': return 'animate-warning-pulse';
      case 'pulse-stress': return 'animate-pulse-stress';
      case 'heartbeat': return 'animate-heartbeat';
      default: return '';
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Header */}
      {showDetails && (
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-white/70" />
            <span className="text-sm font-medium text-white/90">Live Stress Monitor</span>
            {isActive && <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>}
          </div>
          <div className="flex items-center space-x-2">
            {getTrendIcon()}
            <span className={`text-lg font-bold ${colorClasses.text}`}>
              {currentLevel}/10
            </span>
          </div>
        </div>
      )}

      {/* Main Stress Meter */}
      <div className="relative">
        {/* Background Container */}
        <div className={`relative h-6 bg-gray-900/50 rounded-full overflow-hidden border ${colorClasses.border} ${getAnimationClass()}`}>
          {/* Animated Fill */}
          <motion.div
            className={`h-full bg-gradient-to-r ${colorClasses.bg} shadow-lg ${colorClasses.glow} relative overflow-hidden`}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ 
              duration: 1.2,
              ease: [0.4, 0.0, 0.2, 1],
              type: "spring",
              stiffness: 100
            }}
          >
            {/* Shimmer Effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent skew-x-12"
              animate={{ x: ['-100%', '200%'] }}
              transition={{
                repeat: Infinity,
                duration: 2,
                ease: 'easeInOut',
                delay: 1
              }}
            />
            
            {/* Pulse Overlay for High Stress */}
            {currentLevel >= 8 && (
              <motion.div
                className="absolute inset-0 bg-red-400/30"
                animate={{ opacity: [0.3, 0.7, 0.3] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
          </motion.div>

          {/* Center Label */}
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.span 
              className="text-sm font-bold text-white/95 drop-shadow-lg"
              initial={{ scale: 1 }}
              animate={isAnimating ? { scale: [1, 1.1, 1] } : { scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              {stressMeter.label}
            </motion.span>
          </div>
        </div>

        {/* Crisis Alert Indicator */}
        <AnimatePresence>
          {currentLevel >= 9 && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className="absolute -top-2 -right-2"
            >
              <div className="bg-red-500 text-white rounded-full p-1 animate-pulse">
                <AlertTriangle className="w-4 h-4" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Detailed Info */}
      {showDetails && (
        <div className="flex justify-between items-center text-xs text-white/60">
          <div className="flex items-center space-x-4">
            <span>Trend: {stressMeter.trend}</span>
            <span>Level: {stressMeter.label}</span>
          </div>
          {currentLevel >= 8 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center space-x-1 text-red-400"
            >
              <Heart className="w-3 h-3" />
              <span className="font-medium">Support Available</span>
            </motion.div>
          )}
        </div>
      )}

      {/* Mini Stress History Graph */}
      {showDetails && (
        <div className="h-8 bg-gray-900/30 rounded-lg p-1 flex items-end space-x-1">
          {[...Array(10)].map((_, i) => {
            const height = Math.random() * 20 + 10; // Sample data for visualization
            return (
              <motion.div
                key={i}
                className={`flex-1 bg-gradient-to-t ${colorClasses.bg} rounded-sm opacity-60`}
                initial={{ height: 2 }}
                animate={{ height: `${height}px` }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

// Export types for use in other components
export type { StressMeterData, ColorKey, TrendKey, AnimationKey };
export { getColorFromLevel };
