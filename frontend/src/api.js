import axios from 'axios';

export const API_BASE = '/api/v1';

const api = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const authApi = {
    login: (data) => api.post('/auth/login', data),
    register: (data) => api.post('/auth/register', data),
    me: () => api.get('/auth/me'),
};

export const dashboardApi = {
    hr: () => api.get('/dashboard/hr'),
    operations: () => api.get('/dashboard/operations'),
    cfo: () => api.get('/dashboard/cfo'),
    auditor: () => api.get('/dashboard/auditor'),
};

export const complianceApi = {
    overview: () => api.get('/compliance/overview'),
    gaps: () => api.get('/compliance/gaps'),
    stateMap: () => api.get('/compliance/state-map'),
    checklist: () => api.get('/compliance/checklist'),
};

export const regulationApi = {
    list: (state) => api.get('/regulations', { params: { state } }),
    get: (id) => api.get(`/regulations/${id}`),
    diffs: (id) => api.get(`/regulations/${id}/diffs`),
};

export const alertApi = {
    list: (unreadOnly) => api.get('/alerts', { params: { unread_only: unreadOnly } }),
    markRead: (id) => api.put(`/alerts/${id}/read`),
    dismiss: (id) => api.put(`/alerts/${id}/dismiss`),
};

export const policyApi = {
    list: (page) => api.get('/policies', { params: { page } }),
    upload: (formData) => api.post('/policies/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
    delete: (id) => api.delete(`/policies/${id}`),
    update: (id, updates) => api.patch(`/policies/${id}`, updates),
};

export const downloadFile = async (url, filename) => {
    try {
        const response = await api.get(url, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: response.headers['content-type'] });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
        console.error('Download failed:', err);
        throw err;
    }
};

export const reportApi = {
    list: () => api.get('/reports'),
    generate: (data) => api.post('/reports/generate', data),
    types: () => api.get('/reports/types'),
};

export default api;
