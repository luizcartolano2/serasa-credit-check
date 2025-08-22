import { Request, Response, NextFunction } from 'express';
import { authMiddleware } from '../../middleware/authMiddleware';
import { authService } from '../../services/authService';

jest.mock('../../services/authService');

describe('AuthMiddleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {
      headers: {},
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    nextFunction = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should reject request without authorization header', () => {
    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Token não fornecido',
      details: 'Authorization header deve ser fornecido no formato: Bearer <token>',
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  it('should reject request with invalid authorization format', () => {
    mockRequest.headers = {
      authorization: 'Basic invalid-token',
    };

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(nextFunction).not.toHaveBeenCalled();
  });

  it('should reject request with invalid token', () => {
    mockRequest.headers = {
      authorization: 'Bearer invalid-token',
    };

    (authService.validateToken as jest.Mock).mockReturnValue(false);

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(mockResponse.status).toHaveBeenCalledWith(401);
    expect(mockResponse.json).toHaveBeenCalledWith({
      error: 'Token inválido ou expirado',
    });
    expect(nextFunction).not.toHaveBeenCalled();
  });

  it('should allow request with valid token', () => {
    mockRequest.headers = {
      authorization: 'Bearer valid-token',
    };

    (authService.validateToken as jest.Mock).mockReturnValue(true);

    authMiddleware(mockRequest as Request, mockResponse as Response, nextFunction);

    expect(nextFunction).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
    expect(mockResponse.json).not.toHaveBeenCalled();
  });
});