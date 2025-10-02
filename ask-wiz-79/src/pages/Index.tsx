import ChatInterface from '@/components/ChatInterface';
import LoginPage from '@/components/LoginPage';
import { useAuth } from '@/contexts/AuthContext';

const Index = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-background">
      {isAuthenticated ? <ChatInterface /> : <LoginPage />}
    </div>
  );
};

export default Index;
