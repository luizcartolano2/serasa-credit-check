import { Request, Response } from 'express';
import { authController } from '../../controllers/authController';
import { authService } from '../../services/authService';

jest.mock('../../services/authService');

describe('AuthController', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;

  beforeEach(() => {
    mockRequest = {
      headers: {
        authorization: 'Basic dGVzdDp0ZXN0',
      },
    };
    mockResponse = {
      json: jest.fn(),
      status: jest.fn().mockReturnThis(),
    };
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should successfully generate a token on login', async () => {
      const mockToken = 'mock-token-123';
      const mockExpiresIn = 3600;

      (authService.generateToken as jest.Mock).mockReturnValue({
        token: mockToken,
        expiresIn: mockExpiresIn,
      });

      await authController.login(mockRequest as Request, mockResponse as Response);

      expect(authService.generateToken).toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith({
        accessToken: mockToken,
        tokenType: 'Bearer',
        expiresIn: mockExpiresIn.toString(),
        scope: ['read', 'write'],
      });
    });

    it('should handle errors during token generation', async () => {
      (authService.generateToken as jest.Mock).mockImplementation(() => {
        throw new Error('Token generation failed');
      });

      await authController.login(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith({
        error: 'Failed to generate token',
      });
    });
  });
});