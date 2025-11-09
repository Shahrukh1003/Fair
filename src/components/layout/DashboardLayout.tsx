import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Chip,
  Divider,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  Dashboard,
  Analytics,
  Assessment,
  AdminPanelSettings,
  Logout,
  Menu as MenuIcon,
  Close,
  ChevronLeft,
  ChevronRight,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useLayout } from '../../contexts/LayoutContext';

const DRAWER_WIDTH = 280;
const DRAWER_WIDTH_COLLAPSED = 88;

const navigationItems = [
  {
    title: 'Overview',
    path: '/dashboard',
    icon: Dashboard,
    roles: ['admin', 'auditor', 'monitor'],
  },
  {
    title: 'Monitoring',
    path: '/dashboard/monitoring',
    icon: Analytics,
    roles: ['admin', 'auditor', 'monitor'],
  },
  {
    title: 'Compliance',
    path: '/dashboard/compliance',
    icon: Assessment,
    roles: ['admin', 'auditor'],
  },
  {
    title: 'Administration',
    path: '/dashboard/admin',
    icon: AdminPanelSettings,
    roles: ['admin'],
  },
];

export function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { user, logout } = useAuth();
  const { sidebarOpen, toggleSidebar } = useLayout();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
    handleMenuClose();
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'auditor':
        return 'warning';
      case 'monitor':
        return 'info';
      default:
        return 'default';
    }
  };

  const drawerWidth = sidebarOpen ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED;

  const drawer = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          p: sidebarOpen ? 3 : 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarOpen ? 'flex-start' : 'center',
          gap: 2,
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          transition: theme.transitions.create(['padding', 'justify-content'], {
            duration: theme.transitions.duration.standard,
            easing: theme.transitions.easing.easeInOut,
          }),
        }}
      >
        <Box
          sx={{
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            p: 1.5,
            borderRadius: 2,
            display: 'flex',
            boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
          }}
        >
          <Assessment sx={{ fontSize: 28, color: 'white' }} />
        </Box>
        {sidebarOpen && (
          <Box
            sx={{
              opacity: sidebarOpen ? 1 : 0,
              transition: theme.transitions.create('opacity', {
                duration: theme.transitions.duration.short,
                easing: theme.transitions.easing.easeInOut,
              }),
            }}
          >
            <Typography
              variant="h6"
              sx={{
                fontWeight: 900,
                color: 'white',
                letterSpacing: '-0.02em',
              }}
            >
              FairLens
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                fontSize: '0.7rem',
              }}
            >
              Enterprise v3.0
            </Typography>
          </Box>
        )}
      </Box>

      <List sx={{ flexGrow: 1, p: 2 }}>
        {navigationItems
          .filter((item) => user && item.roles.includes(user.role))
          .map((item) => {
            const isActive = location.pathname === item.path;
            const navButton = (
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                  if (mobileOpen) handleDrawerToggle();
                }}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  px: sidebarOpen ? 2 : 2,
                  justifyContent: sidebarOpen ? 'initial' : 'center',
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)'
                    : 'transparent',
                  border: isActive
                    ? '1px solid rgba(99, 102, 241, 0.3)'
                    : '1px solid transparent',
                  transition: theme.transitions.create(['background', 'padding', 'justify-content'], {
                    duration: theme.transitions.duration.standard,
                    easing: theme.transitions.easing.easeInOut,
                  }),
                  '&:hover': {
                    background: isActive
                      ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%)'
                      : 'rgba(255, 255, 255, 0.05)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? '#818cf8' : 'rgba(255, 255, 255, 0.7)',
                    minWidth: sidebarOpen ? 40 : 'auto',
                    justifyContent: 'center',
                    transition: theme.transitions.create('min-width', {
                      duration: theme.transitions.duration.standard,
                      easing: theme.transitions.easing.easeInOut,
                    }),
                  }}
                >
                  <item.icon />
                </ListItemIcon>
                {sidebarOpen && (
                  <ListItemText
                    primary={item.title}
                    primaryTypographyProps={{
                      fontWeight: isActive ? 600 : 500,
                      color: isActive ? 'white' : 'rgba(255, 255, 255, 0.8)',
                      fontSize: '0.95rem',
                    }}
                    sx={{
                      opacity: sidebarOpen ? 1 : 0,
                      transition: theme.transitions.create('opacity', {
                        duration: theme.transitions.duration.short,
                        easing: theme.transitions.easing.easeInOut,
                      }),
                    }}
                  />
                )}
              </ListItemButton>
            );

            return (
              <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
                {!sidebarOpen ? (
                  <Tooltip title={item.title} placement="right" arrow>
                    {navButton}
                  </Tooltip>
                ) : (
                  navButton
                )}
              </ListItem>
            );
          })}
      </List>

      <Box
        sx={{
          p: 2,
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        {sidebarOpen ? (
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              transition: theme.transitions.create('opacity', {
                duration: theme.transitions.duration.short,
                easing: theme.transitions.easing.easeInOut,
              }),
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.5)',
                display: 'block',
                mb: 0.5,
              }}
            >
              Logged in as
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: 'white',
                fontWeight: 600,
                mb: 1,
              }}
            >
              {user?.username}
            </Typography>
            <Chip
              label={user?.role.toUpperCase()}
              size="small"
              color={getRoleBadgeColor(user?.role || '')}
              sx={{ fontWeight: 600, fontSize: '0.7rem' }}
            />
          </Box>
        ) : (
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Tooltip title={`${user?.username} (${user?.role})`} placement="right" arrow>
              <Avatar
                sx={{
                  width: 40,
                  height: 40,
                  bgcolor: 'secondary.main',
                  fontSize: '1rem',
                  fontWeight: 700,
                }}
              >
                {user?.username.charAt(0).toUpperCase()}
              </Avatar>
            </Tooltip>
          </Box>
        )}
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          display: { md: 'none' },
          background: 'rgba(15, 23, 42, 0.95)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
            aria-label="toggle drawer"
          >
            {mobileOpen ? <Close /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            FairLens
          </Typography>
          <IconButton onClick={handleMenuClick} sx={{ color: 'white' }}>
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: 'secondary.main',
                fontSize: '0.9rem',
              }}
            >
              {user?.username.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawer}
      </Drawer>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            border: 'none',
            transition: theme.transitions.create('width', {
              duration: theme.transitions.duration.standard,
              easing: theme.transitions.easing.easeInOut,
            }),
            overflowX: 'hidden',
          },
        }}
      >
        {drawer}
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { xs: '100%', md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          bgcolor: '#f8fafc',
          pt: { xs: 8, md: 0 },
          transition: theme.transitions.create(['width', 'margin'], {
            duration: theme.transitions.duration.standard,
            easing: theme.transitions.easing.easeInOut,
          }),
        }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            px: 3,
            py: 2,
            borderBottom: '1px solid',
            borderColor: 'divider',
            bgcolor: 'white',
            boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
          }}
        >
          <IconButton
            onClick={toggleSidebar}
            sx={{
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'action.hover',
                transform: 'scale(1.05)',
              },
              transition: theme.transitions.create(['transform', 'background-color'], {
                duration: theme.transitions.duration.shorter,
              }),
            }}
            aria-label={sidebarOpen ? 'collapse sidebar' : 'expand sidebar'}
            aria-expanded={sidebarOpen}
          >
            {sidebarOpen ? <ChevronLeft /> : <ChevronRight />}
          </IconButton>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ textAlign: 'right', display: { xs: 'none', sm: 'block' } }}>
              <Typography variant="body2" fontWeight={600}>
                {user?.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.role}
              </Typography>
            </Box>
            <IconButton onClick={handleMenuClick}>
              <Avatar
                sx={{
                  width: 40,
                  height: 40,
                  bgcolor: 'secondary.main',
                }}
              >
                {user?.username.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
          </Box>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          slotProps={{
            paper: {
              sx: {
                mt: 1,
                minWidth: 180,
                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.12)',
                borderRadius: 2,
              },
            },
          }}
        >
          <MenuItem disabled>
            <Box>
              <Typography variant="body2" fontWeight={600}>
                {user?.username}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.role}
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          <MenuItem
            onClick={handleLogout}
            sx={{
              color: 'error.main',
              '&:hover': {
                bgcolor: 'error.50',
              },
            }}
          >
            <Logout sx={{ mr: 1, fontSize: 20 }} />
            Logout
          </MenuItem>
        </Menu>

        <Box
          sx={{
            p: { xs: 2, sm: 3, md: 4 },
            maxWidth: '1600px',
            mx: 'auto',
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
