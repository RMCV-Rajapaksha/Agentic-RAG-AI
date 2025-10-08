import React, { useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Bot, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { GOOGLE_CLIENT_ID } from '@/config/auth';
import type { GoogleCredentialResponse } from '@/types/google';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const googleButtonRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      if (window.google && googleButtonRef.current) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse
        });

        window.google.accounts.id.renderButton(googleButtonRef.current, {
          type: 'standard',
          size: 'large',
          text: 'signin_with',
          shape: 'pill',
          theme: 'outline',
          width: '300'
        });
      }
    };

    document.head.appendChild(script);

    return () => {
      // Cleanup script on unmount
      if (document.head.contains(script)) {
        document.head.removeChild(script);
      }
    };
  }, []);

  const handleCredentialResponse = (response: GoogleCredentialResponse) => {
    login(response.credential);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-xl">
        <div className="text-center space-y-6">
          {/* Logo and Title */}
          <div className="space-y-4">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-blue-500 text-white">
              <Bot className="w-6 h-6" />
              <span className="text-xl font-bold">WSO2 AI Assistant</span>
            </div>
            
            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome Back
              </h1>
              <p className="text-gray-600">
                Please sign in with Google to access the AI assistant
              </p>
            </div>
          </div>

          {/* Security Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-blue-700 mb-2">
              <Shield className="w-4 h-4" />
              <span className="font-medium text-sm">Secure Authentication</span>
            </div>
            <p className="text-blue-600 text-xs">
              Your data is protected. We only access basic profile information.
            </p>
          </div>

          {/* Google Sign-In Button */}
          <div className="space-y-4">
            <div ref={googleButtonRef} className="flex justify-center" />
            
            <div className="text-xs text-gray-500 px-4">
              By signing in, you agree to our terms of service and privacy policy.
            </div>
          </div>

          {/* Features List */}
          <div className="text-left space-y-2 text-sm text-gray-600 border-t pt-4">
            <p className="font-medium text-gray-900 mb-3">What you can do:</p>
            <ul className="space-y-1">
              <li>• Ask questions about WSO2 products</li>
              <li>• Get instant documentation help</li>
              <li>• Access intelligent knowledge base</li>
              <li>• Receive personalized assistance</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
