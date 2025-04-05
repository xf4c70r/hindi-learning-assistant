import React from 'react';
import {
  AppBar,
  Toolbar,
  Button,
  Typography,
  Box,
  IconButton,
  useTheme,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../../context/AuthContext';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: 'white',
  color: theme.palette.text.primary,
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
}));

const NavButton = styled(Button)(({ theme }) => ({
  color: theme.palette.text.primary,
  margin: theme.spacing(0, 1),
  '&:hover': {
    backgroundColor: 'rgba(0,0,0,0.04)',
  },
}));

const Navbar = () => {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const isHomePage = location.pathname === '/';

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <StyledAppBar position="static">
      <Toolbar>
        {!isHomePage && (
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
        )}
        
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: theme.palette.primary.main,
            fontWeight: 'bold',
          }}
        >
          Hindi QA
        </Typography>

        {user && !isHomePage && (
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <NavButton component={RouterLink} to="/transcripts">
              Transcripts
            </NavButton>
            <NavButton component={RouterLink} to="/favorites">
              Favorites
            </NavButton>
            <NavButton component={RouterLink} to="/practice">
              Practice
            </NavButton>
          </Box>
        )}

        <Box sx={{ ml: 2 }}>
          {!user ? (
            <>
              <NavButton component={RouterLink} to="/login">
                Login
              </NavButton>
              <NavButton
                component={RouterLink}
                to="/signup"
                variant="contained"
                color="primary"
              >
                {isHomePage ? 'Get Started' : 'Sign up'}
              </NavButton>
            </>
          ) : (
            <NavButton
              onClick={handleLogout}
              variant="outlined"
              color="primary"
            >
              Logout
            </NavButton>
          )}
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
};

export default Navbar; 