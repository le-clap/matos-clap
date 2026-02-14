import React, {createContext, useContext, useEffect, useState, useSyncExternalStore} from "react"

type Theme = "dark" | "light" | "system"

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const initialState: ThemeProviderState = {
  theme: "system",
  setTheme: () => null,
}

const preferredTheme = (): Theme => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? "dark" : "light";
}

const subscribeTheme = (callback) => {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', callback);
  return () => {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', callback);
  };
}

const ThemeProviderContext = createContext<ThemeProviderState>(initialState)

export function ThemeProvider({
                                children,
                                defaultTheme = "system",
                                storageKey = "vite-ui-theme",
                                ...props
                              }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  )

  const systemTheme = useSyncExternalStore(subscribeTheme, preferredTheme)


  useEffect(() => {
      const root = window.document.documentElement

      root.classList.remove("light", "dark")

      if (theme === "system") {
        root.classList.add(systemTheme)
        return
      }

      root.classList.add(theme)
    }

    ,[theme, systemTheme]
  )


  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider")

  return context
}