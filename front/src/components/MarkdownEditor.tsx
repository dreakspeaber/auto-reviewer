import React from 'react';
import MDEditor from '@uiw/react-md-editor';
import { ScrollArea } from './ui/scroll-area';

interface MarkdownEditorProps {
  value: string;
  onChange: (value: string | undefined) => void;
  placeholder?: string;
  className?: string;
}

const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  placeholder = "Enter your markdown content here...",
  className = ""
}) => {
  return (
    <div className={`h-full ${className}`} data-color-mode="light">
      <ScrollArea className="h-full">
        <MDEditor
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          preview="edit"
          height="100%"
          style={{
            border: 'none',
            backgroundColor: 'transparent'
          }}
        />
      </ScrollArea>
    </div>
  );
};

export default MarkdownEditor;
