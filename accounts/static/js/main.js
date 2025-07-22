// DOM references for main actions
const userTypeFilter = document.getElementById('user-type-filter');
const applyFiltersBtn = document.getElementById('apply-filters');
const resetFiltersBtn = document.getElementById('reset-filters');

/**
 * Get all table rows from the main table
 * @returns {NodeListOf<HTMLTableRowElement>}
 */
function getTableRows() {
    return document.querySelectorAll('.main-table tbody tr');
}

// Filter table rows by selected user type
function applyFilters() {
    const userTypeValue = userTypeFilter.value;
    getTableRows().forEach(row => {
        let showRow = true;
        if (userTypeValue !== 'all') {
            showRow = matchesUserType(row, userTypeValue);
        }
        row.style.display = showRow ? '' : 'none';
    });
}

/**
 * Check if a row matches the selected user type
 * @param {HTMLTableRowElement} row
 * @param {string} userTypeValue
 * @returns {boolean}
 */
function matchesUserType(row, userTypeValue) {
    const userTypeCell = row.querySelector('td:nth-child(3)');
    if (!userTypeCell) return true;
    const rowUserType = userTypeCell.textContent.trim();
    return rowUserType.toLowerCase().includes(userTypeValue.toLowerCase());
}

// Reset user type filter and show all rows
function resetFilters() {
    userTypeFilter.value = 'all';
    getTableRows().forEach(row => {
        row.style.display = '';
    });
}

// Attach event listeners after DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }
});

// Export document excel
document.addEventListener('DOMContentLoaded', function() {
    // Select the export button
    const exportBtn = document.getElementById('export-excel-btn');
    if(exportBtn) {
        exportBtn.addEventListener('click', exportToExcelXLSX);
    }
    function exportToExcelXLSX() {
        // Select table
        const table = document.querySelector('.main-table');
        if(!table) return;

        // Extract table headers
        const headers = []
        const ths = table.querySelectorAll('thead th');
        ths.forEach((header, idx) => {
            if(idx < ths.length - 1) {
                headers.push(header.textContent.trim());
            }
        });

        // Extract visible rows
        const data = []
        table.querySelectorAll('tbody tr').forEach(row => {
            if(row.style.display !== 'none') {
                const rowData = [];
                const tds = row.querySelectorAll('td');
                tds.forEach((cell, idx) => {
                    if(idx < tds.length - 1) {
                        rowData.push(cell.textContent.trim());
                    }
                });
                data.push(rowData);
            }
        });

        // Combine headers and data
        const ws_data = [headers, ...data];

        // Create spreadsheet
        const ws = XLSX.utils.aoa_to_sheet(ws_data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Datos");

        // Download file .xlsx
        XLSX.writeFile(wb, "UserAttendanceRecords.xlsx");
    }
});