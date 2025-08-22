import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { config } from './config/config';
import { logger } from './utils/logger';
import { requestLogger } from './middleware/requestLogger';
import { errorHandler } from './middleware/errorHandler';
import routes from './routes';
import { reportService } from './services/reportService';
import { authService } from './services/authService';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,
  max: config.rateLimit.maxRequests,
  message: {
    error: 'Too many requests from this IP, please try again later.',
    details: `Maximum ${config.rateLimit.maxRequests} requests per ${config.rateLimit.windowMs / 1000} seconds`,
  },
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    logger.warn('Rate limit exceeded', {
      ip: req.ip,
      path: req.path,
      userAgent: req.get('User-Agent'),
    });
    res.status(429).json({
      error: 'Too many requests from this IP, please try again later.',
      details: `Maximum ${config.rateLimit.maxRequests} requests per ${config.rateLimit.windowMs / 1000} seconds`,
      retryAfter: Math.ceil(config.rateLimit.windowMs / 1000),
    });
  },
});
app.use(limiter);

// Body parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use(requestLogger);

// Routes
app.use(routes);

// Error handling
app.use(errorHandler);

// Cleanup expired tokens periodically
setInterval(() => {
  authService.cleanupExpiredTokens();
}, 60000); // Every minute

// Server initialization
async function startServer() {
  try {
    // Initialize services
    await reportService.initialize();
    
    // Start server
    app.listen(config.port, () => {
      logger.info(`🚀 Mock Serasa Server running on port ${config.port}`);
      logger.info(`Environment: ${config.nodeEnv}`);
      logger.info(`Rate Limit: ${config.rateLimit.maxRequests} requests per ${config.rateLimit.windowMs / 1000} seconds`);
      logger.info('Available endpoints:');
      logger.info('  POST /security/iam/v1/client-identities/login');
      logger.info('  GET  /credit-services/person-information-report/v1/creditreport');
      logger.info('  GET  /credit-services/business-information-report/v1/reports');
      logger.info('  GET  /health');
    });
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  process.exit(0);
});

startServer();