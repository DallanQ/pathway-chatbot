"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Settings, Sun, Moon, Monitor, HelpCircle } from "lucide-react";
import { Button } from "./ui/button";

export function MobileSettings() {
  const [isOpen, setIsOpen] = React.useState(false);
  const [isRotating, setIsRotating] = React.useState(false);
  const { theme, setTheme } = useTheme();
  const hints = "https://missionaries.prod.byu-pathway.psdops.com/How-to-use-the-Missionary-Assistant";

  const handleToggle = () => {
    setIsRotating(true);
    setIsOpen(!isOpen);
    setTimeout(() => setIsRotating(false), 300);
  };

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
  };

  // Close dialog when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (isOpen && !target.closest('.mobile-settings-container')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="sm:hidden mobile-settings-container relative flex items-center">
      {/* Settings Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={handleToggle}
        className="hover:bg-transparent p-0 h-auto"
      >
        <Settings 
          className={`h-5 w-5 text-[#646362] transition-transform duration-300 ${isRotating ? 'rotate-90' : ''}`} 
        />
      </Button>

      {/* Dropdown Dialog */}
      {isOpen && (
        <div 
          className="absolute right-0 top-8 bg-white dark:bg-[#1a1a1a] rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2.5 w-40 z-[9999] pointer-events-auto animate-in fade-in slide-in-from-top-2 duration-200"
          onClick={(e) => e.stopPropagation()}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {/* Theme Section */}
          <div className="pb-2.5 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-[10px] font-semibold text-gray-900 dark:text-white mb-1.5">Theme</h3>
            <div className="flex items-center gap-1">
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleThemeChange("light");
                }}
                className={`h-7 w-7 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${theme === "light" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
                title="Light"
              >
                <Sun className="h-3.5 w-3.5 text-gray-700 dark:text-gray-300" />
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleThemeChange("dark");
                }}
                className={`h-7 w-7 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${theme === "dark" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
                title="Dark"
              >
                <Moon className="h-3.5 w-3.5 text-gray-700 dark:text-gray-300" />
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleThemeChange("system");
                }}
                className={`h-7 w-7 rounded-lg flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ${theme === "system" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
                title="System"
              >
                <Monitor className="h-3.5 w-3.5 text-gray-700 dark:text-gray-300" />
              </button>
            </div>
          </div>

          {/* Help Link */}
          <div className="pt-2.5">
            <a 
              href={hints} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <HelpCircle className="h-3.5 w-3.5" />
              <span>Help</span>
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
