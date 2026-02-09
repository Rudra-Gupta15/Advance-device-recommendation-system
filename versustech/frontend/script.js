const API_URL = 'http://127.0.0.1:5001/api';

// Handle Initial Category Selection (index.html)
function selectCategory(cat) {
    localStorage.setItem('temp_category', cat);
    window.location.href = 'form.html';
}

// Handle Recommendation Form
const recommendForm = document.getElementById('recommendForm');

function toggleCategorySpecs() {
    const category = document.getElementById('category').value;
    const cpuGroup = document.getElementById('cpu-group');
    const cpuLabel = document.getElementById('cpu-label');
    const rtxGroup = document.getElementById('rtx-group');
    const modeGroup = document.getElementById('mode-group'); // Added ID in form.html

    const laptopMockup = document.getElementById('laptop-mockup-container');
    const mobileMockup = document.getElementById('mobile-mockup-container');

    const formTitle = document.getElementById('form-title');

    if (category === 'mobile') {
        if (formTitle) formTitle.innerText = "Mobile Preferences";
        cpuLabel.innerText = "Minimum Processor Power";

        // Hide specific elements for Mobile as requested
        rtxGroup.style.display = 'none';
        if (modeGroup) modeGroup.style.display = 'none';
        if (cpuGroup) cpuGroup.style.display = 'none'; // Remove processor power input

        laptopMockup.style.display = 'none';
        mobileMockup.style.display = 'block';
    } else {
        if (formTitle) formTitle.innerText = "Laptop Preferences";
        cpuLabel.innerText = "Minimum CPU Power";

        // Show elements for Laptop
        rtxGroup.style.display = 'flex';
        if (modeGroup) modeGroup.style.display = 'block'; // Restore User Mode
        if (cpuGroup) cpuGroup.style.display = 'block';   // Restore CPU Power

        laptopMockup.style.display = 'flex';
        mobileMockup.style.display = 'none';
    }

    // Filter Primary Use Options
    const prefSelect = document.getElementById('preference');
    if (prefSelect) {
        for (let i = 0; i < prefSelect.options.length; i++) {
            const opt = prefSelect.options[i];
            if (opt.value === 'camera') {
                opt.style.display = (category === 'mobile') ? 'block' : 'none';
                if (category === 'laptop' && prefSelect.value === 'camera') {
                    prefSelect.value = 'gaming'; // Default to something else if hidden
                }
            }
        }
    }
    updateBrandDropdown(category);
    updateMockup();
}

const BRANDS = {
    mobile: ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi", "Nothing", "Realme", "Motorola", "IQOO", "Vivo", "Asus"],
    laptop: ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "MSI", "Microsoft", "Samsung", "Razer", "Gigabyte", "LG", "Xiaomi"]
};

function updateBrandDropdown(category) {
    const brandSelect = document.getElementById('brand');
    if (!brandSelect) return;

    // Keep the "Any Brand" option
    brandSelect.innerHTML = '<option value="">Any Brand</option>';

    const brandList = BRANDS[category] || [];
    brandList.sort().forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandSelect.appendChild(option);
    });
}

function updateMockup() {
    const category = document.getElementById('category').value;
    const ram = document.getElementById('min_ram').value;
    const storage = document.getElementById('min_storage').value;

    // We only update status message for mobile in ditto look
    if (category === 'mobile') {
        const status = document.getElementById('m-status');
        if (status) status.innerText = "5G Ready";
    }
}

// Add listeners for real-time update
['min_ram', 'min_storage', 'min_cpu', 'needs_rtx'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', updateMockup);
});

// Attach event listener for category change
const categorySelect = document.getElementById('category');
if (categorySelect) {
    categorySelect.addEventListener('change', toggleCategorySpecs);
    // Initial call
    toggleCategorySpecs();
}

if (recommendForm) {
    recommendForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            category: document.getElementById('category').value,
            budget: document.getElementById('budget').value,
            mode: document.getElementById('mode').value,
            preference: document.getElementById('preference').value,
            brand: document.getElementById('brand').value,
            min_ram: document.getElementById('min_ram').value,
            min_storage: document.getElementById('min_storage').value,
            min_cpu: document.getElementById('min_cpu').value,
            needs_rtx: document.getElementById('needs_rtx').checked
        };

        try {
            const response = await fetch(`${API_URL}/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            localStorage.setItem('recommendations', JSON.stringify(data));
            localStorage.setItem('category', payload.category);
            window.location.href = 'results.html';
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to backend. Please ensure Flask app is running.');
        }
    });

    // Handle pre-selection
    const tempCat = localStorage.getItem('temp_category');
    if (tempCat) {
        document.getElementById('category').value = tempCat;
        toggleCategorySpecs();
        localStorage.removeItem('temp_category');
    }

    // Event Listeners for Form Interactivity
    const categorySelect = document.getElementById('category');
    if (categorySelect) {
        categorySelect.addEventListener('change', () => {
            toggleCategorySpecs();
            updateFormOptions();
        });
    }

    // Dynamic Options Update
    const budgetInput = document.getElementById('budget');

    async function updateFormOptions() {
        const category = document.getElementById('category').value;
        const budget = document.getElementById('budget').value;
        const ramSelect = document.getElementById('min_ram');
        const storageSelect = document.getElementById('min_storage');
        const cpuSelect = document.getElementById('min_cpu'); // Only for laptops usually but checking logic

        try {
            const response = await fetch(`${API_URL}/options`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, budget })
            });
            const options = await response.json();

            // Helper to update select
            const updateSelect = (select, values, suffix) => {
                const currentVal = select.value;
                select.innerHTML = '<option value="0">Any</option>';
                values.forEach(val => {
                    const opt = document.createElement('option');
                    opt.value = val;
                    opt.textContent = `${val}${suffix}`;
                    select.appendChild(opt);
                });
                // Restore value if invalid set to 0
                if (values.includes(parseInt(currentVal))) {
                    select.value = currentVal;
                }
            };

            if (options.ram && ramSelect) updateSelect(ramSelect, options.ram, 'GB+');
            if (options.storage && storageSelect) updateSelect(storageSelect, options.storage, 'GB+');

        } catch (e) {
            console.error("Failed to fetch dynamic options", e);
        }
    }

    // Debounce budget input
    let timeout = null;
    if (budgetInput) {
        budgetInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(updateFormOptions, 500);
        });
        // Initial call
        updateFormOptions();
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', () => {
            toggleCategorySpecs();
            updateFormOptions();
        });
    }
}

// Display Results
let selectedItems = [];

function displayResults(data) {
    const grid = document.getElementById('resultsGrid');
    const bestContainer = document.getElementById('bestMatchContainer');

    if (!grid) return;

    // Handle different data formats (Old Array vs New Object)
    let recommendations = [];
    let bestMatch = null;

    if (Array.isArray(data)) {
        recommendations = data;
    } else if (data && data.recommendations) {
        recommendations = data.recommendations;
        bestMatch = data.best_match;
    }

    grid.innerHTML = '';

    if (recommendations.length === 0) {
        grid.innerHTML = '<p style="text-align: center; grid-column: 1/-1;">No recommendations found. Try adjusting filters.</p>';
        return;
    }

    recommendations.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'horizontal-card';
        card.onclick = () => toggleSelection(index, item);
        card.dataset.item = JSON.stringify(item);

        const score = Math.round(item.final_score * 100);
        const isMobile = localStorage.getItem('category') === 'mobile';

        // Icons Logic
        let specsHTML = '';
        if (isMobile) {
            specsHTML = `
                <div class="spec-item"><i>📱</i> <span>${item.screen_size || '6.5"'}</span></div>
                <div class="spec-item"><i>💾</i> <span>${item.ram}GB</span></div>
                <div class="spec-item"><i>💿</i> <span>${item.storage}GB</span></div>
                <div class="spec-item"><i>🔋</i> <span>${item.battery}mAh</span></div>
             `;
        } else {
            // Laptop Icons: Screen, Weight, RAM, Storage
            // Use ⚖️ for weight
            specsHTML = `
                <div class="spec-item"><i>💻</i> <span>${item.screen_size || '15.6"'}</span></div>
                <div class="spec-item"><i>⚖️</i> <span>${item.weight || '1.8 kg'}</span></div>
                <div class="spec-item"><i>💾</i> <span>${item.ram}GB</span></div>
                <div class="spec-item"><i>💿</i> <span>${item.storage}GB</span></div>
             `;
        }

        // Image Placeholder
        const imgUrl = item.img_url || (isMobile ? 'https://cdn-icons-png.flaticon.com/512/644/644458.png' : 'https://cdn-icons-png.flaticon.com/512/428/428001.png');

        card.innerHTML = `
            <div class="score-badge-circle">
                <span class="score-val">${score}</span>
                <span class="score-label">Points</span>
            </div>
            
            <div class="card-img-side">
                <img src="${imgUrl}" alt="${item.model}" onerror="this.src='logo.jpg'"> 
            </div>
            
            <div class="card-info-side">
                <h3 class="h-card-title">${item.model}</h3>
                <div class="h-card-price">₹${item.price.toLocaleString('en-IN')}</div>
                <div class="spec-grid">
                    ${specsHTML}
                </div>
            </div>
            
            <button class="add-btn">+</button>
        `;
        grid.appendChild(card);
    });

    // Render Best Match Sidebar (List of 5)
    bestContainer.innerHTML = ''; // Clear previous

    // bestMatch is now an array (or single object if backend not updated yet, handle both)
    let bestItems = [];
    if (Array.isArray(bestMatch)) {
        bestItems = bestMatch;
    } else if (bestMatch) {
        bestItems = [bestMatch];
    }

    if (bestItems.length > 0) {
        const isMobile = localStorage.getItem('category') === 'mobile';

        bestItems.forEach(match => {
            let specsHTML = '';
            if (isMobile) {
                specsHTML = `
                    <div class="best-spec-item"><span>RAM</span><strong>${match.ram}GB</strong></div>
                    <div class="best-spec-item"><span>Stor</span><strong>${match.storage}GB</strong></div>
                 `;
            } else {
                specsHTML = `
                     <div class="best-spec-item"><span>RAM</span><strong>${match.ram}GB</strong></div>
                     <div class="best-spec-item"><span>SSD</span><strong>${match.storage}GB</strong></div>
                 `;
            }

            const bestCard = document.createElement('div');
            bestCard.className = 'best-card';
            bestCard.style.marginBottom = '20px'; // Spacing between items

            bestCard.innerHTML = `
                <h4 style="font-size: 1.1rem; margin-bottom: 5px;">${match.model}</h4>
                <div class="price" style="font-size: 1.2rem; margin-bottom: 10px;">₹${match.price.toLocaleString('en-IN')}</div>
                <div class="best-specs" style="margin-bottom: 10px;">
                    ${specsHTML}
                </div>
                <a href="${match.amazon_link || '#'}" target="_blank" class="btn btn-primary" style="padding: 8px 15px; font-size: 0.8rem;">View Deal</a>
            `;
            bestContainer.appendChild(bestCard);
        });
    } else {
        bestContainer.innerHTML = '<p style="text-align:center; color:#666;">No Best Pick available.</p>';
    }
}

function toggleSelection(index, product) {
    const cards = document.querySelectorAll('.horizontal-card');
    const card = cards[index];

    if (card.classList.contains('selected')) {
        card.classList.remove('selected');
        selectedItems = selectedItems.filter(item => item.name !== product.name);
    } else {
        if (selectedItems.length >= 2) {
            alert("Delete one selection first to choose another.");
            return;
        }
        card.classList.add('selected');
        selectedItems.push(product);
    }

    const compareBtn = document.getElementById('compareBtn');
    if (selectedItems.length === 2) {
        compareBtn.style.display = 'block';
        compareBtn.onclick = () => {
            localStorage.setItem('selectedForCompare', JSON.stringify(selectedItems));
            window.location.href = 'compare.html';
        };
    } else {
        compareBtn.style.display = 'none';
    }
}

// Render Comparison
async function renderComparison(item1, item2, category) {
    const hero1 = document.getElementById('hero1');
    const hero2 = document.getElementById('hero2');
    const reasons1 = document.getElementById('reasons1');
    const reasons2 = document.getElementById('reasons2');

    // 1. Render Hero Section
    const score1 = Math.round(item1.final_score * 100);
    const score2 = Math.round(item2.final_score * 100);

    const isMobile = category === 'mobile';
    const img1 = item1.img_url || (isMobile ? 'https://cdn-icons-png.flaticon.com/512/644/644458.png' : 'https://cdn-icons-png.flaticon.com/512/428/428001.png');
    const img2 = item2.img_url || (isMobile ? 'https://cdn-icons-png.flaticon.com/512/644/644458.png' : 'https://cdn-icons-png.flaticon.com/512/428/428001.png');

    hero1.innerHTML = `
        <div class="score-badge-circle" style="left: -10px; top: -10px;">${score1}<span style="font-size:0.6rem; display:block;">POINTS</span></div>
        <h2 style="font-size: 1.1rem; margin-bottom: 20px;">${item1.model || item1.name}</h2>
        <img src="${img1}" style="width: 100%; max-width: 250px; border-radius: 10px;">
        <div class="price-tag-hero">₹${item1.price.toLocaleString()}</div>
        <a href="${item1.amazon_link || '#'}" target="_blank" class="btn btn-primary-outline btn-sm">Check Price</a>
    `;

    hero2.innerHTML = `
        <div class="score-badge-circle" style="right: -10px; top: -10px;">${score2}<span style="font-size:0.6rem; display:block;">POINTS</span></div>
        <h2 style="font-size: 1.1rem; margin-bottom: 20px;">${item2.model || item2.name}</h2>
        <img src="${img2}" style="width: 100%; max-width: 250px; border-radius: 10px;">
        <div class="price-tag-hero">₹${item2.price.toLocaleString()}</div>
        <a href="${item2.amazon_link || '#'}" target="_blank" class="btn btn-primary-outline btn-sm">Check Price</a>
    `;

    // 2. Radar Chart Logic
    const ctx = document.getElementById('comparisonChart').getContext('2d');

    // Normalize Data (0-100)
    const norm = (val, max) => Math.min(100, Math.max(20, (val / max) * 100));

    let data1, data2, labels;
    if (isMobile) {
        labels = ['RAM', 'Storage', 'Battery', 'Camera', 'Display', 'Value'];
        data1 = [
            norm(item1.ram, 16),
            norm(item1.storage, 512),
            norm(item1.battery, 6000),
            norm(item1.camera, 108),
            norm(parseFloat(item1.screen_size) || 6.5, 7),
            score1
        ];
        data2 = [
            norm(item2.ram, 16),
            norm(item2.storage, 512),
            norm(item2.battery, 6000),
            norm(item2.camera, 108),
            norm(parseFloat(item2.screen_size) || 6.5, 7),
            score2
        ];
    } else {
        // Laptop
        labels = ['Performance (CPU)', 'Graphics (GPU)', 'Memory (RAM)', 'Storage', 'Portability', 'Value'];
        data1 = [
            norm(item1.cpu_score, 100),
            norm(item1.gpu_score, 100),
            norm(item1.ram, 64),
            norm(item1.storage, 2048),
            100 - norm(parseFloat(item1.weight) || 2.0, 4.0), // Invert weight (lighter is better)
            score1
        ];
        data2 = [
            norm(item2.cpu_score, 100),
            norm(item2.gpu_score, 100),
            norm(item2.ram, 64),
            norm(item2.storage, 2048),
            100 - norm(parseFloat(item2.weight) || 2.0, 4.0),
            score2
        ];
    }

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: item1.model,
                data: data1,
                fill: true,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgb(255, 99, 132)',
                pointBackgroundColor: 'rgb(255, 99, 132)',
            }, {
                label: item2.model,
                data: data2,
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
            }]
        },
        options: {
            elements: { line: { borderWidth: 3 } },
            scales: { r: { min: 0, max: 100, ticks: { display: false } } }
        }
    });

    // 3. Generate Spec Showdown
    const showdownContainer = document.getElementById('specShowdown');
    if (showdownContainer) {
        showdownContainer.innerHTML = ''; // Clear previous

        const createSpecRow = (label, val1Raw, val2Raw, unit = '', higherIsBetter = true) => {
            let val1 = parseFloat(String(val1Raw).replace(/[^0-9.]/g, '')) || 0;
            let val2 = parseFloat(String(val2Raw).replace(/[^0-9.]/g, '')) || 0;

            // Handle specific logic for known fields if raw parsing isn't enough
            if (label === 'Score') { val1 = score1; val2 = score2; }

            let class1 = '';
            let class2 = '';

            if (val1 !== val2) {
                const isBetter = higherIsBetter ? (val1 > val2) : (val1 < val2);
                if (isBetter) class1 = 'winner-glow';
                else class2 = 'winner-glow';
            }

            const row = document.createElement('div');
            row.className = 'spec-row';
            row.innerHTML = `
                <div class="spec-val ${class1}">${val1Raw}${unit}</div>
                <div class="spec-label">${label}</div>
                <div class="spec-val ${class2}">${val2Raw}${unit}</div>
            `;
            return row;
        };

        const attributes = isMobile
            ? [
                { label: 'RAM', key: 'ram', unit: 'GB' },
                { label: 'Storage', key: 'storage', unit: 'GB' },
                { label: 'Battery', key: 'battery', unit: 'mAh' },
                { label: 'Camera', key: 'camera', unit: 'MP' },
                { label: 'Screen', key: 'screen_size', unit: '"' }
            ]
            : [
                { label: 'RAM', key: 'ram', unit: 'GB' },
                { label: 'Storage', key: 'storage', unit: 'GB' },
                { label: 'Weight', key: 'weight', unit: 'kg', lowBetter: true },
                { label: 'CPU Score', key: 'cpu_score', unit: ' pts' },
                { label: 'GPU Score', key: 'gpu_score', unit: ' pts' }
            ];

        // Add Header
        const header = document.createElement('div');
        header.className = 'spec-header';
        header.innerHTML = `
            <div>${item1.model}</div>
            <div>VS</div>
            <div>${item2.model}</div>
         `;
        showdownContainer.appendChild(header);

        attributes.forEach(attr => {
            const val1 = item1[attr.key] || 0;
            const val2 = item2[attr.key] || 0;
            // CPU/GPU scores for laptops might be directly in the item or calculated, assuming they are in item based on chart logic

            showdownContainer.appendChild(createSpecRow(
                attr.label,
                val1,
                val2,
                attr.unit,
                !attr.lowBetter
            ));
        });
    }
}







async function showPrices(name) {
    try {
        const response = await fetch(`${API_URL}/get_prices?name=${encodeURIComponent(name)}`);
        const links = await response.json();
        const win = window.open("", "_blank", "width=400,height=300");
        win.document.write(`
            <div style="font-family: sans-serif; padding: 20px; background: #0f172a; color: white; height: 100%;">
                <h3>Price Links for ${name}</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 10px 0;"><a href="${links.amazon}" target="_blank" style="color: #00f2fe;">Amazon</a></li>
                    <li style="margin: 10px 0;"><a href="${links.flipkart}" target="_blank" style="color: #00f2fe;">Flipkart</a></li>
                    <li style="margin: 10px 0;"><a href="${links.official}" target="_blank" style="color: #00f2fe;">Official Website</a></li>
                </ul>
                <button onclick="window.close()" style="margin-top: 20px; padding: 10px; cursor: pointer;">Close</button>
            </div>
        `);
    } catch (e) {
        alert("Could not fetch prices.");
    }
}
