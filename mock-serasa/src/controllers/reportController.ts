import { Request, Response } from 'express';
import { reportService } from '../services/reportService';
import { logger } from '../utils/logger';

export class ReportController {
  async getPFReport(req: Request, res: Response): Promise<void> {
    try {
      const documentId = req.headers['x-document-id'] as string;
      const reportName = req.query.reportName as string;

      const report = await reportService.getPFReport(documentId, reportName);
      res.json(report);
    } catch (error: any) {
      logger.error('Failed to generate PF report', { error });
      
      const status = error.status || 500;
      const errorResponse: any = {
        error: 'Failed to generate report',
        message: error instanceof Error ? error.message : 'Unknown error',
      };

      if (error.code) {
        errorResponse.code = error.code;
      }

      res.status(status).json(errorResponse);
    }
  }

  async getPJReport(req: Request, res: Response): Promise<void> {
    try {
      const documentId = req.headers['x-document-id'] as string;
      const reportName = req.query.reportName as string;

      const report = await reportService.getPJReport(documentId, reportName);
      res.json(report);
    } catch (error: any) {
      logger.error('Failed to generate PJ report', { error });
      
      const status = error.status || 500;
      const errorResponse: any = {
        error: 'Failed to generate report',
        message: error instanceof Error ? error.message : 'Unknown error',
      };

      if (error.code) {
        errorResponse.code = error.code;
      }

      res.status(status).json(errorResponse);
    }
  }
}

export const reportController = new ReportController();