"use client"

import {Checkbox} from "@/components/ui/checkbox"
import {
  Field,
  // FieldContent,
  // FieldDescription,
  FieldGroup,
  // FieldLabel,
  // FieldTitle,
} from "@/components/ui/field"
import {Label} from "@/components/ui/label"
import type {CategoryPublic} from "@/client";
import type {FC} from "react";

export interface FiltersProps {
  categories: CategoryPublic[] | undefined;
  selectedCategories: Set<number>;
  onChange: (categoryId: number) => void;
}

const FilterCategory: FC<FiltersProps> = ({
                                            categories,
                                            selectedCategories,
                                            onChange
                                          }) => {

  return (
    <FieldGroup className="max-w-sm gap-3">
      {categories?.map((category: CategoryPublic) => {
        return (
          <Field key={category.id} orientation="horizontal">
            <Checkbox name={category.name}
                      checked={selectedCategories.has(category.id)}
                      onCheckedChange={() => onChange(category.id)}
            />
            <Label htmlFor={category.name}>{category.name}</Label>
          </Field>
        )
      })}
    </FieldGroup>
  )
}

export default FilterCategory;
