import {X} from "lucide-react";
import {useState} from "react";
import type {UserBrief} from "@/client";
import {Avatar} from "@/components/ui/Avatar";
import {SearchInput} from "@/components/ui/SearchInput";
import {useDebounce} from "@/hooks/useDebounce";
import {useUsers} from "@/hooks/useUsers";

const RESULTS_LIMIT = 8;

/**
 * Search-and-pick a single user.
 * Queries the paginated /users endpoint server-side.
 */
export function UserCombobox({
                                 value,
                                 onChange,
                                 placeholder = "Rechercher un membre…",
                             }: {
    value: UserBrief | null;
    onChange: (user: UserBrief | null) => void;
    placeholder?: string;
}) {
    const [search, setSearch] = useState("");
    const debouncedSearch = useDebounce(search);
    const query = debouncedSearch.trim();

    const {data, isFetching} = useUsers(
        {search: query, limit: RESULTS_LIMIT},
        query.length > 0,
    );
    const matches = data?.items ?? [];

    if (value) {
        return (
            <div className="flex items-center gap-2.5 rounded-lg border border-border bg-surface py-1.5 pl-2.5 pr-2">
                <Avatar name={value.name} size="sm"/>
                <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{value.name}</p>
                    <p className="truncate text-xs text-content-faint">{value.username}</p>
                </div>
                <button
                    type="button"
                    onClick={() => {
                        setSearch("");
                        onChange(null);
                    }}
                    className="shrink-0 rounded-md p-1.5 text-content-faint transition-colors hover:text-content"
                    aria-label="Changer de membre"
                >
                    <X className="size-4"/>
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-2">
            <SearchInput value={search} onChange={setSearch} placeholder={placeholder}/>

            {query && (
                <div className="flex flex-col gap-1 rounded-lg border border-border p-1.5">
                    {matches.length === 0 ? (
                        <p className="px-2 py-1.5 text-sm text-content-faint">
                            {isFetching ? "Recherche…" : "Aucun membre trouvé."}
                        </p>
                    ) : (
                        matches.map((u) => (
                            <button
                                key={u.id}
                                type="button"
                                onClick={() => {
                                    onChange(u);
                                    setSearch("");
                                }}
                                className="flex items-center gap-2.5 rounded-md p-2 text-left transition-colors hover:bg-surface-raised"
                            >
                                <Avatar name={u.name} size="sm"/>
                                <div className="min-w-0 flex-1">
                                    <p className="truncate text-sm font-medium">{u.name}</p>
                                    <p className="truncate text-xs text-content-faint">{u.username}</p>
                                </div>
                            </button>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
