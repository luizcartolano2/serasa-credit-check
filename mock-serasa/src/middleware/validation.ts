import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { logger } from '../utils/logger';

export const validateLoginRequest = (req: Request, res: Response, next: NextFunction): void => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    logger.warn('Invalid login credentials format');
    res.status(401).json({
      error: 'Credenciais inválidas',
      details: 'Authorization header deve ser fornecido no formato: Basic <base64>',
    });
    return;
  }
  
  next();
};

export const validatePFReportRequest = (req: Request, res: Response, next: NextFunction): void => {
  const schema = Joi.object({
    documentId: Joi.string().required(),
    reportName: Joi.string().valid('RELATORIO_BASICO_PF_PME').required(),
  });

  const { error } = schema.validate({
    documentId: req.headers['x-document-id'],
    reportName: req.query.reportName,
  });

  if (error) {
    logger.warn('Invalid PF report request', { error: error.details });
    res.status(400).json({
      error: error.details[0].message,
    });
    return;
  }

  next();
};

export const validatePJReportRequest = (req: Request, res: Response, next: NextFunction): void => {
  const schema = Joi.object({
    documentId: Joi.string().required(),
    reportName: Joi.string().valid('RELATORIO_BASICO_PJ_PME').required(),
  });

  const { error } = schema.validate({
    documentId: req.headers['x-document-id'],
    reportName: req.query.reportName,
  });

  if (error) {
    logger.warn('Invalid PJ report request', { error: error.details });
    res.status(400).json({
      error: error.details[0].message,
    });
    return;
  }

  next();
};