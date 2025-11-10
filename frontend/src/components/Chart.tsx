'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { ChartData as ChartDataType } from '@/types';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

interface ChartProps {
  chartData: ChartDataType;
}

export const Chart: React.FC<ChartProps> = ({ chartData }) => {
  const { chart_type, data, x_axis, y_axis, title } = chartData;

  if (!data || data.length === 0) {
    return (
      <div className="chart-container">
        <p className="no-data">No data available</p>
      </div>
    );
  }

  // Extract labels and values from data
  const labels = data.map((item) => {
    // Find the x-axis value
    const key = Object.keys(item).find((k) =>
      k.toLowerCase().includes(x_axis?.toLowerCase() || 'component') ||
      k.toLowerCase().includes('material') ||
      k.toLowerCase().includes('type')
    );
    return key ? String(item[key]) : 'Unknown';
  });

  const values = data.map((item) => {
    // Find the y-axis value (numeric)
    const key = Object.keys(item).find((k) =>
      k.toLowerCase().includes(y_axis?.toLowerCase() || 'rate') ||
      k.toLowerCase().includes('units') ||
      k.toLowerCase().includes('score')
    );
    return key ? parseFloat(item[key]) || 0 : 0;
  });

  const chartJsData = {
    labels,
    datasets: [
      {
        label: y_axis || 'Value',
        data: values,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: !!title,
        text: title || '',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (chart_type === 'table') {
    return (
      <div className="chart-container">
        <h3 className="chart-title">{title}</h3>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {Object.keys(data[0]).map((key) => (
                  <th key={key}>{key.split('.').pop()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr key={idx}>
                  {Object.values(row).map((value, vIdx) => (
                    <td key={vIdx}>{String(value)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        {chart_type === 'bar' ? (
          <Bar data={chartJsData} options={options} />
        ) : (
          <Line data={chartJsData} options={options} />
        )}
      </div>
    </div>
  );
};
