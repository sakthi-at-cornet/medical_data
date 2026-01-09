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

  // Check if data is Chart.js format (has labels and datasets) or raw array
  const isChartJsFormat = data && typeof data === 'object' && 'labels' in data && 'datasets' in data;

  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className="chart-container">
        <p className="no-data">No data available</p>
      </div>
    );
  }

  let chartJsData;

  if (isChartJsFormat) {
    // Backend already sent Chart.js format - use it directly
    chartJsData = data as any;
  } else {
    // Legacy: Build Chart.js format from raw data array
    const dataArray = data as Array<Record<string, any>>;

    const labels = dataArray.map((item) => {
      const key = Object.keys(item).find((k) =>
        k.toLowerCase().includes(x_axis?.toLowerCase() || 'component') ||
        k.toLowerCase().includes('material') ||
        k.toLowerCase().includes('type')
      );
      return key ? String(item[key]) : 'Unknown';
    });

    const values = dataArray.map((item) => {
      const key = Object.keys(item).find((k) =>
        k.toLowerCase().includes(y_axis?.toLowerCase() || 'rate') ||
        k.toLowerCase().includes('units') ||
        k.toLowerCase().includes('score')
      );
      return key ? parseFloat(item[key]) || 0 : 0;
    });

    chartJsData = {
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
  }

  // Get options from backend if available, otherwise use defaults
  const backendOptions = chartData.options || {};

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        ...backendOptions?.plugins?.legend,
      },
      title: {
        display: !!title || !!backendOptions?.plugins?.title?.text,
        text: backendOptions?.plugins?.title?.text || title || '',
        ...backendOptions?.plugins?.title,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        // Don't constrain max - let Chart.js auto-scale based on data
        ...backendOptions?.scales?.y,
      },
      x: {
        ...backendOptions?.scales?.x,
      },
    },
    ...backendOptions,
  };

  if (chart_type === 'table') {
    // For table, always use raw data array
    const dataArray = isChartJsFormat ? [] : (data as Array<Record<string, any>>);

    if (dataArray.length === 0) {
      return (
        <div className="chart-container">
          <p className="no-data">No table data available</p>
        </div>
      );
    }

    return (
      <div className="chart-container">
        <h3 className="chart-title">{title}</h3>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {Object.keys(dataArray[0]).map((key) => (
                  <th key={key}>{key.split('.').pop()}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataArray.map((row, idx) => (
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
