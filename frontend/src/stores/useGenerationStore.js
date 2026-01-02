import { create } from 'zustand';
import { generateBatch, getStatus, getFiles, getModels } from '../lib/api';

const useGenerationStore = create((set, get) => ({
    // Configuration state
    config: {
        qty: 3,
        genders: ['any'],
        ethnicities: ['any'],
        origins: ['any'],
        roles: ['any'],  // Changed to 'any' for quick testing
        age_min: 25,
        age_max: 35,
        expertise_levels: ['any'],  // Changed to 'any' for quick testing
        remote: false,
        llm_model: null,
        image_model: null,
    },

    // Available models
    llmModels: [],
    imageModels: [],
    modelsLoaded: false,

    // Generation state
    isGenerating: false,
    currentBatch: null,
    tasks: [],
    pollInterval: null,

    // Files state
    files: [],
    isLoadingFiles: false,

    // Error state
    error: null,

    // Load available models
    loadModels: async () => {
        try {
            const response = await getModels();
            set({
                llmModels: response.llm_models || [],
                imageModels: response.image_models || [],
                modelsLoaded: true,
            });

            // Set default models if not already set
            const { config } = get();
            if (!config.llm_model && response.llm_models?.length > 0) {
                set((state) => ({
                    config: { ...state.config, llm_model: response.llm_models[0].id }
                }));
            }
            if (!config.image_model && response.image_models?.length > 0) {
                set((state) => ({
                    config: { ...state.config, image_model: response.image_models[0].id }
                }));
            }
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    },

    // Actions
    setConfig: (key, value) => {
        set((state) => ({
            config: { ...state.config, [key]: value },
        }));
    },

    addRole: (role) => {
        set((state) => ({
            config: {
                ...state.config,
                roles: [...state.config.roles, role]
            }
        }));
    },

    removeRole: (index) => {
        set((state) => ({
            config: {
                ...state.config,
                roles: state.config.roles.filter((_, i) => i !== index)
            }
        }));
    },

    startGeneration: async () => {
        const { config } = get();

        // Convert age_min/age_max to age range format
        const ageRange = `${config.age_min}-${config.age_max}`;

        // Build request
        const request = {
            ...config,
            ages: [ageRange],  // Convert to array for backend
            roles: config.roles.length > 0 ? config.roles : ['Software Developer'] // Default if empty
        };

        set({ isGenerating: true, error: null, tasks: [] });

        try {
            const response = await generateBatch(request);
            set({ currentBatch: response.batch_id });

            // Start polling for status
            const interval = setInterval(async () => {
                try {
                    const status = await getStatus();
                    set({ tasks: status.tasks || [] });

                    // Stop polling when complete
                    if (status.is_complete) {
                        clearInterval(get().pollInterval);
                        set({ isGenerating: false, pollInterval: null });
                        // Refresh files list
                        get().loadFiles();
                    }
                } catch (error) {
                    console.error('Status poll error:', error);
                }
            }, 2000);

            set({ pollInterval: interval });
        } catch (error) {
            set({
                isGenerating: false,
                error: error.message || 'Failed to start generation',
            });
        }
    },

    stopGeneration: () => {
        const { pollInterval } = get();
        if (pollInterval) {
            clearInterval(pollInterval);
        }
        set({ isGenerating: false, pollInterval: null });
    },

    loadFiles: async () => {
        set({ isLoadingFiles: true });
        try {
            const response = await getFiles();
            set({ files: response.files || [], isLoadingFiles: false });
        } catch (error) {
            set({ isLoadingFiles: false, error: error.message });
        }
    },

    clearError: () => set({ error: null }),
}));

export default useGenerationStore;
