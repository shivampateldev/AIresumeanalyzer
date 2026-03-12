import * as React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const sampleData = [
  { name: 'Jan', uv: 400, pv: 2400, amt: 2400 },
  { name: 'Feb', uv: 300, pv: 1398, amt: 2210 },
  { name: 'Mar', uv: 200, pv: 9800, amt: 2290 },
  { name: 'Apr', uv: 278, pv: 3908, amt: 2000 },
  { name: 'May', uv: 189, pv: 4800, amt: 2181 },
  { name: 'Jun', uv: 239, pv: 3800, amt: 2500 },
  { name: 'Jul', uv: 349, pv: 4300, amt: 2100 },
];

export default function Dashboard() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to the Dashboard
      </Typography>
      <Paper sx={{ padding: 2, marginBottom: 2, bgcolor: 'background.paper', border: 1, borderColor: 'primary.main', borderRadius: 2 }} elevation={2}>
        <Typography variant="h6" color="primary">
          User Growth
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sampleData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="uv" stroke="#8884d8" activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="pv" stroke="#82ca9d" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
}
