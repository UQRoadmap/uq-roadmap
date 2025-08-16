import React from 'react';
import {useDraggable} from '@dnd-kit/core';
import type { ReactNode } from 'react';
import { Course } from '@/types/course'

type DraggableProps = {
  id: string;
  children: ReactNode;
  data: Course; // or `Course` if you always pass course objects
};

export default function Draggable(props:DraggableProps) {
  const {attributes, listeners, setNodeRef} = useDraggable({
    id: props.id,
    data: props.data,
  });

  return (
    <div ref={setNodeRef} {...listeners} {...attributes}>
      {props.children}
    </div>
  );
}
