import React from 'react';
import {useDraggable} from '@dnd-kit/core';
import type { ReactNode } from 'react';
import { Course } from '@/types/course'

type DraggableProps = {
  id: string;
  children: ReactNode;
  data: Course; // or `Course` if you always pass course objects
  disabled: boolean; // or `Course` if you always pass course objects
};

export default function Draggable(props:DraggableProps) {
  const {attributes, listeners, setNodeRef, isDragging} = useDraggable({
    id: props.id,
    data: props.data,
    disabled: props.disabled,
  });

  return (
<div className="relative">
  {/* Original card */}
  <div
    ref={setNodeRef}
    {...listeners}
    {...attributes}
    style={{ opacity: isDragging ? 0 : 1 }}
  >
    {props.children}
  </div>

  {/* Ghost / shadow */}
  {isDragging && (
    <div className="absolute top-0 left-0 w-full h-full rounded-md border-2 border-dashed border-black-500 pointer-events-none z-0" />
  )}
</div>
  );
}
