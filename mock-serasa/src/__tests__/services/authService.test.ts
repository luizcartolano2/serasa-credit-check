import { authService } from '../../services/authService';

describe('AuthService', () => {
  describe('generateToken', () => {
    it('should generate a valid token', () => {
      const clientId = 'test-client-123';
      const result = authService.generateToken(clientId);

      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('expiresIn');
      expect(typeof result.token).toBe('string');
      expect(typeof result.expiresIn).toBe('number');
      expect(result.expiresIn).toBeGreaterThan(0);
    });

    it('should generate different tokens for different clients', () => {
      const client1 = 'client-1';
      const client2 = 'client-2';

      const token1 = authService.generateToken(client1);
      const token2 = authService.generateToken(client2);

      expect(token1.token).not.toBe(token2.token);
    });
  });

  describe('validateToken', () => {
    it('should validate a valid token', () => {
      const clientId = 'test-client';
      const { token } = authService.generateToken(clientId);

      const isValid = authService.validateToken(token);
      expect(isValid).toBe(true);
    });

    it('should reject an invalid token', () => {
      const invalidToken = 'invalid-token-12345';
      const isValid = authService.validateToken(invalidToken);
      expect(isValid).toBe(false);
    });

    it('should reject an expired token', async () => {
      // Mock the token expiry time to be in the past
      const originalEnv = process.env.TOKEN_EXPIRY;
      process.env.TOKEN_EXPIRY = '0';

      const clientId = 'test-client';
      const { token } = authService.generateToken(clientId);

      // Wait a bit to ensure token is expired
      await new Promise(resolve => setTimeout(resolve, 100));

      const isValid = authService.validateToken(token);
      expect(isValid).toBe(false);

      // Restore original env
      process.env.TOKEN_EXPIRY = originalEnv;
    });
  });

  describe('getActiveTokenCount', () => {
    it('should return the correct number of active tokens', () => {
      const initialCount = authService.getActiveTokenCount();

      authService.generateToken('client-1');
      authService.generateToken('client-2');

      const newCount = authService.getActiveTokenCount();
      expect(newCount).toBe(initialCount + 2);
    });
  });
});