import { Router } from 'express';
import { authController } from '../controllers/authController';
import { reportController } from '../controllers/reportController';
import { healthController } from '../controllers/healthController';
import { authMiddleware } from '../middleware/authMiddleware';
import {
  validateLoginRequest,
  validatePFReportRequest,
  validatePJReportRequest,
} from '../middleware/validation';

const router = Router();

// Auth routes
router.post(
  '/security/iam/v1/client-identities/login',
  validateLoginRequest,
  (req, res) => authController.login(req, res)
);

// Report routes
router.get(
  '/credit-services/person-information-report/v1/creditreport',
  authMiddleware,
  validatePFReportRequest,
  (req, res) => reportController.getPFReport(req, res)
);

router.get(
  '/credit-services/business-information-report/v1/reports',
  authMiddleware,
  validatePJReportRequest,
  (req, res) => reportController.getPJReport(req, res)
);

// Health check
router.get('/health', (req, res) => healthController.check(req, res));

// 404 handler
router.use('*', (req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    path: req.originalUrl,
  });
});

export default router;