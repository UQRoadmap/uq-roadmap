"use client"

import { Field, Label } from '@/components/fieldset'
import { Combobox, ComboboxLabel, ComboboxOption } from '@/components/combobox'

interface BetterDropdownProps<T> {
    label: string
    options: T[]
    value: T | undefined
    onChange: (value: T) => void
    displayValue: (item: T | null) => string
    id?: string
    isEnabled: boolean
}

export default function BetterDropdown<T>({
    label,
    options,
    value,
    onChange,
    displayValue,
    id,
    isEnabled
}: BetterDropdownProps<T>) {
    return (
        <Field disabled={!isEnabled}>
            <Label htmlFor={id}>{label}</Label>
            <Combobox
                name={id}
                options={options}
                displayValue={displayValue}
                aria-label={label}
                value={value}
                onChange={onChange}
            >
                {item => (
                    <ComboboxOption key={displayValue(item)} value={item}>
                        <ComboboxLabel>{displayValue(item)}</ComboboxLabel>
                    </ComboboxOption>
                )}
            </Combobox>
        </Field>
    )
}