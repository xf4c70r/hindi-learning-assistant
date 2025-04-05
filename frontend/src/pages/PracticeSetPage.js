import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    Container,
    Typography,
    Box,
    Card,
    CardContent,
    Button,
    LinearProgress,
    TextField,
    Alert,
    Grid,
    Collapse,
    IconButton,
    Paper,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import practiceService from '../services/practiceService';
import { ALLOWED_TYPES, getTypeDisplayName, generateTitleFromTranscript } from './PracticePage';

const PracticeSetPage = () => {
    const { videoId, type } = useParams();
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [progress, setProgress] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answer, setAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [showTranscript, setShowTranscript] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [videoTitle, setVideoTitle] = useState('');

    useEffect(() => {
        // Check if type is allowed
        if (!ALLOWED_TYPES[type] || ALLOWED_TYPES[type].enabled === false) {
            setLoading(false);
            setError(`${getTypeDisplayName(type)} questions are not available. Please select from the available practice types.`);
            return;
        }

        const fetchQuestions = async () => {
            try {
                setLoading(true);
                const data = await practiceService.getPracticeQuestions(videoId, type);
                
                // Always fetch transcript separately to ensure we have it
                let transcriptContent = data.transcript || '';
                if (!transcriptContent) {
                    try {
                        const transcriptData = await practiceService.getTranscript(videoId);
                        if (transcriptData && transcriptData.content) {
                            transcriptContent = transcriptData.content;
                        }
                    } catch (transcriptErr) {
                        console.warn(`Couldn't fetch transcript for video ${videoId}:`, transcriptErr);
                        // Continue even if transcript fetch fails
                    }
                }
                
                if (!data.questions || data.questions.length === 0) {
                    setError(`No ${getTypeDisplayName(type)} questions available for this practice set.`);
                    setQuestions([]);
                } else {
                    // Normalize questions data to ensure consistent format
                    const normalizedQuestions = data.questions.map(q => ({
                        ...q,
                        // Ensure question_text exists (some APIs return 'question' instead)
                        question_text: q.question_text || q.question || '',
                        // Ensure consistent type property
                        type: q.type || type,
                        // Ensure options is an array if present
                        options: Array.isArray(q.options) ? q.options : []
                    }));
                    
                    // Try to get title from multiple sources in order of preference
                    if (data.questions[0]?.video_title && data.questions[0].video_title !== 'Untitled') {
                        setVideoTitle(data.questions[0].video_title);
                    } else if (transcriptContent) {
                        const transcriptTitle = generateTitleFromTranscript(transcriptContent);
                        setVideoTitle(transcriptTitle || 'Practice Set');
                    } else {
                        // Use generic "Practice Set" instead of showing video ID
                        setVideoTitle('Practice Set');
                    }
                    
                    setQuestions(normalizedQuestions);
                    setProgress(data.progress || {});
                    setTranscript(transcriptContent);
                    setError(null);
                    
                    // Set transcript visible by default if there's content
                    if (transcriptContent) {
                        setShowTranscript(true);
                    }
                }
            } catch (err) {
                console.error('Error fetching questions:', err);
                setError(err.message || 'Failed to fetch questions');
            } finally {
                setLoading(false);
            }
        };

        fetchQuestions();
    }, [videoId, type]);

    const moveToNextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setAnswer('');
            setFeedback(null);
        }
    };

    const handleSubmitAnswer = async () => {
        if (!answer.trim()) return;

        const currentQuestion = questions[currentQuestionIndex];
        try {
            // Handle different question types
            let isCorrect = false;
            
            if (currentQuestion.type === 'mcq' && currentQuestion.options) {
                // For MCQ, check if selected option matches the answer
                isCorrect = answer === currentQuestion.answer;
            } else {
                // For text answers, clean and compare
                const cleanUserAnswer = answer.toLowerCase().trim().replace(/\s+/g, ' ');
                const cleanCorrectAnswer = (currentQuestion.answer || '').toLowerCase().trim().replace(/\s+/g, ' ');
                isCorrect = cleanUserAnswer === cleanCorrectAnswer;
            }

            await practiceService.submitAnswer({
                question_id: currentQuestion._id,
                answer: answer,
                video_id: videoId,
                type: type,
                is_correct: isCorrect
            });

            if (isCorrect) {
                setFeedback({
                    type: 'success',
                    message: 'Correct!'
                });
                setProgress(prev => ({
                    ...prev,
                    [currentQuestion._id]: {
                        answer,
                        is_correct: true,
                        submitted_at: new Date().toISOString()
                    }
                }));
                
                // Move to next question after a short delay
                setTimeout(moveToNextQuestion, 1000);
            } else {
                setFeedback({
                    type: 'error',
                    message: `Incorrect. The correct answer is: ${currentQuestion.answer}`
                });
            }
        } catch (err) {
            console.error('Error submitting answer:', err);
            setFeedback({
                type: 'error',
                message: 'Failed to submit answer. Please try again.'
            });
        }
    };

    const handleGoBack = () => {
        navigate('/practice');
    };

    if (loading) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <LinearProgress />
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
                <Button variant="contained" onClick={handleGoBack}>
                    Back to Practice Sets
                </Button>
            </Container>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const progressPercentage = (Object.keys(progress).length / questions.length) * 100;

    return (
        <Container maxWidth="md" sx={{ mt: 4 }}>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" gutterBottom>
                    {videoTitle ? `${videoTitle} - ${getTypeDisplayName(type)}` : `Practice Set - ${getTypeDisplayName(type)}`}
                </Typography>
                <Typography variant="subtitle2" color="text.secondary">
                    Video ID: {videoId.substring(0, 8)}
                </Typography>
                <LinearProgress 
                    variant="determinate" 
                    value={progressPercentage} 
                    sx={{ mt: 2, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                    Progress: {Math.round(progressPercentage)}% ({Object.keys(progress).length}/{questions.length} questions)
                </Typography>
            </Box>

            {transcript ? (
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                            <Typography variant="h6">Transcript</Typography>
                            <IconButton onClick={() => setShowTranscript(!showTranscript)}>
                                {showTranscript ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                        </Box>
                        <Collapse in={showTranscript}>
                            <Paper 
                                sx={{ 
                                    p: 2, 
                                    backgroundColor: 'background.paper',
                                    maxHeight: '400px',
                                    overflow: 'auto'
                                }}
                            >
                                <Typography 
                                    variant="body1" 
                                    sx={{ 
                                        whiteSpace: 'pre-wrap',
                                        lineHeight: 1.8
                                    }}
                                >
                                    {transcript}
                                </Typography>
                            </Paper>
                        </Collapse>
                    </CardContent>
                </Card>
            ) : (
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="h6">Transcript</Typography>
                            <Button 
                                variant="outlined" 
                                size="small"
                                onClick={async () => {
                                    try {
                                        setLoading(true);
                                        const transcriptData = await practiceService.getTranscript(videoId);
                                        if (transcriptData && transcriptData.content) {
                                            setTranscript(transcriptData.content);
                                            setShowTranscript(true);
                                        } else {
                                            setError("Transcript not available for this video.");
                                        }
                                    } catch (err) {
                                        console.error("Error fetching transcript:", err);
                                        setError("Failed to load transcript. Please try again.");
                                    } finally {
                                        setLoading(false);
                                    }
                                }}
                            >
                                Load Transcript
                            </Button>
                        </Box>
                    </CardContent>
                </Card>
            )}

            {currentQuestion && (
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Question {currentQuestionIndex + 1} of {questions.length}
                        </Typography>
                        
                        {/* Display question text */}
                        {currentQuestion.type === 'fill_blanks' ? (
                            // For fill in the blanks, display question with highlighted blank
                            <Box sx={{ mb: 3 }}>
                                {currentQuestion.question_text.split('_____').map((part, index, array) => (
                                    <React.Fragment key={index}>
                                        <Typography variant="body1" component="span">
                                            {part}
                                        </Typography>
                                        {index < array.length - 1 && (
                                            <span style={{ 
                                                backgroundColor: '#f0f0f0', 
                                                padding: '2px 8px',
                                                borderRadius: '4px',
                                                fontWeight: 'bold',
                                                display: 'inline-block',
                                                margin: '0 4px'
                                            }}>_____</span>
                                        )}
                                    </React.Fragment>
                                ))}
                            </Box>
                        ) : (
                            <Typography variant="body1" sx={{ mb: 3 }}>
                                {currentQuestion.question_text}
                            </Typography>
                        )}

                        {/* For MCQ questions, show multiple choice options */}
                        {currentQuestion.options && currentQuestion.options.length > 0 ? (
                            <Grid container direction="column" spacing={1} sx={{ mb: 3 }}>
                                {currentQuestion.options.map((option, index) => (
                                    <Grid item key={index}>
                                        <Button
                                            fullWidth
                                            variant={answer === option ? "contained" : "outlined"}
                                            onClick={() => setAnswer(option)}
                                            sx={{ justifyContent: "flex-start", textAlign: "left" }}
                                        >
                                            {option}
                                        </Button>
                                    </Grid>
                                ))}
                            </Grid>
                        ) : (
                            <TextField
                                fullWidth
                                label="Your Answer"
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                                variant="outlined"
                                sx={{ mb: 2 }}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && answer.trim()) {
                                        handleSubmitAnswer();
                                    }
                                }}
                                autoFocus
                            />
                        )}

                        {feedback && (
                            <Alert severity={feedback.type} sx={{ mt: 2, mb: 2 }}>
                                {feedback.message}
                            </Alert>
                        )}

                        <Grid container spacing={2} sx={{ mt: 2 }}>
                            <Grid item>
                                <Button
                                    variant="contained"
                                    onClick={handleSubmitAnswer}
                                    disabled={!answer.trim()}
                                >
                                    Submit Answer
                                </Button>
                            </Grid>
                            {feedback && feedback.type === 'error' && (
                                <Grid item>
                                    <Button
                                        variant="outlined"
                                        onClick={moveToNextQuestion}
                                    >
                                        Next Question
                                    </Button>
                                </Grid>
                            )}
                        </Grid>
                    </CardContent>
                </Card>
            )}
        </Container>
    );
};

export default PracticeSetPage; 