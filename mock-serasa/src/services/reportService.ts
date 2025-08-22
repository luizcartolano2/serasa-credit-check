import fs from 'fs/promises';
import { config } from '../config/config';
import { logger } from '../utils/logger';

class ReportService {
  private payloadPF: any = null;
  private payloadPJ: any = null;

  async initialize(): Promise<void> {
    try {
      await this.loadPayloads();
    } catch (error) {
      logger.error('Failed to initialize ReportService', { error });
    }
  }

  private async loadPayloads(): Promise<void> {
    try {
      const [pfData, pjData] = await Promise.all([
        this.loadPayload(config.paths.payloadPF),
        this.loadPayload(config.paths.payloadPJ),
      ]);

      this.payloadPF = pfData;
      this.payloadPJ = pjData;

      logger.info('Payloads loaded successfully', {
        pf: !!this.payloadPF,
        pj: !!this.payloadPJ,
      });
    } catch (error) {
      logger.error('Error loading payloads', { error });
    }
  }

  private async loadPayload(filePath: string): Promise<any> {
    try {
      const data = await fs.readFile(filePath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      logger.error(`Error loading payload from ${filePath}`, { error });
      return null;
    }
  }

  async generateDelay(): Promise<number> {
    const { min, max } = config.delays;
    return Math.floor(Math.random() * (max - min + 1) + min);
  }

  private shouldGenerateRandomError(): boolean {
    const randomValue = Math.floor(Math.random() * 100);
    return randomValue < config.errors.chance;
  }

  private generateRandomError(): { status: number; message: string; code?: string } {
    const errors = [
      { status: 400, message: 'Bad Request - Invalid document format', code: 'INVALID_DOCUMENT' },
      { status: 401, message: 'Unauthorized - Token expired or invalid', code: 'TOKEN_EXPIRED' },
      { status: 403, message: 'Forbidden - Insufficient permissions', code: 'INSUFFICIENT_PERMISSIONS' },
      { status: 429, message: 'Too Many Requests - Rate limit exceeded', code: 'RATE_LIMIT_EXCEEDED' },
      { status: 500, message: 'Internal Server Error - Service temporarily unavailable', code: 'SERVICE_ERROR' },
      { status: 503, message: 'Service Unavailable - External service down', code: 'EXTERNAL_SERVICE_DOWN' },
    ];

    const randomIndex = Math.floor(Math.random() * errors.length);
    return errors[randomIndex];
  }

  async getPFReport(documentId: string, reportName: string): Promise<any> {
    if (!this.payloadPF) {
      throw new Error('PF payload not available');
    }

    // Check for random error first
    if (this.shouldGenerateRandomError()) {
      const randomError = this.generateRandomError();
      logger.warn(`Generating random error for PF report`, {
        documentId: documentId.substring(0, 3) + '***',
        reportName,
        errorCode: randomError.code,
        status: randomError.status,
      });
      
      const error = new Error(randomError.message) as any;
      error.status = randomError.status;
      error.code = randomError.code;
      throw error;
    }

    const delay = await this.generateDelay();
    logger.info(`Generating PF report with ${delay}ms delay`, {
      documentId: documentId.substring(0, 3) + '***',
      reportName,
    });

    await new Promise(resolve => setTimeout(resolve, delay));

    const response = JSON.parse(JSON.stringify(this.payloadPF));
    
    if (response.reports?.[0]?.registration) {
      response.reports[0].registration.documentNumber = documentId;
      response.reports[0].reportName = reportName;
    }

    return response;
  }

  async getPJReport(documentId: string, reportName: string): Promise<any> {
    if (!this.payloadPJ) {
      throw new Error('PJ payload not available');
    }

    // Check for random error first
    if (this.shouldGenerateRandomError()) {
      const randomError = this.generateRandomError();
      logger.warn(`Generating random error for PJ report`, {
        documentId: documentId.substring(0, 8) + '***',
        reportName,
        errorCode: randomError.code,
        status: randomError.status,
      });
      
      const error = new Error(randomError.message) as any;
      error.status = randomError.status;
      error.code = randomError.code;
      throw error;
    }

    const delay = await this.generateDelay();
    logger.info(`Generating PJ report with ${delay}ms delay`, {
      documentId: documentId.substring(0, 8) + '***',
      reportName,
    });

    await new Promise(resolve => setTimeout(resolve, delay));

    const response = JSON.parse(JSON.stringify(this.payloadPJ));
    
    if (response.reports?.[0]?.registration) {
      response.reports[0].registration.documentId = documentId;
      response.reports[0].reportName = reportName;
    }

    return response;
  }

  getPayloadStatus(): { pf: boolean; pj: boolean } {
    return {
      pf: !!this.payloadPF,
      pj: !!this.payloadPJ,
    };
  }
}

export const reportService = new ReportService();