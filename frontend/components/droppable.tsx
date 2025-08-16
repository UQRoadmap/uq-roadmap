import React from 'react';
import {useDroppable} from '@dnd-kit/core';

export default function Droppable({id, children}: {id: string, children: React.ReactNode}) {
  const {isOver, setNodeRef} = useDroppable({
    id: id,
  });
  const style = {
    color: isOver ? 'green' : 'red',
  };


  return (
    <div key={id} ref={setNodeRef} style={style}>
      {children}
    </div>
  );
}
