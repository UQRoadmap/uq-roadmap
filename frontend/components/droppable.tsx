import React from 'react';
import {useDroppable} from '@dnd-kit/core';

export default function Droppable({id, children, full}: {id: string, children: React.ReactNode, full?: boolean}) {
  const {isOver, setNodeRef} = useDroppable({
    id: id,
    data: {full: full}
  });
  const style = {
    backgroundColor: isOver ? 'rgba(156,163,175,0.9)' : 'rgba(156,163,175,0.2)',
  };


  return (
    <div key={id} ref={setNodeRef} style={style}>
      {children}
    </div>
  );
}
