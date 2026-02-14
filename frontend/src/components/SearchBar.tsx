// import {React, useState} from "react";

import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"

import {Search} from "lucide-react";
import {useState} from "react";
import {number} from "motion";

const SearchBar = () => {

  const [search, setSearch] = useState<string>("");
  const [array, setArray] = useState<Array<string>>([]);

  const debounce = (func, delay:number) => {
    return (...args) => {
      let timeoutId:number
      timeoutId = setTimeout(() => func(...args), delay)
    }
  }

  return (
    <div>
        <InputGroup >
          <InputGroupInput placeholder="Rechercher..."
          onChange={(e) => setSearch(e.target.value)}
          />
          <InputGroupAddon>
            <Search />
          </InputGroupAddon>
          <InputGroupAddon align="inline-end">2 Résultats</InputGroupAddon>
        </InputGroup>
    </div>
  )
}

export default SearchBar;