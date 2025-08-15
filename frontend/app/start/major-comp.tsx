"use client"
import { useState } from "react";

import { Field, Label } from '@/components/fieldset'
import { Select } from '@/components/select'

export default function MajorSelect({name, options, disabled}) {
  return (
    <Field disabled={disabled}>
        <Label>{name}</Label>
        <Select
            name="commencement-date"
        >
          {options?.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
        ))}
        </Select>
    </Field>
  )
}
