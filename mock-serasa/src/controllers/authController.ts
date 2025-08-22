import { Request, Response } from 'express';
import crypto from 'crypto';
import { authService } from '../services/authService';
import { logger } from '../utils/logger';
import { LoginResponse } from '../types';

export class AuthController {
  async login(req: Request, res: Response): Promise<void> {
    try {
      const authHeader = req.headers.authorization as string;
      
      const clientId = crypto
        .createHash('sha256')
        .update(authHeader)
        .digest('hex')
        .substring(0, 16);

      const { token, expiresIn } = authService.generateToken(clientId);

      const response: LoginResponse = {
        accessToken: token,
        tokenType: 'Bearer',
        expiresIn: expiresIn.toString(),
        scope: ['read', 'write'],
      };

      logger.info('Login successful', { clientId });
      res.json(response);
    } catch (error) {
      logger.error('Login failed', { error });
      res.status(500).json({
        error: 'Failed to generate token',
      });
    }
  }
}

export const authController = new AuthController();