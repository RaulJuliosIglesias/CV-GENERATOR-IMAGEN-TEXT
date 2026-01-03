import { create } from 'zustand';
import { generateBatch, getStatus, getFiles, getModels, getBatchStatus, getConfig } from '../lib/api';

const useGenerationStore = create((set, get) => ({
    // Configuration state
    config: {
        qty: 1,
        genders: ['any'],
        ethnicities: ['any'],
        origins: ['any'],
        roles: ['any'],
        age_min: 18,
        age_max: 70,
        expertise_levels: ['any'],
        remote: false,
        profile_model: null,
        cv_model: null,
        llm_model: null,
        image_model: null,
        llmSort: 'default',
    },

    // Available options from centralized database
    configOptions: {
        roles: [],
        genders: [],
        ethnicities: [],
        origins: [],
        expertise_levels: [],
        configLoaded: false
    },

    // Available models
    llmModels: [],
    imageModels: [],
    modelsLoaded: false,

    // Generation state - AGGREGATE QUEUE (FIXED)
    isGenerating: false,
    activeBatchIds: [],     // Array of active (incomplete) batch IDs
    completedBatchIds: [],  // Array of completed batch IDs (to keep their tasks visible)
    allTasks: [],           // Aggregated tasks from ALL batches (active + completed)
    currentBatch: null,
    pollInterval: null,

    // Files state
    files: [],
    isLoadingFiles: false,

    // Error state
    error: null,

    // Load config options from backend database
    loadConfig: async () => {
        try {
            const response = await getConfig();
            console.log('Loaded config from API:', response);
            set({
                configOptions: {
                    roles: response.roles || [],
                    genders: response.genders || [],
                    ethnicities: response.ethnicities || [],
                    origins: response.origins || [],
                    expertise_levels: response.expertise_levels || [],
                    configLoaded: true
                }
            });
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    },

    // Load available models
    loadModels: async () => {
        try {
            const response = await getModels();
            set({
                llmModels: response.llm_models || [],
                imageModels: response.image_models || [],
                modelsLoaded: true,
            });

            const { config } = get();
            if (response.llm_models?.length > 0) {
                // Find specific default models or fallback to first
                const models = response.llm_models;

                // Default Profile Model: Mistral Devstral 2 2512 (free)
                const defaultProfileModel = models.find(m =>
                    m.id.includes('mistral/devstral') || m.id.includes('devstral')
                )?.id || models.find(m => m.is_free === true)?.id || models.find(m => m.id.endsWith(':free'))?.id || models[0].id;

                // Default CV Model: NVIDIA Nemotron 3 Nano 30B (free)
                const defaultCvModel = models.find(m =>
                    m.id.includes('nvidia/nemotron') || m.id.includes('nemotron')
                )?.id || models.find(m => m.is_free === true)?.id || models.find(m => m.id.endsWith(':free'))?.id || models[0].id;

                set((state) => ({
                    config: {
                        ...state.config,
                        llm_model: state.config.llm_model || defaultProfileModel,
                        profile_model: state.config.profile_model || defaultProfileModel,
                        cv_model: state.config.cv_model || defaultCvModel
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
        const { config, activeBatchIds, completedBatchIds, pollInterval } = get();

        const ageRange = `${config.age_min}-${config.age_max}`;

        const request = {
            ...config,
            ages: [ageRange],
            roles: config.roles.length > 0 ? config.roles : ['any']
        };

        set({ isGenerating: true, error: null });

        try {
            const response = await generateBatch(request);
            const newBatchId = response.batch_id;

            // Add new batch ID to active list
            const newActiveBatchIds = [...activeBatchIds, newBatchId];
            set({
                activeBatchIds: newActiveBatchIds,
                currentBatch: newBatchId
            });

            // Start polling if not already running
            if (!pollInterval) {
                const interval = setInterval(async () => {
                    try {
                        const { activeBatchIds: currentActive, completedBatchIds: currentCompleted } = get();

                        // All batch IDs we need to track
                        const allBatchIds = [...currentActive, ...currentCompleted];

                        if (allBatchIds.length === 0) {
                            clearInterval(get().pollInterval);
                            set({ isGenerating: false, pollInterval: null });
                            get().loadFiles();
                            return;
                        }

                        // Fetch status for ALL batches (active + completed for display)
                        const statusPromises = allBatchIds.map(batchId =>
                            getBatchStatus(batchId).catch(() => null)
                        );
                        const results = await Promise.all(statusPromises);

                        // Aggregate all tasks
                        let aggregatedTasks = [];
                        const stillActiveBatchIds = [];
                        const newlyCompletedBatchIds = [...currentCompleted];

                        for (let i = 0; i < results.length; i++) {
                            const batchStatus = results[i];
                            if (!batchStatus) continue;

                            // Add all tasks from this batch
                            aggregatedTasks = aggregatedTasks.concat(batchStatus.tasks || []);

                            const batchId = allBatchIds[i];
                            const wasActive = currentActive.includes(batchId);

                            if (wasActive) {
                                if (!batchStatus.is_complete) {
                                    stillActiveBatchIds.push(batchId);
                                } else {
                                    // Move to completed list
                                    if (!newlyCompletedBatchIds.includes(batchId)) {
                                        newlyCompletedBatchIds.push(batchId);
                                    }
                                }
                            }
                        }

                        set({
                            allTasks: aggregatedTasks,
                            activeBatchIds: stillActiveBatchIds,
                            completedBatchIds: newlyCompletedBatchIds
                        });

                        // If no more active batches, stop polling but keep tasks visible
                        if (stillActiveBatchIds.length === 0) {
                            clearInterval(get().pollInterval);
                            set({ isGenerating: false, pollInterval: null });
                            get().loadFiles();
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
        set({ isGenerating: false, pollInterval: null, activeBatchIds: [] });
        // Keep allTasks and completedBatchIds for display
    },

    clearQueue: () => {
        // New action to clear all tasks when user wants fresh start
        set({ activeBatchIds: [], completedBatchIds: [], allTasks: [] });
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
