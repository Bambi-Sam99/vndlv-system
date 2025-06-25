document.addEventListener('DOMContentLoaded', function() {
    // Existing verification code for plates and licenses
    document.getElementById('plateForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const plate = document.getElementById('plate').value;
        const response = await fetch('/verify_plate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plate_number: plate})
        });
        const data = await response.json();
        const resultDiv = document.getElementById('plateResult');
        if (data.status === 'found') {
            resultDiv.innerHTML = `Vehicle found: ${data.details.plate}, Owner: ${data.details.owner}, Status: ${data.details.status}, Model: ${data.details.model}`;
        } else {
            resultDiv.innerHTML = `Vehicle not found<br><button onclick="showReportForm('plate', '${plate}')">Report Issue</button>`;
        }
    });

    document.getElementById('licenseForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const license = document.getElementById('license').value;
        const response = await fetch('/verify_license', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({license_id: license})
        });
        const data = await response.json();
        const resultDiv = document.getElementById('licenseResult');
        if (data.status === 'found') {
            resultDiv.innerHTML = `Driver found: ${data.details.license_id}, Name: ${data.details.name}, Status: ${data.details.status}`;
        } else {
            resultDiv.innerHTML = `Driver not found<br><button onclick="showReportForm('license', '${license}')">Report Issue</button>`;
        }
    });

    // Function to show report form
    function showReportForm(type, id) {
        document.getElementById('reportType').value = type; // 'plate' or 'license'
        document.getElementById('reportId').value = id; // plate number or license ID
        document.getElementById('reportForm').style.display = 'block';
    }

    // Handle report form submission
    document.getElementById('reportIssueForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const reportType = document.getElementById('reportType').value;
        const reportId = document.getElementById('reportId').value;
        const comments = document.getElementById('comments').value;
        let body;
        if (reportType === 'plate') {
            body = JSON.stringify({plate_number: reportId, comments: comments});
        } else if (reportType === 'license') {
            body = JSON.stringify({license_id: reportId, comments: comments});
        }
        const response = await fetch('/report_issue', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: body
        });
        const data = await response.json();
        if (data.status === 'reported') {
            alert('Issue reported successfully');
            document.getElementById('reportForm').style.display = 'none';
        }
    });
});