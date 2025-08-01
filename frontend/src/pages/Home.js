import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Paper
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getTrendingWords } from '../services/vocabularyService';
import YouTubeIcon from '@mui/icons-material/YouTube';
import QuizIcon from '@mui/icons-material/Quiz';
import TranslateIcon from '@mui/icons-material/Translate';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SchoolIcon from '@mui/icons-material/School';
import { TypeAnimation } from 'react-type-animation';
import BackgroundImage from '../assets/hindi-text-bg.png'; // Make sure to add this image to your assets

const PageWrapper = styled(Box)({
  position: 'relative',
  minHeight: '100vh',
  background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.02) 0%, rgba(66, 165, 245, 0.02) 100%)',
  '&::before': {
    content: '""',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundImage: `url(${BackgroundImage})`,
    backgroundSize: '70%',
    backgroundPosition: 'center',
    opacity: 0.2,
    zIndex: -1,
    filter: 'contrast(1.2) brightness(1.1)',
  }
});

const WelcomeSection = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(4),
  marginBottom: theme.spacing(6),
  '& .MuiTypography-h3': {
    fontWeight: 700,
    textShadow: '1px 1px 2px rgba(0, 0, 0, 0.1)',
    color: theme.palette.primary.dark,
    fontSize: '3.5rem',
  },
  '& .MuiTypography-subtitle1': {
    fontSize: '1.4rem',
    fontWeight: 500,
    color: theme.palette.text.primary,
  }
}));

const TrendingSection = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(6),
  '& .MuiTypography-h4': {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(4),
    fontWeight: 700,
    color: theme.palette.primary.dark,
    textShadow: '1px 1px 2px rgba(0, 0, 0, 0.1)',
    fontSize: '2.5rem',
  }
}));

const AnimatedText = styled(Typography)(({ theme }) => ({
  fontFamily: 'monospace',
  minHeight: '120px',
  fontSize: '2.2em',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.text.primary,
  fontWeight: 600,
  letterSpacing: '0.5px',
  textShadow: '1px 1px 2px rgba(0, 0, 0, 0.1)',
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(3),
  cursor: 'pointer',
  transition: 'all 0.2s ease-in-out',
  background: 'rgba(255, 255, 255, 0.97)',
  backdropFilter: 'blur(4px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  '&:hover': {
    transform: 'translateY(-4px)',
    background: 'rgba(255, 255, 255, 1)',
    boxShadow: '0 4px 20px rgba(30, 136, 229, 0.1)',
  },
}));

const IconWrapper = styled(Box)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  borderRadius: '50%',
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  color: 'white',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: '56px',
  height: '56px',
  boxShadow: '0 4px 12px rgba(30, 136, 229, 0.2)',
}));

// Add this for the landing page
const LandingTitle = styled(Typography)(({ theme }) => ({
  fontSize: '4.5rem',
  fontWeight: 800,
  background: 'linear-gradient(135deg,rgb(15, 71, 128) 0%, #42a5f5 100%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  marginBottom: theme.spacing(3),
  textAlign: 'center',
  letterSpacing: '-0.5px',
  lineHeight: 1.2,
  position: 'relative',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: '-16px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '80px',
    height: '4px',
    background: 'linear-gradient(90deg,rgb(58, 127, 196), #42a5f5)',
    borderRadius: '2px',
  }
}));

const LandingSubtitle = styled(Typography)(({ theme }) => ({
  fontSize: '1.8rem',
  fontWeight: 600,
  color: theme.palette.text.secondary,
  textAlign: 'center',
  maxWidth: '800px',
  margin: '0 auto',
  marginTop: theme.spacing(5),
  lineHeight: 1.5,
  letterSpacing: '0.3px',
}));

const StartButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(6),
  padding: '16px 40px',
  fontSize: '1.2rem',
  fontWeight: 600,
  borderRadius: '50px',
  textTransform: 'none',
  background: 'linear-gradient(135deg,rgb(25, 102, 180) 0%, #42a5f5 100%)',
  boxShadow: '0 4px 20px rgb(19, 110, 201)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 25px rgb(57, 124, 191)',
  }
}));

const HeroSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(8, 4),
  background: 'rgba(255, 255, 255, 0.95)',
  borderRadius: '24px',
  backdropFilter: 'blur(10px)',
  boxShadow: '0 8px 32px rgba(15, 71, 128, 0.08)',
  border: '1px solid rgba(66, 165, 245, 0.1)',
  maxWidth: '900px',
  margin: '0 auto',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    background: 'linear-gradient(90deg, rgb(15, 71, 128), #42a5f5)',
  }
}));

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [trendingWords, setTrendingWords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrendingWords = async () => {
      try {
        const words = await getTrendingWords();
        setTrendingWords(words);
      } catch (error) {
        console.error('Error fetching trending words:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchTrendingWords();
    }
  }, [user]);

  const createAnimationSequence = (words) => {
    const sequence = [];
    words.forEach((word, index) => {
      sequence.push(word.word);
      sequence.push(1000);
      sequence.push(' → ');
      sequence.push(500);
      sequence.push(`${word.word} → ${word.meaning}`);
      sequence.push(2000);
      if (index < words.length - 1) {
        sequence.push('');
        sequence.push(500);
      }
    });
    return sequence;
  };

  if (user) {
    return (
      <PageWrapper>
        <Container maxWidth="lg" sx={{ py: 6 }}>
          <WelcomeSection>
            <Typography variant="h3" gutterBottom>
              नमस्ते, {user.first_name || 'Learner'}!
            </Typography>
            <Typography variant="subtitle1">
              Ready to enhance your Hindi skills today?
            </Typography>
          </WelcomeSection>

          <TrendingSection>
            <Typography variant="h4">
              <TrendingUpIcon sx={{ fontSize: '1.8em' }} color="primary" />
              Today's Popular Words
            </Typography>

            <AnimatedText>
              {loading ? (
                'Loading trending words...'
              ) : trendingWords.length > 0 ? (
                <TypeAnimation
                  sequence={createAnimationSequence(trendingWords)}
                  wrapper="span"
                  speed={50}
                  repeat={Infinity}
                />
              ) : (
                'No trending words available'
              )}
            </AnimatedText>
          </TrendingSection>

          <Grid container spacing={3} justifyContent="center">
            <Grid item xs={12} sm={6} md={2.4}>
              <FeatureCard onClick={() => navigate('/transcripts')}>
                <IconWrapper>
                  <YouTubeIcon fontSize="large" />
                </IconWrapper>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    Add New Video
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Learn from YouTube videos
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FeatureCard onClick={() => navigate('/curated-videos')}>
                <IconWrapper>
                  <SchoolIcon fontSize="large" />
                </IconWrapper>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    Guided Learning
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Personalized learning from curated videos
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FeatureCard onClick={() => navigate('/practice')}>
                <IconWrapper>
                  <QuizIcon fontSize="large" />
                </IconWrapper>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    Practice Now
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Test your knowledge
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FeatureCard onClick={() => navigate('/vocabulary')}>
                <IconWrapper>
                  <TranslateIcon fontSize="large" />
                </IconWrapper>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    Look Up Words
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expand your vocabulary
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
            <Grid item xs={12} sm={6} md={2.4}>
              <FeatureCard onClick={() => navigate('/favorites')}>
                <IconWrapper>
                  <MenuBookIcon fontSize="large" />
                </IconWrapper>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                    My Favorites
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Review saved content
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
          </Grid>
        </Container>
      </PageWrapper>
    );
  }

  // Landing page for logged-out users
  return (
    <PageWrapper>
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
      <HeroSection>
          <LandingTitle variant="h1">
            Learn Hindi Through Videos
          </LandingTitle>
          <LandingSubtitle>
            Generate personalized questions from any Hindi YouTube video and improve your language skills
          </LandingSubtitle>
          <StartButton
            variant="contained"
            color="primary"
            onClick={() => navigate('/signup')}
          >
            Start Learning Now
          </StartButton>
      </HeroSection>

        <Grid container spacing={4} sx={{ mt: 8 }}>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard>
              <IconWrapper>
                <YouTubeIcon fontSize="large" />
              </IconWrapper>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  YouTube Integration
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Learn from any Hindi video
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard>
              <IconWrapper>
                <QuizIcon fontSize="large" />
              </IconWrapper>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Questions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Practice with smart quizzes
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard>
              <IconWrapper>
                <TranslateIcon fontSize="large" />
              </IconWrapper>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Word Lookup
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Build your vocabulary
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FeatureCard>
              <IconWrapper>
                <MenuBookIcon fontSize="large" />
              </IconWrapper>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Track Progress
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Monitor your learning
                </Typography>
              </CardContent>
            </FeatureCard>
          </Grid>
        </Grid>
      </Container>
    </PageWrapper>
  );
};

export default Home; 