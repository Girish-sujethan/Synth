import React from 'react';

export enum TagType {
  ASSIGNEE = 'assignee',
  SENIORITY = 'seniority',
  RISK = 'risk',
  SKILL = 'skill',
}

interface TagChipsProps {
  tags: string[];
  type?: TagType;
  assigneeType?: 'human' | 'ai' | 'unassigned';
  risk?: 'low' | 'medium' | 'high';
  seniority?: string;
}

export const TagChips: React.FC<TagChipsProps> = ({
  tags,
  type,
  assigneeType,
  risk,
  seniority,
}) => {
  const getTagStyle = (tag: string) => {
    const baseStyle = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium';
    
    // Risk tags get red outline
    if (risk && tag.toLowerCase().includes(risk)) {
      return `${baseStyle} border-2 border-red-500 text-red-700 bg-red-50`;
    }
    
    // Seniority tags are bold
    if (seniority && tag.toLowerCase().includes(seniority.toLowerCase())) {
      return `${baseStyle} font-bold bg-blue-100 text-blue-800`;
    }
    
    // Default style
    return `${baseStyle} bg-gray-100 text-gray-800`;
  };

  const getAssigneeIcon = () => {
    if (assigneeType === 'ai') {
      return '🤖';
    }
    if (assigneeType === 'human') {
      return '@';
    }
    return null;
  };

  return (
    <div className="flex flex-wrap gap-2">
      {assigneeType && (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
          {getAssigneeIcon()} {assigneeType}
        </span>
      )}
      {seniority && (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
          {seniority}
        </span>
      )}
      {risk && (
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border-2 border-red-500 text-red-700 bg-red-50`}>
          Risk: {risk}
        </span>
      )}
      {tags.map((tag, index) => (
        <span key={index} className={getTagStyle(tag)}>
          {tag}
        </span>
      ))}
    </div>
  );
};
