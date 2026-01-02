import { create } from 'zustand';
import { generateBatch, getStatus, getFiles, getModels, getBatchStatus } from '../lib/api';

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
        profile_model: null, // New: Phase 1
        cv_model: null,      // New: Phase 2
        llm_model: null,     // Legacy/Fallback
        image_model: null,
        llmSort: 'default',   // default, price_asc, price_desc
    },

    // Available models
    llmModels: [],
    imageModels: [],
    modelsLoaded: false,

    // Generation state - AGGREGATE QUEUE
    isGenerating: false,
    activeBatchIds: [],     // Array of active batch IDs
    allTasks: [],           // Aggregated tasks from ALL active batches
    currentBatch: null,     // Most recent batch (for display)
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
            if (response.llm_models?.length > 0) {
                const defaultModel = response.llm_models[0].id;
                set((state) => ({
                    config: {
                        ...state.config,
                        llm_model: state.config.llm_model || defaultModel,
                        profile_model: state.config.profile_model || defaultModel,
                        cv_model: state.config.cv_model || defaultModel
                    }
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
        const { config, activeBatchIds, pollInterval } = get();

        // Convert age_min/age_max to age range format
        const ageRange = `${config.age_min}-${config.age_max}`;

        // Build request
        const request = {
            ...config,
            ages: [ageRange],  // Convert to array for backend
            roles: config.roles.length > 0 ? config.roles : ['Software Developer'] // Default if empty
        };

        set({ isGenerating: true, error: null });

        try {
            const response = await generateBatch(request);
            const newBatchId = response.batch_id;

            // Add new batch ID to the queue
            const newBatchIds = [...activeBatchIds, newBatchId];
            set({
                activeBatchIds: newBatchIds,
                currentBatch: newBatchId
            });

            // Start polling if not already running
            if (!pollInterval) {
                const interval = setInterval(async () => {
                    try {
                        const { activeBatchIds: currentBatchIds } = get();

                        if (currentBatchIds.length === 0) {
                            // No active batches, stop polling
                            clearInterval(get().pollInterval);
                            set({ isGenerating: false, pollInterval: null, allTasks: [] });
                            get().loadFiles();
                            return;
                        }

                        // Fetch status for ALL active batches in parallel
                        const statusPromises = currentBatchIds.map(batchId =>
                            getBatchStatus(batchId).catch(() => null)
                        );
                        const results = await Promise.all(statusPromises);

                        // Aggregate tasks and filter out completed batches
                        let aggregatedTasks = [];
                        const stillActiveBatchIds = [];

                        for (let i = 0; i < results.length; i++) {
                            const batchStatus = results[i];
                            if (!batchStatus) continue;

                            // Add tasks from this batch
                            aggregatedTasks = aggregatedTasks.concat(batchStatus.tasks || []);

                            // Keep batch if not complete
                            if (!batchStatus.is_complete) {
                                stillActiveBatchIds.push(currentBatchIds[i]);
                            }
                        }

                        set({ allTasks: aggregatedTasks });

                        // If some batches completed, update the active list
                        if (stillActiveBatchIds.length !== currentBatchIds.length) {
                            set({ activeBatchIds: stillActiveBatchIds });

                            // If all done, stop
                            if (stillActiveBatchIds.length === 0) {
                                clearInterval(get().pollInterval);
                                set({ isGenerating: false, pollInterval: null });
                                get().loadFiles();
                            }
                        }

                    } catch (error) {
                        console.error('Status poll error:', error);
                    }
                }, 2000);

                set({ pollInterval: interval });
            }
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
        set({ isGenerating: false, pollInterval: null, activeBatchIds: [], allTasks: [] });
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
