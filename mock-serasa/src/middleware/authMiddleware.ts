import { Request, Response, NextFunction } from 'express';
import { authService } from '../services/authService';
import { logger } from '../utils/logger';

export const authMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  logger.info('Validating authentication token');
  
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    logger.warn('Missing or invalid authorization header');
    res.status(401).json({
      error: 'Token não fornecido',
      details: 'Authorization header deve ser fornecido no formato: Bearer <token>',
    });
    return;
  }

  const token = authHeader.split(' ')[1];

  if (!authService.validateToken(token)) {
    logger.warn('Invalid or expired token');
    res.status(401).json({
      error: 'Token inválido ou expirado',
    });
    return;
  }

  logger.info('Token validated successfully');
  next();
};