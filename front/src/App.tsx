import React, { useState } from 'react';
import { Button } from './components/ui/button';
import { ScrollArea } from './components/ui/scroll-area';
import MarkdownEditor from './components/MarkdownEditor';
import YamlRenderer from './components/YamlRenderer';
import { Play } from 'lucide-react';
import axios from 'axios';

function App() {
  const [inputMarkdown, setInputMarkdown] = useState('');
  const [outputYaml, setOutputYaml] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRun = async () => {
    if (!inputMarkdown.trim()) {
      alert('Please enter some content in the input editor');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/review', {
        content: inputMarkdown
      });
      
      setOutputYaml(response.data.reviewed_content);
    } catch (error) {
      console.error('Error calling API:', error);
      setOutputYaml('Error: Could not process the content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-4 h-screen">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-center mb-4">
            <h1 className="text-3xl font-bold text-foreground">Auto Reviewer</h1>
          </div>
          
          {/* Main Content */}
          <div className="flex-1 flex gap-4 h-full">
            {/* Left Markdown Editor */}
            <div className="flex-1 border rounded-lg overflow-hidden bg-card">
              <div className="p-3 border-b bg-muted">
                <h2 className="text-sm font-medium text-muted-foreground">Input Content</h2>
              </div>
              <div className="h-full">
                <MarkdownEditor
                  value={inputMarkdown}
                  onChange={(value) => setInputMarkdown(value || '')}
                  placeholder="Enter your content here for review..."
                  className="h-full h-100%"
                />
              </div>
            </div>

            {/* Center Run Button */}
            <div className="flex items-center justify-center px-4">
              <Button
                onClick={handleRun}
                disabled={isLoading || !inputMarkdown.trim()}
                size="lg"
                className="w-16 h-16 rounded-full"
              >
                <Play className="h-6 w-6" />
              </Button>
            </div>

            {/* Right YAML Renderer */}
            <div className="flex-1 border rounded-lg overflow-hidden bg-card">
              <div className="p-3 border-b bg-muted">
                <h2 className="text-sm font-medium text-muted-foreground">Reviewed Content (YAML)</h2>
              </div>
              <div className="h-full">
                <YamlRenderer
                  value={outputYaml}
                  className="h-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
