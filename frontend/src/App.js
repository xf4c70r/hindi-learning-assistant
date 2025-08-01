import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import TranscriptsPage from './pages/TranscriptsPage';
import PracticePage from './pages/PracticePage';
import PracticeSetPage from './pages/PracticeSetPage';
import FavoritesPage from './pages/FavoritesPage';
import VocabularyPage from './pages/VocabularyPage';
import CuratedVideosPage from './pages/CuratedVideosPage';
import GuidedSessionPage from './pages/GuidedSessionPage';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/auth/PrivateRoute';
import PublicRoute from './components/auth/PublicRoute';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Layout>
            <Routes>
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Home />
                  </PrivateRoute>
                }
              />
              <Route
                path="/login"
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                }
              />
              <Route
                path="/signup"
                element={
                  <PublicRoute>
                    <Signup />
                  </PublicRoute>
                }
              />
              <Route
                path="/transcripts"
                element={
                  <PrivateRoute>
                    <TranscriptsPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/practice"
                element={
                  <PrivateRoute>
                    <PracticePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/practice/:setId"
                element={
                  <PrivateRoute>
                    <PracticeSetPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/favorites"
                element={
                  <PrivateRoute>
                    <FavoritesPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/vocabulary"
                element={
                  <PrivateRoute>
                    <VocabularyPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/curated-videos"
                element={
                  <PrivateRoute>
                    <CuratedVideosPage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/guided-session/:videoId"
                element={
                  <PrivateRoute>
                    <GuidedSessionPage />
                  </PrivateRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
