"use client"

import {useState, useMemo} from "react";

import {useCatalog} from "@/hooks/useCatalog.ts";
import {useCategories} from "@/hooks/useCategory.ts";
import {useDebounce} from "@/hooks/useDebounce.ts";

import CatalogGrid from "@/components/CatalogGrid.tsx";
import FilterCategory from "@/components/FilterCategory.tsx";
import SearchBar from "@/components/SearchBar.tsx";

import {Calendar} from "@/components/ui/calendar.tsx";
import {addDays} from "date-fns"
import {type DateRange} from "react-day-picker"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const Inventory = () => {

    const {data: allItems, isLoading, error} = useCatalog();

    const [searchQuery, setSearch] = useState<string>("");
    const debouncedQuery = useDebounce(searchQuery, 150);

    const {data: allCategories} = useCategories();

    const [selectedCategories, setSelectedCategories] = useState<Set<number>>(new Set());
    const debouncedCategories = useDebounce(selectedCategories, 100);

    const [dateRange, setDateRange] = useState<DateRange | undefined>({
      from: new Date(new Date().getFullYear(), 0, 12),
      to: addDays(new Date(new Date().getFullYear(), 0, 12), 30),
    })

    const handleCheckboxChange = (categoryId: number) => {
      setSelectedCategories((prevSet) => {
        const newSet = new Set(prevSet);
        if (newSet.has(categoryId)) {
          newSet.delete(categoryId);
        } else {
          newSet.add(categoryId);
        }
        return newSet;
      });
    };

    const filteredData = useMemo(() => {
      if (!allItems) return [];
      return allItems.filter(item =>
        (
          debouncedCategories.size == 0 || debouncedCategories.has(item.category.id)
        ) &&
        (
          item.name.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
          item.description?.toLowerCase().includes(debouncedQuery.toLowerCase())
        )
      );
    }, [allItems, debouncedQuery, debouncedCategories]);

    return (
      // Padding TOP pour rester en dessous du menu (à voir si on encapsule le menu dans header pour éviter d'avoir à faire ça)
      <div className="min-h-screen mt-20 md:mt-25 px-4 mb-20">

        <div className="md:max-w-350 mx-auto">
          <h1 className="text-4xl font-heading mb-6 pb-2 border-b border-teal-900 dark:border-primary">Inventaire</h1>

          <div className="inventory-container flex flex-col gap-3">
            <div className="search-bar pb-3 rounded-lg">
              <SearchBar matchCount={filteredData.length} value={searchQuery} onChange={setSearch}/>
            </div>
            <div className="grid-filters-container flex flex-row items-start gap-3 h-180 w-full">
              <div className="filters flex flex-col w-70 shrink-0 p-4 rounded-t-lg gap-2 items-start h-180">

                <h2 className="font-heading text-2xl">Trier par...</h2>

                <Accordion type="single" collapsible className="border-b border-primary w-full">
                  <AccordionItem value="FilterCategory">
                    <AccordionTrigger>Catégorie</AccordionTrigger>
                    <AccordionContent>
                      <FilterCategory categories={allCategories} selectedCategories={selectedCategories}
                                      onChange={handleCheckboxChange}/>
                    </AccordionContent>
                  </AccordionItem>

                  <AccordionItem value="Calendar">
                    <AccordionTrigger>Date de disponibilité</AccordionTrigger>
                    <AccordionContent>
                      <Calendar
                        mode="range"
                        className="rounded-lg"
                        captionLayout="label"
                        selected={dateRange}
                        onSelect={setDateRange}
                      />
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>

              </div>
              <div className="catalog-grid h-180 pr-4 overflow-y-auto">
                <CatalogGrid
                  items={filteredData}
                  isLoading={isLoading}
                  error={error}
                />
              </div>
            </div>
          </div>

        </div>

      </div>
    )
      ;
  }
;

export default Inventory;
