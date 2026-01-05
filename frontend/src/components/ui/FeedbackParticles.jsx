import React, { useState, useCallback, useImperativeHandle, forwardRef, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * FeedbackParticles - Long-duration, randomized flow.
 * 
 * - Duration: ~3s
 * - Movement: Random X drift, slow Y rise.
 */
const FeedbackParticles = memo(forwardRef(({ color = "text-emerald-400" }, ref) => {
    const [particles, setParticles] = useState([]);
    const nextId = React.useRef(0);

    const trigger = useCallback((x, y, text = "+1") => {
        const id = nextId.current++;
        // Wider spawn area
        const offsetX = (Math.random() - 0.5) * 60;

        const newParticle = {
            id,
            text,
            // Randomize physics per particle
            randomX: (Math.random() - 0.5) * 100, // Drift left or right
            randomRotate: (Math.random() - 0.5) * 45,
            duration: 2 + Math.random() // Between 2s and 3s
        };

        setParticles(prev => [...prev, newParticle]);

        // Cleanup after 3.5s (allow animation to finish)
        setTimeout(() => {
            setParticles(prev => prev.filter(p => p.id !== id));
        }, 3500);
    }, []);

    useImperativeHandle(ref, () => ({
        trigger
    }));

    return (
        <div className="absolute inset-x-0 bottom-full h-48 pointer-events-none flex justify-center overflow-visible z-50">
            <AnimatePresence mode="popLayout">
                {particles.map((p) => (
                    <motion.div
                        key={p.id}
                        initial={{ opacity: 0, y: 10, scale: 0.8 }}
                        animate={{
                            opacity: [0, 1, 1, 1, 0], // Stay visible longer
                            y: -120 + (Math.random() * -40), // Float higher
                            x: p.randomX,
                            scale: 1,
                            rotate: p.randomRotate
                        }}
                        exit={{ opacity: 0 }}
                        transition={{
                            duration: p.duration,
                            ease: "easeOut",
                            times: [0, 0.1, 0.7, 0.9, 1]
                        }}
                        className={`absolute bottom-0 font-medium text-sm ${color} drop-shadow-sm select-none`}
                        style={{ left: '50%' }}
                    >
                        {p.text}
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
}));

FeedbackParticles.displayName = "FeedbackParticles";

export { FeedbackParticles };
