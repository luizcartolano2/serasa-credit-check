import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3006', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  
  security: {
    jwtSecret: process.env.JWT_SECRET || 'default-secret-key',
    tokenExpiry: parseInt(process.env.TOKEN_EXPIRY || '3600', 10),
  },
  
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000', 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
  },
  
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    dir: process.env.LOG_DIR || 'logs',
  },
  
  delays: {
    min: parseInt(process.env.MIN_DELAY || '2000', 10),
    max: parseInt(process.env.MAX_DELAY || '60000', 10),
  },
  
  errors: {
    chance: parseInt(process.env.ERROR_CHANCE_PERCENT || '15', 10), // 15% chance of random error
  },
  
  paths: {
    payloadPF: path.join(process.cwd(), 'payload-pf.json'),
    payloadPJ: path.join(process.cwd(), 'payload-pj.json'),
  },
} as const;

export type Config = typeof config;