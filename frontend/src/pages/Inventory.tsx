"use client"

import {useState} from "react";

import {useCatalog} from "@/hooks/useCatalog.ts";

import CatalogGrid from "@/components/CatalogGrid.tsx";
import FilterBar from "@/components/FilterBar.tsx";
import Filters from "@/components/Filters.tsx";
import SearchBar from "@/components/SearchBar.tsx";

import {Calendar} from "@/components/ui/calendar.tsx";
import { addDays } from "date-fns"
import { type DateRange } from "react-day-picker"

const Inventory = () => {

    const {data: allItems, isLoading} = useCatalog();
    const [dateRange, setDateRange] = useState<DateRange | undefined>({
      from: new Date(new Date().getFullYear(), 0, 12),
      to: addDays(new Date(new Date().getFullYear(), 0, 12), 30),
    })
    return (
      // Padding TOP pour rester en dessous du menu (à voir si on encapsule le menu dans header pour éviter d'avoir à faire ça)
      <div className="min-h-screen mt-20 px-4 md:px-8 pb-20">

        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-heading mb-6 pb-2 border-b border-teal-900 dark:border-primary">Inventaire</h1>

          <div className="inventory-container flex flex-col gap-3">
            <div className="filter-bar p-4 flex justify-between rounded-lg bg-secondary gap-4">
              <div className="flex-1"><SearchBar/></div>
              <div className="flex-2"><FilterBar/></div>
            </div>
            <div className="grid-filters-container flex flex-row gap-3">
              <div className="filters flex-1 bg-secondary p-4 rounded-lg flex flex-col items-start gap-3">
                <Filters/>
                <Calendar
                  mode="range"
                  className="rounded-lg border min-w-3xs"
                  captionLayout="label"
                  selected={dateRange}
                  onSelect={setDateRange}
                />
              </div>
              <div className="catalog-grid flex flex-6 rounded-lg">
                <CatalogGrid
                  items={allItems}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </div>

        </div>

      </div>
    );
  }
;

export default Inventory;