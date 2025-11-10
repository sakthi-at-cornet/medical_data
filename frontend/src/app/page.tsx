import { ChatInterface } from '@/components/ChatInterface';
import { LeftSidebar } from '@/components/LeftSidebar';
import { RightSidebar } from '@/components/RightSidebar';

export default function Home() {
  return (
    <main className="main-container">
      <LeftSidebar />
      <ChatInterface />
      <RightSidebar />
    </main>
  );
}
