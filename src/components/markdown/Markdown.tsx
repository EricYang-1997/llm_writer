// components/Markdown/Markdown.tsx
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'highlight.js/styles/default.css';
import './Markdown.css'; // 样式文件

const Markdown: React.FC = () => {
  const [markdownContent, setMarkdownContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadMarkdown();
  }, []);

  const loadMarkdown = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/public/content.md');
      if (!response.ok) {
        throw new Error(`Failed to load markdown: ${response.status}`);
      }
      const text = await response.text();
      setMarkdownContent(text);
      setEditContent(text);
      setError(null);
    } catch (err) {
      console.error('Failed to load markdown:', err);
      setError('加载内容失败');
      setMarkdownContent('# 加载失败\n\n无法加载内容，请稍后重试。');
      setEditContent('# 加载失败\n\n无法加载内容，请稍后重试。');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    setEditContent(markdownContent);
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      // 假保存：更新本地状态
      setMarkdownContent(editContent);
      
      // 这里可以添加实际的保存逻辑（如发送到服务器）
      // 模拟保存操作
      console.log('保存内容到服务器:', editContent);
      
      setIsEditing(false);
    } catch (err) {
      console.error('保存失败:', err);
      setError('保存失败');
    }
  };

  const handleCancel = () => {
    setEditContent(markdownContent);
    setIsEditing(false);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditContent(e.target.value);
  };

  if (isLoading) {
    return <div className="markdown-loading">加载中...</div>;
  }

  if (error) {
    return <div className="markdown-error">{error}</div>;
  }

  // 编辑模式下的渲染
  if (isEditing) {
    return (
      <div className="markdown-editor-container">
        <div className="markdown-editor">
          <textarea
            ref={textareaRef}
            value={editContent}
            onChange={handleContentChange}
            className="markdown-textarea"
            placeholder="输入 Markdown 内容..."
            rows={20}
          />
          <div className="editor-controls">
            <button onClick={handleSave} className="save-btn">保存</button>
            <button onClick={handleCancel} className="cancel-btn">取消</button>
          </div>
        </div>
      </div>
    );
  }

  // 预览模式下的渲染
  return (
    <div className="markdown-container">
      <div className="markdown-controls">
        <button onClick={handleEdit} className="edit-btn">编辑</button>
      </div>
      <div className="markdown-content">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight, rehypeRaw]}
          components={{
            // 自定义组件渲染
            h1: ({ node, ...props }) => <h1 style={{ color: '#333', marginTop: '24px' }} {...props} />,
            h2: ({ node, ...props }) => <h2 style={{ color: '#444', marginTop: '20px' }} {...props} />,
            h3: ({ node, ...props }) => <h3 style={{ color: '#555', marginTop: '16px' }} {...props} />,
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <pre className={className} {...props}>
                  <code>{children}</code>
                </pre>
              ) : (
                <code className={className} {...props}>{children}</code>
              );
            },
            a: ({ node, ...props }) => <a target="_blank" rel="noopener noreferrer" {...props} />,
          }}
        >
          {markdownContent}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default Markdown;