// import {React, useState} from "react";

import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"

import {Search} from "lucide-react";
import type {FC} from "react";

export interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  matchCount: number;
}

const SearchBar: FC<SearchBarProps> = ({value, onChange, matchCount}) => {

  return (
    <div>
        <InputGroup>
          <InputGroupInput placeholder="Rechercher..."
                           value={value}
                           onChange={(e) => onChange(e.target.value)}
          />
          <InputGroupAddon>
            <Search />
          </InputGroupAddon>
          {matchCount > 0 && (
          <InputGroupAddon align="inline-end">{matchCount} {matchCount === 1 ? 'élément trouvé' : 'éléments trouvés'}</InputGroupAddon>
          )}
        </InputGroup>
    </div>
  )
}

export default SearchBar;
