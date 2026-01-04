import React from 'react';
import { X, Github, Linkedin, ExternalLink, Code, Heart } from 'lucide-react';
import { Button } from './ui/Button';

export function AboutModal({ onClose }) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-md overflow-hidden relative animate-in zoom-in-95 duration-200">
                {/* Decorative Background Header */}
                <div className="h-32 bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 relative">
                    <div className="absolute inset-0 bg-black/10"></div>
                    <div className="absolute -bottom-10 left-1/2 transform -translate-x-1/2">
                        <div className="w-24 h-24 rounded-full border-4 border-card bg-zinc-800 flex items-center justify-center shadow-lg">
                            <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">RI</span>
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-4 top-4 text-white/80 hover:text-white hover:bg-white/10"
                        onClick={onClose}
                    >
                        <X className="w-5 h-5" />
                    </Button>
                </div>

                <div className="pt-14 pb-8 px-6 text-center">
                    <h2 className="text-2xl font-bold">Raul Iglesias</h2>
                    <p className="text-muted-foreground text-sm mb-6">Full Stack Developer & AI Enthusiast</p>

                    <p className="text-sm text-muted-foreground/80 mb-8 leading-relaxed">
                        Creator of the <span className="text-primary font-semibold">AI CV Suite</span>.
                        Passionate about building tools that bridge the gap between creative potential and practical utility using the latest in Generative AI.
                    </p>

                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <a
                            href="https://github.com/RaulJuliosIglesias"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex flex-col items-center justify-center p-4 rounded-xl bg-secondary/30 hover:bg-secondary/60 border border-border/50 transition-all hover:scale-105 group"
                        >
                            <Github className="w-6 h-6 mb-2 text-foreground group-hover:text-primary transition-colors" />
                            <span className="text-sm font-medium">GitHub</span>
                        </a>
                        <a
                            href="https://www.linkedin.com/in/rauliglesiasjulios/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex flex-col items-center justify-center p-4 rounded-xl bg-secondary/30 hover:bg-secondary/60 border border-border/50 transition-all hover:scale-105 group"
                        >
                            <Linkedin className="w-6 h-6 mb-2 text-foreground group-hover:text-blue-400 transition-colors" />
                            <span className="text-sm font-medium">LinkedIn</span>
                        </a>
                    </div>

                    <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                        <Code className="w-3 h-3" />
                        <span>Built with React, Python & AI</span>
                        <Heart className="w-3 h-3 text-red-500 fill-red-500" />
                    </div>
                </div>
            </div>
        </div>
    );
}
