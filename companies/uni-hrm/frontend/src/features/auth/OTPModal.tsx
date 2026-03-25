import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal, Button, toast } from '@/shared/ui';
import { useVerifyOTP } from './api';

interface OTPModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const OTP_LENGTH = 6;

export function OTPModal({ open, onClose, onSuccess }: OTPModalProps) {
  const { t } = useTranslation();
  const [digits, setDigits] = useState<string[]>(Array(OTP_LENGTH).fill(''));
  const [timer, setTimer] = useState(60);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const verifyOTP = useVerifyOTP();

  useEffect(() => {
    if (!open) return;
    setDigits(Array(OTP_LENGTH).fill(''));
    setTimer(60);
    setTimeout(() => inputRefs.current[0]?.focus(), 50);
  }, [open]);

  useEffect(() => {
    if (!open || timer <= 0) return;
    const interval = setInterval(() => setTimer((prev) => prev - 1), 1000);
    return () => clearInterval(interval);
  }, [open, timer]);

  const handleChange = useCallback(
    (index: number, value: string) => {
      if (!/^\d*$/.test(value)) return;
      const newDigits = [...digits];
      newDigits[index] = value.slice(-1);
      setDigits(newDigits);

      if (value && index < OTP_LENGTH - 1) {
        inputRefs.current[index + 1]?.focus();
      }

      const code = newDigits.join('');
      if (code.length === OTP_LENGTH && newDigits.every((d) => d !== '')) {
        verifyOTP.mutate(
          { code },
          {
            onSuccess: () => {
              toast(t('auth.otpSuccess'), 'success');
              onSuccess();
            },
            onError: () => {
              toast(t('auth.otpError'), 'error');
              setDigits(Array(OTP_LENGTH).fill(''));
              inputRefs.current[0]?.focus();
            },
          },
        );
      }
    },
    [digits, verifyOTP, t, onSuccess],
  );

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={t('auth.otpTitle')} size="sm">
      <p className="mb-6 text-sm text-slate-500">{t('auth.otpDescription')}</p>
      <div className="mb-6 flex justify-center gap-3">
        {digits.map((digit, index) => (
          <input
            key={index}
            ref={(el) => {
              inputRefs.current[index] = el;
            }}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            className="h-12 w-12 rounded-lg border border-slate-300 text-center text-lg font-semibold focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        ))}
      </div>
      <div className="text-center">
        {timer > 0 ? (
          <p className="text-sm text-slate-500">{t('auth.otpResendIn', { seconds: timer })}</p>
        ) : (
          <Button variant="ghost" size="sm" onClick={() => setTimer(60)}>
            {t('auth.otpResend')}
          </Button>
        )}
      </div>
    </Modal>
  );
}
