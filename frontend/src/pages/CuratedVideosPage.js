import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Typography,
    Box,
    Grid,
    Alert,
    Skeleton,
    Fab,
    Tooltip,
    IconButton,
    Drawer,
    Button
} from '@mui/material';
import {
    PlayArrow,
    FilterList,
    Close
} from '@mui/icons-material';

import { useCuratedVideos, useCuratedVideoTopics, useUserProgress } from '../hooks/useAgenticWorkflow';
import VideoCard from '../components/curated-videos/VideoCard';
import VideoDetailModal from '../components/curated-videos/VideoDetailModal';
import FilterSidebar from '../components/curated-videos/FilterSidebar';
import VideoPagination from '../components/curated-videos/VideoPagination';

const CuratedVideosPage = () => {
    const navigate = useNavigate();
    
    // State
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [selectedDuration, setSelectedDuration] = useState('');
    const [selectedVideo, setSelectedVideo] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [useInfiniteScroll, setUseInfiniteScroll] = useState(true);
    const videosPerPage = 12;

    // Data fetching
    const { videos, loading: videosLoading, error: videosError } = useCuratedVideos();
    const { topics, loading: topicsLoading } = useCuratedVideoTopics();
    const { progress, loading: progressLoading, saveProgress } = useUserProgress();

    // Filter videos based on search and filters
    const filteredVideos = useMemo(() => {
        if (!videos) return [];

        return videos.filter(video => {
            // Search term filter
            if (searchTerm && !video.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
                !video.description?.toLowerCase().includes(searchTerm.toLowerCase())) {
                return false;
            }

            // Topic filter
            if (selectedTopic && video.topic !== selectedTopic) {
                return false;
            }

            // Difficulty filter
            if (selectedDifficulty && video.difficulty !== selectedDifficulty) {
                return false;
            }

            // Duration filter
            if (selectedDuration) {
                const videoDuration = video.duration_seconds || parseInt(video.duration) || 0;
                switch (selectedDuration) {
                    case 'short':
                        if (videoDuration > 300) return false; // > 5 minutes
                        break;
                    case 'medium':
                        if (videoDuration < 300 || videoDuration > 900) return false; // 5-15 minutes
                        break;
                    case 'long':
                        if (videoDuration < 900) return false; // < 15 minutes
                        break;
                }
            }

            return true;
        });
    }, [videos, searchTerm, selectedTopic, selectedDifficulty, selectedDuration]);

    // Pagination logic
    const totalVideos = filteredVideos.length;
    const totalPages = Math.ceil(totalVideos / videosPerPage);
    const hasMore = currentPage < totalPages;

    const paginatedVideos = useMemo(() => {
        if (useInfiniteScroll) {
            // For infinite scroll, show all videos up to current page
            return filteredVideos.slice(0, currentPage * videosPerPage);
        } else {
            // For traditional pagination, show only current page
            const startIndex = (currentPage - 1) * videosPerPage;
            return filteredVideos.slice(startIndex, startIndex + videosPerPage);
        }
    }, [filteredVideos, currentPage, videosPerPage, useInfiniteScroll]);

    // Get progress for a specific video
    const getVideoProgress = (videoId) => {
        return progress.find(p => p.video_id === videoId) || null;
    };

    // Handle video actions
    const handlePlayVideo = (video) => {
        setSelectedVideo(video);
        setModalOpen(true);
    };

    const handleMarkWatched = async (video) => {
        try {
            await saveProgress({
                video_id: video.video_id,
                completion_status: 'completed',
                time_spent: parseInt(video.duration) * 60, // Full duration in seconds
                notes: 'Marked as completed'
            });
        } catch (error) {
            console.error('Error marking video as watched:', error);
        }
    };

    const handleMarkInProgress = async (video) => {
        try {
            await saveProgress({
                video_id: video.video_id,
                completion_status: 'in_progress',
                time_spent: 0,
                notes: 'Started learning'
            });
        } catch (error) {
            console.error('Error marking video as in progress:', error);
        }
    };

    const handleStartGuidedSession = (video) => {
        navigate(`/guided-session/${video.video_id}`);
    };

    const handleCloseModal = () => {
        setModalOpen(false);
        setSelectedVideo(null);
    };

    const clearFilters = () => {
        setSearchTerm('');
        setSelectedTopic('');
        setSelectedDifficulty('');
        setSelectedDuration('');
        setCurrentPage(1);
    };

    const handleLoadMore = () => {
        setCurrentPage(prev => prev + 1);
    };

    const handlePageChange = (page) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const hasActiveFilters = searchTerm || selectedTopic || selectedDifficulty || selectedDuration;

    // Loading state
    if (videosLoading || topicsLoading || progressLoading) {
        return (
            <Box sx={{ display: 'flex', minHeight: '100vh' }}>
                {/* Sidebar Skeleton */}
                <Box sx={{ width: 240, p: 1.5, borderRight: '1px solid #e0e0e0' }}>
                    <Skeleton variant="rectangular" height={40} sx={{ mb: 2 }} />
                    {[...Array(4)].map((_, index) => (
                        <Skeleton key={index} variant="rectangular" height={50} sx={{ mb: 1 }} />
                    ))}
                </Box>
                
                {/* Main Content Skeleton */}
                <Box sx={{ flex: 1, p: 4 }}>
                    <Skeleton variant="rectangular" height={60} sx={{ mb: 3 }} />
                    <Grid container spacing={3}>
                        {[...Array(8)].map((_, index) => (
                            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
                                <Skeleton 
                                    variant="rectangular" 
                                    height={320} 
                                    sx={{ 
                                        borderRadius: 1,
                                        backgroundColor: '#f5f5f5'
                                    }} 
                                />
                            </Grid>
                        ))}
                    </Grid>
                </Box>
            </Box>
        );
    }

    return (
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Desktop Sidebar */}
            <Box sx={{ 
                display: { xs: 'none', md: 'block' },
                width: 200, // Fixed width to match sidebar
                flexShrink: 0 // Prevent sidebar from shrinking
            }}>
                <FilterSidebar
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                    selectedTopic={selectedTopic}
                    setSelectedTopic={setSelectedTopic}
                    selectedDifficulty={selectedDifficulty}
                    setSelectedDifficulty={setSelectedDifficulty}
                    selectedDuration={selectedDuration}
                    setSelectedDuration={setSelectedDuration}
                    topics={topics}
                    clearFilters={clearFilters}
                    hasActiveFilters={hasActiveFilters}
                />
            </Box>

            {/* Mobile Sidebar Drawer */}
            <Drawer
                anchor="left"
                open={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                sx={{
                    '& .MuiDrawer-paper': {
                        width: 240, // Updated to match desktop sidebar
                        boxSizing: 'border-box',
                    },
                }}
            >
                <Box sx={{ p: 1.5, borderBottom: '1px solid #e0e0e0' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="h6" sx={{ color: '#1976d2', fontWeight: 600, fontSize: '1rem' }}>
                            Filters
                        </Typography>
                        <IconButton onClick={() => setSidebarOpen(false)}>
                            <Close />
                        </IconButton>
                    </Box>
                </Box>
                <FilterSidebar
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                    selectedTopic={selectedTopic}
                    setSelectedTopic={setSelectedTopic}
                    selectedDifficulty={selectedDifficulty}
                    setSelectedDifficulty={setSelectedDifficulty}
                    selectedDuration={selectedDuration}
                    setSelectedDuration={setSelectedDuration}
                    topics={topics}
                    clearFilters={clearFilters}
                    hasActiveFilters={hasActiveFilters}
                />
            </Drawer>

            {/* Main Content */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Header */}
                <Box sx={{ p: 3, pb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                        <Box>
                            <Typography variant="h4" sx={{ mb: 1, fontWeight: 600, color: '#1976d2' }}>
                                Curated Videos
                            </Typography>
                            <Typography variant="body1" color="text.secondary" sx={{ fontSize: '1rem' }}>
                                Discover carefully selected Hindi learning videos tailored to your level
                            </Typography>
                        </Box>
                        
                        {/* Mobile Filter Button */}
                        <IconButton
                            onClick={() => setSidebarOpen(true)}
                            sx={{ 
                                display: { xs: 'flex', md: 'none' },
                                backgroundColor: '#1976d2',
                                color: 'white',
                                '&:hover': {
                                    backgroundColor: '#1565c0'
                                }
                            }}
                        >
                            <FilterList />
                        </IconButton>
                    </Box>

                    {/* Results Info */}
                    <Typography variant="h6" sx={{ color: '#1976d2', fontWeight: 600 }}>
                        {totalVideos} video{totalVideos !== 1 ? 's' : ''} found
                    </Typography>
                </Box>

                {/* Error Display */}
                {videosError && (
                    <Box sx={{ px: 3, mb: 3 }}>
                        <Alert 
                            severity="error" 
                            sx={{ 
                                borderRadius: 2,
                                '& .MuiAlert-message': {
                                    fontSize: '0.95rem',
                                    lineHeight: 1.4
                                }
                            }}
                            action={
                                <Button 
                                    color="inherit" 
                                    size="small" 
                                    onClick={() => window.location.reload()}
                                    sx={{ textTransform: 'none' }}
                                >
                                    Retry
                                </Button>
                            }
                        >
                            <Typography variant="body1" sx={{ fontWeight: 500, mb: 0.5 }}>
                                Unable to load videos
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {videosError}
                            </Typography>
                        </Alert>
                    </Box>
                )}

                {/* Videos Grid */}
                <Box sx={{ flex: 1, px: 2 }}>
                    {paginatedVideos.length > 0 ? (
                        <Grid container spacing={2}>
                            {paginatedVideos.map((video) => (
                                <Grid item xs={12} sm={6} md={4} lg={3} key={video.video_id}>
                                    <VideoCard
                                        video={video}
                                        progress={getVideoProgress(video.video_id)}
                                        onPlay={handlePlayVideo}
                                        onMarkWatched={handleMarkWatched}
                                        onMarkInProgress={handleMarkInProgress}
                                        onStartGuidedSession={handleStartGuidedSession}
                                    />
                                </Grid>
                            ))}
                        </Grid>
                    ) : (
                        <Box sx={{ 
                            textAlign: 'center',
                            py: 8,
                            backgroundColor: 'white',
                            borderRadius: 2,
                            border: '1px solid #e0e0e0'
                        }}>
                            <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                                No videos found
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Try adjusting your filters or search terms
                            </Typography>
                        </Box>
                    )}

                    {/* Pagination */}
                    {totalVideos > 0 && (
                        <VideoPagination
                            currentPage={currentPage}
                            totalPages={totalPages}
                            hasMore={hasMore}
                            loading={false}
                            onLoadMore={handleLoadMore}
                            onPageChange={handlePageChange}
                            totalVideos={totalVideos}
                            videosPerPage={videosPerPage}
                        />
                    )}
                </Box>
            </Box>

            {/* Video Detail Modal */}
            <VideoDetailModal
                video={selectedVideo}
                open={modalOpen}
                onClose={handleCloseModal}
                onPlay={handlePlayVideo}
                onMarkWatched={handleMarkWatched}
                onMarkInProgress={handleMarkInProgress}
                progress={selectedVideo ? getVideoProgress(selectedVideo.video_id) : null}
            />

            {/* Floating Action Button for Quick Start */}
            <Tooltip title="Start Learning">
                <Fab
                    color="primary"
                    sx={{ 
                        position: 'fixed', 
                        bottom: 16, 
                        right: 16,
                        backgroundColor: '#1976d2',
                        '&:hover': {
                            backgroundColor: '#1565c0'
                        }
                    }}
                    onClick={() => {
                        // Find first uncompleted video
                        const firstVideo = filteredVideos.find(video => 
                            !getVideoProgress(video.video_id) || 
                            getVideoProgress(video.video_id).completion_status !== 'completed'
                        );
                        if (firstVideo) {
                            handlePlayVideo(firstVideo);
                        }
                    }}
                >
                    <PlayArrow />
                </Fab>
            </Tooltip>
        </Box>
    );
};

export default CuratedVideosPage; 