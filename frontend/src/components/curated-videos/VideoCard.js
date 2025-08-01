import React from 'react';
import { 
    Card, 
    CardContent, 
    Typography, 
    Chip, 
    Box,
    LinearProgress,
    IconButton,
    Tooltip
} from '@mui/material';
import { 
    PlayArrow, 
    CheckCircle, 
    Schedule, 
    AccessTime,
    School,
    Star,
    Quiz
} from '@mui/icons-material';

const VideoCard = ({ video, onPlay, onMarkWatched, onMarkInProgress, onStartGuidedSession, progress = null }) => {
    const getDifficultyColor = (difficulty) => {
        switch (difficulty.toLowerCase()) {
            case 'beginner': return 'success';
            case 'intermediate': return 'warning';
            case 'advanced': return 'error';
            default: return 'default';
        }
    };

    const getProgressStatus = () => {
        if (!progress) return 'not_started';
        return progress.completion_status || 'not_started';
    };

    const getProgressColor = () => {
        const status = getProgressStatus();
        switch (status) {
            case 'completed': return 'success';
            case 'in_progress': return 'warning';
            default: return 'default';
        }
    };

    const getProgressText = () => {
        const status = getProgressStatus();
        switch (status) {
            case 'completed': return 'Completed';
            case 'in_progress': return 'In Progress';
            default: return 'Not Started';
        }
    };

    const formatDuration = (duration) => {
        if (!duration) return 'Unknown';
        if (typeof duration === 'string') {
            if (duration.includes(':')) return duration;
            const seconds = parseInt(duration);
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
        return duration;
    };

    return (
        <Card 
            sx={{ 
                height: 320, // Fixed height for consistency
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: 1,
                boxShadow: 'none',
                border: '1px solid transparent',
                transition: 'all 0.2s ease-in-out',
                cursor: 'pointer',
                '&:hover': {
                    borderColor: '#e0e0e0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    transform: 'translateY(-1px)'
                },
                backgroundColor: 'transparent'
            }}
            onClick={() => onPlay(video)}
        >
            {/* Video Thumbnail - YouTube Style */}
            <Box
                sx={{
                    position: 'relative',
                    width: '100%',
                    aspectRatio: '16/9',
                    backgroundColor: '#f8f9fa',
                    background: video.thumbnail_url ? `url(${video.thumbnail_url})` : 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    borderRadius: 1,
                    overflow: 'hidden',
                    mb: 1,
                    flexShrink: 0 // Prevent thumbnail from shrinking
                }}
            >
                {/* Play Button Overlay */}
                <Box
                    sx={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: 48,
                        height: 48,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: 0,
                        transition: 'opacity 0.2s ease-in-out',
                        '&:hover': {
                            opacity: 1
                        }
                    }}
                >
                    <PlayArrow sx={{ color: 'white', fontSize: 24 }} />
                </Box>

                {/* Duration Badge - YouTube Style */}
                <Box
                    sx={{
                        position: 'absolute',
                        bottom: 8,
                        right: 8,
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: 1,
                        fontSize: '0.75rem',
                        fontWeight: 500
                    }}
                >
                    {formatDuration(video.duration)}
                </Box>

                {/* Progress Badge */}
                <Box
                    sx={{
                        position: 'absolute',
                        top: 8,
                        left: 8,
                        zIndex: 1
                    }}
                >
                    <Chip
                        label={getProgressText()}
                        color={getProgressColor()}
                        size="small"
                        variant="filled"
                        sx={{
                            fontSize: '0.7rem',
                            height: 20,
                            backgroundColor: getProgressStatus() === 'completed' ? '#4caf50' : 
                                           getProgressStatus() === 'in_progress' ? '#ff9800' : '#757575',
                            color: 'white',
                            '& .MuiChip-label': {
                                padding: '0 6px'
                            }
                        }}
                    />
                </Box>

                {/* Progress Bar Overlay (if in progress) */}
                {getProgressStatus() === 'in_progress' && progress?.time_spent && (
                    <Box
                        sx={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: 3,
                            backgroundColor: 'rgba(0,0,0,0.3)'
                        }}
                    >
                        <LinearProgress 
                            variant="determinate" 
                            value={Math.min((progress.time_spent / (parseInt(video.duration) * 60)) * 100, 100)}
                            sx={{ 
                                height: '100%',
                                backgroundColor: 'transparent',
                                '& .MuiLinearProgress-bar': {
                                    backgroundColor: '#1976d2'
                                }
                            }}
                        />
                    </Box>
                )}
            </Box>

            {/* Video Info - YouTube Style */}
            <CardContent sx={{ 
                p: 0, 
                flexGrow: 1, 
                display: 'flex', 
                flexDirection: 'column',
                minHeight: 0 // Allow content to shrink
            }}>
                {/* Title - Fixed height container */}
                <Box sx={{ height: 48, mb: 1, overflow: 'hidden' }}>
                    <Typography 
                        variant="subtitle1" 
                        component="h3" 
                        sx={{ 
                            fontWeight: 500,
                            lineHeight: 1.3,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            color: '#0f0f0f',
                            fontSize: '0.9rem',
                            height: '100%'
                        }}
                    >
                        {video.title}
                    </Typography>
                </Box>

                {/* Topic - Fixed height */}
                <Box sx={{ height: 20, mb: 1 }}>
                    <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                            fontSize: '0.8rem',
                            color: '#606060',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {video.topic}
                    </Typography>
                </Box>

                {/* Metadata Row - Fixed height */}
                <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1, 
                    mb: 1, 
                    flexWrap: 'wrap',
                    height: 24,
                    minHeight: 24
                }}>
                    <Chip
                        icon={<School />}
                        label={video.difficulty}
                        color={getDifficultyColor(video.difficulty)}
                        size="small"
                        variant="outlined"
                        sx={{ 
                            fontSize: '0.7rem', 
                            height: 20,
                            borderColor: getDifficultyColor(video.difficulty) === 'success' ? '#4caf50' :
                                         getDifficultyColor(video.difficulty) === 'warning' ? '#ff9800' : '#f44336',
                            color: getDifficultyColor(video.difficulty) === 'success' ? '#4caf50' :
                                   getDifficultyColor(video.difficulty) === 'warning' ? '#ff9800' : '#f44336'
                        }}
                    />
                    {video.metadata?.rating && (
                        <Chip
                            icon={<Star />}
                            label={`${video.metadata.rating}/5`}
                            size="small"
                            variant="outlined"
                            sx={{ 
                                fontSize: '0.7rem', 
                                height: 20,
                                borderColor: '#ffc107',
                                color: '#ffc107'
                            }}
                        />
                    )}
                </Box>

                {/* Vocabulary Count - Fixed position at bottom */}
                <Box sx={{ mt: 'auto', pt: 1 }}>
                    <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                            fontSize: '0.8rem',
                            color: '#606060'
                        }}
                    >
                        {video.vocabulary_count || video.metadata?.key_vocabulary?.length || 0} vocabulary words
                    </Typography>
                </Box>
            </CardContent>

            {/* Action Buttons - Hover Only */}
            <Box
                sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    display: 'flex',
                    gap: 0.5,
                    opacity: 0,
                    transition: 'opacity 0.2s ease-in-out',
                    '&:hover': {
                        opacity: 1
                    }
                }}
            >
                {/* Guided Session Button */}
                <Tooltip title="Start Guided Learning">
                    <IconButton
                        onClick={(e) => {
                            e.stopPropagation();
                            onStartGuidedSession(video);
                        }}
                        size="small"
                        sx={{
                            backgroundColor: 'rgba(255,255,255,0.9)',
                            '&:hover': {
                                backgroundColor: '#1976d2',
                                color: 'white'
                            }
                        }}
                    >
                        <Quiz fontSize="small" />
                    </IconButton>
                </Tooltip>

                {getProgressStatus() !== 'completed' && (
                    <Tooltip title="Mark as completed">
                        <IconButton
                            onClick={(e) => {
                                e.stopPropagation();
                                onMarkWatched(video);
                            }}
                            size="small"
                            sx={{
                                backgroundColor: 'rgba(255,255,255,0.9)',
                                '&:hover': {
                                    backgroundColor: '#4caf50',
                                    color: 'white'
                                }
                            }}
                        >
                            <CheckCircle fontSize="small" />
                        </IconButton>
                    </Tooltip>
                )}
                
                {getProgressStatus() === 'not_started' && (
                    <Tooltip title="Mark as in progress">
                        <IconButton
                            onClick={(e) => {
                                e.stopPropagation();
                                onMarkInProgress(video);
                            }}
                            size="small"
                            sx={{
                                backgroundColor: 'rgba(255,255,255,0.9)',
                                '&:hover': {
                                    backgroundColor: '#ff9800',
                                    color: 'white'
                                }
                            }}
                        >
                            <Schedule fontSize="small" />
                        </IconButton>
                    </Tooltip>
                )}
            </Box>
        </Card>
    );
};

export default VideoCard; 