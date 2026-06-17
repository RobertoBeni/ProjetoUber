import { firebaseConfig, API_BASE_URL } from './config.js';

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// State
let currentUser = null;
let jwtToken = null;

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginCard = document.querySelector('.login-card');
const registerCard = document.querySelector('.register-card');

// Navigation
document.addEventListener('DOMContentLoaded', () => {
    const isAuthPage = window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/') || window.location.pathname.endsWith('web');
    const isDashboard = window.location.pathname.includes('dashboard.html');
    
    if (isAuthPage) {
        initAuthPage();
    } else if (isDashboard) {
        initDashboard();
    }
});

function initAuthPage() {
    // Toggle between login and register
    document.getElementById('showRegister')?.addEventListener('click', (e) => {
        e.preventDefault();
        loginCard.style.display = 'none';
        registerCard.style.display = 'block';
    });

    document.getElementById('showLogin')?.addEventListener('click', (e) => {
        e.preventDefault();
        registerCard.style.display = 'none';
        loginCard.style.display = 'block';
    });

    // Login form
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const userCredential = await auth.signInWithEmailAndPassword(email, password);
            const idToken = await userCredential.user.getIdToken();
            
            // Store Firebase token
            localStorage.setItem('firebaseToken', idToken);
            localStorage.setItem('userEmail', email);
            
            Swal.fire({
                icon: 'success',
                title: 'Login realizado!',
                text: 'Redirecionando...',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                window.location.href = 'dashboard.html';
            });
        } catch (error) {
            console.error('Login error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro no login',
                text: error.message
            });
        }
    });

    // Register form
    registerForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('regEmail').value;
        const phone = document.getElementById('phone').value;
        const documentType = document.getElementById('documentType').value;
        const documentNumber = document.getElementById('documentNumber').value;
        const userType = document.getElementById('userType').value;
        const password = document.getElementById('regPassword').value;

        try {
            // Create user in Firebase Auth
            const userCredential = await auth.createUserWithEmailAndPassword(email, password);
            const idToken = await userCredential.user.getIdToken();

            // Register in Django API
            const response = await fetch(`${API_BASE_URL}/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    name,
                    email,
                    phone,
                    document_type: documentType,
                    document_number: documentNumber.replace(/\D/g, ''),
                    user_type: userType,
                    password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao cadastrar');
            }

            localStorage.setItem('firebaseToken', idToken);
            localStorage.setItem('userEmail', email);

            Swal.fire({
                icon: 'success',
                title: 'Cadastro realizado!',
                text: 'Redirecionando...',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                window.location.href = 'dashboard.html';
            });
        } catch (error) {
            console.error('Register error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro no cadastro',
                text: error.message
            });
        }
    });

    // Google Sign In
    document.getElementById('googleLogin')?.addEventListener('click', async () => {
        try {
            const provider = new firebase.auth.GoogleAuthProvider();
            const result = await auth.signInWithPopup(provider);
            const idToken = await result.user.getIdToken();
            
            localStorage.setItem('firebaseToken', idToken);
            localStorage.setItem('userEmail', result.user.email);
            localStorage.setItem('userName', result.user.displayName);

            // Try to register/login in Django
            await fetch(`${API_BASE_URL}/auth/register/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`
                },
                body: JSON.stringify({
                    name: result.user.displayName || 'Usuario Google',
                    email: result.user.email,
                    user_type: 'PF',
                    password: 'GoogleAuth' + Date.now()
                })
            });

            Swal.fire({
                icon: 'success',
                title: 'Login com Google!',
                text: 'Redirecionando...',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                window.location.href = 'dashboard.html';
            });
        } catch (error) {
            console.error('Google login error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: error.message
            });
        }
    });

    // Check auth state
    auth.onAuthStateChanged((user) => {
        if (user) {
            window.location.href = 'dashboard.html';
        }
    });
}

async function initDashboard() {
    // Check auth
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
        if (!user) {
            window.location.href = 'index.html';
            return;
        }

        currentUser = user;
        
        try {
            const idToken = await user.getIdToken();
            localStorage.setItem('firebaseToken', idToken);
            
            // Get Django JWT
            const response = await fetch(`${API_BASE_URL}/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: user.email,
                    password: localStorage.getItem('djangoPassword') || 'FirebaseAuth'
                })
            });

            if (response.ok) {
                const data = await response.json();
                jwtToken = data.access;
                localStorage.setItem('jwtToken', jwtToken);
                localStorage.setItem('refreshToken', data.refresh);
            }
        } catch (error) {
            console.error('Auth error:', error);
        }

        setupDashboard();
        unsubscribe();
    });

    setupNavigation();
}

function setupDashboard() {
    // Load user profile
    loadUserProfile();
    
    // Load freights
    loadFreights();

    // Setup modal
    setupFreightModal();

    // Logout
    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        await auth.signOut();
        localStorage.removeItem('firebaseToken');
        localStorage.removeItem('jwtToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userEmail');
        window.location.href = 'index.html';
    });

    // Profile form
    document.getElementById('profileForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateProfile();
    });
}

function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
            document.getElementById(`${page}-section`)?.classList.add('active');
        });
    });
}

async function loadUserProfile() {
    const jwt = localStorage.getItem('jwtToken');
    if (!jwt) return;

    try {
        const response = await fetch(`${API_BASE_URL}/users/me/`, {
            headers: {
                'Authorization': `Bearer ${jwt}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            
            document.getElementById('userName').textContent = user.name;
            document.getElementById('welcomeMessage').textContent = `Bem-vindo, ${user.name}!`;
            document.getElementById('profileName').textContent = user.name;
            document.getElementById('profileEmail').textContent = user.email;
            document.getElementById('profileType').textContent = `Tipo: ${getUserTypeLabel(user.user_type)}`;
            document.getElementById('profilePhone').value = user.phone || '';
            document.getElementById('profileDocument').value = `${user.document_type}: ${user.document_number}`;
            document.getElementById('profileInitials').textContent = getInitials(user.name);
        }
    } catch (error) {
        console.error('Profile load error:', error);
    }
}

async function loadFreights() {
    const jwt = localStorage.getItem('jwtToken');
    if (!jwt) return;

    try {
        const response = await fetch(`${API_BASE_URL}/freight-orders/`, {
            headers: {
                'Authorization': `Bearer ${jwt}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const freights = data.results || data;
            renderFreights(freights);
            updateStats(freights);
        }
    } catch (error) {
        console.error('Freights load error:', error);
    }
}

function renderFreights(freights) {
    const container = document.getElementById('freightsList');
    
    if (!freights || freights.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhum frete encontrado</p>';
        return;
    }

    container.innerHTML = freights.map(freight => `
        <div class="freight-card">
            <h3>Frete #${freight.id.substring(0, 8)}</h3>
            <div class="freight-route">
                <span class="route-dot"></span>
                <span>${freight.origin_address}</span>
                <span class="route-line"></span>
                <span class="route-dot" style="background: var(--success)"></span>
                <span>${freight.destination_address}</span>
            </div>
            <div class="freight-meta">
                <span>Carga: ${freight.cargo_description.substring(0, 30)}...</span>
                <span>Peso: ${freight.estimated_weight_kg} kg</span>
                <span>Preço: R$ ${freight.estimated_price || 'A calcular'}</span>
            </div>
            <div style="margin-top: 12px">
                <span class="status-badge status-${freight.status}">${getStatusLabel(freight.status)}</span>
            </div>
        </div>
    `).join('');
}

function updateStats(freights) {
    if (!freights) return;
    
    document.getElementById('statFreights').textContent = freights.length;
    document.getElementById('statPending').textContent = freights.filter(f => 
        ['requested', 'waiting_driver', 'driver_found'].includes(f.status)
    ).length;
    document.getElementById('statInTransit').textContent = freights.filter(f => 
        ['driver_going_to_pickup', 'arrived_at_origin', 'cargo_collected', 'in_transit'].includes(f.status)
    ).length;
    document.getElementById('statCompleted').textContent = freights.filter(f => 
        ['delivered', 'completed'].includes(f.status)
    ).length;
}

function setupFreightModal() {
    const modal = document.getElementById('freightModal');
    const btn = document.getElementById('newFreightBtn');
    const close = modal?.querySelector('.modal-close');
    const form = document.getElementById('freightForm');

    btn?.addEventListener('click', () => {
        modal.classList.add('active');
    });

    close?.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await createFreight();
    });
}

async function createFreight() {
    const jwt = localStorage.getItem('jwtToken');
    if (!jwt) return;

    const freightData = {
        origin_address: document.getElementById('originAddress').value,
        origin_latitude: parseFloat(document.getElementById('originLat').value),
        origin_longitude: parseFloat(document.getElementById('originLng').value),
        destination_address: document.getElementById('destAddress').value,
        destination_latitude: parseFloat(document.getElementById('destLat').value),
        destination_longitude: parseFloat(document.getElementById('destLng').value),
        cargo_category: document.getElementById('cargoCategory').value,
        cargo_description: document.getElementById('cargoDescription').value,
        estimated_weight_kg: parseFloat(document.getElementById('estimatedWeight').value),
        estimated_volume_m3: parseFloat(document.getElementById('estimatedVolume').value),
        required_vehicle_type: document.getElementById('vehicleType').value,
        required_body_type: document.getElementById('bodyType').value,
        requires_helper: document.getElementById('requiresHelper').checked,
        requires_insurance: document.getElementById('requiresInsurance').checked
    };

    try {
        const response = await fetch(`${API_BASE_URL}/freight-orders/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwt}`
            },
            body: JSON.stringify(freightData)
        });

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Frete criado!',
                text: 'Sua solicitação de frete foi enviada.'
            });
            
            document.getElementById('freightModal').classList.remove('active');
            document.getElementById('freightForm').reset();
            loadFreights();
        } else {
            const error = await response.json();
            throw new Error(error.message || 'Erro ao criar frete');
        }
    } catch (error) {
        console.error('Create freight error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: error.message
        });
    }
}

async function updateProfile() {
    const jwt = localStorage.getItem('jwtToken');
    if (!jwt) return;

    const data = {
        phone: document.getElementById('profilePhone').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/me/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwt}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Perfil atualizado!',
                text: 'Suas informações foram salvas.'
            });
        }
    } catch (error) {
        console.error('Update profile error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'Não foi possível atualizar o perfil.'
        });
    }
}

// Helpers
function getUserTypeLabel(type) {
    const labels = {
        'PF': 'Cliente Pessoa Física',
        'PJ': 'Cliente Pessoa Jurídica',
        'DRIVER': 'Motorista',
        'CARRIER': 'Transportadora',
        'ADMIN': 'Administrador'
    };
    return labels[type] || type;
}

function getStatusLabel(status) {
    const labels = {
        'requested': 'Solicitado',
        'waiting_driver': 'Aguardando',
        'driver_found': 'Motorista Encontrado',
        'driver_going_to_pickup': 'Motorista a Caminho',
        'arrived_at_origin': 'Chegou na Origem',
        'cargo_collected': 'Carga Coletada',
        'in_transit': 'Em Trânsito',
        'temporarily_stopped': 'Parado',
        'near_destination': 'Próximo ao Destino',
        'arrived_at_destination': 'Chegou ao Destino',
        'delivered': 'Entregue',
        'completed': 'Finalizado',
        'cancelled': 'Cancelado'
    };
    return labels[status] || status;
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
}