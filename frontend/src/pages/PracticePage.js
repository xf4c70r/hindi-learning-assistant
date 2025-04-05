import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Card,
    CardContent,
    Grid,
    Tabs,
    Tab,
    TextField,
    InputAdornment,
    LinearProgress,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';
import practiceService from '../services/practiceService';

// Define allowed practice types centrally
export const ALLOWED_TYPES = {
    'factual': {
        enabled: true,
        displayName: 'Factual'
    },
    'novice': {
        enabled: true,
        displayName: 'Novice'
    },
    'fill_blanks': {
        enabled: true,
        displayName: 'Fill in Blanks'
    },
    'mcq': {
        enabled: false, // Disabled MCQs
        displayName: 'Multiple Choice'
    }
};

// Helper function to get user-friendly type name
export const getTypeDisplayName = (type) => {
    return ALLOWED_TYPES[type]?.displayName || type.charAt(0).toUpperCase() + type.slice(1);
};

// Helper function to generate a title from transcript content
export const generateTitleFromTranscript = (transcriptText) => {
    if (!transcriptText) return '';
    
    // Get first 30 characters of transcript and add ellipsis if longer
    const firstLine = transcriptText.split('\n')[0] || '';
    const shortTitle = firstLine.trim().substring(0, 30);
    return shortTitle + (firstLine.length > 30 ? '...' : '');
};

const PracticePage = () => {
    const navigate = useNavigate();
    const [practiceSets, setPracticeSets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedType, setSelectedType] = useState('all');
    
    // Fetch practice sets from MongoDB
    useEffect(() => {
        const fetchPracticeSets = async () => {
            try {
                setLoading(true);
                const data = await practiceService.getPracticeSets();
                console.log("Raw practice sets from MongoDB:", data);
                
                // Get transcripts for better titles
                const videoIds = [...new Set(data.map(set => set.video_id))];
                const transcripts = {};
                
                try {
                    // Fetch transcripts for each unique video ID
                    for (const videoId of videoIds) {
                        const transcriptData = await practiceService.getTranscript(videoId);
                        if (transcriptData && transcriptData.content) {
                            transcripts[videoId] = transcriptData.content;
                        }
                    }
                } catch (err) {
                    console.error("Error fetching transcripts:", err);
                    // Continue even if transcripts couldn't be fetched
                }
                
                // Filter out disabled types
                const filteredData = data.filter(set => 
                    ALLOWED_TYPES[set.type]?.enabled !== false
                );
                
                // Group practice sets by video
                const videoGroups = {};
                filteredData.forEach(set => {
                    const videoId = set.video_id;
                    if (!videoGroups[videoId]) {
                        videoGroups[videoId] = {
                            videoId: videoId,
                            title: set.title || 'Untitled Video',
                            transcript: transcripts[videoId] || '',
                            types: {}
                        };
                    }
                    
                    if (!videoGroups[videoId].types[set.type]) {
                        videoGroups[videoId].types[set.type] = [];
                    }
                    
                    videoGroups[videoId].types[set.type].push(set);
                });
                
                // Create final array with consistent naming based on video and type
                const finalSets = [];
                Object.values(videoGroups).forEach((videoGroup, videoIndex) => {
                    Object.entries(videoGroup.types).forEach(([type, sets]) => {
                        sets.forEach((set, typeIndex) => {
                            // Create a short video ID for display (first 6 chars)
                            const shortVideoId = set.video_id.substring(0, 6);
                            
                            // Use transcript for title if available, then video title, then fallback
                            let videoTitle;
                            if (videoGroup.transcript) {
                                videoTitle = generateTitleFromTranscript(videoGroup.transcript);
                            } else if (set.title && set.title !== 'Untitled') {
                                videoTitle = set.title;
                            } else {
                                // Use "Practice X" instead of showing raw video ID
                                videoTitle = `Practice ${videoIndex + 1}`;
                            }
                                
                            finalSets.push({
                                ...set,
                                title: `${videoTitle} - ${getTypeDisplayName(type)}`,
                                originalTitle: set.title,
                                originalIndex: typeIndex + 1,
                                displayId: shortVideoId
                            });
                        });
                    });
                });
                
                setPracticeSets(finalSets);
                setError(null);
            } catch (error) {
                console.error('Error fetching practice sets:', error);
                setError(error.message || 'Failed to fetch practice sets');
            } finally {
                setLoading(false);
            }
        };

        fetchPracticeSets();
    }, []);

    // Get available types from the practice sets
    const availableTypes = React.useMemo(() => {
        const types = new Set();
        practiceSets.forEach(set => {
            if (set.type) {
                types.add(set.type);
            }
        });
        return Array.from(types);
    }, [practiceSets]);

    // Filter practice sets based on type and search query
    const filteredSets = React.useMemo(() => {
        return (practiceSets || []).filter(set => {
            const matchesSearch = set.title?.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesType = selectedType === 'all' || set.type === selectedType;
            return matchesSearch && matchesType;
        });
    }, [practiceSets, searchQuery, selectedType]);

    const handleTypeChange = (event, newValue) => {
        setSelectedType(newValue);
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <LinearProgress />
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4 }}>
                <Typography color="error" variant="h6">
                    {error}
                </Typography>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Practice Hindi
            </Typography>
            
            {/* Filters and Search */}
            <Box sx={{ mb: 4 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            placeholder="Search practice sets..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon />
                                    </InputAdornment>
                                ),
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Tabs
                            value={selectedType}
                            onChange={handleTypeChange}
                            variant="scrollable"
                            scrollButtons="auto"
                        >
                            <Tab label="All Types" value="all" />
                            {availableTypes.map(type => (
                                <Tab 
                                    key={type} 
                                    label={getTypeDisplayName(type)} 
                                    value={type} 
                                />
                            ))}
                        </Tabs>
                    </Grid>
                </Grid>
            </Box>
            
            {/* Practice Sets Grid */}
            <Grid container spacing={3}>
                {filteredSets.length > 0 ? (
                    filteredSets.map((set) => (
                        <Grid item xs={12} sm={6} md={4} key={`${set.video_id}-${set.type}`}>
                            <Card 
                                sx={{ 
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    cursor: 'pointer',
                                    '&:hover': {
                                        boxShadow: 6,
                                    },
                                }}
                                onClick={() => navigate(`/practice/${set.video_id}/${set.type}`)}
                            >
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>
                                        {set.title}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Type: {getTypeDisplayName(set.type)}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Questions: {set.questionCount}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Video ID: {set.displayId}
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={set.progress || 0}
                                        sx={{ mt: 2 }}
                                    />
                                    <Typography variant="body2" color="text.secondary" align="right">
                                        {Math.round(set.progress || 0)}% Complete
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))
                ) : (
                    <Grid item xs={12}>
                        <Typography variant="h6" align="center" color="text.secondary">
                            No practice sets found
                        </Typography>
                    </Grid>
                )}
            </Grid>
        </Container>
    );
};

export default PracticePage; 