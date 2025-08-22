import { Request, Response } from 'express';
import { authService } from '../services/authService';
import { reportService } from '../services/reportService';
import { HealthCheckResponse } from '../types';

export class HealthController {
  async check(_req: Request, res: Response): Promise<void> {
    const response: HealthCheckResponse = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      payloads: reportService.getPayloadStatus(),
      activeTokens: authService.getActiveTokenCount(),
    };

    res.json(response);
  }
}

export const healthController = new HealthController();