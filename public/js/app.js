// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyAwaKjK61ziUEipF_o_zuOQNdFyMgpy4fc",
    authDomain: "projetouber-24a49.firebaseapp.com",
    projectId: "projetouber-24a49",
    storageBucket: "projetouber-24a49.firebasestorage.app",
    messagingSenderId: "567136926588",
    appId: "1:567136926588:web:78a5dba385965f2bdf02f9",
    measurementId: "G-JG61V2G29F"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// State
let currentUser = null;
let userProfile = null;

// DOM Elements
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginCard = document.querySelector('.login-card');
const registerCard = document.querySelector('.register-card');

// Check auth state on load
auth.onAuthStateChanged(async (user) => {
    const isAuthPage = window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/') || window.location.pathname.endsWith('public');
    const isDashboard = window.location.pathname.includes('dashboard.html');
    
    if (isAuthPage) {
        if (user) {
            window.location.href = 'dashboard.html';
        }
    } else if (isDashboard) {
        if (!user) {
            window.location.href = 'index.html';
        } else {
            currentUser = user;
            await loadUserProfile();
            initDashboard();
        }
    }
});

// AUTH PAGE
if (loginForm || registerForm) {
    // Toggle login/register
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

    // Login
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const userCredential = await auth.signInWithEmailAndPassword(email, password);
            
            // Save password for later Django token exchange if needed
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userPass', password);
            
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

    // Register
    registerForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('regEmail').value;
        const phone = document.getElementById('phone').value;
        const documentType = document.getElementById('documentType').value;
        const documentNumber = document.getElementById('documentNumber').value.replace(/\D/g, '');
        const userType = document.getElementById('userType').value;
        const password = document.getElementById('regPassword').value;

        try {
            // Create user in Firebase Auth
            const userCredential = await auth.createUserWithEmailAndPassword(email, password);
            const user = userCredential.user;

            // Save password
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userPass', password);

            // Create user profile in Firestore
            await db.collection('users').doc(user.uid).set({
                name,
                email,
                phone,
                documentType,
                documentNumber,
                userType,
                createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                updatedAt: firebase.firestore.FieldValue.serverTimestamp()
            });

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
            const user = result.user;

            // Check if user profile exists
            const userDoc = await db.collection('users').doc(user.uid).get();

            if (!userDoc.exists) {
                // Create user profile
                await db.collection('users').doc(user.uid).set({
                    name: user.displayName || 'Usuario Google',
                    email: user.email,
                    phone: '',
                    documentType: 'CPF',
                    documentNumber: '',
                    userType: 'PF',
                    createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            }

            localStorage.setItem('userEmail', user.email);

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
}

// DASHBOARD
async function loadUserProfile() {
    if (!currentUser) return;

    try {
        const doc = await db.collection('users').doc(currentUser.uid).get();
        if (doc.exists) {
            userProfile = doc.data();
        } else {
            // Create default profile if doesn't exist
            userProfile = {
                name: currentUser.displayName || currentUser.email,
                email: currentUser.email,
                phone: '',
                documentType: 'CPF',
                documentNumber: '',
                userType: 'PF'
            };
            await db.collection('users').doc(currentUser.uid).set(userProfile);
        }
    } catch (error) {
        console.error('Profile load error:', error);
        userProfile = {
            name: currentUser.displayName || currentUser.email,
            email: currentUser.email,
            phone: '',
            userType: 'PF'
        };
    }
}

function initDashboard() {
    setupNavigation();
    setupProfile();
    setupFreightModal();
    loadFreights();
    setupLogout();
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

function setupProfile() {
    if (!userProfile) return;

    document.getElementById('userName').textContent = userProfile.name;
    document.getElementById('welcomeMessage').textContent = `Bem-vindo, ${userProfile.name}!`;
    document.getElementById('profileName').textContent = userProfile.name;
    document.getElementById('profileEmail').textContent = userProfile.email;
    document.getElementById('profileType').textContent = `Tipo: ${getUserTypeLabel(userProfile.userType)}`;
    document.getElementById('profilePhone').value = userProfile.phone || '';
    document.getElementById('profileDocument').value = userProfile.documentNumber 
        ? `${userProfile.documentType}: ${userProfile.documentNumber}` 
        : '';
    document.getElementById('profileInitials').textContent = getInitials(userProfile.name);

    // Profile form submit
    document.getElementById('profileForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateProfile();
    });
}

async function updateProfile() {
    if (!currentUser) return;

    const phone = document.getElementById('profilePhone').value;

    try {
        await db.collection('users').doc(currentUser.uid).update({
            phone,
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        userProfile.phone = phone;

        Swal.fire({
            icon: 'success',
            title: 'Perfil atualizado!',
            text: 'Suas informações foram salvas.'
        });
    } catch (error) {
        console.error('Update profile error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'Não foi possível atualizar o perfil.'
        });
    }
}

function setupLogout() {
    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        await auth.signOut();
        localStorage.removeItem('userEmail');
        localStorage.removeItem('userPass');
        window.location.href = 'index.html';
    });
}

// FREIGHTS
async function loadFreights() {
    if (!currentUser) return;

    try {
        const snapshot = await db.collection('freights')
            .where('customerId', '==', currentUser.uid)
            .orderBy('createdAt', 'desc')
            .get();

        const freights = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));

        renderFreights(freights);
        updateStats(freights);
    } catch (error) {
        console.error('Load freights error:', error);
    }
}

function renderFreights(freights) {
    const container = document.getElementById('freightsList');
    
    if (!freights || freights.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhum frete encontrado</p>';
        return;
    }

    container.innerHTML = freights.map(freight => `
        <div class="freight-card" onclick="showFreightDetail('${freight.id}')">
            <h3>Frete #${freight.id.substring(0, 8)}</h3>
            <div class="freight-route">
                <span class="route-dot"></span>
                <span>${freight.originAddress || 'Origem'}</span>
                <span class="route-line"></span>
                <span class="route-dot" style="background: var(--success)"></span>
                <span>${freight.destinationAddress || 'Destino'}</span>
            </div>
            <div class="freight-meta">
                <span>Carga: ${(freight.cargoDescription || '').substring(0, 30)}...</span>
                <span>Peso: ${freight.estimatedWeight || 0} kg</span>
                <span>Preço: R$ ${freight.estimatedPrice || 'A calcular'}</span>
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
    if (!currentUser) return;

    const freightData = {
        customerId: currentUser.uid,
        customerName: userProfile?.name || currentUser.displayName,
        originAddress: document.getElementById('originAddress').value,
        originLat: parseFloat(document.getElementById('originLat').value),
        originLng: parseFloat(document.getElementById('originLng').value),
        destinationAddress: document.getElementById('destAddress').value,
        destLat: parseFloat(document.getElementById('destLat').value),
        destLng: parseFloat(document.getElementById('destLng').value),
        cargoCategory: document.getElementById('cargoCategory').value,
        cargoDescription: document.getElementById('cargoDescription').value,
        estimatedWeight: parseFloat(document.getElementById('estimatedWeight').value),
        estimatedVolume: parseFloat(document.getElementById('estimatedVolume').value),
        vehicleType: document.getElementById('vehicleType').value,
        requiresHelper: document.getElementById('requiresHelper').checked,
        requiresInsurance: document.getElementById('requiresInsurance').checked,
        status: 'requested',
        estimatedPrice: calculatePrice(),
        createdAt: firebase.firestore.FieldValue.serverTimestamp(),
        updatedAt: firebase.firestore.FieldValue.serverTimestamp()
    };

    try {
        await db.collection('freights').add(freightData);

        // Add tracking event
        await db.collection('tracking').add({
            freightId: null, // Will be updated
            eventType: 'order_created',
            description: 'Pedido criado',
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });

        Swal.fire({
            icon: 'success',
            title: 'Frete criado!',
            text: 'Sua solicitação de frete foi enviada.'
        });
        
        document.getElementById('freightModal').classList.remove('active');
        document.getElementById('freightForm').reset();
        loadFreights();
    } catch (error) {
        console.error('Create freight error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: error.message
        });
    }
}

function calculatePrice() {
    const weight = parseFloat(document.getElementById('estimatedWeight').value) || 0;
    const volume = parseFloat(document.getElementById('estimatedVolume').value) || 0;
    const hasHelper = document.getElementById('requiresHelper').checked;
    const hasInsurance = document.getElementById('requiresInsurance').checked;

    let basePrice = 50;
    let weightPrice = weight * 0.5;
    let volumePrice = volume * 100;
    let helperPrice = hasHelper ? 100 : 0;
    let insurancePrice = hasInsurance ? 80 : 0;

    return (basePrice + weightPrice + volumePrice + helperPrice + insurancePrice).toFixed(2);
}

// Tracking
document.getElementById('trackBtn')?.addEventListener('click', async () => {
    const code = document.getElementById('trackingCode').value.trim();
    if (!code) {
        Swal.fire({
            icon: 'warning',
            title: 'Atenção',
            text: 'Digite o código do frete'
        });
        return;
    }

    try {
        const doc = await db.collection('freights').doc(code).get();
        
        if (doc.exists) {
            showTrackingResult(code, doc.data());
        } else {
            // Try to search by short ID
            const snapshot = await db.collection('freights')
                .where('shortId', '==', code)
                .get();

            if (!snapshot.empty) {
                const freight = snapshot.docs[0];
                showTrackingResult(freight.id, freight.data());
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Frete não encontrado',
                    text: 'Verifique o código e tente novamente'
                });
            }
        }
    } catch (error) {
        console.error('Tracking error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: error.message
        });
    }
});

function showTrackingResult(id, freight) {
    const result = document.getElementById('trackingResult');
    document.getElementById('trackId').textContent = id.substring(0, 8);
    document.getElementById('trackStatus').textContent = getStatusLabel(freight.status);
    document.getElementById('trackStatus').className = `status-badge status-${freight.status}`;
    
    // Render timeline
    const timeline = document.getElementById('trackingTimeline');
    const events = getTrackingEvents(freight);
    
    timeline.innerHTML = events.map((event, index) => `
        <div class="timeline-item ${index === 0 ? 'active' : ''}">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <h4>${event.title}</h4>
                <p>${event.description}</p>
                <small>${event.time}</small>
            </div>
        </div>
    `).join('');

    result.style.display = 'block';
}

function getTrackingEvents(freight) {
    const events = [];
    const createdAt = freight.createdAt?.toDate() || new Date();

    events.push({
        title: 'Pedido Criado',
        description: 'Sua solicitação de frete foi recebida',
        time: createdAt.toLocaleString('pt-BR')
    });

    if (['driver_found', 'driver_going_to_pickup', 'arrived_at_origin', 'cargo_collected', 'in_transit'].includes(freight.status)) {
        events.push({
            title: 'Motorista Encontrado',
            description: 'Um motorista foi designado para sua entrega',
            time: createdAt.toLocaleString('pt-BR')
        });
    }

    if (['in_transit', 'delivered', 'completed'].includes(freight.status)) {
        events.push({
            title: 'Em Trânsito',
            description: 'Sua carga está a caminho do destino',
            time: createdAt.toLocaleString('pt-BR')
        });
    }

    if (['delivered', 'completed'].includes(freight.status)) {
        events.push({
            title: 'Entregue',
            description: 'Sua carga foi entregue com sucesso',
            time: createdAt.toLocaleString('pt-BR')
        });
    }

    if (freight.status === 'cancelled') {
        events.push({
            title: 'Cancelado',
            description: freight.cancellationReason || 'Frete cancelado',
            time: createdAt.toLocaleString('pt-BR')
        });
    }

    return events.reverse();
}

// HELPERS
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

function showFreightDetail(freightId) {
    // Simple alert for now - could expand to modal
    Swal.fire({
        title: 'Código do Frete',
        text: `Copie este código: ${freightId}`,
        icon: 'info'
    });
}