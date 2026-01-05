import React from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

/**
 * FluidButton - Matte & Cohesive Edition.
 * 
 * Features:
 * - DEEP MATTE PURPLE/INDIGO to match app identity.
 * - No gradients, just solid, rich color logic.
 * - Elegant bevel/inner-shadow for depth.
 */
const FluidButton = React.forwardRef(({ className, children, onClick, disabled, type = "button", ...props }, ref) => {

    // Non-blocking interaction handler
    const handleClick = (e) => {
        if (disabled) return;
        if (onClick) {
            requestAnimationFrame(() => onClick(e));
        }
    };

    return (
        <motion.button
            ref={ref}
            type={type}
            disabled={disabled}
            className={cn(
                "relative inline-flex items-center justify-center whitespace-nowrap rounded-xl text-base font-semibold transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
                // Base: Deep Indigo/Violet (Matte, not Neon)
                // Using Slate-900 mixed with Violet-900 for that premium "Obsidian" look
                "bg-[#1a1a2e] border border-[#2d2d44] text-indigo-100",

                // Hover: Subtle lift in lightness
                "hover:bg-[#20203a] hover:border-[#3d3d5c]",

                // Shadow: Deep colored shadow for richness without glow
                "shadow-[0_4px_20px_-8px_rgba(79,70,229,0.5)]",

                // Active: Physical press feeling
                "active:scale-[0.98]",
                className
            )}
            style={{
                WebkitTapHighlightColor: "transparent",
            }}
            whileHover={{
                scale: 1.01,
                transition: { type: "spring", stiffness: 400, damping: 20 }
            }}
            whileTap={{
                scale: 0.96,
                transition: { type: "spring", stiffness: 500, damping: 15 }
            }}
            onClick={handleClick}
            {...props}
        >
            {/* Subtle Inner Bevel (Top) for tactile matte feel */}
            <div className="absolute inset-x-0 top-0 h-[1px] bg-white/10 opacity-50 rounded-t-xl" />

            {/* Subtle Bottom Refection (Glassy Matte) */}
            <div className="absolute inset-x-0 bottom-0 h-[1px] bg-black/40 opacity-50 rounded-b-xl" />

            <span className="relative z-10 flex items-center justify-center gap-2 tracking-wide font-medium">
                {children}
            </span>
        </motion.button>
    );
});

FluidButton.displayName = "FluidButton";

export { FluidButton };
