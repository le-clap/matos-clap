// import {React, useState} from "react";

import {InputGroup, InputGroupAddon, InputGroupInput} from "@/components/ui/input-group.tsx";
import {Search} from "lucide-react";
// import {Input} from "@/components/ui/input"

const FilterBar = () => {

  return (
    <div>
      <InputGroup>
        <InputGroupInput placeholder="Filtres (WIP)"/>
        <InputGroupAddon>
          <Search/>
        </InputGroupAddon>
      </InputGroup>
    </div>
  )
}

export default FilterBar;