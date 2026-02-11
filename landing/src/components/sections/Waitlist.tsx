import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
    Box,
    Container,
    Typography,
    TextField,
    Select,
    SelectChangeEvent,
    MenuItem,
    FormControl,
    InputLabel,
    Button,
    Alert,
    CircularProgress,
    Stack,
    Paper
} from '@mui/material';
import {
    Send as SendIcon,
    CheckCircle as CheckCircleIcon,
    AutoAwesome as SparklesIcon
} from '@mui/icons-material';

const Waitlist: React.FC = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [organization, setOrganization] = useState('');
  const [role, setRole] = useState<string>('');
  const [suggestions, setSuggestions] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const roleOptions = [
    "Student (Currently in school, university, or bootcamp)",
    "Working Professional (Employed in tech or a related field)",
    "Business Professional (Entrepreneur, startup founder, or executive)",
    "Open Source & Community Member (Contributor, maintainer, or community volunteer)",
    "Other:"
  ];

  const FORM_ID = '1FAIpQLSet1YnQTfOmfSzDblYxTXHSEHDhT4l7_LoqtN-5k-WUJAZUBw';
  const FORM_URL = `https://docs.google.com/forms/d/e/${FORM_ID}/formResponse`;

  const FIELD_MAPPINGS = {
    name: 'entry.1958162697',
    email: 'entry.1305603809',
    organization: 'entry.1486768385',
    role: 'entry.1449836771',
    suggestions: 'entry.1484217632'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (!name.trim() || !email.trim() || !organization.trim() || !role) {
        throw new Error('All fields are required except suggestions');
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        throw new Error('Please enter a valid email address');
      }

      const formData = new URLSearchParams();
      formData.append(FIELD_MAPPINGS.name, name);
      formData.append(FIELD_MAPPINGS.email, email);
      formData.append(FIELD_MAPPINGS.organization, organization);
      formData.append(FIELD_MAPPINGS.role, role);
      if (suggestions) {
        formData.append(FIELD_MAPPINGS.suggestions, suggestions);
      }

      await fetch(FORM_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });

      setSubmitted(true);
      toast.success('You have been added to the waitlist!');

      setEmail('');
      setName('');
      setOrganization('');
      setRole('');
      setSuggestions('');

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      component="section"
      id="waitlist"
      className="section relative overflow-hidden"
      sx={{
        position: 'relative',
        overflow: 'hidden',
        py: { xs: 8, md: 12 },
      }}
    >
      {/* Background decoration with blue */}
      <Box
        className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 blur-3xl"
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to bottom right, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.03), transparent, rgba(6, 182, 212, 0.05))',
          filter: 'blur(64px)',
        }}
      />
      <Box
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-full blur-3xl"
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '24rem',
          height: '24rem',
          background: 'linear-gradient(to right, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.08), rgba(6, 182, 212, 0.1))',
          borderRadius: '50%',
          filter: 'blur(64px)',
        }}
      />
      {/* Additional blue accent */}
      <Box
        sx={{
          position: 'absolute',
          top: '20%',
          right: '15%',
          width: '20rem',
          height: '20rem',
          borderRadius: '50%',
          background: 'linear-gradient(to right, rgba(37, 99, 235, 0.06), rgba(59, 130, 246, 0.04))',
          filter: 'blur(60px)',
        }}
      />

      <Container maxWidth="md" className="relative z-10" sx={{ position: 'relative', zIndex: 10 }}>
        <Box className="max-w-4xl mx-auto">
          {/* Gradient border container */}
          <Box
            className="relative p-[1px] bg-gradient-to-r from-primary via-secondary to-primary rounded-2xl"
            sx={{
              position: 'relative',
              padding: '1px',
              background: 'linear-gradient(to right, #22c55e, #3b82f6, #06b6d4, #2563eb, #22c55e)',
              borderRadius: '16px',
            }}
          >
            <Paper
              className="bg-dark/95 backdrop-blur-xl rounded-2xl p-8 md:p-12"
              sx={{
                backgroundColor: 'rgba(9, 9, 11, 0.95)',
                backdropFilter: 'blur(24px)',
                borderRadius: '15px',
                padding: { xs: 4, md: 6 },
              }}
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                <Stack
                  direction="row"
                  spacing={1}
                  justifyContent="center"
                  alignItems="center"
                  sx={{ mb: 2 }}
                >
                  <SparklesIcon sx={{ color: '#06b6d4', fontSize: 24 }} />
                  <Typography
                    variant="h3"
                    component="h2"
                    className="font-bold"
                    sx={{
                      fontWeight: 700,
                      fontSize: { xs: '2rem', md: '2.5rem' },
                      textAlign: 'center',
                      color: '#06b6d4',
                    }}
                  >
                    Join the{' '}
                    <Box
                      component="span"
                      className="gradient-text"
                      sx={{
                        background: 'linear-gradient(to right, #06b6d4, #3b82f6, #22d3ee, #2563eb, #4ade80)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        backgroundClip: 'text',
                      }}
                    >
                      Waitlist
                    </Box>
                  </Typography>
                  <SparklesIcon sx={{ color: '#06b6d4', fontSize: 24 }} />
                </Stack>
                <Typography
                  variant="body1"
                  className="text-gray-400 text-lg text-center"
                  sx={{
                    color: 'rgba(161, 161, 170, 1)',
                    fontSize: '1.125rem',
                    textAlign: 'center',
                    mb: 4,
                  }}
                >
                  Be among the first to experience Devr.AI and revolutionize your open-source community management.
                </Typography>
              </motion.div>

              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <Paper
                    sx={{
                      background: 'linear-gradient(to right, rgba(5, 150, 105, 0.4), rgba(16, 185, 129, 0.4))',
                      border: '1px solid rgba(34, 197, 94, 0.5)',
                      borderRadius: '12px',
                      padding: 4,
                      textAlign: 'center',
                      backdropFilter: 'blur(8px)',
                    }}
                  >
                    <Stack spacing={2} alignItems="center">
                      <CheckCircleIcon sx={{ color: '#4ade80', fontSize: 48 }} />
                      <Typography
                        variant="h5"
                        sx={{
                          fontWeight: 700,
                          color: '#86efac',
                        }}
                      >
                        Welcome to the future!
                      </Typography>
                      <Typography
                        variant="body1"
                        sx={{
                          color: 'rgba(209, 213, 219, 1)',
                          fontSize: '1.125rem',
                        }}
                      >
                        You're now on our exclusive waitlist. We'll notify you the moment early access becomes available.
                      </Typography>
                      <Box
                        sx={{
                          mt: 3,
                          p: 2,
                          backgroundColor: 'rgba(5, 150, 105, 0.2)',
                          borderRadius: '8px',
                          border: '1px solid rgba(34, 197, 94, 0.3)',
                        }}
                      >
                        <Typography
                          sx={{
                            color: '#4ade80',
                            fontWeight: 500,
                          }}
                        >
                          🎉 Keep an eye on your inbox for exciting updates!
                        </Typography>
                      </Box>
                    </Stack>
                  </Paper>
                </motion.div>
              ) : (
                <Box
                  component={motion.form}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2 }}
                  onSubmit={handleSubmit}
                  sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}
                >
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      <Alert
                        severity="error"
                        sx={{
                          backgroundColor: 'rgba(127, 29, 29, 0.4)',
                          border: '1px solid rgba(239, 68, 68, 0.5)',
                          borderRadius: '8px',
                          backdropFilter: 'blur(8px)',
                          '& .MuiAlert-icon': {
                            color: '#f87171',
                          },
                          '& .MuiAlert-message': {
                            color: '#fca5a5',
                            fontWeight: 500,
                          },
                        }}
                      >
                        {error}
                      </Alert>
                    </motion.div>
                  )}

                  <Box className="grid md:grid-cols-2 gap-6" sx={{ display: 'grid', gridTemplateColumns: { md: '1fr 1fr' }, gap: 3 }}>
                    <TextField
                      id="name"
                      name="name"
                      label="Full Name"
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      placeholder="Enter your full name"
                      fullWidth
                      className="relative group"
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(39, 39, 42, 0.8)',
                          backdropFilter: 'blur(8px)',
                          color: 'white',
                          borderRadius: '12px',
                          border: '1px solid rgba(63, 63, 70, 1)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            borderColor: 'rgba(82, 82, 91, 1)',
                          },
                          '&.Mui-focused': {
                            borderColor: 'rgba(34, 197, 94, 0.5)',
                            boxShadow: '0 0 0 2px rgba(34, 197, 94, 0.1)',
                          },
                          '& fieldset': {
                            border: 'none',
                          },
                        },
                        '& .MuiInputLabel-root': {
                          color: 'rgba(209, 213, 219, 1)',
                          fontWeight: 600,
                          fontSize: '0.875rem',
                          '&.Mui-focused': {
                            color: 'rgba(34, 197, 94, 1)',
                          },
                        },
                        '& .MuiInputBase-input': {
                          color: 'white',
                          '&::placeholder': {
                            color: 'rgba(113, 113, 122, 1)',
                            opacity: 1,
                          },
                        },
                      }}
                    />

                    <TextField
                      id="email"
                      name="email"
                      label="Email Address"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="your@email.com"
                      fullWidth
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(39, 39, 42, 0.8)',
                          backdropFilter: 'blur(8px)',
                          color: 'white',
                          borderRadius: '12px',
                          border: '1px solid rgba(63, 63, 70, 1)',
                          transition: 'all 0.3s ease',
                          '&:hover': {
                            borderColor: 'rgba(82, 82, 91, 1)',
                          },
                          '&.Mui-focused': {
                            borderColor: 'rgba(34, 197, 94, 0.5)',
                            boxShadow: '0 0 0 2px rgba(34, 197, 94, 0.1)',
                          },
                          '& fieldset': {
                            border: 'none',
                          },
                        },
                        '& .MuiInputLabel-root': {
                          color: 'rgba(209, 213, 219, 1)',
                          fontWeight: 600,
                          fontSize: '0.875rem',
                          '&.Mui-focused': {
                            color: 'rgba(34, 197, 94, 1)',
                          },
                        },
                        '& .MuiInputBase-input': {
                          color: 'white',
                          '&::placeholder': {
                            color: 'rgba(113, 113, 122, 1)',
                            opacity: 1,
                          },
                        },
                      }}
                    />
                  </Box>

                  <TextField
                    id="organization"
                    name="organization"
                    label="Organization"
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    required
                    placeholder="Your company, university, or organization"
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(39, 39, 42, 0.8)',
                        backdropFilter: 'blur(8px)',
                        color: 'white',
                        borderRadius: '12px',
                        border: '1px solid rgba(63, 63, 70, 1)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'rgba(82, 82, 91, 1)',
                        },
                        '&.Mui-focused': {
                          borderColor: 'rgba(59, 130, 246, 0.5)',
                          boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.15), 0 0 0 4px rgba(34, 197, 94, 0.1)',
                        },
                        '& fieldset': {
                          border: 'none',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: 'rgba(209, 213, 219, 1)',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        '&.Mui-focused': {
                          color: 'rgba(59, 130, 246, 1)',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: 'white',
                        '&::placeholder': {
                          color: 'rgba(113, 113, 122, 1)',
                          opacity: 1,
                        },
                      },
                    }}
                  />

                  <FormControl
                    fullWidth
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(39, 39, 42, 0.8)',
                        backdropFilter: 'blur(8px)',
                        color: 'white',
                        borderRadius: '12px',
                        border: '1px solid rgba(63, 63, 70, 1)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'rgba(82, 82, 91, 1)',
                        },
                        '&.Mui-focused': {
                          borderColor: 'rgba(59, 130, 246, 0.5)',
                          boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.15), 0 0 0 4px rgba(34, 197, 94, 0.1)',
                        },
                        '& fieldset': {
                          border: 'none',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: 'rgba(209, 213, 219, 1)',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        '&.Mui-focused': {
                          color: 'rgba(59, 130, 246, 1)',
                        },
                      },
                      '& .MuiSelect-select': {
                        color: 'white',
                        padding: '16px 14px',
                      },
                      '& .MuiSelect-icon': {
                        color: 'rgba(161, 161, 170, 1)',
                      },
                    }}
                  >
                    <InputLabel id="role-label">Your Role</InputLabel>
                    <Select
                      id="role"
                      name="role"
                      labelId="role-label"
                      value={role}
                      onChange={(e: SelectChangeEvent<string>) => setRole(e.target.value)}
                      required
                      MenuProps={{
                        PaperProps: {
                          sx: {
                            backgroundColor: 'rgba(39, 39, 42, 1)',
                            border: '1px solid rgba(63, 63, 70, 1)',
                            borderRadius: '12px',
                            mt: 1,
                            '& .MuiMenuItem-root': {
                              color: 'white',
                              '&:hover': {
                                backgroundColor: 'rgba(63, 63, 70, 1)',
                              },
                              '&.Mui-selected': {
                                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                                '&:hover': {
                                  backgroundColor: 'rgba(34, 197, 94, 0.3)',
                                },
                              },
                            },
                          },
                        },
                      }}
                    >
                      <MenuItem value="">
                        <em>Select your role</em>
                      </MenuItem>
                      {roleOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    id="suggestions"
                    name="suggestions"
                    label={
                      <>
                        Suggestions & Comments{' '}
                        <Box component="span" sx={{ color: 'rgba(113, 113, 122, 1)', fontWeight: 400 }}>
                          (optional)
                        </Box>
                      </>
                    }
                    multiline
                    rows={4}
                    value={suggestions}
                    onChange={(e) => setSuggestions(e.target.value)}
                    placeholder="Share your thoughts, feature requests, or any feedback..."
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(39, 39, 42, 0.8)',
                        backdropFilter: 'blur(8px)',
                        color: 'white',
                        borderRadius: '12px',
                        border: '1px solid rgba(63, 63, 70, 1)',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: 'rgba(82, 82, 91, 1)',
                        },
                        '&.Mui-focused': {
                          borderColor: 'rgba(59, 130, 246, 0.5)',
                          boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.15), 0 0 0 4px rgba(34, 197, 94, 0.1)',
                        },
                        '& fieldset': {
                          border: 'none',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: 'rgba(209, 213, 219, 1)',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        '&.Mui-focused': {
                          color: 'rgba(59, 130, 246, 1)',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: 'white',
                        '&::placeholder': {
                          color: 'rgba(113, 113, 122, 1)',
                          opacity: 1,
                        },
                      },
                    }}
                  />

                  <Stack
                    direction="column"
                    spacing={2}
                    alignItems="center"
                    sx={{ pt: 2 }}
                  >
                    {/* Enhanced Button with Premium Design */}
                    <motion.div
                      className="relative group w-full md:w-auto"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {/* Animated gradient border */}
                      <Box
                        className="absolute -inset-0.5 bg-gradient-to-r from-primary via-secondary to-primary rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300 group-hover:duration-200 animate-gradient-xy"
                        sx={{
                          position: 'absolute',
                          inset: '-2px',
                          background: 'linear-gradient(to right, #22c55e, #3b82f6, #06b6d4, #2563eb, #22c55e)',
                          borderRadius: '12px',
                          filter: 'blur(4px)',
                          opacity: 0.75,
                          transition: 'opacity 0.3s ease',
                          '&:hover': {
                            opacity: 1,
                          },
                        }}
                      />

                      {/* Glow effect on hover */}
                      <Box
                        className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-xl opacity-0 group-hover:opacity-70 transition-opacity duration-500"
                        sx={{
                          position: 'absolute',
                          inset: '-4px',
                          background: 'linear-gradient(to right, rgba(34, 197, 94, 0.5), rgba(59, 130, 246, 0.4), rgba(6, 182, 212, 0.5))',
                          borderRadius: '12px',
                          filter: 'blur(24px)',
                          opacity: 0,
                          transition: 'opacity 0.5s ease',
                          '&:hover': {
                            opacity: 0.7,
                          },
                        }}
                      />

                      {/* Button container with glassmorphism */}
                      <Box sx={{ position: 'relative' }}>
                        <Button
                          type="submit"
                          disabled={submitting}
                          variant="contained"
                          startIcon={
                            submitting ? (
                              <CircularProgress size={20} sx={{ color: 'white' }} />
                            ) : (
                              <SendIcon />
                            )
                          }
                          endIcon={!submitting && <SparklesIcon sx={{ fontSize: 16, opacity: 0.8 }} />}
                          className="relative w-full md:w-auto bg-gradient-to-r from-primary via-secondary to-primary text-white font-bold py-4 px-10 rounded-xl min-w-[280px] shadow-2xl shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed disabled:grayscale overflow-hidden group/btn"
                          sx={{
                            background: 'linear-gradient(to right, #22c55e, #3b82f6, #06b6d4, #2563eb, #22c55e)',
                            backgroundSize: '200% auto',
                            color: 'white',
                            fontWeight: 700,
                            padding: '16px 40px',
                            borderRadius: '12px',
                            minWidth: '280px',
                            boxShadow: '0 25px 50px -12px rgba(34, 197, 94, 0.25), 0 0 30px rgba(59, 130, 246, 0.15)',
                            textTransform: 'none',
                            fontSize: '1rem',
                            letterSpacing: '0.025em',
                            position: 'relative',
                            overflow: 'hidden',
                            '&:hover': {
                              backgroundPosition: 'right center',
                              boxShadow: '0 25px 50px -12px rgba(59, 130, 246, 0.4), 0 0 40px rgba(34, 197, 94, 0.3)',
                            },
                            '&:disabled': {
                              opacity: 0.5,
                              cursor: 'not-allowed',
                              filter: 'grayscale(100%)',
                            },
                            '&::before': {
                              content: '""',
                              position: 'absolute',
                              inset: 0,
                              background: 'linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent)',
                              transform: 'translateX(-100%)',
                              transition: 'transform 1s ease',
                            },
                            '&:hover::before': {
                              transform: 'translateX(100%)',
                            },
                          }}
                        >
                          {submitting ? 'Joining Waitlist...' : 'Join Waitlist'}
                        </Button>
                      </Box>
                    </motion.div>

                    <Stack spacing={1} alignItems="center" sx={{ textAlign: 'center' }}>
                      <Typography
                        variant="body2"
                        sx={{
                          color: 'rgba(161, 161, 170, 1)',
                          fontSize: '0.875rem',
                        }}
                      >
                        🚀 We'll notify you when early access becomes available
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: 'rgba(113, 113, 122, 1)',
                          fontSize: '0.75rem',
                        }}
                      >
                        Join{' '}
                        <Box component="span" sx={{ color: '#22c55e', fontWeight: 600 }}>
                          1000+
                        </Box>{' '}
                        developers already on the list
                      </Typography>
                    </Stack>
                  </Stack>
                </Box>
              )}
            </Paper>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Waitlist;