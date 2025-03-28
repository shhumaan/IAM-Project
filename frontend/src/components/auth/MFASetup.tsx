import React, { useState, ChangeEvent } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import QRCode from 'qrcode.react';
import { useAuth } from '@/contexts/AuthContext';

const steps = ['Setup MFA', 'Verify Code'];

export default function MFASetup() {
  const { setupMFA, verifyMFA } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [qrCode, setQrCode] = useState<string>('');
  const [secret, setSecret] = useState<string>('');
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSetupMFA = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const { qrCode, secret } = await setupMFA();
      setQrCode(qrCode);
      setSecret(secret);
      setActiveStep(1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to setup MFA');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await verifyMFA(verificationCode);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body1" gutterBottom>
              Scan this QR code with your authenticator app
            </Typography>
            {qrCode ? (
              <Box sx={{ mt: 2 }}>
                <QRCode value={qrCode} size={200} />
                <Typography variant="body2" sx={{ mt: 2 }}>
                  Manual entry code: {secret}
                </Typography>
              </Box>
            ) : (
              <Button
                variant="contained"
                onClick={handleSetupMFA}
                disabled={isLoading}
                sx={{ mt: 2 }}
              >
                {isLoading ? <CircularProgress size={24} /> : 'Setup MFA'}
              </Button>
            )}
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1" gutterBottom>
              Enter the verification code from your authenticator app
            </Typography>
            <TextField
              fullWidth
              margin="normal"
              label="Verification Code"
              value={verificationCode}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setVerificationCode(e.target.value)}
              disabled={isLoading}
            />
            <Button
              variant="contained"
              onClick={handleVerifyCode}
              disabled={isLoading || !verificationCode}
              sx={{ mt: 2 }}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Verify Code'}
            </Button>
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h5" component="h1" gutterBottom>
        Multi-Factor Authentication Setup
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {renderStepContent(activeStep)}
    </Paper>
  );
} 