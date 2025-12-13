import { X } from "lucide-react";

interface AcmToggleTooltipProps {
  show: boolean;
  isAcmChecked: boolean;
  onClose: () => void;
}

export default function AcmToggleTooltip({
  show,
  isAcmChecked,
  onClose,
}: AcmToggleTooltipProps) {
  if (!show) return null;

  return (
    <div className="absolute bottom-full left-0 min-[860px]:left-1/2 min-[860px]:-translate-x-1/2 mb-3 z-50 animate-fade-slide-up">
      {/* Tooltip container */}
      <div className="relative bg-blue-100 dark:bg-blue-900/50 border border-blue-300 dark:border-blue-600 rounded-xl shadow-lg px-3 py-2 w-[160px] min-[860px]:w-[240px]">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-1.5 right-1.5 h-5 w-5 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors flex items-center justify-center"
          aria-label="Close tooltip"
        >
          <X className="h-3 w-3 text-blue-700 dark:text-blue-300" />
        </button>

        {/* Message content */}
        <p className="text-[11px] sm:text-xs text-gray-900 dark:text-white pr-5 leading-snug">
          Not getting what you&apos;re looking for? Try toggling this{" "}
          <span className="font-semibold text-amber-600 dark:text-[#FFC328]">
            {isAcmChecked ? "OFF" : "ON"}
          </span>
        </p>

        {/* Downward pointing arrow */}
        <div className="absolute top-full left-4 min-[860px]:left-1/2 min-[860px]:-translate-x-1/2 mt-[5px]">
          <div className="w-0 h-0 border-l-[10px] border-l-transparent border-r-[10px] border-r-transparent border-t-[10px] border-t-blue-100 dark:border-t-blue-900/50"></div>
          {/* Border shadow for arrow */}
          <div className="absolute top-[-11px] left-1/2 -translate-x-1/2 w-0 h-0 border-l-[11px] border-l-transparent border-r-[11px] border-r-transparent border-t-[11px] border-t-blue-300 dark:border-t-blue-600 -z-10"></div>
        </div>
      </div>
    </div>
  );
}
