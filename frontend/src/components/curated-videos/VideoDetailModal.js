import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Typography,
    Box,
    Chip,
    Button,
    List,
    ListItem,
    ListItemText,
    Divider,
    LinearProgress,
    IconButton,
    Grid,
    Paper
} from '@mui/material';
import {
    Close,
    PlayArrow,
    CheckCircle,
    Schedule,
    AccessTime,
    School,
    Star,
    Translate,
    Book
} from '@mui/icons-material';

const VideoDetailModal = ({ 
    video, 
    open, 
    onClose, 
    onPlay, 
    onMarkWatched, 
    onMarkInProgress,
    progress = null 
}) => {
    if (!video) return null;

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

    const getProgressPercentage = () => {
        if (!progress?.time_spent || !video.duration) return 0;
        const totalSeconds = parseInt(video.duration) * 60;
        return Math.min((progress.time_spent / totalSeconds) * 100, 100);
    };

    return (
        <Dialog 
            open={open} 
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: 2,
                    maxHeight: '90vh'
                }
            }}
        >
            <DialogTitle sx={{ pb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                        {video.title}
                    </Typography>
                    <IconButton onClick={onClose} size="small">
                        <Close />
                    </IconButton>
                </Box>
            </DialogTitle>

            <DialogContent sx={{ pt: 0 }}>
                <Grid container spacing={3}>
                    {/* Left Column - Video Info */}
                    <Grid item xs={12} md={8}>
                        {/* Video Thumbnail */}
                        <Box
                            sx={{
                                height: 200,
                                backgroundColor: 'grey.200',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                position: 'relative',
                                background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`,
                                borderRadius: 2,
                                mb: 2
                            }}
                        >
                            <Typography variant="h2" color="white" sx={{ opacity: 0.8 }}>
                                {video.title.charAt(0).toUpperCase()}
                            </Typography>
                            <IconButton
                                sx={{
                                    position: 'absolute',
                                    color: 'white',
                                    backgroundColor: 'rgba(0,0,0,0.3)',
                                    '&:hover': {
                                        backgroundColor: 'rgba(0,0,0,0.5)'
                                    }
                                }}
                                onClick={() => onPlay(video)}
                            >
                                <PlayArrow fontSize="large" />
                            </IconButton>
                        </Box>

                        {/* Description */}
                        <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.6 }}>
                            {video.description || 'No description available.'}
                        </Typography>

                        {/* Metadata Grid */}
                        <Grid container spacing={2} sx={{ mb: 3 }}>
                            <Grid item xs={6} sm={3}>
                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                    <School color="primary" sx={{ mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        Difficulty
                                    </Typography>
                                    <Chip
                                        label={video.difficulty}
                                        color={getDifficultyColor(video.difficulty)}
                                        size="small"
                                        sx={{ mt: 1 }}
                                    />
                                </Paper>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                    <AccessTime color="primary" sx={{ mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        Duration
                                    </Typography>
                                    <Typography variant="h6">
                                        {formatDuration(video.duration)}
                                    </Typography>
                                </Paper>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                    <Translate color="primary" sx={{ mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        Vocabulary
                                    </Typography>
                                    <Typography variant="h6">
                                        {video.metadata?.key_vocabulary?.length || 0}
                                    </Typography>
                                </Paper>
                            </Grid>
                            <Grid item xs={6} sm={3}>
                                <Paper sx={{ p: 2, textAlign: 'center' }}>
                                    <Star color="primary" sx={{ mb: 1 }} />
                                    <Typography variant="body2" color="text.secondary">
                                        Rating
                                    </Typography>
                                    <Typography variant="h6">
                                        {video.metadata?.rating ? `${video.metadata.rating}/5` : 'N/A'}
                                    </Typography>
                                </Paper>
                            </Grid>
                        </Grid>

                        {/* Progress Section */}
                        <Paper sx={{ p: 2, mb: 3 }}>
                            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Book />
                                Learning Progress
                            </Typography>
                            
                            <Box sx={{ mb: 2 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="body2" color="text.secondary">
                                        {getProgressText()}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {Math.round(getProgressPercentage())}%
                                    </Typography>
                                </Box>
                                <LinearProgress 
                                    variant="determinate" 
                                    value={getProgressPercentage()}
                                    sx={{ height: 8, borderRadius: 4 }}
                                />
                            </Box>

                            {progress?.time_spent && (
                                <Typography variant="body2" color="text.secondary">
                                    Time spent: {Math.floor(progress.time_spent / 60)}m {progress.time_spent % 60}s
                                </Typography>
                            )}
                        </Paper>
                    </Grid>

                    {/* Right Column - Vocabulary */}
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 2, height: 'fit-content' }}>
                            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Translate />
                                Key Vocabulary
                            </Typography>
                            
                            {video.metadata?.key_vocabulary?.length > 0 ? (
                                <List dense>
                                    {video.metadata.key_vocabulary.map((word, index) => (
                                        <React.Fragment key={index}>
                                            <ListItem sx={{ px: 0 }}>
                                                <ListItemText
                                                    primary={word.hindi || word}
                                                    secondary={word.english || word.translation}
                                                />
                                            </ListItem>
                                            {index < video.metadata.key_vocabulary.length - 1 && (
                                                <Divider />
                                            )}
                                        </React.Fragment>
                                    ))}
                                </List>
                            ) : (
                                <Typography variant="body2" color="text.secondary">
                                    No vocabulary data available.
                                </Typography>
                            )}
                        </Paper>
                    </Grid>
                </Grid>
            </DialogContent>

            <DialogActions sx={{ p: 3, pt: 0 }}>
                <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
                    <Button
                        variant="contained"
                        startIcon={<PlayArrow />}
                        onClick={() => onPlay(video)}
                        sx={{ flex: 1 }}
                        size="large"
                    >
                        Start Learning
                    </Button>
                    
                    {getProgressStatus() !== 'completed' && (
                        <Button
                            variant="outlined"
                            startIcon={<CheckCircle />}
                            onClick={() => onMarkWatched(video)}
                            color="success"
                        >
                            Mark Complete
                        </Button>
                    )}
                    
                    {getProgressStatus() === 'not_started' && (
                        <Button
                            variant="outlined"
                            startIcon={<Schedule />}
                            onClick={() => onMarkInProgress(video)}
                            color="warning"
                        >
                            Start Later
                        </Button>
                    )}
                </Box>
            </DialogActions>
        </Dialog>
    );
};

export default VideoDetailModal; 