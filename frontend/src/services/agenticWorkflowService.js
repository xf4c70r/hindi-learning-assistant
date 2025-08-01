import api from './axiosConfig';

const agenticWorkflowService = {
    // ========================================
    // CURATED VIDEOS ENDPOINTS
    // ========================================
    
    getCuratedVideos: async (filters = {}) => {
        try {
            const response = await api.get('/curated/videos/', { params: filters });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch curated videos' };
        }
    },

    getCuratedVideoDetail: async (videoId) => {
        try {
            const response = await api.get(`/curated/videos/${videoId}/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch video details' };
        }
    },

    getCuratedVideoTopics: async () => {
        try {
            const response = await api.get('/curated/topics/');
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch video topics' };
        }
    },

    // ========================================
    // LEARNING PATHS ENDPOINTS
    // ========================================
    
    getLearningPaths: async (filters = {}) => {
        try {
            const response = await api.get('/learning-paths/', { params: filters });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch learning paths' };
        }
    },

    getLearningPathDetail: async (pathId) => {
        try {
            const response = await api.get(`/learning-paths/${pathId}/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch learning path details' };
        }
    },

    getRecommendedLearningPaths: async (preferences = {}) => {
        try {
            const response = await api.get('/learning-paths/recommended/', { 
                params: preferences 
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch recommended learning paths' };
        }
    },

    // ========================================
    // USER PROGRESS ENDPOINTS
    // ========================================
    
    saveUserProgress: async (progressData) => {
        try {
            const response = await api.post('/progress/save/', progressData);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to save user progress' };
        }
    },

    getUserProgress: async (videoId = null) => {
        try {
            const params = videoId ? { video_id: videoId } : {};
            const response = await api.get('/progress/', { params });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch user progress' };
        }
    },

    getUserLearningStats: async () => {
        try {
            const response = await api.get('/progress/stats/');
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch learning statistics' };
        }
    },

    updateVideoCompletion: async (videoId, completionData) => {
        try {
            const response = await api.post(`/progress/videos/${videoId}/complete/`, completionData);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to update video completion' };
        }
    },

    // ========================================
    // CONVENIENCE METHODS
    // ========================================
    
    getVideosByTopic: async (topic) => {
        return agenticWorkflowService.getCuratedVideos({ topic });
    },

    getVideosByDifficulty: async (difficulty) => {
        return agenticWorkflowService.getCuratedVideos({ difficulty });
    },

    getLearningPathsByLevel: async (userLevel) => {
        return agenticWorkflowService.getLearningPaths({ user_level: userLevel });
    },

    getLearningPathsByTopic: async (topic) => {
        return agenticWorkflowService.getLearningPaths({ topic });
    },

    getRecommendationsForUser: async (userLevel, preferredTopic = null, maxDuration = null) => {
        const preferences = { user_level: userLevel };
        if (preferredTopic) preferences.preferred_topic = preferredTopic;
        if (maxDuration) preferences.max_duration = maxDuration;
        
        return agenticWorkflowService.getRecommendedLearningPaths(preferences);
    },

    // ========================================
    // PROGRESS TRACKING HELPERS
    // ========================================
    
    markVideoAsWatched: async (videoId, timeSpent = 0, notes = '') => {
        return agenticWorkflowService.saveUserProgress({
            video_id: videoId,
            completion_status: 'completed',
            time_spent: timeSpent,
            notes: notes
        });
    },

    markVideoAsInProgress: async (videoId, timeSpent = 0) => {
        return agenticWorkflowService.saveUserProgress({
            video_id: videoId,
            completion_status: 'in_progress',
            time_spent: timeSpent
        });
    },

    updateVideoScores: async (videoId, scores) => {
        return agenticWorkflowService.saveUserProgress({
            video_id: videoId,
            scores: scores
        });
    },

    // ========================================
    // GUIDED SESSION ENDPOINTS
    // ========================================
    
    startGuidedSession: async (videoId, query) => {
        try {
            const response = await api.post(`/guided/start-session/${videoId}/`, {
                query: query
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to start guided session' };
        }
    },

    submitGuidedAnswer: async (sessionId, answer) => {
        try {
            const response = await api.post(`/guided/answer/${sessionId}/`, {
                answer: answer
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to submit answer' };
        }
    }
};

export default agenticWorkflowService; 