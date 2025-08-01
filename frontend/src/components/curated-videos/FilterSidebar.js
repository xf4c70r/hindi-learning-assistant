import React, { useState } from 'react';
import {
    Box,
    Typography,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip,
    Button,
    Divider,
    IconButton,
    Collapse
} from '@mui/material';
import {
    ExpandMore,
    FilterList,
    Clear,
    Search,
    School,
    AccessTime,
    Category
} from '@mui/icons-material';

const FilterSidebar = ({
    searchTerm,
    setSearchTerm,
    selectedTopic,
    setSelectedTopic,
    selectedDifficulty,
    setSelectedDifficulty,
    selectedDuration,
    setSelectedDuration,
    topics,
    clearFilters,
    hasActiveFilters
}) => {
    const [expanded, setExpanded] = useState('search');

    const handleAccordionChange = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
    };

    const getDifficultyColor = (difficulty) => {
        switch (difficulty.toLowerCase()) {
            case 'beginner': return '#4caf50';
            case 'intermediate': return '#ff9800';
            case 'advanced': return '#f44336';
            default: return '#1976d2';
        }
    };

    return (
        <Box
            sx={{
                width: 200, // Reduced from 280px
                backgroundColor: 'white',
                borderRight: '1px solid #e0e0e0',
                height: '100vh',
                position: 'sticky',
                top: 0,
                overflowY: 'auto',
                p: 1.5 // Reduced padding
            }}
        >
            {/* Header */}
            <Box sx={{ mb: 2, px: 1 }}> {/* Reduced margin and added horizontal padding */}
                <Typography variant="h6" sx={{ color: '#1976d2', fontWeight: 600, mb: 1, fontSize: '1rem' }}>
                    Filters
                </Typography>
                {hasActiveFilters && (
                    <Button
                        startIcon={<Clear />}
                        onClick={clearFilters}
                        size="small"
                        variant="outlined"
                        sx={{
                            borderColor: '#1976d2',
                            color: '#1976d2',
                            '&:hover': {
                                backgroundColor: '#1976d2',
                                color: 'white'
                            },
                            textTransform: 'none',
                            fontSize: '0.75rem',
                            py: 0.5,
                            px: 1
                        }}
                    >
                        Clear All
                    </Button>
                )}
            </Box>

            {/* Search Section */}
            <Accordion 
                expanded={expanded === 'search'} 
                onChange={handleAccordionChange('search')}
                sx={{ 
                    boxShadow: 'none',
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                    mb: 1.5, // Reduced margin
                    '&:before': { display: 'none' }
                }}
            >
                <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{ 
                        minHeight: 40, // Reduced height
                        '& .MuiAccordionSummary-content': { margin: '4px 0' }
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Search fontSize="small" color="primary" />
                        <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            Search
                        </Typography>
                    </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, px: 1, pb: 1 }}>
                    <input
                        type="text"
                        placeholder="Search videos..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '6px 10px',
                            border: '1px solid #e0e0e0',
                            borderRadius: '4px',
                            fontSize: '13px',
                            outline: 'none',
                            transition: 'border-color 0.2s',
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#1976d2'}
                        onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
                    />
                </AccordionDetails>
            </Accordion>

            {/* Topics Section */}
            <Accordion 
                expanded={expanded === 'topics'} 
                onChange={handleAccordionChange('topics')}
                sx={{ 
                    boxShadow: 'none',
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                    mb: 1.5,
                    '&:before': { display: 'none' }
                }}
            >
                <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{ 
                        minHeight: 40,
                        '& .MuiAccordionSummary-content': { margin: '4px 0' }
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Category fontSize="small" color="primary" />
                        <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            Topics
                        </Typography>
                    </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, px: 1, pb: 1 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Chip
                            label="All Topics"
                            onClick={() => setSelectedTopic('')}
                            variant={selectedTopic === '' ? 'filled' : 'outlined'}
                            color="primary"
                            size="small"
                            sx={{
                                backgroundColor: selectedTopic === '' ? '#1976d2' : 'transparent',
                                color: selectedTopic === '' ? 'white' : '#1976d2',
                                borderColor: '#1976d2',
                                fontSize: '0.75rem',
                                height: 24,
                                '&:hover': {
                                    backgroundColor: selectedTopic === '' ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                }
                            }}
                        />
                        {topics.map((topic) => (
                            <Chip
                                key={topic.topic}
                                label={topic.name}
                                onClick={() => setSelectedTopic(topic.topic)}
                                variant={selectedTopic === topic.topic ? 'filled' : 'outlined'}
                                color="primary"
                                size="small"
                                sx={{
                                    backgroundColor: selectedTopic === topic.topic ? '#1976d2' : 'transparent',
                                    color: selectedTopic === topic.topic ? 'white' : '#1976d2',
                                    borderColor: '#1976d2',
                                    fontSize: '0.75rem',
                                    height: 24,
                                    '&:hover': {
                                        backgroundColor: selectedTopic === topic.topic ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                    }
                                }}
                            />
                        ))}
                    </Box>
                </AccordionDetails>
            </Accordion>

            {/* Difficulty Section */}
            <Accordion 
                expanded={expanded === 'difficulty'} 
                onChange={handleAccordionChange('difficulty')}
                sx={{ 
                    boxShadow: 'none',
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                    mb: 1.5,
                    '&:before': { display: 'none' }
                }}
            >
                <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{ 
                        minHeight: 40,
                        '& .MuiAccordionSummary-content': { margin: '4px 0' }
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <School fontSize="small" color="primary" />
                        <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            Difficulty Level
                        </Typography>
                    </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, px: 1, pb: 1 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Chip
                            label="All Levels"
                            onClick={() => setSelectedDifficulty('')}
                            variant={selectedDifficulty === '' ? 'filled' : 'outlined'}
                            color="primary"
                            size="small"
                            sx={{
                                backgroundColor: selectedDifficulty === '' ? '#1976d2' : 'transparent',
                                color: selectedDifficulty === '' ? 'white' : '#1976d2',
                                borderColor: '#1976d2',
                                fontSize: '0.75rem',
                                height: 24,
                                '&:hover': {
                                    backgroundColor: selectedDifficulty === '' ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                }
                            }}
                        />
                        {['beginner', 'intermediate', 'advanced'].map((level) => (
                            <Chip
                                key={level}
                                label={level.charAt(0).toUpperCase() + level.slice(1)}
                                onClick={() => setSelectedDifficulty(level)}
                                variant={selectedDifficulty === level ? 'filled' : 'outlined'}
                                size="small"
                                sx={{
                                    backgroundColor: selectedDifficulty === level ? getDifficultyColor(level) : 'transparent',
                                    color: selectedDifficulty === level ? 'white' : getDifficultyColor(level),
                                    borderColor: getDifficultyColor(level),
                                    fontSize: '0.75rem',
                                    height: 24,
                                    '&:hover': {
                                        backgroundColor: selectedDifficulty === level ? getDifficultyColor(level) : `${getDifficultyColor(level)}10`
                                    }
                                }}
                            />
                        ))}
                    </Box>
                </AccordionDetails>
            </Accordion>

            {/* Duration Section */}
            <Accordion 
                expanded={expanded === 'duration'} 
                onChange={handleAccordionChange('duration')}
                sx={{ 
                    boxShadow: 'none',
                    border: '1px solid #e0e0e0',
                    borderRadius: 1,
                    mb: 1.5,
                    '&:before': { display: 'none' }
                }}
            >
                <AccordionSummary
                    expandIcon={<ExpandMore />}
                    sx={{ 
                        minHeight: 40,
                        '& .MuiAccordionSummary-content': { margin: '4px 0' }
                    }}
                >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AccessTime fontSize="small" color="primary" />
                        <Typography variant="subtitle2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                            Duration
                        </Typography>
                    </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, px: 1, pb: 1 }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Chip
                            label="Any Length"
                            onClick={() => setSelectedDuration('')}
                            variant={selectedDuration === '' ? 'filled' : 'outlined'}
                            color="primary"
                            size="small"
                            sx={{
                                backgroundColor: selectedDuration === '' ? '#1976d2' : 'transparent',
                                color: selectedDuration === '' ? 'white' : '#1976d2',
                                borderColor: '#1976d2',
                                fontSize: '0.75rem',
                                height: 24,
                                '&:hover': {
                                    backgroundColor: selectedDuration === '' ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                }
                            }}
                        />
                        {[
                            { value: 'short', label: 'Short (< 5 min)' },
                            { value: 'medium', label: 'Medium (5-15 min)' },
                            { value: 'long', label: 'Long (> 15 min)' }
                        ].map((duration) => (
                            <Chip
                                key={duration.value}
                                label={duration.label}
                                onClick={() => setSelectedDuration(duration.value)}
                                variant={selectedDuration === duration.value ? 'filled' : 'outlined'}
                                color="primary"
                                size="small"
                                sx={{
                                    backgroundColor: selectedDuration === duration.value ? '#1976d2' : 'transparent',
                                    color: selectedDuration === duration.value ? 'white' : '#1976d2',
                                    borderColor: '#1976d2',
                                    fontSize: '0.75rem',
                                    height: 24,
                                    '&:hover': {
                                        backgroundColor: selectedDuration === duration.value ? '#1565c0' : 'rgba(25, 118, 210, 0.1)'
                                    }
                                }}
                            />
                        ))}
                    </Box>
                </AccordionDetails>
            </Accordion>
        </Box>
    );
};

export default FilterSidebar; 