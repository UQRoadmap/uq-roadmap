import * as Headless from '@headlessui/react'
import clsx from 'clsx'
import type React from 'react'

export function SwitchGroup({ className, ...props }: React.ComponentPropsWithoutRef<'div'>) {
  return (
    <div
      data-slot="control"
      {...props}
      className={clsx(
        className,
        // Basic groups
        'space-y-3 **:data-[slot=label]:font-normal',
        // With descriptions
        'has-data-[slot=description]:space-y-6 has-data-[slot=description]:**:data-[slot=label]:font-medium'
      )}
    />
  )
}

export function SwitchField({
  className,
  ...props
}: { className?: string } & Omit<Headless.FieldProps, 'as' | 'className'>) {
  return (
    <Headless.Field
      data-slot="field"
      {...props}
      className={clsx(
        className,
        // Base layout
        'grid grid-cols-[1fr_auto] gap-x-8 gap-y-1 sm:grid-cols-[1fr_auto]',
        // Control layout
        '*:data-[slot=control]:col-start-2 *:data-[slot=control]:self-start sm:*:data-[slot=control]:mt-0.5',
        // Label layout
        '*:data-[slot=label]:col-start-1 *:data-[slot=label]:row-start-1',
        // Description layout
        '*:data-[slot=description]:col-start-1 *:data-[slot=description]:row-start-2',
        // With description
        'has-data-[slot=description]:**:data-[slot=label]:font-medium'
      )}
    />
  )
}        '',

export function Switch({
  className,
  ...props
}: {
  className?: string
} & Omit<Headless.SwitchProps, 'as' | 'className' | 'children'>) {
  return (
    <Headless.Switch
      data-slot="control"
      {...props}
      className={clsx(
        className,
        // Base styles
        'group relative isolate inline-flex h-6 w-10 cursor-default rounded-full p-[3px] sm:h-5 sm:w-8',
        // Transitions
        'transition duration-0 ease-in-out data-changing:duration-200',
        // Outline and background color in forced-colors mode so switch is still visible
        'forced-colors:outline forced-colors:[--switch-bg:Highlight]',
        // Unchecked
        'bg-zinc-200 ring-1 ring-black/5 ring-inset',
        // Checked
        'data-checked:bg-(--switch-bg) data-checked:ring-(--switch-bg-ring)',
        // Focus
        'focus:not-data-focus:outline-hidden data-focus:outline-2 data-focus:outline-offset-2 data-focus:outline-blue-500',
        // Hover
        'data-hover:ring-black/15 data-hover:data-checked:ring-(--switch-bg-ring)',
        // Disabled
        'data-disabled:bg-zinc-200 data-disabled:opacity-50 data-disabled:data-checked:bg-zinc-200 data-disabled:data-checked:ring-black/5',      )}
    >
      <span
        aria-hidden="true"
        className={clsx(
          // Basic layout
          'pointer-events-none relative inline-block size-4.5 rounded-full sm:size-3.5',
          // Transition
          'translate-x-0 transition duration-200 ease-in-out',
          // Invisible border so the switch is still visible in forced-colors mode
          'border border-transparent',
          // Unchecked
          'bg-white shadow-sm ring-1 ring-black/5',
          // Checked
          'group-data-checked:bg-(--switch) group-data-checked:shadow-(--switch-shadow) group-data-checked:ring-(--switch-ring)',
          'group-data-checked:translate-x-4 sm:group-data-checked:translate-x-3',
          // Disabled
          'group-data-checked:group-data-disabled:bg-white group-data-checked:group-data-disabled:shadow-sm group-data-checked:group-data-disabled:ring-black/5'
        )}
      />
    </Headless.Switch>
  )
}
