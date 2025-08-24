import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Divider,
} from '@mui/material';

interface Nonprofit {
  id: number;
  ein: string;
  name: string;
  ntee_code: string;
  ntee_description: string;
  city: string;
  state: string;
  street_address: string;
  zip_code: string;
  total_revenue: number;
  total_expenses: number;
  net_assets: number;
  mission_description: string;
  program_description: string;
  activities_description: string;
  website: string;
  phone: string;
}

const NonprofitDetail: React.FC = () => {
  const { ein } = useParams<{ ein: string }>();
  const [nonprofit, setNonprofit] = useState<Nonprofit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNonprofit = async () => {
      try {
        // For now, we'll fetch from the list and find the matching EIN
        // In a real implementation, you'd have a specific endpoint like /api/nonprofit/{ein}
        const response = await fetch('/api/nonprofits?limit=100');
        const data = await response.json();
        
        const foundNonprofit = data.nonprofits.find((np: Nonprofit) => np.ein === ein);
        
        if (foundNonprofit) {
          setNonprofit(foundNonprofit);
        } else {
          setError('Nonprofit not found');
        }
        setLoading(false);
      } catch (err) {
        setError('Error loading nonprofit details');
        setLoading(false);
      }
    };

    if (ein) {
      fetchNonprofit();
    }
  }, [ein]);

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value}`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !nonprofit) {
    return (
      <Container maxWidth="lg">
        <Typography variant="h6" color="error" textAlign="center" mt={4}>
          {error || 'Nonprofit not found'}
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 2, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          {nonprofit.name}
        </Typography>
        
        <Chip 
          label={nonprofit.ntee_description} 
          color="primary" 
          sx={{ mb: 2 }}
        />

        <Grid container spacing={3}>
          {/* Main Information */}
          <Grid item xs={12} md={8}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Mission Statement
                </Typography>
                <Typography variant="body1" paragraph>
                  {nonprofit.mission_description || 'No mission statement available.'}
                </Typography>

                {nonprofit.program_description && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Programs & Services
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {nonprofit.program_description}
                    </Typography>
                  </>
                )}

                {nonprofit.activities_description && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      Activities
                    </Typography>
                    <Typography variant="body1" paragraph>
                      {nonprofit.activities_description}
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Sidebar Information */}
          <Grid item xs={12} md={4}>
            {/* Contact Information */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Contact Information
                </Typography>
                
                <Typography variant="body2" gutterBottom>
                  <strong>EIN:</strong> {nonprofit.ein}
                </Typography>
                
                {nonprofit.street_address && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Address:</strong><br />
                    {nonprofit.street_address}<br />
                    {nonprofit.city}, {nonprofit.state} {nonprofit.zip_code}
                  </Typography>
                )}
                
                {!nonprofit.street_address && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Location:</strong> {nonprofit.city}, {nonprofit.state}
                  </Typography>
                )}

                {nonprofit.phone && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Phone:</strong> {nonprofit.phone}
                  </Typography>
                )}

                {nonprofit.website && (
                  <Typography variant="body2" gutterBottom>
                    <strong>Website:</strong>{' '}
                    <a 
                      href={nonprofit.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ color: 'inherit' }}
                    >
                      {nonprofit.website}
                    </a>
                  </Typography>
                )}
              </CardContent>
            </Card>

            {/* Financial Information */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Financial Information
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Revenue
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(nonprofit.total_revenue || 0)}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Expenses
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(nonprofit.total_expenses || 0)}
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Net Assets
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(nonprofit.net_assets || 0)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default NonprofitDetail;