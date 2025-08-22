import crypto from 'crypto';
import { config } from '../config/config';
import { TokenPayload, TokenData } from '../types';
import { logger } from '../utils/logger';

class AuthService {
  private tokenStore: Map<string, TokenPayload> = new Map();
  private secretKey: string;

  constructor() {
    this.secretKey = config.security.jwtSecret;
  }

  generateToken(clientId: string): { token: string; expiresIn: number } {
    try {
      const timestamp = Date.now();
      const expiresIn = config.security.tokenExpiry;
      const expiryTimestamp = timestamp + (expiresIn * 1000);

      const payload: TokenPayload = {
        clientId,
        timestamp,
        expiryTimestamp,
      };

      const hash = crypto
        .createHmac('sha256', this.secretKey)
        .update(JSON.stringify(payload))
        .digest('hex');

      const tokenData: TokenData = { payload, hash };
      const token = Buffer.from(JSON.stringify(tokenData)).toString('base64');

      this.tokenStore.set(token, payload);
      
      logger.info('Token generated successfully', { clientId });

      return { token, expiresIn };
    } catch (error) {
      logger.error('Error generating token', { error, clientId });
      throw new Error('Failed to generate token');
    }
  }

  validateToken(token: string): boolean {
    try {
      const paddedToken = this.addBase64Padding(token);
      
      const decoded: TokenData = JSON.parse(
        Buffer.from(paddedToken, 'base64').toString()
      );
      
      const { payload, hash } = decoded;

      const storedPayload = this.tokenStore.get(paddedToken) || this.tokenStore.get(token);
      
      if (!storedPayload) {
        logger.warn('Token not found in store');
        return false;
      }

      if (payload.expiryTimestamp < Date.now()) {
        this.tokenStore.delete(token);
        this.tokenStore.delete(paddedToken);
        logger.warn('Token expired', { clientId: payload.clientId });
        return false;
      }

      const validHash = crypto
        .createHmac('sha256', this.secretKey)
        .update(JSON.stringify(payload))
        .digest('hex');

      const isValid = hash === validHash;
      
      if (!isValid) {
        logger.warn('Invalid token hash', { clientId: payload.clientId });
      }

      return isValid;
    } catch (error) {
      logger.error('Error validating token', { error });
      return false;
    }
  }

  private addBase64Padding(base64String: string): string {
    const padding = (4 - (base64String.length % 4)) % 4;
    return base64String + '='.repeat(padding);
  }

  getActiveTokenCount(): number {
    return this.tokenStore.size;
  }

  cleanupExpiredTokens(): void {
    const now = Date.now();
    let cleaned = 0;
    
    for (const [token, payload] of this.tokenStore.entries()) {
      if (payload.expiryTimestamp < now) {
        this.tokenStore.delete(token);
        cleaned++;
      }
    }
    
    if (cleaned > 0) {
      logger.info(`Cleaned up ${cleaned} expired tokens`);
    }
  }
}

export const authService = new AuthService();