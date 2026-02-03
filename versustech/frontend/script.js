const API_URL = 'http://127.0.0.1:5000/api';

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

    if (category === 'mobile') {
        cpuLabel.innerText = "Minimum Processor Power";
        rtxGroup.style.display = 'none';
    } else {
        cpuLabel.innerText = "Minimum CPU Power";
        rtxGroup.style.display = 'flex';
    }
}

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
}

// Display Results
let selectedItems = [];

function displayResults(products) {
    const grid = document.getElementById('resultsGrid');
    if (!grid) return;

    grid.innerHTML = products.map((p, index) => `
        <div class="product-card" onclick="toggleSelection(${index}, ${JSON.stringify(p).replace(/"/g, '&quot;')})">
            <span class="score-badge">Score: ${Math.round(p.final_score * 100)}%</span>
            <h3 style="margin-bottom: 10px;">${p.name}</h3>
            <p style="color: var(--primary); font-weight: 700;">₹${p.price.toLocaleString()}</p>
            <div style="margin-top: 15px; font-size: 0.9rem; color: #94a3b8;">
                ${p.ram ? `RAM: ${p.ram}GB |` : ''} 
                ${p.storage ? `Storage: ${p.storage}GB` : ''}
                <br>
                ${p.processor_score ? `CPU Score: ${p.processor_score}` : ''}
                ${p.cpu_score ? `CPU: ${p.cpu_score} | GPU: ${p.gpu_score}` : ''}
            </div>
        </div>
    `).join('');
}

function toggleSelection(index, product) {
    const cards = document.querySelectorAll('.product-card');
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
    const item1Div = document.getElementById('item1');
    const item2Div = document.getElementById('item2');

    const renderSpecs = (item) => `
        <h2 style="margin-bottom: 15px;">${item.name}</h2>
        <p style="font-size: 1.5rem; color: var(--primary); margin-bottom: 20px;">₹${item.price.toLocaleString()}</p>
        <div style="text-align: left; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; border: 1px solid var(--glass-border);">
            <p><strong>Brand:</strong> ${item.brand}</p>
            <p><strong>RAM:</strong> ${item.ram}GB</p>
            <p><strong>Storage:</strong> ${item.storage}GB</p>
            ${category === 'mobile' ?
            `<p><strong>Battery:</strong> ${item.battery}mAh</p><p><strong>Camera:</strong> ${item.camera}MP</p>` :
            `<p><strong>Battery:</strong> ${item.battery}hrs</p><p><strong>CPU Score:</strong> ${item.cpu_score}</p><p><strong>GPU Score:</strong> ${item.gpu_score}</p>`
        }
        </div>
        <div style="margin-top: 20px;">
            <a href="#" onclick="showPrices('${item.name}')" class="btn btn-primary" style="padding: 8px 15px; font-size: 0.8rem;">View Price Links</a>
        </div>
    `;

    item1Div.innerHTML = renderSpecs(item1);
    item2Div.innerHTML = renderSpecs(item2);

    // Call Compare API
    try {
        const response = await fetch(`${API_URL}/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item1, item2, category })
        });
        const result = await response.json();
        const details = result.details;

        const vsRow = (label, val1, val2, winner, suffix = "") => `
            <div class="vs-detail-row">
                <div class="vs-val ${winner === 'item1' ? 'vs-winner' : ''}">${val1}${suffix}</div>
                <div class="vs-label">${label}</div>
                <div class="vs-val ${winner === 'item2' ? 'vs-winner' : ''}">${val2}${suffix}</div>
            </div>
        `;

        let detailsHtml = `
            <h3 style="text-align: center; margin-bottom: 20px; color: var(--primary);">Specifications Versus</h3>
            ${vsRow('RAM', item1.ram, item2.ram, details.ram.winner, "GB")}
            ${vsRow('STORAGE', item1.storage, item2.storage, details.storage.winner, "GB")}
            ${category === 'mobile' ?
                vsRow('POWER', item1.processor_score, item2.processor_score, details.power.winner) +
                vsRow('CAMERA', item1.camera, item2.camera, details.camera.winner, "MP") :
                vsRow('POWER', item1.cpu_score + item1.gpu_score, item2.cpu_score + item2.gpu_score, details.power.winner) +
                vsRow('CPU', item1.cpu_score, item2.cpu_score, details.cpu.winner) +
                vsRow('GPU', item1.gpu_score, item2.gpu_score, details.gpu.winner)
            }
            ${vsRow('BATTERY', item1.battery, item2.battery, details.battery.winner, category === 'mobile' ? "mAh" : "hrs")}
        `;

        // Inject detailed VS section
        const winnersContainer = document.getElementById('winnersContainer');
        const detailVsBox = document.createElement('div');
        detailVsBox.className = 'vs-details-container';
        detailVsBox.innerHTML = detailsHtml;
        winnersContainer.parentNode.insertBefore(detailVsBox, winnersContainer);

        document.getElementById('winnersList').innerHTML = `
            <div class="winner-item"><span>Budget Winner:</span> <strong style="color: var(--primary)">${result.budget_winner}</strong></div>
            <div class="winner-item"><span>Specification Winner:</span> <strong style="color: var(--primary)">${result.spec_winner}</strong></div>
            <div class="winner-item"><span>Overall Winner:</span> <strong style="color: var(--accent); font-size: 1.2rem;">${result.overall_winner}</strong></div>
        `;
    } catch (error) {
        console.error('Error fetching winners:', error);
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
