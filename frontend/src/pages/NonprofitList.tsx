import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Pagination,
} from '@mui/material';

interface Nonprofit {
  id: number;
  ein: string;
  name: string;
  ntee_code: string;
  ntee_description: string;
  city: string;
  state: string;
  total_revenue: number;
  total_expenses: number;
  net_assets: number;
  mission_description: string;
  website: string;
}

const NonprofitList: React.FC = () => {
  const [nonprofits, setNonprofits] = useState<Nonprofit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNtee, setSelectedNtee] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const nteeOptions = [
    { code: '', label: 'All Categories' },
    { code: 'A20', label: 'Arts & Culture - Visual Arts' },
    { code: 'A25', label: 'Arts & Culture - Arts Education' },
    { code: 'B21', label: 'Education - Schools' },
    { code: 'B25', label: 'Education - Higher Education' },
    { code: 'B28', label: 'Education - Libraries' },
    { code: 'E20', label: 'Health - Hospitals' },
    { code: 'E21', label: 'Health - Community Centers' },
    { code: 'P20', label: 'Human Services - Housing' },
    { code: 'P21', label: 'Human Services - Youth Development' },
    { code: 'P24', label: 'Human Services - Emergency Aid' },
  ];

  const fetchNonprofits = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: '20',
        offset: ((page - 1) * 20).toString(),
      });
      
      if (searchTerm) params.append('search', searchTerm);
      if (selectedNtee) params.append('ntee_code', selectedNtee);

      const response = await fetch(`/api/nonprofits?${params}`);
      const data = await response.json();
      
      setNonprofits(data.nonprofits);
      setTotalPages(Math.ceil(data.total / 20));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching nonprofits:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNonprofits();
  }, [page, searchTerm, selectedNtee]);

  const formatCurrency = (value: number) => {
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value}`;
  };

  const handleSearch = () => {
    setPage(1);
    fetchNonprofits();
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Houston Nonprofits
      </Typography>

      {/* Search and Filter Controls */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search organizations"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedNtee}
                onChange={(e) => setSelectedNtee(e.target.value)}
                label="Category"
              >
                {nteeOptions.map((option) => (
                  <MenuItem key={option.code} value={option.code}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button variant="contained" onClick={handleSearch} fullWidth>
              Search
            </Button>
          </Grid>
        </Grid>
      </Box>

      {/* Loading Spinner */}
      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Nonprofit Cards */}
      {!loading && (
        <>
          <Grid container spacing={3}>
            {nonprofits.map((nonprofit) => (
              <Grid item xs={12} md={6} lg={4} key={nonprofit.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {nonprofit.name}
                    </Typography>
                    
                    <Chip 
                      label={nonprofit.ntee_description} 
                      size="small" 
                      sx={{ mb: 1 }}
                      color="primary"
                    />
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {nonprofit.mission_description?.substring(0, 150)}
                      {nonprofit.mission_description?.length > 150 && '...'}
                    </Typography>
                    
                    <Box sx={{ mt: 'auto' }}>
                      <Typography variant="body2">
                        <strong>EIN:</strong> {nonprofit.ein}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Location:</strong> {nonprofit.city}, {nonprofit.state}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Revenue:</strong> {formatCurrency(nonprofit.total_revenue || 0)}
                      </Typography>
                      {nonprofit.website && (
                        <Typography variant="body2">
                          <strong>Website:</strong>{' '}
                          <a 
                            href={nonprofit.website} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ color: 'inherit' }}
                          >
                            Visit
                          </a>
                        </Typography>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={4}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(event, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}

          {nonprofits.length === 0 && !loading && (
            <Box textAlign="center" mt={4}>
              <Typography variant="h6" color="text.secondary">
                No nonprofits found matching your search criteria.
              </Typography>
            </Box>
          )}
        </>
      )}
    </Container>
  );
};

export default NonprofitList;