export interface TokenPayload {
  clientId: string;
  timestamp: number;
  expiryTimestamp: number;
}

export interface TokenData {
  payload: TokenPayload;
  hash: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: string;
  scope: string[];
}

export interface ErrorResponse {
  error: string;
  details?: string;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  payloads: {
    pf: boolean;
    pj: boolean;
  };
  activeTokens: number;
}

export interface ReportRequest {
  documentId: string;
  reportName: string;
}