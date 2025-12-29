<template>
  <div class="chart-container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({}),
  },
});

const getThemeColor = (variable) => {
  return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
};

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  scales: {
    x: {
      beginAtZero: true,
      max: 100,
      min: 0,
      ticks: { display: false },
      grid: { display: false },
    },
    y: {
      grid: { display: false },
      ticks: {
        display: true,
        font: { weight: 'bold', size: 14 },
        color: getThemeColor('--colortext') || '#666', // Theme aware text
      },
    },
  },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
    datalabels: {
      display: true,
      align: context => {
        const value = context.dataset.data[context.dataIndex];
        return value === 0 || value < 10 ? 'center' : 'end';
      },
      anchor: context => {
        const value = context.dataset.data[context.dataIndex];
        return value === 0 || value < 10 ? 'center' : 'end';
      },
      color: context => {
        const value = context.dataset.data[context.dataIndex];
        // If bar is very small, text might be on background (dark/light), otherwise on bar (white)
        // usage of mix-blend-mode in CSS handles this better for DOM elements, but this is canvas.
        // For now, simpler logic:
        return value === 0 || value < 10 ? getThemeColor('--colortext') : '#ffffff';
      },
      font: { weight: 'bold', size: 14 },
      formatter: value => `${value}%`,
    },
  },
  elements: {
    bar: {
      borderRadius: 10,
      backgroundColor: getThemeColor('--colorprimary') || '#3b82f6',
    },
  },
}));

const renderChart = () => {
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(canvas.value, {
    type: 'bar',
    data: props.chartData,
    options: { ...chartOptions.value, ...props.options },
    plugins: [ChartDataLabels],
  });
};

onMounted(() => {
    // Initial render
    renderChart();
    
    // Optional: Refresh on theme change if needed (could rely on a prop or store, but simple re-render works)
    // A simple way to catch theme changes is watching the class on body if we had a global state for it.
    // For now, simple mount read is a huge improvement over hardcoded #007bff.
});

watch(() => props.chartData, renderChart, { deep: true });
watch(() => props.options, renderChart, { deep: true });
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
