import api from './axiosConfig';

const transcriptService = {
    getAllTranscripts: async () => {
        try {
            const response = await api.get('/transcripts/');
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch transcripts' };
        }
    },

    getFavoriteTranscripts: async () => {
        try {
            const response = await api.get('/transcripts/', {
                params: { favorite: true }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch favorite transcripts' };
        }
    },

    getTranscript: async (id) => {
        try {
            const response = await api.get(`/transcripts/${id}/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch transcript' };
        }
    },

    createTranscript: async (videoUrl, title = '') => {
        try {
            const response = await api.post('/transcripts/create-from-video/', {
                video_id: videoUrl,
                title: title || 'Untitled'
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to create transcript' };
        }
    },

    deleteTranscript: async (id) => {
        try {
            await api.delete(`/transcripts/${id}/`);
        } catch (error) {
            throw error.response?.data || { message: 'Failed to delete transcript' };
        }
    },

    updateTranscript: async (id, data) => {
        try {
            const response = await api.patch(`/transcripts/${id}/`, data);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to update transcript' };
        }
    },

    generateQuestions: async (id, type = 'novice') => {
        try {
            const response = await api.get(`/transcripts/${id}/generate_questions/`, {
                params: { type }
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to generate questions' };
        }
    },

    toggleFavorite: async (id) => {
        try {
            const response = await api.post(`/transcripts/${id}/toggle_favorite/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to toggle favorite status' };
        }
    }
};

export default transcriptService; 