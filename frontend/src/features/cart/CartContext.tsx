import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

export interface CartLine {
  catalogId: number;
  name: string;
  imagePath?: string | null;
  quantity: number;
}

interface CartContextValue {
  lines: CartLine[];
  count: number;
  add: (line: Omit<CartLine, 'quantity'>, quantity?: number) => void;
  setQuantity: (catalogId: number, quantity: number) => void;
  remove: (catalogId: number) => void;
  clear: () => void;
  has: (catalogId: number) => boolean;
}

const CartContext = createContext<CartContextValue | null>(null);
const STORAGE_KEY = 'matos-clap.cart';

function load(): CartLine[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as CartLine[]) : [];
  } catch {
    return [];
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>(load);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lines));
  }, [lines]);

  const add = useCallback((line: Omit<CartLine, 'quantity'>, quantity = 1) => {
    setLines((prev) => {
      const existing = prev.find((l) => l.catalogId === line.catalogId);
      if (existing) {
        return prev.map((l) =>
          l.catalogId === line.catalogId ? { ...l, quantity: l.quantity + quantity } : l,
        );
      }
      return [...prev, { ...line, quantity }];
    });
  }, []);

  const setQuantity = useCallback((catalogId: number, quantity: number) => {
    setLines((prev) =>
      quantity <= 0
        ? prev.filter((l) => l.catalogId !== catalogId)
        : prev.map((l) => (l.catalogId === catalogId ? { ...l, quantity } : l)),
    );
  }, []);

  const remove = useCallback((catalogId: number) => {
    setLines((prev) => prev.filter((l) => l.catalogId !== catalogId));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const value = useMemo<CartContextValue>(
    () => ({
      lines,
      count: lines.reduce((sum, l) => sum + l.quantity, 0),
      add,
      setQuantity,
      remove,
      clear,
      has: (catalogId) => lines.some((l) => l.catalogId === catalogId),
    }),
    [lines, add, setQuantity, remove, clear],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error('useCart must be used within CartProvider');
  return ctx;
}
