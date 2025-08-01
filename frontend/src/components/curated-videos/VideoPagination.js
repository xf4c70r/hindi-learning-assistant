import React from 'react';
import {
    Box,
    Button,
    Typography,
    CircularProgress,
    Fab,
    Tooltip
} from '@mui/material';
import {
    KeyboardArrowUp,
    KeyboardArrowDown,
    Refresh
} from '@mui/icons-material';

const VideoPagination = ({
    currentPage,
    totalPages,
    hasMore,
    loading,
    onLoadMore,
    onPageChange,
    totalVideos,
    videosPerPage = 12
}) => {
    const startIndex = (currentPage - 1) * videosPerPage + 1;
    const endIndex = Math.min(currentPage * videosPerPage, totalVideos);

    return (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
            {/* Results Info */}
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Showing {startIndex}-{endIndex} of {totalVideos} videos
            </Typography>

            {/* Load More Button (Infinite Scroll Style) */}
            {hasMore && (
                <Box sx={{ mb: 3 }}>
                    <Button
                        variant="outlined"
                        onClick={onLoadMore}
                        disabled={loading}
                        startIcon={loading ? <CircularProgress size={16} /> : <KeyboardArrowDown />}
                        sx={{
                            borderColor: '#1976d2',
                            color: '#1976d2',
                            '&:hover': {
                                backgroundColor: '#1976d2',
                                color: 'white'
                            },
                            textTransform: 'none',
                            px: 3
                        }}
                    >
                        {loading ? 'Loading...' : 'Load More Videos'}
                    </Button>
                </Box>
            )}

            {/* Traditional Pagination (Alternative) */}
            {totalPages > 1 && !hasMore && (
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 3 }}>
                    <Button
                        variant="outlined"
                        onClick={() => onPageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        sx={{
                            borderColor: '#1976d2',
                            color: '#1976d2',
                            '&:hover': {
                                backgroundColor: '#1976d2',
                                color: 'white'
                            },
                            '&:disabled': {
                                borderColor: '#e0e0e0',
                                color: '#e0e0e0'
                            },
                            textTransform: 'none'
                        }}
                    >
                        Previous
                    </Button>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            let pageNum;
                            if (totalPages <= 5) {
                                pageNum = i + 1;
                            } else if (currentPage <= 3) {
                                pageNum = i + 1;
                            } else if (currentPage >= totalPages - 2) {
                                pageNum = totalPages - 4 + i;
                            } else {
                                pageNum = currentPage - 2 + i;
                            }
                            
                            return (
                                <Button
                                    key={pageNum}
                                    variant={currentPage === pageNum ? 'contained' : 'outlined'}
                                    onClick={() => onPageChange(pageNum)}
                                    sx={{
                                        minWidth: 40,
                                        height: 40,
                                        backgroundColor: currentPage === pageNum ? '#1976d2' : 'transparent',
                                        color: currentPage === pageNum ? 'white' : '#1976d2',
                                        borderColor: '#1976d2',
                                        '&:hover': {
                                            backgroundColor: currentPage === pageNum ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                        },
                                        textTransform: 'none'
                                    }}
                                >
                                    {pageNum}
                                </Button>
                            );
                        })}
                    </Box>
                    
                    <Button
                        variant="outlined"
                        onClick={() => onPageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        sx={{
                            borderColor: '#1976d2',
                            color: '#1976d2',
                            '&:hover': {
                                backgroundColor: '#1976d2',
                                color: 'white'
                            },
                            '&:disabled': {
                                borderColor: '#e0e0e0',
                                color: '#e0e0e0'
                            },
                            textTransform: 'none'
                        }}
                    >
                        Next
                    </Button>
                </Box>
            )}

            {/* Back to Top Button */}
            {currentPage > 1 && (
                <Tooltip title="Back to Top">
                    <Fab
                        size="small"
                        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                        sx={{
                            position: 'fixed',
                            bottom: 80,
                            right: 16,
                            backgroundColor: '#1976d2',
                            '&:hover': {
                                backgroundColor: '#1565c0'
                            }
                        }}
                    >
                        <KeyboardArrowUp />
                    </Fab>
                </Tooltip>
            )}
        </Box>
    );
};

export default VideoPagination; 