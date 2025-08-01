import { useState, useEffect, useCallback, useMemo } from 'react';
import agenticWorkflowService from '../services/agenticWorkflowService';

// ========================================
// CURATED VIDEOS HOOKS
// ========================================

export const useCuratedVideos = (filters = {}) => {
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Memoize filters to prevent unnecessary re-renders
    const filtersString = useMemo(() => JSON.stringify(filters), [filters]);
    const memoizedFilters = useMemo(() => filters, [filtersString]);

    const fetchVideos = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getCuratedVideos(memoizedFilters);
            setVideos(data.videos || []);
        } catch (err) {
            // Enhanced error handling with specific messages
            let errorMessage = 'Failed to fetch videos';
            
            if (err.response?.status === 400) {
                errorMessage = err.response.data?.error || 'Invalid request parameters';
            } else if (err.response?.status === 503) {
                errorMessage = 'Service temporarily unavailable. Please try again in a few moments.';
            } else if (err.response?.status === 500) {
                errorMessage = 'Server error. Please try again later.';
            } else if (err.message) {
                errorMessage = err.message;
            }
            
            setError(errorMessage);
            console.error('Error fetching curated videos:', err);
        } finally {
            setLoading(false);
        }
    }, [memoizedFilters]);

    useEffect(() => {
        fetchVideos();
    }, [fetchVideos]);

    return { videos, loading, error, refetch: fetchVideos };
};

export const useCuratedVideoDetail = (videoId) => {
    const [video, setVideo] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchVideo = useCallback(async () => {
        if (!videoId) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getCuratedVideoDetail(videoId);
            setVideo(data);
        } catch (err) {
            // Enhanced error handling with specific messages
            let errorMessage = 'Failed to fetch video details';
            
            if (err.response?.status === 404) {
                errorMessage = 'Video not found';
            } else if (err.response?.status === 400) {
                errorMessage = err.response.data?.error || 'Invalid video ID';
            } else if (err.response?.status === 503) {
                errorMessage = 'Service temporarily unavailable. Please try again in a few moments.';
            } else if (err.response?.status === 500) {
                errorMessage = 'Server error. Please try again later.';
            } else if (err.message) {
                errorMessage = err.message;
            }
            
            setError(errorMessage);
            console.error('Error fetching video details:', err);
        } finally {
            setLoading(false);
        }
    }, [videoId]);

    useEffect(() => {
        fetchVideo();
    }, [fetchVideo]);

    return { video, loading, error, refetch: fetchVideo };
};

export const useCuratedVideoTopics = () => {
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchTopics = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getCuratedVideoTopics();
            setTopics(data.topics || []);
        } catch (err) {
            setError(err.message || 'Failed to fetch topics');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTopics();
    }, [fetchTopics]);

    return { topics, loading, error, refetch: fetchTopics };
};

// ========================================
// LEARNING PATHS HOOKS
// ========================================

export const useLearningPaths = (filters = {}) => {
    const [paths, setPaths] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Memoize filters to prevent unnecessary re-renders
    const filtersString = useMemo(() => JSON.stringify(filters), [filters]);
    const memoizedFilters = useMemo(() => filters, [filtersString]);

    const fetchPaths = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getLearningPaths(memoizedFilters);
            setPaths(data.learning_paths || []);
        } catch (err) {
            setError(err.message || 'Failed to fetch learning paths');
        } finally {
            setLoading(false);
        }
    }, [memoizedFilters]);

    useEffect(() => {
        fetchPaths();
    }, [fetchPaths]);

    return { paths, loading, error, refetch: fetchPaths };
};

export const useLearningPathDetail = (pathId) => {
    const [path, setPath] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPath = useCallback(async () => {
        if (!pathId) {
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getLearningPathDetail(pathId);
            setPath(data);
        } catch (err) {
            setError(err.message || 'Failed to fetch learning path details');
        } finally {
            setLoading(false);
        }
    }, [pathId]);

    useEffect(() => {
        fetchPath();
    }, [fetchPath]);

    return { path, loading, error, refetch: fetchPath };
};

export const useRecommendedLearningPaths = (preferences = {}) => {
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Memoize preferences to prevent unnecessary re-renders
    const preferencesString = useMemo(() => JSON.stringify(preferences), [preferences]);
    const memoizedPreferences = useMemo(() => preferences, [preferencesString]);

    const fetchRecommendations = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getRecommendedLearningPaths(memoizedPreferences);
            setRecommendations(data.recommended_paths || []);
        } catch (err) {
            setError(err.message || 'Failed to fetch recommendations');
        } finally {
            setLoading(false);
        }
    }, [memoizedPreferences]);

    useEffect(() => {
        fetchRecommendations();
    }, [fetchRecommendations]);

    return { recommendations, loading, error, refetch: fetchRecommendations };
};

// ========================================
// USER PROGRESS HOOKS
// ========================================

export const useUserProgress = (videoId = null) => {
    const [progress, setProgress] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchProgress = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getUserProgress(videoId);
            setProgress(data.progress || []);
        } catch (err) {
            setError(err.message || 'Failed to fetch user progress');
        } finally {
            setLoading(false);
        }
    }, [videoId]);

    useEffect(() => {
        fetchProgress();
    }, [fetchProgress]);

    const saveProgress = useCallback(async (progressData) => {
        try {
            const result = await agenticWorkflowService.saveUserProgress(progressData);
            await fetchProgress(); // Refresh the data
            return result;
        } catch (err) {
            setError(err.message || 'Failed to save progress');
            throw err;
        }
    }, [fetchProgress]);

    return { progress, loading, error, saveProgress, refetch: fetchProgress };
};

export const useUserLearningStats = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await agenticWorkflowService.getUserLearningStats();
            setStats(data);
        } catch (err) {
            setError(err.message || 'Failed to fetch learning statistics');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    return { stats, loading, error, refetch: fetchStats };
};

// ========================================
// CONVENIENCE HOOKS
// ========================================

export const useVideosByTopic = (topic) => {
    return useCuratedVideos({ topic });
};

export const useVideosByDifficulty = (difficulty) => {
    return useCuratedVideos({ difficulty });
};

export const useLearningPathsByLevel = (userLevel) => {
    return useLearningPaths({ user_level: userLevel });
};

export const useLearningPathsByTopic = (topic) => {
    return useLearningPaths({ topic });
};

// ========================================
// PROGRESS TRACKING HOOKS
// ========================================

export const useVideoProgress = (videoId) => {
    const { progress, loading, error, saveProgress } = useUserProgress(videoId);
    
    const videoProgress = progress.find(p => p.video_id === videoId) || null;

    const markAsWatched = useCallback(async (timeSpent = 0, notes = '') => {
        return saveProgress({
            video_id: videoId,
            completion_status: 'completed',
            time_spent: timeSpent,
            notes: notes
        });
    }, [videoId, saveProgress]);

    const markAsInProgress = useCallback(async (timeSpent = 0) => {
        return saveProgress({
            video_id: videoId,
            completion_status: 'in_progress',
            time_spent: timeSpent
        });
    }, [videoId, saveProgress]);

    const updateScores = useCallback(async (scores) => {
        return saveProgress({
            video_id: videoId,
            scores: scores
        });
    }, [videoId, saveProgress]);

    return {
        progress: videoProgress,
        loading,
        error,
        markAsWatched,
        markAsInProgress,
        updateScores
    };
};

// ========================================
// GUIDED SESSION HOOKS
// ========================================

export const useGuidedSession = () => {
    const [sessionId, setSessionId] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState('');
    const [expectedAnswer, setExpectedAnswer] = useState('');
    const [userAnswer, setUserAnswer] = useState('');
    const [isCorrect, setIsCorrect] = useState(null);
    const [score, setScore] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const startSession = useCallback(async (videoId, query) => {
        try {
            setLoading(true);
            setError(null);
            const result = await agenticWorkflowService.startGuidedSession(videoId, query);
            
            setSessionId(result.session_id);
            setCurrentQuestion(result.question);
            setExpectedAnswer(result.answer);
            setUserAnswer('');
            setIsCorrect(null);
            setScore(null);
            
            return result;
        } catch (err) {
            setError(err.message || 'Failed to start session');
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    const submitAnswer = useCallback(async (answer) => {
        if (!sessionId) {
            throw new Error('No active session');
        }

        try {
            setLoading(true);
            setError(null);
            const result = await agenticWorkflowService.submitGuidedAnswer(sessionId, answer);
            
            setUserAnswer(answer);
            setIsCorrect(result.is_correct);
            setScore(result.score);
            
            return result;
        } catch (err) {
            setError(err.message || 'Failed to submit answer');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    const resetSession = useCallback(() => {
        setSessionId(null);
        setCurrentQuestion('');
        setExpectedAnswer('');
        setUserAnswer('');
        setIsCorrect(null);
        setScore(null);
        setError(null);
    }, []);

    return {
        sessionId,
        currentQuestion,
        expectedAnswer,
        userAnswer,
        isCorrect,
        score,
        loading,
        error,
        startSession,
        submitAnswer,
        resetSession
    };
}; 