"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

// Infer the ThemeProvider props directly from the NextThemesProvider component
type ThemeProviderProps = React.ComponentProps<typeof NextThemesProvider>;

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
