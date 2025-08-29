import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { ScrollArea } from './ui/scroll-area';

interface YamlRendererProps {
  value: string;
  className?: string;
}

const YamlRenderer: React.FC<YamlRendererProps> = ({
  value,
  className = ""
}) => {
  return (
    <div className={`h-full ${className}`}>
      <ScrollArea className="h-full">
        <div className="p-4">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm">
            <div className="px-4 py-2 border-b border-blue-200 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-t-lg">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                <span className="ml-2 text-sm font-medium text-blue-800">YAML Output</span>
              </div>
            </div>
            <SyntaxHighlighter
              language="yaml"
              style={oneLight}
              customStyle={{
                margin: 0,
                padding: '1.5rem',
                borderRadius: '0 0 0.5rem 0.5rem',
                fontSize: '0.875rem',
                lineHeight: '1.6',
                backgroundColor: 'transparent',
                border: 'none',
                fontFamily: '"JetBrains Mono", "Fira Code", "Monaco", "Consolas", monospace'
              }}
              showLineNumbers={true}
              wrapLines={true}
              lineNumberStyle={{
                color: '#9ca3af',
                fontSize: '0.75rem',
                paddingRight: '1.5rem',
                minWidth: '3rem',
                fontFamily: '"JetBrains Mono", "Fira Code", "Monaco", "Consolas", monospace'
              }}
              codeTagProps={{
                style: {
                  fontFamily: '"JetBrains Mono", "Fira Code", "Monaco", "Consolas", monospace'
                }
              }}
            >
              {value || '# YAML content will appear here...\n# The evaluation results will be displayed in a beautiful YAML format'}
            </SyntaxHighlighter>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
};

export default YamlRenderer;
