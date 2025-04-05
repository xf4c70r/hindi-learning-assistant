import api from './axiosConfig';

const practiceService = {
    // Get all available practice sets
    getPracticeSets: async () => {
        try {
            const response = await api.get('/practice/sets/');
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch practice sets' };
        }
    },

    // Get questions for a specific practice set
    getPracticeQuestions: async (videoId, questionType) => {
        try {
            const response = await api.get(`/practice/questions/${videoId}/${questionType}/`);
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch practice questions' };
        }
    },

    // Get transcript for a video
    getTranscript: async (videoId) => {
        try {
            const response = await api.get(`/transcripts/${videoId}/`);
            return response.data;
        } catch (error) {
            console.warn(`Couldn't fetch transcript for video ${videoId}:`, error);
            return null;  // Return null instead of throwing to handle gracefully
        }
    },

    // Submit an answer for a practice question
    submitAnswer: async (data) => {
        try {
            const response = await api.post(`/practice/submit/${data.question_id}/`, {
                answer: data.answer,
                video_id: data.video_id,
                type: data.type,
                is_correct: data.is_correct
            });
            return response.data;
        } catch (error) {
            throw error.response?.data || { message: 'Failed to submit answer' };
        }
    }
};

export default practiceService; 