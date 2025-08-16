"use client"

import { Field, Label } from '@/components/fieldset'
import { Select } from '@/components/select'

export default function MajorSelect({name, options, disabled, setter}: {name: string, options: number[], disabled?: boolean, setter: (value: number | null) => void}) {
  const shouldHaveNoneOption = name === "Majors" || name === "Minors";
  
  return (
    <Field disabled={disabled}>
        <Label>{name}</Label>
        <Select
            name={name}
            onChange={(e) => {
              if (e.target.value === "none") {
                setter(null);
              } else {
                setter(+e.target.value);
              }
            }}
            defaultValue={shouldHaveNoneOption ? "none" : options[0] || ""}
        >
          {shouldHaveNoneOption && (
            <option value="none">None</option>
          )}
          {options?.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </Select>
    </Field>
  )
}
