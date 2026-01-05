import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Github, Linkedin, ExternalLink, Code, Heart, Sparkles } from 'lucide-react';
import { Button } from './ui/Button';

const backdropVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { duration: 0.2 }
    },
    exit: {
        opacity: 0,
        transition: { duration: 0.2, delay: 0.1 }
    }
};

const modalVariants = {
    hidden: {
        opacity: 0,
        scale: 0.8,
        y: 50,
        rotateX: -15
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        rotateX: 0,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 25,
            delay: 0.1
        }
    },
    exit: {
        opacity: 0,
        scale: 0.9,
        y: 30,
        transition: { duration: 0.2 }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
        opacity: 1,
        y: 0,
        transition: {
            delay: 0.2 + i * 0.1,
            type: "spring",
            stiffness: 300,
            damping: 20
        }
    })
};

export function AboutModal({ onClose }) {
    return (
        <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
            variants={backdropVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={onClose}
        >
            <motion.div
                className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden relative"
                variants={modalVariants}
                onClick={(e) => e.stopPropagation()}
                style={{ perspective: 1000 }}
            >
                {/* Decorative Background Header */}
                <motion.div
                    className="h-32 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 relative overflow-hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                >
                    {/* Animated particles */}
                    <div className="absolute inset-0">
                        {[...Array(6)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute w-2 h-2 bg-white/30 rounded-full"
                                style={{
                                    left: `${15 + i * 15}%`,
                                    top: `${20 + (i % 3) * 25}%`
                                }}
                                animate={{
                                    y: [0, -20, 0],
                                    opacity: [0.3, 0.6, 0.3],
                                    scale: [1, 1.2, 1]
                                }}
                                transition={{
                                    duration: 2 + i * 0.3,
                                    repeat: Infinity,
                                    delay: i * 0.2
                                }}
                            />
                        ))}
                    </div>

                    <div className="absolute inset-0 bg-black/10"></div>

                    {/* Avatar */}
                    <motion.div
                        className="absolute -bottom-10 left-1/2 transform -translate-x-1/2"
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{
                            type: "spring",
                            stiffness: 200,
                            damping: 15,
                            delay: 0.3
                        }}
                    >
                        <motion.div
                            className="w-24 h-24 rounded-full border-4 border-card bg-zinc-800 flex items-center justify-center shadow-lg"
                            whileHover={{ scale: 1.1, rotate: 5 }}
                            transition={{ type: "spring", stiffness: 400 }}
                        >
                            <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">RI</span>
                        </motion.div>
                    </motion.div>

                    {/* Close Button */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <Button
                            variant="ghost"
                            size="icon"
                            className="absolute right-4 top-4 text-white/80 hover:text-white hover:bg-white/10"
                            onClick={onClose}
                        >
                            <X className="w-5 h-5" />
                        </Button>
                    </motion.div>
                </motion.div>

                <div className="pt-14 pb-8 px-6 text-center">
                    <motion.h2
                        className="text-2xl font-bold"
                        custom={0}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        Raul Iglesias
                    </motion.h2>

                    <motion.p
                        className="text-muted-foreground text-sm mb-6"
                        custom={1}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        Full Stack Developer & AI Enthusiast
                    </motion.p>

                    <motion.p
                        className="text-sm text-muted-foreground/80 mb-8 leading-relaxed"
                        custom={2}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        Creator of the <span className="text-primary font-semibold">AI CV Suite</span>.
                        Passionate about building tools that bridge the gap between creative potential and practical utility using the latest in Generative AI.
                    </motion.p>

                    {/* Social Links */}
                    <motion.div
                        className="grid grid-cols-2 gap-4 mb-8"
                        custom={3}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        <motion.a
                            href="https://github.com/RaulJuliosIglesias"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex flex-col items-center justify-center p-4 rounded-xl bg-secondary/30 hover:bg-secondary/60 border border-border/50 transition-colors group"
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Github className="w-6 h-6 mb-2 text-foreground group-hover:text-primary transition-colors" />
                            <span className="text-sm font-medium">GitHub</span>
                        </motion.a>
                        <motion.a
                            href="https://www.linkedin.com/in/rauliglesiasjulios/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex flex-col items-center justify-center p-4 rounded-xl bg-secondary/30 hover:bg-secondary/60 border border-border/50 transition-colors group"
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <Linkedin className="w-6 h-6 mb-2 text-foreground group-hover:text-blue-400 transition-colors" />
                            <span className="text-sm font-medium">LinkedIn</span>
                        </motion.a>
                    </motion.div>

                    {/* Footer */}
                    <motion.div
                        className="flex items-center justify-center gap-2 text-xs text-muted-foreground"
                        custom={4}
                        variants={itemVariants}
                        initial="hidden"
                        animate="visible"
                    >
                        <Code className="w-3 h-3" />
                        <span>Built with React, Python & AI</span>
                        <motion.div
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 1, repeat: Infinity }}
                        >
                            <Heart className="w-3 h-3 text-red-500 fill-red-500" />
                        </motion.div>
                    </motion.div>
                </div>
            </motion.div>
        </motion.div>
    );
}
