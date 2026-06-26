const jobNames = JSON.parse(document.getElementById('job-names-data').textContent);
const applicationCounts = JSON.parse(document.getElementById('application-counts-data').textContent);

const ctx = document.getElementById('applicationsChart').getContext('2d');
const applicationsChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: jobNames,
        datasets: [{
            label: 'Applications per Job',
            data: applicationCounts,
            backgroundColor: 'rgba(30, 111, 99, 0.2)',
            borderColor: 'rgba(30, 111, 99, 1)',
            borderWidth: 2,
            borderRadius: 5,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    allowDecimal: false,
                    stepSize: 1
                }
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    }
});
