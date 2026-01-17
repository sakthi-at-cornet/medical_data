'use client';

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import { ChartData as ChartDataType } from '@/types';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
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
    // Defensive check: ensure data is an array
    const dataArray = Array.isArray(data) ? data : [];

    if (dataArray.length === 0) {
      return (
        <div className="chart-container">
          <p className="no-data">No data available for chart</p>
        </div>
      );
    }

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
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)',
          ],
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
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
        display: chart_type !== 'donut' && chart_type !== 'gauge' && chart_type !== 'kpi',
      },
      x: {
        ...backendOptions?.scales?.x,
        display: chart_type !== 'donut' && chart_type !== 'gauge' && chart_type !== 'kpi',
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

  if (chart_type === 'kpi') {
    const kpiData = chartData as any; // Assuming it has specific fields
    return (
      <div className="chart-container flex items-center justify-center">
        <div className="text-center p-6 bg-white rounded-lg shadow-sm border border-gray-100">
          <h3 className="text-gray-500 text-sm font-medium uppercase tracking-wider">{kpiData.label || 'Value'}</h3>
          <div className="mt-2 text-4xl font-bold text-gray-900">
            {typeof kpiData.value === 'number'
              ? kpiData.format === 'percent'
                ? `${kpiData.value.toFixed(1)}%`
                : kpiData.value.toLocaleString()
              : kpiData.value}
          </div>
        </div>
      </div>
    )
  }

  // Handle Gauge (using Doughnut) specially to display center value
  if (chart_type === 'gauge') {
    const centerValue = (chartData as any).centerValue;
    return (
      <div className="chart-container relative">
        <div className="chart-wrapper">
          <Doughnut data={chartJsData} options={options} />
        </div>
        {centerValue !== undefined && (
          <div className="absolute inset-0 flex items-center justify-center mt-10 pointer-events-none">
            <div className="text-3xl font-bold text-gray-800">
              {Math.round(centerValue)}%
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="chart-wrapper">
        {chart_type === 'bar' || chart_type === 'grouped_bar' ? (
          <Bar data={chartJsData} options={options} />
        ) : chart_type === 'donut' ? (
          <Doughnut data={chartJsData} options={options} />
        ) : (
          <Line data={chartJsData} options={options} />
        )}
      </div>
    </div>
  );
};
