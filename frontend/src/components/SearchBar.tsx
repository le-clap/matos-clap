// import {React, useState} from "react";

import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"

import type {FC} from "react";

import {Search} from "lucide-react";

export type SearchBarProps = {
  setSearch: (search: string) => void;
}

const SearchBar: FC<SearchBarProps> = ({
                                         setSearch
                                       }) => {

  return (
    <div>
      <InputGroup>
        <InputGroupInput placeholder="Rechercher..."
                         onChange={(e) => setSearch(e.target.value)}
        />
        <InputGroupAddon>
          <Search/>
        </InputGroupAddon>
        <InputGroupAddon align="inline-end">2 Résultats</InputGroupAddon>
      </InputGroup>
    </div>
  )
}

export default SearchBar;