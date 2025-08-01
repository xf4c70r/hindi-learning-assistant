import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Alert,
    CircularProgress,
    Chip,
    Paper,
    Divider,
    IconButton
} from '@mui/material';
import {
    CheckCircle,
    Cancel,
    School,
    ArrowBack,
    Refresh
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { useGuidedSession } from '../hooks/useAgenticWorkflow';
import { useCuratedVideoDetail } from '../hooks/useAgenticWorkflow';

const GuidedSessionPage = () => {
    const navigate = useNavigate();
    const { videoId } = useParams();
    const [answer, setAnswer] = useState('');
    const [sessionStarted, setSessionStarted] = useState(false);
    
    const { video, loading: videoLoading } = useCuratedVideoDetail(videoId);
    const {
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
    } = useGuidedSession();

    // Auto-start session when page loads
    useEffect(() => {
        if (video && !sessionStarted) {
            const initialQuery = "इस वीडियो के बारे में मुझे कुछ सवाल पूछें";
            startSession(videoId, initialQuery)
                .then(() => setSessionStarted(true))
                .catch(console.error);
        }
    }, [video, videoId, sessionStarted, startSession]);

    const handleSubmitAnswer = async () => {
        if (!answer.trim()) return;
        
        try {
            await submitAnswer(answer.trim());
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    const handleNextQuestion = async () => {
        setAnswer('');
        const nextQuery = "अगला सवाल पूछें";
        try {
            await startSession(videoId, nextQuery);
        } catch (error) {
            console.error('Error getting next question:', error);
        }
    };

    const handleReset = () => {
        resetSession();
        setSessionStarted(false);
        setAnswer('');
    };

    if (videoLoading) {
        return (
            <Container maxWidth="md" sx={{ py: 4 }}>
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                    <CircularProgress />
                </Box>
            </Container>
        );
    }

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <IconButton onClick={() => navigate('/curated-videos')} sx={{ mr: 2 }}>
                        <ArrowBack />
                    </IconButton>
                    <Typography variant="h4" sx={{ fontWeight: 600, color: '#1976d2' }}>
                        Guided Learning Session
                    </Typography>
                </Box>
                
                {video && (
                    <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f8f9fa' }}>
                        <Typography variant="h6" gutterBottom>
                            {video.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            {video.description}
                        </Typography>
                    </Paper>
                )}
            </Box>

            {/* Error Display */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Session Content */}
            {sessionId && (
                <Card sx={{ mb: 3 }}>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <School sx={{ mr: 1, color: '#1976d2' }} />
                            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                Current Question
                            </Typography>
                        </Box>
                        
                        <Typography variant="body1" sx={{ mb: 3, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                            {currentQuestion}
                        </Typography>

                        {/* Answer Input */}
                        {isCorrect === null && (
                            <Box sx={{ mb: 3 }}>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    variant="outlined"
                                    label="Your Answer"
                                    value={answer}
                                    onChange={(e) => setAnswer(e.target.value)}
                                    placeholder="Type your answer here..."
                                    disabled={loading}
                                />
                                
                                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                                    <Button
                                        variant="contained"
                                        onClick={handleSubmitAnswer}
                                        disabled={!answer.trim() || loading}
                                        startIcon={loading ? <CircularProgress size={20} /> : null}
                                    >
                                        Submit Answer
                                    </Button>
                                </Box>
                            </Box>
                        )}

                        {/* Answer Feedback */}
                        {isCorrect !== null && (
                            <Box sx={{ mb: 3 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                    {isCorrect ? (
                                        <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
                                    ) : (
                                        <Cancel sx={{ mr: 1, color: 'error.main' }} />
                                    )}
                                    <Typography variant="h6" color={isCorrect ? 'success.main' : 'error.main'}>
                                        {isCorrect ? 'Correct!' : 'Incorrect'}
                                    </Typography>
                                </Box>

                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Your Answer:
                                    </Typography>
                                    <Typography variant="body1" sx={{ p: 1, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                                        {userAnswer}
                                    </Typography>
                                </Box>

                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="body2" color="text.secondary" gutterBottom>
                                        Expected Answer:
                                    </Typography>
                                    <Typography variant="body1" sx={{ p: 1, backgroundColor: '#e8f5e8', borderRadius: 1 }}>
                                        {expectedAnswer}
                                    </Typography>
                                </Box>

                                <Chip 
                                    label={`Score: ${score}/1`} 
                                    color={score > 0 ? 'success' : 'error'}
                                    sx={{ mb: 2 }}
                                />

                                <Box sx={{ display: 'flex', gap: 2 }}>
                                    <Button
                                        variant="contained"
                                        onClick={handleNextQuestion}
                                        disabled={loading}
                                        startIcon={loading ? <CircularProgress size={20} /> : null}
                                    >
                                        Next Question
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        onClick={handleReset}
                                        startIcon={<Refresh />}
                                    >
                                        Start Over
                                    </Button>
                                </Box>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Loading State */}
            {loading && !sessionId && (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                    <CircularProgress />
                </Box>
            )}
        </Container>
    );
};

export default GuidedSessionPage; 