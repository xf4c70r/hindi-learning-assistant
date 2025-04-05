import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Paper,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import YouTubeIcon from '@mui/icons-material/YouTube';
import QuizIcon from '@mui/icons-material/Quiz';
import TranslateIcon from '@mui/icons-material/Translate';
import SchoolIcon from '@mui/icons-material/School';

const HeroSection = styled(Box)(({ theme }) => ({
  background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
  color: 'white',
  padding: theme.spacing(12, 0, 10),
  textAlign: 'center',
  position: 'relative',
  overflow: 'hidden',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '4rem',
    background: 'linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.1) 100%)',
  }
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(4),
  transition: 'transform 0.2s, box-shadow 0.2s',
  cursor: 'pointer',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 12px 20px rgba(0,0,0,0.1)',
  },
}));

const IconWrapper = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.primary.light,
  borderRadius: '50%',
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '64px',
  height: '64px',
}));

const StatsSection = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(8, 0),
  textAlign: 'center',
}));

const StatCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  backgroundColor: 'rgba(25, 118, 210, 0.04)',
}));

const Home = () => {
  const navigate = useNavigate();

  return (
    <Box>
      <HeroSection>
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom>
            Learn Hindi Through Videos
          </Typography>
          <Typography variant="h5" paragraph sx={{ mb: 4 }}>
            Generate personalized questions from any Hindi YouTube video and improve your language skills
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            size="large"
            onClick={() => navigate('/signup')}
            sx={{
              fontSize: '1.2rem',
              py: 1.5,
              px: 4,
              borderRadius: '30px',
              boxShadow: '0 4px 14px 0 rgba(0,0,0,0.25)',
            }}
          >
            Start Learning Now
          </Button>
        </Container>
      </HeroSection>

      <Container maxWidth="md" sx={{ mt: -6, position: 'relative', zIndex: 2 }}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} sm={6} md={4}>
            <FeatureCard onClick={() => navigate('/transcripts')}>
              <IconWrapper>
                <YouTubeIcon fontSize="large" />
              </IconWrapper>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h5" component="h2" gutterBottom>
                  YouTube Integration
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Choose any Hindi YouTube video as your learning material
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <FeatureCard onClick={() => navigate('/practice')}>
              <IconWrapper>
                <QuizIcon fontSize="large" />
              </IconWrapper>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h5" component="h2" gutterBottom>
                  AI-Generated Questions
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Practice with automatically generated comprehension questions
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <FeatureCard onClick={() => navigate('/favorites')}>
              <IconWrapper>
                <TranslateIcon fontSize="large" />
              </IconWrapper>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h5" component="h2" gutterBottom>
                  Track Progress
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Monitor your Hindi language learning journey
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
        </Grid>
      </Container>

      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Container maxWidth="sm">
          <Typography variant="h3" gutterBottom>
            Ready to Start?
          </Typography>
          <Typography variant="body1" paragraph sx={{ mb: 4 }}>
            Start your Hindi language learning journey with our new platform.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={() => navigate('/signup')}
            sx={{
              fontSize: '1.1rem',
              py: 1.5,
              px: 4,
              borderRadius: '30px',
            }}
          >
            Create Free Account
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default Home; 