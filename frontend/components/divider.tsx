import clsx from 'clsx'

export function Divider({
  soft = false,
  className,
  ...props
}: { soft?: boolean } & React.ComponentPropsWithoutRef<'hr'>) {
  return (
    <hr
      role="presentation"
      {...props}
      className={clsx(
        className,
        'w-full border-t',
        soft && 'border-zinc-950/5 border-white/5',
        !soft && 'border-zinc-950/10 border-white/10'
      )}
    />
  )
}
