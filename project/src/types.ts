export interface EmailRequest {
  query: string;
}

export interface ApprovalRequest {
  toolName: string;
  args: Record<string, any>;
}

export interface EmailResponse {
  requiresApproval: boolean;
  toolName?: string;
  args?: Record<string, any>;
  result?: string;
  error?: string;
}