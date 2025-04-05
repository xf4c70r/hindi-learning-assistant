import api from './axiosConfig';

const qaService = {
    generateQuestions: async (transcriptId, questionType = 'novice') => {
        try {
            const response = await api.get(`/transcripts/${transcriptId}/generate_questions/`, {
                params: { type: questionType }
            });
            
            // Handle both response formats
            if (response.data.questions) {
                return response.data;
            } else if (Array.isArray(response.data)) {
                return { questions: response.data };
            } else {
                return { questions: [] };
            }
        } catch (error) {
            throw error.response?.data || { message: 'Failed to generate questions' };
        }
    },

    getQuestions: async (transcriptId) => {
        try {
            const response = await api.get(`/transcripts/${transcriptId}/questions/`);
            
            // Handle both MongoDB and Django response formats
            if (Array.isArray(response.data)) {
                return response.data.map(q => ({
                    ...q,
                    id: q._id || q.id,
                    question_text: q.question_text || q.question
                }));
            }
            return [];
        } catch (error) {
            throw error.response?.data || { message: 'Failed to fetch questions' };
        }
    },

    answerQuestion: async (transcriptId, questionId, answer) => {
        try {
            const response = await api.post(`/transcripts/${transcriptId}/questions/${questionId}/answer/`, {
                answer: answer
            });
            
            // Ensure consistent response format
            return {
                is_correct: response.data.is_correct,
                correct_answer: response.data.correct_answer,
                feedback: response.data.feedback || (response.data.is_correct ? 'Correct!' : 'Incorrect. Try again!'),
                attempts: response.data.attempts,
                correct_attempts: response.data.correct_attempts
            };
        } catch (error) {
            throw error.response?.data || { message: 'Failed to submit answer' };
        }
    }
};

export default qaService; 