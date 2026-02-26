/**
 * 灵感食仓 (InspiLarder) - 主应用逻辑 v2.1
 * AI驱动的智能食物管理助手
 */

// ============================================
// 全局配置
// ============================================
const CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api/v1'
        : '/api/v1',
    APP_NAME: '灵感食仓',
    VERSION: '2.1.0',
    TOKEN_KEY: 'inspilarder_token',
    USER_KEY: 'inspilarder_user',
    DEFAULT_AVATAR: '👤'
};

// ============================================
// 状态管理
// ============================================
const state = {
    currentUser: null,
    token: null,
    currentPage: 'home',
    isLoading: false,
    foods: [],
    locations: [],
    currentRecipes: [],
    selectedImage: null,
    aiLoadingTexts: ['正在分析图片...', '识别食物中...', '提取信息中...', '即将完成...'],
    categories: [
        { id: 'vegetable', name: '新鲜蔬菜', icon: '🥬' },
        { id: 'fruit', name: '时令水果', icon: '🍎' },
        { id: 'meat', name: '生鲜肉类', icon: '🥩' },
        { id: 'seafood', name: '海鲜水产', icon: '🐟' },
        { id: 'dairy', name: '蛋奶制品', icon: '🥚' },
        { id: 'condiment', name: '调味品', icon: '🧂' },
        { id: 'grain', name: '米面粮油', icon: '🍚' },
        { id: 'snack', name: '零食饮料', icon: '🍿' },
        { id: 'frozen', name: '冷冻食品', icon: '🧊' },
        { id: 'prepared', name: '成品菜肴', icon: '🍱' },
        { id: 'other', name: '其他', icon: '📦' }
    ]
};

// ============================================
// 工具函数
// ============================================
const utils = {
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        const now = new Date();
        const diff = Math.floor((date - now) / (1000 * 60 * 60 * 24));
        
        if (diff < 0) return `已过期 ${Math.abs(diff)} 天`;
        if (diff === 0) return '今天到期';
        if (diff === 1) return '明天到期';
        if (diff <= 3) return `${diff} 天后到期 🔥`;
        return `${date.getMonth() + 1}月${date.getDate()}日`;
    },

    getRemainingDays(expiryDate) {
        if (!expiryDate) return null;
        const date = new Date(expiryDate);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        return Math.floor((date - now) / (1000 * 60 * 60 * 24));
    },

    getExpiryDisplayText(days) {
        if (days === null) return '-';
        if (days < 0) return `已过期 ${Math.abs(days)} 天`;
        if (days === 0) return '今天';
        if (days === 1) return '明天';
        return `剩 ${days} 天`;
    },

    getCategoryIcon(category) {
        const cat = state.categories.find(c => c.id === category);
        return cat ? cat.icon : '🍽️';
    },

    getCategoryName(category) {
        const cat = state.categories.find(c => c.id === category);
        return cat ? cat.name : '其他';
    },

    getIngredientColorClass(ingText) {
        if (ingText.match(/苹果|香蕉|橙子|柚子|梨|桃|李|杏|樱桃|草莓|蓝莓|芒果|菠萝|西瓜|哈密瓜|葡萄|猕猴桃|石榴|榴莲|山竹|火龙果|荔枝|龙眼|枇杷|椰子|柠檬|甘蔗|柿子|枣|橘子|柑|百香果|牛油果|桃子|水果/)) {
            return 'bg-pink-100 text-pink-700 border border-pink-200';
        }
        if (ingText.match(/菜|蔬|瓜|葱|蒜|豆|菇|笋|莲|薯|芋|玉米|萝卜|梅|番茄|黄瓜|茄子|土豆|红薯|南瓜|冬瓜|西瓜|苦瓜|丝瓜|腐竹|木耳|银耳|莴笋|莲花白|茼蒿|芥蓝|茴香|芫荽|韭黄|折耳根|马齿苋/)) {
            return 'bg-green-100 text-green-700 border border-green-200';
        }
        if (ingText.match(/水|奶|酪|酵|黄油|蛋/)) {
            return 'bg-blue-100 text-blue-700 border border-blue-200';
        }
        if (ingText.match(/肉|肠|排|腿|翅|爪|骨|腊|鸡|鸭|鹅|猪|牛|羊|五花|里脊|脑花|血/)) {
            return 'bg-red-100 text-red-700 border border-red-200';
        }
        if (ingText.match(/鱼|虾|蟹|贝|鱿|墨|鲍|参|海参|海胆|海螺|花蛤|文蛤|蛏子|青口|生蚝|扇贝|海带|紫菜|裙带菜|海白菜|海藻/)) {
            return 'bg-cyan-100 text-cyan-700 border border-cyan-200';
        }
        if (ingText.match(/米|饭|粥|馒头|饼|饺|包|粉|面|面条|米粉|粉丝|年糕|糍粑|汤圆|元宵|粽子|面包|蛋糕|饼干|披萨|汉堡|三明治|沙拉|土豆泥/)) {
            return 'bg-amber-100 text-amber-700 border border-amber-200';
        }
        if (ingText.match(/酱|椒|味|鸡精|味精|油|酒|生抽|老抽|盐|糖|醋|八角|桂皮|香叶|草果|陈皮|甘草|小茴香|孜然|五香粉|十三香|咖喱|芥末|喼汁/)) {
            return 'bg-purple-100 text-purple-700 border border-purple-200';
        }
        return 'bg-gray-100 text-gray-600';
    },

    debounce(fn, delay) {
        let timer = null;
        return function (...args) {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    },

    uuid() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    async compressImage(file, maxWidth = 1024, maxHeight = 1024, quality = 0.8) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;
                    if (width > height) {
                        if (width > maxWidth) { height *= maxWidth / width; width = maxWidth; }
                    } else {
                        if (height > maxHeight) { width *= maxHeight / height; height = maxHeight; }
                    }
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    canvas.toBlob(blob => resolve(blob), 'image/jpeg', quality);
                };
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },

    formatDateForInput(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toISOString().split('T')[0];
    },

    formatDateFull(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    formatLocationOptions(locations) {
        const parentMap = {};
        locations.forEach(loc => {
            if (loc.parent_id) {
                const parent = locations.find(p => p.id === loc.parent_id);
                parentMap[loc.id] = parent ? parent.name : null;
            }
        });
        
        return locations.map(location => {
            const parentName = parentMap[location.id];
            const label = parentName 
                ? `${location.icon || '📦'} ${parentName} - ${location.name}`
                : `${location.icon || '📦'} ${location.name}`;
            return { value: location.id, label };
        });
    }
};

// ============================================
// API 客户端
// ============================================
const api = {
    setToken(token) {
        state.token = token;
        localStorage.setItem(CONFIG.TOKEN_KEY, token);
    },

    getToken() {
        if (!state.token) state.token = localStorage.getItem(CONFIG.TOKEN_KEY);
        return state.token;
    },

    clearToken() {
        state.token = null;
        state.currentUser = null;
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
    },

    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const token = this.getToken();
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };
        if (options.body instanceof FormData) {
            delete defaultOptions.headers['Content-Type'];
        }
        try {
            const response = await fetch(url, { 
                ...defaultOptions, 
                ...options, 
                headers: { ...defaultOptions.headers, ...options.headers } 
            });
            if (response.status === 401) {
                const currentPath = window.location.pathname;
                if (!currentPath.includes('/login')) {
                    this.clearToken();
                    if (typeof app !== 'undefined' && app.navigateTo) {
                        app.navigateTo('login');
                    } else {
                        window.location.href = '/login';
                    }
                    throw new Error('会话已过期，请重新登录');
                }
                const data = await response.json();
                throw new Error(data.detail || data.message || '用户名或密码错误');
            }
            const data = response.status === 204 ? null : await response.json();
            if (!response.ok) throw new Error(data.detail || data.message || '请求失败');
            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    },

    get(endpoint) { return this.request(endpoint, { method: 'GET' }); },
    post(endpoint, data) { return this.request(endpoint, { method: 'POST', body: JSON.stringify(data) }); },
    put(endpoint, data) { return this.request(endpoint, { method: 'PUT', body: JSON.stringify(data) }); },
    delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }); },
    upload(endpoint, formData) { return this.request(endpoint, { method: 'POST', body: formData }); }
};

// ============================================
// UI 组件
// ============================================
const ui = {
    toast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        const styles = {
            success: 'bg-white border-l-4 border-green-500 text-green-700 shadow-lg shadow-green-100',
            error: 'bg-white border-l-4 border-red-500 text-red-700 shadow-lg shadow-red-100',
            warning: 'bg-white border-l-4 border-amber-500 text-amber-700 shadow-lg shadow-amber-100',
            info: 'bg-white border-l-4 border-blue-500 text-blue-700 shadow-lg shadow-blue-100'
        };
        const icons = {
            success: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>',
            error: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>',
            warning: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>',
            info: '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>'
        };
        toast.className = `${styles[type]} px-5 py-3.5 rounded-xl flex items-center gap-3 animate-toastIn pointer-events-auto min-w-[280px] backdrop-blur-sm`;
        toast.innerHTML = `<span class="flex-shrink-0">${icons[type]}</span><span class="font-medium text-sm">${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    confirm(options) {
        return new Promise((resolve) => {
            const dialog = document.getElementById('confirm-dialog');
            const titleEl = document.getElementById('confirm-title');
            const messageEl = document.getElementById('confirm-message');
            const iconEl = document.getElementById('confirm-icon');
            const cancelBtn = document.getElementById('confirm-cancel');
            const okBtn = document.getElementById('confirm-ok');
            const buttonsContainer = document.getElementById('confirm-buttons');
            const content = document.getElementById('confirm-modal-content'); 
            const backdrop = document.getElementById('confirm-backdrop');

            titleEl.textContent = options.title || '确认操作';

            if (options.html) {
                messageEl.innerHTML = options.message || '';
            } else {
                messageEl.textContent = options.message || '您确定要执行此操作吗？';
            }

            const iconColors = {
                danger: 'bg-red-100 text-red-600',
                warning: 'bg-yellow-100 text-yellow-600',
                info: 'bg-blue-100 text-blue-600'
            };
            iconEl.className = `w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${iconColors[options.type] || iconColors.info}`;
            iconEl.innerHTML = options.icon || '?';

            let editBtn = document.getElementById('confirm-edit');
            if (options.showEdit) {
                if (!editBtn) {
                    editBtn = document.createElement('button');
                    editBtn.id = 'confirm-edit';
                    editBtn.className = options.editBtnClass || 'flex-1 py-3 border border-orange-300 text-orange-600 rounded-xl font-medium hover:bg-orange-50 transition-all';
                    editBtn.textContent = '编辑';
                    buttonsContainer.insertBefore(editBtn, okBtn);
                } else if (options.editBtnClass) {
                    editBtn.className = options.editBtnClass;
                }
                editBtn.style.display = 'block';
                editBtn.onclick = () => {
                    dialog.classList.add('hidden');
                    resolve('edit');
                    if (options.onEdit) options.onEdit();
                };
            } else if (editBtn) {
                editBtn.style.display = 'none';
            }

            let deleteBtn = document.getElementById('confirm-delete');
            if (options.showDelete) {
                if (!deleteBtn) {
                    deleteBtn = document.createElement('button');
                    deleteBtn.id = 'confirm-delete';
                    deleteBtn.className = 'flex-1 py-3 border border-red-200 text-red-500 rounded-xl font-medium hover:bg-red-50 transition-all';
                    deleteBtn.textContent = '删除';
                    buttonsContainer.insertBefore(deleteBtn, buttonsContainer.firstChild); // Insert at start
                }
                deleteBtn.style.display = 'block';
                deleteBtn.onclick = () => {
                    dialog.classList.add('hidden');
                    resolve('delete');
                    if (options.onDelete) options.onDelete();
                };
            } else if (deleteBtn) {
                deleteBtn.style.display = 'none';
            }

            // --- 动画显示逻辑 START ---
            dialog.classList.remove('hidden'); // 先显示整个对话框容器
            // 确保在下一帧DOM更新后，再添加/移除类，以触发CSS过渡动画
            requestAnimationFrame(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            });
            // --- 动画显示逻辑 END ---

            const close = (result) => {
                // --- 动画隐藏逻辑 START ---
                content.classList.remove('scale-100', 'opacity-100');
                content.classList.add('scale-95', 'opacity-0');
                setTimeout(() => {
                    dialog.classList.add('hidden'); // 动画完成后隐藏整个对话框容器
                    resolve(result);
                }, 200); // 等待动画完成，这里的200ms应与CSS的duration-200匹配
                // --- 动画隐藏逻辑 END ---
            };
            
            if (options.showCancel === false) {
                 if (cancelBtn) cancelBtn.style.display = 'none';
            } else {
                 if (!cancelBtn) {
                    // Recreate if missing (unlikely given HTML structure, but good for safety)
                    // For now, assuming it exists in HTML template
                 }
                 if (cancelBtn) {
                     cancelBtn.style.display = 'block';
                     cancelBtn.onclick = () => close(false);
                 }
            }
            
            okBtn.onclick = () => close(true);
            backdrop.onclick = () => close(false); // 点击背景关闭
        });
    },

    input(options) {
        return new Promise((resolve) => {
            const dialog = document.getElementById('input-dialog');
            const titleEl = document.getElementById('input-title');
            const messageEl = document.getElementById('input-message');
            const iconEl = document.getElementById('input-icon');
            const inputEl = document.getElementById('input-field');
            const cancelBtn = document.getElementById('input-cancel');
            const okBtn = document.getElementById('input-ok');

            titleEl.textContent = options.title || '请输入';
            messageEl.textContent = options.message || '';
            inputEl.placeholder = options.placeholder || '';
            inputEl.value = options.defaultValue || '';
            iconEl.innerHTML = options.icon || '📝';

            dialog.classList.remove('hidden');
            setTimeout(() => inputEl.focus(), 100);

            const close = (result) => {
                dialog.classList.add('hidden');
                resolve(result);
            };

            const handleConfirm = () => {
                const value = inputEl.value.trim();
                close(value || null);
            };

            cancelBtn.onclick = () => close(null);
            okBtn.onclick = handleConfirm;
            inputEl.onkeydown = (e) => {
                if (e.key === 'Enter') handleConfirm();
                if (e.key === 'Escape') close(null);
            };
        });
    },

    showLoading(element, text = '加载中...') {
        if (typeof element === 'string') element = document.querySelector(element);
        if (!element) return;
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = `<div class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5 text-current" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>${text}</span>
        </div>`;
        element.disabled = true;
    },

    hideLoading(element) {
        if (typeof element === 'string') element = document.querySelector(element);
        if (!element || !element.dataset.originalContent) return;
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
        delete element.dataset.originalContent;
    },

    showEditModal(options) {
        return new Promise((resolve) => {
            const modal = document.getElementById('edit-modal');
            const formContainer = document.getElementById('edit-modal-form');
            const titleEl = document.getElementById('edit-modal-title');
            const iconEl = document.getElementById('edit-modal-icon');
            const saveBtn = document.getElementById('edit-modal-save');
            const cancelBtn = document.getElementById('edit-modal-cancel');
            const closeBtn = document.getElementById('close-edit-modal');
            const backdrop = document.getElementById('edit-modal-backdrop');

            titleEl.textContent = options.title || '编辑';
            iconEl.textContent = options.icon || '✏️';
            
            formContainer.innerHTML = '';
            
            options.fields.forEach(field => {
                const div = document.createElement('div');
                div.className = 'space-y-1';
                
                const label = document.createElement('label');
                label.className = 'block text-sm font-medium text-gray-700';
                label.textContent = field.label;
                div.appendChild(label);
                
                if (field.type === 'select') {
                    const select = document.createElement('select');
                    select.id = `field-${field.name}`;
                    select.className = 'w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all bg-white';
                    field.options.forEach(opt => {
                        const option = document.createElement('option');
                        option.value = opt.value;
                        option.textContent = opt.label;
                        if (opt.value == field.value) option.selected = true;
                        select.appendChild(option);
                    });
                    div.appendChild(select);
                } else if (field.type === 'textarea') {
                    const textarea = document.createElement('textarea');
                    textarea.id = `field-${field.name}`;
                    textarea.rows = 3;
                    textarea.className = 'w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all resize-none';
                    textarea.value = field.value || '';
                    div.appendChild(textarea);
                } else if (field.type === 'checkbox') {
                    div.className = 'flex items-center gap-3 py-2 bg-gray-50 rounded-xl px-4 border border-gray-100';
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `field-${field.name}`;
                    checkbox.className = 'w-5 h-5 rounded border-gray-300 text-orange-500 focus:ring-orange-500';
                    checkbox.checked = !!field.value;
                    
                    const checkLabel = document.createElement('label');
                    checkLabel.htmlFor = `field-${field.name}`;
                    checkLabel.className = 'text-sm font-medium text-gray-700 select-none cursor-pointer flex-1';
                    checkLabel.textContent = field.label;
                    
                    div.innerHTML = ''; 
                    div.appendChild(checkbox);
                    div.appendChild(checkLabel);
                } else if (field.type === 'combined') {
                    const flex = document.createElement('div');
                    flex.className = 'flex';
                    
                    const input = document.createElement('input');
                    input.type = 'number';
                    input.step = '0.1';
                    input.id = `field-${field.name}_value`;
                    input.className = 'flex-1 px-4 py-2 border border-gray-300 rounded-l-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all';
                    input.value = field.value.value || '';
                    
                    const select = document.createElement('select');
                    select.id = `field-${field.name}_unit`;
                    select.className = 'px-3 py-2 border border-l-0 border-gray-300 rounded-r-xl bg-gray-50 text-sm focus:ring-2 focus:ring-orange-500 focus:outline-none';
                    field.units.forEach(u => {
                        const opt = document.createElement('option');
                        opt.value = u;
                        opt.textContent = u;
                        if (u === field.value.unit) opt.selected = true;
                        select.appendChild(opt);
                    });
                    
                    flex.appendChild(input);
                    flex.appendChild(select);
                    div.appendChild(flex);
                } else if (field.type === 'icon') {
                    const flex = document.createElement('div');
                    flex.className = 'flex gap-2 items-center';
                    
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.id = `field-${field.name}`;
                    input.className = 'w-16 px-2 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all text-center flex-shrink-0';
                    input.value = field.value || '📦';
                    input.readOnly = true;
                    
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'flex-1 h-10 px-3 bg-orange-50 text-orange-600 rounded-xl border border-orange-200 hover:bg-orange-100 transition-colors text-sm font-medium flex items-center justify-center';
                    btn.textContent = '选择图标';
                    btn.onclick = async () => {
                        const emoji = await ui.emojiPicker.show({ context: field.context || 'food' });
                        if (emoji) input.value = emoji;
                    };
                    
                    flex.appendChild(input);
                    flex.appendChild(btn);
                    div.appendChild(flex);
                } else {
                    const input = document.createElement('input');
                    input.type = field.type || 'text';
                    input.id = `field-${field.name}`;
                    input.className = 'w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all';
                    input.value = field.value || '';
                    if (field.placeholder) input.placeholder = field.placeholder;
                    div.appendChild(input);
                }
                
                formContainer.appendChild(div);
            });

            // Add expiry date sync logic removed to avoid duplication
            // Logic moved to after loop execution (lines 543+)
            
            modal.classList.remove('hidden');
            const content = document.getElementById('edit-modal-content');
            setTimeout(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }, 10);

            const close = (result = null) => {
                content.classList.remove('scale-100', 'opacity-100');
                content.classList.add('scale-95', 'opacity-0');
                setTimeout(() => { modal.classList.add('hidden'); }, 200);
                resolve(result);
            };

            const handleSave = () => {
                const result = {};
                options.fields.forEach(field => {
                    if (field.type === 'checkbox') {
                        result[field.name] = document.getElementById(`field-${field.name}`).checked;
                    } else if (field.type === 'combined') {
                        result[field.name] = parseFloat(document.getElementById(`field-${field.name}_value`).value) || 0;
                        result[field.unitName || 'unit'] = document.getElementById(`field-${field.name}_unit`).value;
                    } else {
                        const val = document.getElementById(`field-${field.name}`).value;
                        result[field.name] = field.type === 'number' ? parseFloat(val) : val;
                    }
                });
                
                const locationField = options.fields.find(f => f.name === 'location_id');
                if (locationField && !result.location_id) {
                    ui.toast('请选择存放位置', 'warning');
                    return;
                }
                
                close(result);
            };

            const handleCancel = () => {
                close(null);
            };

            // Setup Remaining Days sync for expiry_date fields
            const expiryField = options.fields.find(f => f.name === 'expiry_date');
            if (expiryField) {
                const expiryInput = document.getElementById('field-expiry_date');
                
                // Remove any existing container to prevent duplicates
                const existingContainer = document.getElementById('remaining-days-container');
                if (existingContainer) {
                    existingContainer.remove();
                }
                
                // Create remaining days input field
                const remainingDaysDiv = document.createElement('div');
                remainingDaysDiv.className = 'mt-2';
                remainingDaysDiv.id = 'remaining-days-container';
                remainingDaysDiv.innerHTML = `
                    <label class="block text-sm font-medium text-gray-700 mb-1">剩余天数</label>
                    <input type="number" id="field-remaining_days" class="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all" placeholder="输入天数自动计算日期">
                `;
                expiryInput.parentNode.appendChild(remainingDaysDiv);

                const remainingDaysInput = document.getElementById('field-remaining_days');

                // Calculate remaining days from expiry date
                const updateRemainingDays = () => {
                    const expiryDate = expiryInput.value;
                    if (expiryDate) {
                        const expiry = new Date(expiryDate);
                        const now = new Date();
                        now.setHours(0, 0, 0, 0);
                        const diffTime = expiry - now;
                        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        remainingDaysInput.value = diffDays;
                    }
                };

                // Update expiry date from remaining days
                const updateExpiryDate = () => {
                    const days = parseInt(remainingDaysInput.value);
                    if (!isNaN(days)) {
                        const now = new Date();
                        now.setHours(0, 0, 0, 0);
                        const expiry = new Date(now);
                        expiry.setDate(expiry.getDate() + days);
                        expiryInput.value = expiry.toISOString().split('T')[0];
                    }
                };

                expiryInput.addEventListener('change', updateRemainingDays);
                remainingDaysInput.addEventListener('input', updateExpiryDate);

                // Initialize with default value if specified
                if (expiryField.defaultRemainingDays !== undefined) {
                    remainingDaysInput.value = expiryField.defaultRemainingDays;
                    updateExpiryDate();
                } else {
                    updateRemainingDays();
                }
            }

            // Remove existing listeners to avoid duplicates if reused (though elements are static, logic rebinds)
            // Better to clone or specific binding. For now, simple onclick override is fine.
            cancelBtn.onclick = handleCancel;
            closeBtn.onclick = handleCancel;
            backdrop.onclick = handleCancel;
            saveBtn.onclick = handleSave;
        });
    },

    createFoodCard(food) {
        const remainingDays = utils.getRemainingDays(food.expiry_date);
        const isExpiringSoon = remainingDays !== null && remainingDays <= 3 && remainingDays >= 0;
        const isExpired = remainingDays !== null && remainingDays < 0;
        const isFinished = food.is_finished;
        
        let statusClass = 'border-l-4 border-green-400';
        let statusBg = 'bg-green-50';
        let statusText = 'fresh';
        
        if (isExpired) {
            statusClass = 'border-l-4 border-red-400';
            statusBg = 'bg-red-50';
            statusText = 'expired';
        } else if (isExpiringSoon) {
            statusClass = 'border-l-4 border-orange-400';
            statusBg = 'bg-orange-50';
            statusText = 'expiring';
        }
        
        const daysText = remainingDays !== null 
            ? remainingDays < 0 
                ? `过期 ${Math.abs(remainingDays)} 天`
                : remainingDays === 0 
                    ? '今天到期'
                    : `还剩 ${remainingDays} 天`
            : '-';
        
        let locationDisplay = '';
        if (food.location_name) {
            if (food.parent_location_name) {
                locationDisplay = `${food.parent_location_name} - ${food.location_name}`;
            } else {
                locationDisplay = food.location_name;
            }
        }
        
        const locationEmoji = food.location_icon || '📍';
        
        const cardClass = isFinished ? `${statusClass} bg-gray-50 opacity-60 rounded-xl p-4 cursor-pointer hover:shadow-md transition-all` : `food-card ${statusClass} ${statusBg} rounded-xl p-4 cursor-pointer hover:shadow-md transition-all`;
        
        return `
            <div class="${cardClass}" onclick="app.showFoodDetail(${food.id})" data-food-id="${food.id}">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-full bg-white flex items-center justify-center text-2xl shadow-sm">
                        ${food.icon || utils.getCategoryIcon(food.category)}
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-semibold text-gray-800 truncate">${food.name}</h3>
                        <div class="flex items-center gap-2 text-sm">
                            <span class="${statusText === 'expired' ? 'text-red-600 font-medium' : statusText === 'expiring' ? 'text-orange-600 font-medium' : 'text-gray-500'}">
                                ${daysText}
                            </span>
                            ${food.quantity ? `<span class="text-gray-400">· ${Math.round(food.quantity)}${food.unit || ''}</span>` : ''}
                        </div>
                        ${locationDisplay ? `<div class="text-xs text-gray-400 mt-1">${locationEmoji} ${locationDisplay}</div>` : ''}
                    </div>
                    ${isFinished 
                        ? `<button onclick="event.stopPropagation(); app.unconsumeFood(${food.id})" class="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-lg transition-colors" title="撤销消耗">
                            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                                <path d="M9 14L4 9l5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>`
                        : `<button onclick="event.stopPropagation(); app.consumeFood(${food.id})" class="p-2 text-gray-400 hover:text-orange-500 hover:bg-orange-50 rounded-lg transition-colors" title="标记已消耗">
                            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12,23a10.927,10.927,0,0,0,7.778-3.222,1,1,0,0,0,0-1.414L13.414,12l6.364-6.364a1,1,0,0,0,0-1.414A11,11,0,1,0,12,23ZM12,3a8.933,8.933,0,0,1,5.618,1.967l-6.325,6.326a1,1,0,0,0,0,1.414l6.325,6.326A9,9,0,1,1,12,3Zm11,9a2,2,0,1,1-2-2A2,2,0,0,1,23,12ZM8,7a2,2,0,1,1,2,2A2,2,0,0,1,8,7Z"/>
                            </svg>
                        </button>`
                    }
                </div>
            </div>
        `;
    },

    emojiPicker: {
        // 根据上下文定义不同的emoji集合
        categories: {
            // 食材相关emoji
            food: {
                '蔬菜': ['🥬','🥦','🥕','🌽','🧄','🧅','🍆','🌶','🥒','🫑','🍠','🥔','🍄'],
                '水果': ['🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🍍','🥝','🥥','🥑'],
                '肉类': ['🥩','🍖','🍗','🥓','🦴'],
                '海鲜': ['🐟','🐠','🐡','🦈','🐙','🦑','🦐','🦞','🦀','🦪','🍣','🍤'],
                '蛋奶': ['🥚','🥛','🧀','🧈','🥞','🧇','🥐','🥯'],
                '主食': ['🍚','🍙','🍛','🍜','🍝','🍞','🥖','🥨','🥐','🥯','🫓','🥪','🌯','🌮','🥙'],
                '零食': ['🍿','🍫','🍬','🍭','🍮','🍩','🍪','🧁','🥧','🍦','🍧','🍨','🎂','🍰'],
                '饮料': ['☕','🍵','🧃','🥤','🧋','🍺','🍻','🥂','🍷','🥃','🍸','🍹','🍶','🥛','🧊'],
                '调味品': ['🧂','🧈','🍯','🥫','🫙','🧉','🌿','🧅','🧄']
            },
            // 空间相关emoji
            space: {
                '房屋': ['🏠','🏡','🏢','🏣','🏤','🏥','🏦','🏨','🏩','🏪','🏫','🏬','🏭','🏯','🏰','💒','🗼'],
                '室内': ['🚪','🪟','🛋','🪑','🛏','🛁','🚿','🧴','🧺','🧻','🧼','🧽','🪞','🧹'],
                '厨房': ['🍽','🍴','🥄','🔪','🥢','🥣','🍳','🔥','🧊','🍶','🥛','🫖','☕','🍵'],
                '存储': ['📦','🗄','🗃','📂','📁','🧰','🎒','👜','🛍','🧳','🗳','🗑'],
                '电器': ['❄','🔥','🧊','📺','🖥','💻','📱','🔌','💡','🔦','🕯','📡','🔋'],
                '户外': ['🌳','🌲','🌴','🌵','🌷','🌹','🌻','🌺','🏕','🛖']
            }
        },
        
        show(options = {}) {
            return new Promise((resolve) => {
                const modal = document.getElementById('emoji-picker-modal');
                const customInput = document.getElementById('custom-emoji');
                const grid = document.getElementById('emoji-grid');
                const categoryTabs = document.getElementById('emoji-categories');
                
                // 根据上下文选择emoji集合
                const context = options.context || 'food';
                const emojiCategories = this.categories[context] || this.categories.food;
                
                let selectedEmoji = null;
                let currentSubcategory = Object.keys(emojiCategories)[0];
                
                modal.classList.remove('hidden');
                
                // Add animation classes
                const content = document.getElementById('emoji-picker-content');
                if (content) {
                    requestAnimationFrame(() => {
                        content.classList.remove('scale-95', 'opacity-0');
                        content.classList.add('scale-100', 'opacity-100');
                    });
                }
                
                // 清空并隐藏搜索框（简化界面）
                const searchContainer = document.getElementById('emoji-search')?.parentElement;
                if (searchContainer) searchContainer.style.display = 'none';
                
                // 隐藏最近使用区域（简化界面）
                const recentSection = document.getElementById('recent-emojis')?.parentElement;
                if (recentSection) recentSection.style.display = 'none';
                
                // 渲染分类标签
                categoryTabs.innerHTML = Object.keys(emojiCategories).map(cat => `
                    <button class="px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${cat === currentSubcategory ? 'bg-orange-100 text-orange-600' : 'text-gray-500 hover:bg-gray-50'}" data-category="${cat}">
                        ${cat}
                    </button>
                `).join('');
                
                // 渲染初始emoji网格
                this.renderCategoryGrid(grid, emojiCategories, currentSubcategory);
                
                // 分类标签点击事件
                categoryTabs.onclick = (e) => {
                    const btn = e.target.closest('button');
                    if (btn && btn.dataset.category) {
                        currentSubcategory = btn.dataset.category;
                        
                        categoryTabs.querySelectorAll('button').forEach(b => {
                            if (b.dataset.category === currentSubcategory) {
                                b.classList.add('bg-orange-100', 'text-orange-600');
                                b.classList.remove('text-gray-500', 'hover:bg-gray-50');
                            } else {
                                b.classList.remove('bg-orange-100', 'text-orange-600');
                                b.classList.add('text-gray-500', 'hover:bg-gray-50');
                            }
                        });

                        this.renderCategoryGrid(grid, emojiCategories, currentSubcategory);
                    }
                };
                
                const close = () => {
                    const content = document.getElementById('emoji-picker-content');
                    if (content) {
                        content.classList.remove('scale-100', 'opacity-100');
                        content.classList.add('scale-95', 'opacity-0');
                    }
                    setTimeout(() => { 
                        modal.classList.add('hidden');
                        // 恢复搜索框和最近使用区域的显示（为下次打开做准备）
                        if (searchContainer) searchContainer.style.display = '';
                        if (recentSection) recentSection.style.display = '';
                    }, 200);
                    resolve(null);
                };

                const closeBtn = document.getElementById('close-emoji-picker');
                if (closeBtn) closeBtn.onclick = close;

                // Emoji点击选择
                grid.onclick = (e) => {
                    const btn = e.target.closest('button');
                    if (btn && btn.dataset.emoji) {
                        selectedEmoji = btn.dataset.emoji;
                        resolve(selectedEmoji);
                        close();
                    }
                };
                
                // 确认按钮（使用自定义输入）
                document.getElementById('emoji-confirm').onclick = () => {
                    selectedEmoji = customInput.value || selectedEmoji;
                    if (selectedEmoji) {
                        resolve(selectedEmoji);
                    }
                    close();
                };
                
                // 取消按钮
                document.getElementById('emoji-cancel').onclick = () => {
                    resolve(null);
                    close();
                };
                
                // 点击背景关闭
                document.getElementById('emoji-picker-backdrop').onclick = close;
            });
        },
        
        // 渲染分类emoji网格
        renderCategoryGrid(container, categories, subcategory) {
            const emojis = categories[subcategory] || [];
            container.innerHTML = emojis.map(emoji => `
                <button class="w-10 h-10 text-2xl hover:bg-orange-100 rounded-lg transition-colors flex items-center justify-center" data-emoji="${emoji}">
                    ${emoji}
                </button>
            `).join('');
        }
    }
};

// ============================================
// 应用核心逻辑
// ============================================
const app = {
    async init() {
        console.log('🍊 灵感食仓 v2.1 初始化中...');
        try {
            this.restoreSession();
            this.initRouter();
            this.bindGlobalEvents();
            
            // 如果用户已登录，先加载数据
            if (state.currentUser) {
                await this.loadInitialData();
            }
            
            // 触发初始路由渲染
            let path = window.location.pathname.slice(1) || 'home';
            path = path.replace(/^\//, '');
            if (!path) path = 'home';
            state.currentPage = path;
            this.renderPage(path);
            this.updateNavState(path);
            
            console.log('✅ 数据加载完成');
            this.hideLoadingScreen();
            console.log('✅ 应用初始化完成');
        } catch (error) {
            console.error('❌ 初始化失败:', error);
            this.showError('初始化失败，请刷新页面重试');
            this.hideLoadingScreen();
        }
    },

    restoreSession() {
        const token = localStorage.getItem(CONFIG.TOKEN_KEY);
        const userStr = localStorage.getItem(CONFIG.USER_KEY);
        if (token && userStr) {
            state.token = token;
            try {
                state.currentUser = JSON.parse(userStr);
                this.updateUserUI();
            } catch (e) {
                api.clearToken();
            }
        }
    },

    updateUserUI() {
        const user = state.currentUser;
        const nameEl = document.getElementById('user-name');
        const avatarEl = document.getElementById('user-avatar');
        const roleEl = document.getElementById('user-role');

        if (user) {
            const displayName = user.nickname || user.username || '用户';
            const displaySub = user.email || (user.role === 'admin' ? '管理员' : '普通用户');
            if (nameEl) nameEl.textContent = displayName;
            if (avatarEl) avatarEl.textContent = user.avatar || (user.username ? user.username[0].toUpperCase() : '用');
            if (roleEl) {
                roleEl.textContent = displaySub;
                roleEl.className = user.role === 'admin' ? 'text-xs text-orange-500 font-medium' : 'text-xs text-gray-400';
            }
        } else {
            if (nameEl) nameEl.textContent = '未登录';
            if (avatarEl) avatarEl.textContent = '👤';
            if (roleEl) roleEl.textContent = '';
        }
    },

    initRouter() {
        const handleRoute = async () => {
            let path = window.location.pathname.slice(1) || 'home';
            path = path.replace(/^\//, '');
            if (!path) path = 'home';
            state.currentPage = path;
            
            // 如果数据未加载且用户已登录，先加载数据
            if (state.currentUser && state.foods.length === 0 && state.locations.length === 0) {
                await this.loadInitialData();
            }
            
            this.renderPage(path);
            this.updateNavState(path);
        };
        
        // 使用 popstate 监听浏览器前进/后退
        window.addEventListener('popstate', handleRoute);
        // 不再在此处立即调用 handleRoute()，而是在 loadInitialData 完成后调用
    },

    navigateTo(path) {
        if (path.startsWith('#/')) {
            path = path.slice(2);
        }
        if (path.startsWith('/')) {
            path = path.slice(1);
        }
        if (!path) path = 'home';
        
        window.history.pushState({}, '', '/' + path);
        this.renderPage(path);
        this.updateNavState(path);
    },

    async renderPage(page) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;
        
        const protectedPages = ['spaces', 'inspiration', 'profile', 'recipes'];
        if (protectedPages.includes(page) && !state.currentUser) {
            mainContent.innerHTML = this.getLoginPromptHTML();
            this.bindPageEvents('login_prompt');
            return;
        }
        
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(10px)';
        mainContent.style.transition = 'all 0.3s ease';
        
        setTimeout(async () => {
            switch (page) {
                case 'home': mainContent.innerHTML = this.getHomePageHTML(); break;
                case 'login': mainContent.innerHTML = this.getLoginPageHTML(); break;
                case 'spaces': mainContent.innerHTML = this.getSpacesPageHTML(); break;
                case 'inspiration': mainContent.innerHTML = this.getInspirationPageHTML(); break;
                case 'profile': 
                    mainContent.innerHTML = this.getProfilePageHTML(); 
                    break;
                case 'recipes': mainContent.innerHTML = this.getRecipesPageHTML(); break;
                default: mainContent.innerHTML = this.getHomePageHTML();
            }
            
            this.bindPageEvents(page);
            if (typeof lucide !== 'undefined') lucide.createIcons();
            
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 150);
    },

    getHomePageHTML() {
        if (!state.currentUser) {
            return `
                <div class="min-h-screen flex flex-col items-center justify-center p-6">
                    <div class="text-center max-w-md animate-fadeInUp">
                        <div class="w-28 h-28 mx-auto mb-8 relative">
                            <div class="absolute inset-0 bg-gradient-to-tr from-orange-400 to-amber-500 rounded-3xl rotate-6 animate-pulse"></div>
                            <div class="absolute inset-0 bg-white rounded-3xl flex items-center justify-center shadow-2xl">
                                <span class="text-6xl">🍊</span>
                            </div>
                        </div>
                        <h1 class="text-4xl font-extrabold text-gray-800 mb-4 gradient-text">灵感食仓</h1>
                        <p class="text-gray-500 mb-8 text-lg">AI驱动的智能食物管理助手</p>
                        <div class="space-y-3">
                            <a href="/login" onclick="event.preventDefault(); app.navigateTo('login');" class="inline-flex items-center justify-center gap-2 w-full px-8 py-4 bg-gradient-to-r from-orange-400 to-amber-500 text-white rounded-2xl font-semibold shadow-lg shadow-orange-200 hover:shadow-xl hover:scale-[1.02] transition-all">
                                <span>开始体验</span>
                                <i data-lucide="arrow-right" class="w-5 h-5"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }
        
        const expiringFoods = state.foods.filter(f => {
            const days = utils.getRemainingDays(f.expiry_date);
            return days !== null && days >= 0 && days <= 3 && !f.is_finished;
        });

        const freshFoods = state.foods.filter(f => {
            const days = utils.getRemainingDays(f.expiry_date);
            return days !== null && days > 3 && !f.is_finished;
        });

        // 获取过期食品（已过期）
        const expiredFoods = state.foods.filter(f => {
            const days = utils.getRemainingDays(f.expiry_date);
            return days !== null && days < 0 && !f.is_finished;
        });

        return `
            <div class="p-4 md:p-6">
                <!-- 欢迎区域 -->
                <div class="welcome-banner mb-6 animate-fadeIn">
                    <div class="relative z-10">
                        <h1 class="text-2xl md:text-3xl font-bold mb-2">欢迎回来，${state.currentUser?.nickname || state.currentUser?.username || '用户'}！👋</h1>
                        <p class="text-white/90">今天想吃点什么呢？让AI为您推荐美味菜谱</p>
                    </div>
                </div>
                
                <!-- 统计卡片 -->
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 stagger-list">
                    <div class="stat-card cursor-pointer hover:shadow-md transition-shadow" onclick="document.getElementById('food-list').scrollIntoView({behavior: 'smooth'})">
                        <div class="stat-card-icon stat-card-icon-green">🥬</div>
                        <div class="stat-card-value">${state.foods?.filter(f => !f.is_finished).length || 0}</div>
                        <div class="stat-card-label">食材总数</div>
                    </div>
                    <div class="stat-card cursor-pointer hover:shadow-md transition-shadow" onclick="document.getElementById('expiry-section').scrollIntoView({behavior: 'smooth'})">
                        <div class="stat-card-icon stat-card-icon-amber">⚠️</div>
                        <div class="stat-card-value text-orange-500">${expiringFoods.length + expiredFoods.length || 0}</div>
                        <div class="stat-card-label">临期/过期</div>
                    </div>
                    <div class="stat-card cursor-pointer hover:shadow-md transition-shadow" onclick="app.navigateTo('spaces')">
                        <div class="stat-card-icon stat-card-icon-blue">📍</div>
                        <div class="stat-card-value">${state.locations?.length || 0}</div>
                        <div class="stat-card-label">储存空间</div>
                    </div>
                    <div class="stat-card cursor-pointer hover:shadow-md transition-shadow" onclick="app.navigateTo('recipes')">
                        <div class="stat-card-icon stat-card-icon-orange">📖</div>
                        <div class="stat-card-value">${state.recipeCount || 0}</div>
                        <div class="stat-card-label">灵感菜谱</div>
                    </div>
                </div>

                ${(expiringFoods.length > 0 || expiredFoods.length > 0) ? `
                <!-- 临期/过期提醒 -->
                <div id="expiry-section" class="expiry-alert mb-6 animate-fadeIn">
                    ${expiredFoods.length > 0 ? `
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-xl">⚠️</span>
                        <span class="font-bold text-red-800">已过期提醒</span>
                        <span class="text-sm text-red-700 ml-auto">${expiredFoods.length} 个食材</span>
                    </div>
                    <div class="flex flex-wrap gap-2 mb-3">
                        ${expiredFoods.slice(0, 5).map(f => {
                            return `<span class="px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-sm border-2 border-red-500 font-bold shadow-sm cursor-pointer hover:shadow-md transition-shadow" onclick="app.showFoodDetail(${f.id})">
                                ${f.icon || utils.getCategoryIcon(f.category)} ${f.name} (已过期)
                            </span>`;
                        }).join('')}
                        ${expiredFoods.length > 5 ? `<span class="px-3 py-1.5 bg-red-100 text-red-700 rounded-full text-sm font-bold">+${expiredFoods.length - 5}</span>` : ''}
                    </div>
                    ` : ''}
                    ${expiringFoods.length > 0 ? `
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-xl">🔥</span>
                        <span class="font-bold text-red-700">即将过期提醒</span>
                        <span class="text-sm text-red-600 ml-auto">${expiringFoods.length} 个食材</span>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        ${expiringFoods.slice(0, 5).map(f => {
                            const days = utils.getRemainingDays(f.expiry_date);
                            const displayText = days === 0 ? '今天' : `剩 ${days} 天`;
                            return `<span class="px-3 py-1.5 bg-white text-red-600 rounded-full text-sm border border-red-200 font-medium shadow-sm cursor-pointer hover:shadow-md transition-shadow" onclick="app.showFoodDetail(${f.id})">
                                ${f.icon || utils.getCategoryIcon(f.category)} ${f.name} (${displayText})
                            </span>`;
                        }).join('')}
                        ${expiringFoods.length > 5 ? `<span class="px-3 py-1.5 bg-red-100 text-red-600 rounded-full text-sm font-medium">+${expiringFoods.length - 5}</span>` : ''}
                    </div>
                    ` : ''}
                </div>
                ` : ''}
                
                <!-- 食材列表 -->
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <div class="p-4 border-b border-gray-100 flex items-center justify-between">
                        <h2 class="font-bold text-gray-800 flex items-center gap-2">
                            <i data-lucide="utensils" class="w-5 h-5 text-orange-500"></i>
                            我的食材
                        </h2>
                        <button onclick="app.showAddModal()" class="btn btn-primary text-sm py-2 px-4">
                            <i data-lucide="plus" class="w-4 h-4"></i>
                            添加食材
                        </button>
                    </div>
                    <div id="food-list" class="p-4">
                        ${(state.foods?.filter(f => !f.is_finished).length > 0 || state.foods?.filter(f => f.is_finished).length > 0)
                            ? `<div class="space-y-4">
                                ${state.foods.filter(f => !f.is_finished).length > 0 
                                    ? `<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-list">
                                        ${state.foods.filter(f => !f.is_finished).map(food => ui.createFoodCard(food)).join('')}
                                       </div>`
                                    : ''
                                }
                                ${state.foods.filter(f => f.is_finished).length > 0 
                                    ? `<div class="mt-6 pt-4 border-t border-gray-200">
                                        <h3 class="text-sm font-medium text-gray-500 mb-3 flex items-center gap-2">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                            </svg>
                                            已消耗 (${state.foods.filter(f => f.is_finished).length})
                                        </h3>
                                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-list opacity-60">
                                            ${state.foods.filter(f => f.is_finished).sort((a, b) => {
                                                const dateA = a.finished_at ? new Date(a.finished_at) : new Date(0);
                                                const dateB = b.finished_at ? new Date(b.finished_at) : new Date(0);
                                                return dateB - dateA;
                                            }).map(food => ui.createFoodCard(food)).join('')}
                                        </div>
                                       </div>`
                                    : ''
                                }
                               </div>`
                            : `<div class="empty-state">
                                <div class="empty-state-icon">🍽️</div>
                                <h3 class="empty-state-title">还没有添加任何食材</h3>
                                <p class="empty-state-text mb-6">开始使用AI智能录入，轻松管理您的食材</p>
                                <button onclick="app.showAddModal()" class="btn btn-primary">
                                    <i data-lucide="camera" class="w-4 h-4"></i>
                                    AI 智能录入
                                </button>
                            </div>`
                        }
                    </div>
                </div>
            </div>
        `;
    },

    getLoginPageHTML() {
        return `
            <div class="min-h-screen flex items-center justify-center p-6">
                <div class="w-full max-w-md">
                    <div class="text-center mb-8 animate-fadeInUp">
                        <div class="w-24 h-24 mx-auto mb-6 relative">
                            <div class="absolute inset-0 bg-gradient-to-tr from-orange-400 to-amber-500 rounded-3xl rotate-3 animate-pulse"></div>
                            <div class="absolute inset-0 bg-white rounded-3xl flex items-center justify-center shadow-xl">
                                <span class="text-5xl">🍊</span>
                            </div>
                        </div>
                        <h1 class="text-3xl font-bold text-gray-800 mb-2">欢迎回来</h1>
                        <p class="text-gray-500">登录您的灵感食仓账户</p>
                    </div>
                    
                    <div class="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 animate-fadeInUp delay-100">
                        <form id="login-form" class="space-y-5">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">用户名或邮箱</label>
                                <div class="relative">
                                    <i data-lucide="user" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"></i>
                                    <input type="text" id="login-username" required
                                        class="w-full pl-12 pr-4 py-3.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all text-gray-800"
                                        placeholder="请输入用户名或邮箱"
                                        value="">
                                </div>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
                                <div class="relative">
                                    <i data-lucide="lock" class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"></i>
                                    <input type="password" id="login-password" required 
                                        class="w-full pl-12 pr-4 py-3.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all text-gray-800"
                                        placeholder="请输入密码"
                                        value="">
                                </div>
                            </div>
                            <button type="submit" id="login-btn" 
                                class="w-full py-4 bg-gradient-to-r from-orange-400 to-amber-500 text-white rounded-xl font-semibold shadow-lg shadow-orange-200 hover:shadow-xl hover:scale-[1.02] transition-all flex items-center justify-center gap-2">
                                <span>登录</span>
                                <i data-lucide="arrow-right" class="w-5 h-5"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    },

    getSpacesPageHTML() {
        const rootLocations = state.locations.filter(l => !l.parent_id);
        
        return `
            <div class="p-4 md:p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2">储存空间</h1>
                        <p class="text-gray-500">管理您的冰箱、橱柜等储存位置</p>
                    </div>
                    <button onclick="app.showCreateLocationModal()" class="btn btn-primary text-sm py-2 px-4 whitespace-nowrap">
                        <i data-lucide="plus" class="w-4 h-4"></i>
                        新建空间
                    </button>
                </div>

                ${rootLocations.length === 0 ? `
                    <div class="empty-state bg-white rounded-2xl shadow-sm border border-gray-100">
                        <div class="empty-state-icon">🏠</div>
                        <h3 class="empty-state-title">还没有储存空间</h3>
                        <p class="empty-state-text mb-6">创建您的第一个储存空间，比如"冰箱"、"储藏室"</p>
                        <button onclick="app.showCreateLocationModal()" class="btn btn-primary text-sm py-2 px-4 whitespace-nowrap">
                            <i data-lucide="plus" class="w-4 h-4"></i>
                            创建第一个空间
                        </button>
                    </div>
                ` : `
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-list pb-4">
                        ${rootLocations.map(location => this.createLocationCard(location)).join('')}
                    </div>
                `}
            </div>
        `;
    },

    createLocationCard(location) {
        const childLocations = state.locations.filter(l => l.parent_id === location.id);
        const foodCount = state.foods.filter(f => f.location_id === location.id && !f.is_finished).length;
        const childFoodCount = childLocations.reduce((sum, child) => {
            return sum + state.foods.filter(f => f.location_id === child.id && !f.is_finished).length;
        }, 0);
        const totalFoodCount = foodCount + childFoodCount;

        return `
            <div class="glass-card p-5 cursor-pointer hover:shadow-lg hover:scale-[1.02] transition-all" onclick="app.showLocationDetail(${location.id})">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-gradient-to-br from-orange-100 to-amber-100 rounded-xl flex items-center justify-center text-2xl">
                            ${location.icon || '📦'}
                        </div>
                        <div>
                            <h3 class="font-bold text-gray-800">${location.name}</h3>
                            <p class="text-sm text-gray-500">${totalFoodCount} 个食材</p>
                        </div>
                    </div>
                    <div class="flex gap-1" onclick="event.stopPropagation()">
                        <button onclick="app.showCreateChildLocationModal(${location.id})" class="p-2 text-gray-400 hover:text-orange-500 transition-colors" title="添加子空间">
                            <i data-lucide="folder-plus" class="w-4 h-4"></i>
                        </button>
                        <button onclick="app.deleteLocation(${location.id})" class="p-2 text-gray-400 hover:text-red-500 transition-colors" title="删除空间">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>

                ${childLocations.length > 0 ? `
                    <div class="space-y-2 mt-4 pt-4 border-t border-gray-100">
                        <p class="text-xs text-gray-400 mb-2">子空间 (${childLocations.length})</p>
                        ${childLocations.map(child => `
                        <div class="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg hover:bg-orange-50 transition-colors" onclick="app.showLocationDetail(${child.id}); event.stopPropagation()">
                            <div class="flex items-center gap-2">
                                <span>${child.icon || '📁'}</span>
                                <span class="text-sm text-gray-700">${child.name}</span>
                            </div>
                            <span class="text-xs text-gray-400">${state.foods.filter(f => f.location_id === child.id && !f.is_finished).length} 个</span>
                        </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    },

    showLocationDetail(locationId) {
        const location = state.locations.find(l => l.id === locationId);
        if (!location) return;

        const childLocations = state.locations.filter(l => l.parent_id === locationId);
        const locationFoods = state.foods.filter(f => f.location_id === locationId && !f.is_finished);

        let foodsHTML = '';
        if (locationFoods.length > 0) {
            foodsHTML = `
                <div class="mt-4">
                    <p class="text-sm font-medium text-gray-700 mb-3">存放的食材 (${locationFoods.length})</p>
                    <div class="space-y-2 max-h-48 overflow-y-auto">
                        ${locationFoods.map(food => `
                            <div class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                                <span class="text-xl">${food.icon || utils.getCategoryIcon(food.category)}</span>
                                <div class="flex-1">
                                    <p class="text-sm font-medium text-gray-800">${food.name}</p>
                                    <p class="text-xs text-gray-500">${utils.formatDateFull(food.expiry_date)}</p>
                                </div>
                                <span class="text-xs text-gray-400">${Math.round(food.quantity)} ${food.unit}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let childHTML = '';
        if (childLocations.length > 0) {
            childHTML = `
                <div class="mt-4 pt-4 border-t border-gray-100">
                    <p class="text-sm font-medium text-gray-700 mb-3">子空间 (${childLocations.length})</p>
                    <div class="space-y-2">
                        ${childLocations.map(child => {
                            const childFoodCount = state.foods.filter(f => f.location_id === child.id && !f.is_finished).length;
                            return `
                                <div class="flex items-center justify-between p-2 bg-orange-50 rounded-lg cursor-pointer hover:bg-orange-100 transition-colors" onclick="app.showLocationDetail(${child.id})">
                                    <div class="flex items-center gap-2">
                                        <span>${child.icon || '📁'}</span>
                                        <span class="text-sm text-gray-700">${child.name}</span>
                                    </div>
                                    <span class="text-xs text-gray-500">${childFoodCount} 个食材</span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }

        ui.confirm({
            title: location.name,
            message: `${foodsHTML}${childHTML}`,
            type: 'info',
            icon: location.icon || '📦',
            html: true,
            showEdit: true,
            onEdit: () => this.editLocation(locationId)
        });
    },

    showLocationModal(options = {}) {
        return new Promise((resolve) => {
            const modal = document.getElementById('location-modal');
            const content = document.getElementById('location-modal-content');
            const titleEl = document.getElementById('location-modal-title');
            const headerIconEl = document.getElementById('location-modal-header-icon');
            const nameInput = document.getElementById('location-name');
            const iconInput = document.getElementById('location-icon');
            const parentIdInput = document.getElementById('location-parent-id');
            const locationIdInput = document.getElementById('location-id');
            const selectIconBtn = document.getElementById('location-select-icon-btn');
            const cancelBtn = document.getElementById('location-modal-cancel');
            const saveBtn = document.getElementById('location-modal-save');
            const closeBtn = document.getElementById('close-location-modal');
            const backdrop = document.getElementById('location-modal-backdrop');

            // 设置标题和初始值
            titleEl.textContent = options.title || '创建空间';
            headerIconEl.textContent = options.headerIcon || '📦';
            nameInput.value = options.name || '';
            iconInput.value = options.icon || '📦';
            parentIdInput.value = options.parentId || '';
            locationIdInput.value = options.locationId || '';

            // 显示模态框
            modal.classList.remove('hidden');
            requestAnimationFrame(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            });

            // 选择图标按钮
            selectIconBtn.onclick = async () => {
                const emoji = await ui.emojiPicker.show({ context: 'space' });
                if (emoji) {
                    iconInput.value = emoji;
                }
            };

            const close = (result = null) => {
                content.classList.remove('scale-100', 'opacity-100');
                content.classList.add('scale-95', 'opacity-0');
                setTimeout(() => { modal.classList.add('hidden'); }, 200);
                resolve(result);
            };

            const handleSave = async () => {
                const name = nameInput.value.trim();
                const icon = iconInput.value || '📦';
                const parentId = parentIdInput.value;
                const locationId = locationIdInput.value;

                if (!name) {
                    ui.toast('请输入空间名称', 'warning');
                    return;
                }

                try {
                    ui.showLoading(saveBtn, '保存中...');
                    
                    if (locationId) {
                        // 编辑模式
                        await api.put(`/locations/${locationId}`, { name, icon });
                        ui.toast('修改成功！', 'success');
                    } else if (parentId) {
                        // 创建子空间
                        const parsedParentId = parseInt(parentId);
                        if (isNaN(parsedParentId) || parsedParentId <= 0) {
                            ui.toast('无效的父空间ID', 'error');
                            ui.hideLoading(saveBtn);
                            return;
                        }
                        await api.post('/locations', { name, icon, parent_id: parsedParentId });
                        ui.toast('子空间创建成功！', 'success');
                    } else {
                        // 创建根空间
                        await api.post('/locations', { name, icon });
                        ui.toast('空间创建成功！', 'success');
                    }
                    
                    ui.hideLoading(saveBtn);
                    close(true);
                    await this.loadInitialData();
                    this.renderPage('spaces');
                } catch (error) {
                    ui.hideLoading(saveBtn);
                    ui.toast(error.message || '保存失败', 'error');
                }
            };

            cancelBtn.onclick = () => close(null);
            closeBtn.onclick = () => close(null);
            backdrop.onclick = () => close(null);
            saveBtn.onclick = handleSave;
        });
    },

    async editLocation(locationId) {
        const location = state.locations.find(l => l.id === locationId);
        if (!location) return;
        
        await this.showLocationModal({
            title: '编辑空间',
            headerIcon: '✏️',
            name: location.name,
            icon: location.icon || '📦',
            locationId: locationId
        });
    },

    async showCreateLocationModal() {
        await this.showLocationModal({
            title: '创建空间',
            headerIcon: '📦',
            name: '',
            icon: '📦'
        });
    },

    async showCreateChildLocationModal(parentId) {
        const parsedParentId = parseInt(parentId);
        if (isNaN(parsedParentId) || parsedParentId <= 0) {
            ui.toast('无效的父空间ID，请刷新页面后重试', 'error');
            console.error('Invalid parentId for createChildLocation:', parentId);
            return;
        }

        await this.showLocationModal({
            title: '创建子空间',
            headerIcon: '📁',
            name: '',
            icon: '📦',
            parentId: parsedParentId
        });
    },

    getInspirationPageHTML() {
        return `
            <div class="p-4 md:p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
                            灵机一动 <span class="text-3xl">✨</span>
                        </h1>
                        <p class="text-gray-500">AI 根据您的食材智能推荐菜谱</p>
                    </div>
                    <button onclick="app.navigateTo('recipes')" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-colors flex items-center gap-2">
                        <i data-lucide="book-open" class="w-4 h-4"></i>
                        查看菜谱
                    </button>
                </div>

                <!-- AI 对话区域 -->
                <div class="ai-message mb-6">
                    <div class="flex gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-orange-400 to-amber-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg">
                            <span class="text-2xl">🤔</span>
                        </div>
                        <div class="flex-1">
                            <p class="text-gray-700 mb-3 leading-relaxed">
                                您好！我已经查看了您的食材库，共有 <strong>${state.foods.filter(f => !f.is_finished).length}</strong> 种食材。
                                ${state.foods.filter(f => !f.is_finished).length > 0 ? '想吃点什么特别的吗？我可以为您推荐！' : '请先添加一些食材，我就能为您推荐菜谱了！'}
                            </p>
                            <div class="flex flex-wrap gap-2">
                                <button onclick="app.fetchRecipes('quick')" class="px-4 py-2 bg-white text-orange-600 rounded-xl text-sm font-medium border border-orange-200 hover:bg-orange-50 hover:border-orange-300 transition-all flex items-center gap-2 shadow-sm">
                                    <span>⚡</span> 快手晚餐
                                </button>
                                <button onclick="app.fetchRecipes('expiring')" class="px-4 py-2 bg-white text-amber-600 rounded-xl text-sm font-medium border border-amber-200 hover:bg-amber-50 hover:border-amber-300 transition-all flex items-center gap-2 shadow-sm">
                                    <span>🔥</span> 消耗临期
                                </button>
                                <button onclick="app.fetchRecipes('creative')" class="px-4 py-2 bg-white text-purple-600 rounded-xl text-sm font-medium border border-purple-200 hover:bg-purple-50 hover:border-purple-300 transition-all flex items-center gap-2 shadow-sm">
                                    <span>✨</span> 创意混搭
                                </button>
                                <button onclick="app.fetchRecipesCustom()" class="px-4 py-2 bg-white text-blue-600 rounded-xl text-sm font-medium border border-blue-200 hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center gap-2 shadow-sm">
                                    <span>💭</span> 我来决定
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 推荐结果区域 -->
                <div id="recipe-results">
                    <div class="text-center py-12 text-gray-400">
                        <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                            <span class="text-4xl">👨‍🍳</span>
                        </div>
                        <p class="text-lg">点击上方按钮，获取AI智能推荐</p>
                        <p class="text-sm mt-2">根据您的食材为您定制专属菜谱</p>
                    </div>
                </div>
            </div>
        `;
    },

    getProfilePageHTML() {
        const user = state.currentUser;
        if (!user) {
            return `
                <div class="min-h-screen flex items-center justify-center">
                    <div class="text-center">
                        <p class="text-gray-500 mb-4">请先登录</p>
                        <a href="/login" onclick="event.preventDefault(); app.navigateTo('login');" class="btn btn-primary">去登录</a>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="p-4 md:p-6">
                <h1 class="text-2xl font-bold text-gray-800 mb-6">个人中心</h1>
                
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
                    <div class="flex items-center gap-4 mb-6">
                        <div class="w-20 h-20 rounded-full bg-gradient-to-br from-orange-300 to-amber-400 flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                            ${user.avatar || user.username[0].toUpperCase()}
                        </div>
                        <div class="flex-1">
                            <h2 class="text-xl font-bold text-gray-800">${user.nickname || user.username}</h2>
                            <p class="text-gray-500">${user.email || ''}</p>
                            <span class="inline-flex items-center gap-1 px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs font-medium mt-2">
                                <i data-lucide="shield" class="w-3 h-3"></i>
                                ${user.role === 'admin' ? '管理员' : '普通用户'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-3 gap-4 pt-6 border-t border-gray-100">
                        <div class="text-center cursor-pointer hover:opacity-80" onclick="app.navigateTo('home')">
                            <div class="text-2xl font-bold text-gray-800">${state.foods?.filter(f => !f.is_finished).length || 0}</div>
                            <div class="text-sm text-gray-500">食材</div>
                        </div>
                        <div class="text-center cursor-pointer hover:opacity-80" onclick="app.navigateTo('spaces')">
                            <div class="text-2xl font-bold text-gray-800">${state.locations?.length || 0}</div>
                            <div class="text-sm text-gray-500">空间</div>
                        </div>
                        <div class="text-center cursor-pointer hover:opacity-80" onclick="app.navigateTo('recipes')">
                            <div class="text-2xl font-bold text-orange-500">${state.recipeCount || 0}</div>
                            <div class="text-sm text-gray-500">菜谱</div>
                        </div>
                    </div>
                </div>
                
                <div class="space-y-3">
                    <button onclick="app.showEditProfileModal()" class="w-full py-3.5 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 font-medium">
                        <i data-lucide="settings" class="w-5 h-5"></i>
                        账号设置
                    </button>
                    ${user.role === 'admin' ? `
                        <button onclick="app.showAdminPanel()" class="w-full py-3.5 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 font-medium">
                            <i data-lucide="users" class="w-5 h-5"></i>
                            用户管理
                        </button>
                    ` : ''}
                    <button onclick="app.logout()" class="w-full py-3.5 border border-red-200 text-red-500 rounded-xl hover:bg-red-50 transition-colors flex items-center justify-center gap-2 font-medium">
                        <i data-lucide="log-out" class="w-5 h-5"></i>
                        退出登录
                    </button>
                </div>
            </div>
        `;
    },

    getRecipesPageHTML() {
        return `
            <div class="p-4 md:p-6">
                <div class="flex items-center justify-between mb-4">
                    <h1 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
                        <i data-lucide="chef-hat" class="w-7 h-7 text-orange-500"></i>
                        灵感菜谱
                    </h1>
                    <button onclick="app.navigateTo('inspiration')" class="px-4 py-2 bg-gradient-to-r from-orange-400 to-amber-500 text-white rounded-xl font-medium shadow-lg shadow-orange-200 hover:shadow-xl transition-all flex items-center gap-2">
                        <i data-lucide="sparkles" class="w-4 h-4"></i>
                        灵机一动
                    </button>
                </div>
                
                <!-- 筛选和批量管理 -->
                <div class="flex flex-wrap items-center gap-3 mb-4">
                    <button id="filter-btn" onclick="app.showFilterModal()" class="px-4 py-2 border border-gray-300 text-gray-700 rounded-xl text-sm hover:bg-gray-50 transition-colors flex items-center gap-2">
                        <i data-lucide="filter" class="w-4 h-4"></i>
                        筛选
                    </button>
                    <div class="flex items-center gap-2 ml-auto">
                        <button id="batch-manage-btn" onclick="app.toggleBatchMode()" class="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50 transition-colors flex items-center gap-1">
                            <i data-lucide="check-square" class="w-4 h-4"></i>
                            批量管理
                        </button>
                        <button id="batch-delete-btn" onclick="app.deleteSelectedRecipes()" class="hidden px-3 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition-colors flex items-center gap-1">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                            删除选中
                        </button>
                    </div>
                </div>
                
                <div id="recipes-loading" class="flex items-center justify-center py-12">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
                </div>
                
                <div id="recipes-list" class="hidden space-y-4"></div>
                
                <div id="recipes-empty" class="hidden text-center py-12">
                    <div class="w-20 h-20 mx-auto mb-4 bg-orange-50 rounded-full flex items-center justify-center">
                        <span class="text-4xl">🍳</span>
                    </div>
                    <h3 class="text-lg font-medium text-gray-800 mb-2">暂无菜谱</h3>
                    <p class="text-gray-500 mb-6">去"灵机一动"生成你的第一个菜谱吧！</p>
                    <button onclick="app.navigateTo('inspiration')" class="px-6 py-3 bg-gradient-to-r from-orange-400 to-amber-500 text-white rounded-xl font-medium shadow-lg shadow-orange-200 hover:shadow-xl transition-all">
                        生成菜谱
                    </button>
                </div>
            </div>
        `;
    },

    async loadRecipes() {
        try {
            const data = await api.get('/recipes?page=1&page_size=100');
            state.recipes = data.items || [];
            const loading = document.getElementById('recipes-loading');
            const list = document.getElementById('recipes-list');
            const empty = document.getElementById('recipes-empty');
            
            loading?.classList.add('hidden');
            
            if (!data.items || data.items.length === 0) {
                list?.classList.add('hidden');
                empty?.classList.remove('hidden');
                return;
            }
            
            empty?.classList.add('hidden');
            list?.classList.remove('hidden');
            
            const categoryLabels = {
                'quick': '快手晚餐',
                'expiring': '消耗临期',
                'creative': '创意混搭',
                'custom': '自定义'
            };
            
            const categoryColors = {
                'quick': { bg: 'bg-red-100', text: 'text-red-600', label: '⚡' },
                'expiring': { bg: 'bg-amber-100', text: 'text-amber-600', label: '🔥' },
                'creative': { bg: 'bg-purple-100', text: 'text-purple-600', label: '✨' },
                'custom': { bg: 'bg-blue-100', text: 'text-blue-600', label: '💭' }
            };
            
            list.innerHTML = data.items.map(recipe => {
                const colors = categoryColors[recipe.category] || categoryColors['creative'];
                return `
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden" data-recipe-id="${recipe.id}">
                    <div class="p-5">
                        <div class="flex items-start gap-3 mb-3">
                            <label class="batch-checkbox hidden flex-shrink-0 mt-1">
                                <input type="checkbox" value="${recipe.id}" class="recipe-checkbox w-5 h-5 text-orange-500 rounded border-gray-300 focus:ring-orange-500">
                            </label>
                            <div class="flex-1">
                                <h3 class="text-lg font-bold text-gray-800">${recipe.name}</h3>
                                <p class="text-sm text-gray-500 mt-1">${recipe.description || ''}</p>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="px-2 py-1 ${colors.bg} ${colors.text} rounded-lg text-xs">${colors.label} ${categoryLabels[recipe.category] || recipe.category}</span>
                                <button onclick="app.deleteRecipe(${recipe.id})" class="p-1.5 text-gray-400 hover:text-red-500 transition-colors">
                                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                        
                        <div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
                            <span class="flex items-center gap-1">
                                <i data-lucide="clock" class="w-4 h-4"></i>
                                ${recipe.cooking_time || 20}分钟
                            </span>
                            <span class="flex items-center gap-1">
                                <i data-lucide="chef-hat" class="w-4 h-4"></i>
                                ${recipe.difficulty || '简单'}
                            </span>
                            <span class="flex items-center gap-1">
                                <i data-lucide="users" class="w-4 h-4"></i>
                                ${recipe.servings || 2}人份
                            </span>
                        </div>

                        <div class="border-t border-gray-100 pt-4">
                            <h4 class="font-medium text-gray-700 mb-2">所需食材</h4>
                            <div class="flex flex-wrap gap-2 mb-4">
                                ${(recipe.ingredients || []).map(ing => {
                                    let ingText = typeof ing === 'string' ? ing : (ing.name || '未知食材');
                                    let colorClass = utils.getIngredientColorClass(ingText);
                                    return `<span class="px-3 py-1 rounded-full text-sm ${colorClass}">${ing}</span>`;
                                }).join('')}
                            </div>
                        </div>

                        <div class="border-t border-gray-100 pt-4">
                            <h4 class="font-medium text-gray-700 mb-2">烹饪步骤</h4>
                            <ol class="space-y-2 text-sm text-gray-600">
                                ${(recipe.steps || []).map((step, i) => `
                                    <li class="flex gap-3">
                                        <span class="flex-shrink-0 w-6 h-6 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-xs font-medium">${i + 1}</span>
                                        <span>${step}</span>
                                    </li>
                                `).join('')}
                            </ol>
                        </div>
                    </div>
                </div>
            `}).join('');
            
            if (typeof lucide !== 'undefined') lucide.createIcons();
            
        } catch (error) {
            console.error('加载菜谱失败:', error);
            ui.toast('加载菜谱失败', 'error');
        }
    },

    async deleteRecipe(recipeId) {
        const confirmed = await ui.confirm({
            title: '删除菜谱',
            message: '确定要删除这个菜谱吗？',
            type: 'danger',
            icon: '🗑️'
        });
        
        if (!confirmed) return;
        
        try {
            await api.delete(`/recipes/${recipeId}`);
            ui.toast('菜谱已删除', 'success');
            this.loadRecipes();
        } catch (error) {
            ui.toast('删除失败: ' + error.message, 'error');
        }
    },

    toggleBatchMode() {
        const checkboxes = document.querySelectorAll('.batch-checkbox');
        const deleteBtn = document.getElementById('batch-delete-btn');
        const manageBtn = document.getElementById('batch-manage-btn');
        
        const isHidden = checkboxes[0]?.classList.contains('hidden');
        
        if (isHidden) {
            checkboxes.forEach(cb => cb.classList.remove('hidden'));
            deleteBtn?.classList.remove('hidden');
            manageBtn.innerHTML = '<i data-lucide="x" class="w-4 h-4"></i> 取消';
        } else {
            checkboxes.forEach(cb => cb.classList.add('hidden'));
            document.querySelectorAll('.recipe-checkbox').forEach(cb => cb.checked = false);
            deleteBtn?.classList.add('hidden');
            manageBtn.innerHTML = '<i data-lucide="check-square" class="w-4 h-4"></i> 批量管理';
        }
        
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async deleteSelectedRecipes() {
        const checkedBoxes = document.querySelectorAll('.recipe-checkbox:checked');
        const selectedIds = Array.from(checkedBoxes).map(cb => parseInt(cb.value));
        
        if (selectedIds.length === 0) {
            ui.toast('请选择要删除的菜谱', 'warning');
            return;
        }
        
        const confirmed = await ui.confirm({
            title: '批量删除菜谱',
            message: `确定要删除选中的 ${selectedIds.length} 个菜谱吗？`,
            type: 'danger',
            icon: '🗑️'
        });
        
        if (!confirmed) return;
        
        try {
            for (const id of selectedIds) {
                await api.delete(`/recipes/${id}`);
            }
            ui.toast(`已删除 ${selectedIds.length} 个菜谱`, 'success');
            this.toggleBatchMode();
            this.loadRecipes();
        } catch (error) {
            ui.toast('删除失败: ' + error.message, 'error');
        }
    },

    filterRecipes() {
        const difficulty = state.recipeFilters?.difficulty || '';
        const time = state.recipeFilters?.time || '';
        const category = state.recipeFilters?.category || '';
        
        const recipeCards = document.querySelectorAll('#recipes-list > div');
        
        recipeCards.forEach(card => {
            const recipeId = parseInt(card.dataset.recipeId);
            const recipe = state.recipes?.find(r => r.id === recipeId);
            
            if (!recipe) {
                card.classList.add('hidden');
                return;
            }
            
            let show = true;
            
            if (difficulty && recipe.difficulty !== difficulty) {
                show = false;
            }
            
            if (time) {
                const maxTime = parseInt(time);
                if (!recipe.cooking_time || recipe.cooking_time > maxTime) {
                    show = false;
                }
            }
            
            if (category && recipe.category !== category) {
                show = false;
            }
            
            if (show) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
        
        // Update filter button appearance
        const filterBtn = document.getElementById('filter-btn');
        if (filterBtn) {
            if (difficulty || time || category) {
                filterBtn.classList.add('bg-orange-100', 'border-orange-400', 'text-orange-700');
            } else {
                filterBtn.classList.remove('bg-orange-100', 'border-orange-400', 'text-orange-700');
            }
        }
    },

    showFilterModal() {
        const modal = document.getElementById('filter-modal');
        const content = document.getElementById('filter-modal-content');
        
        if (modal && content) {
            modal.classList.remove('hidden');
            requestAnimationFrame(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            });
            return;
        }
        
        const newModal = document.createElement('div');
        newModal.id = 'filter-modal';
        newModal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm';
        
        newModal.innerHTML = `
            <div id="filter-modal-content" class="bg-white rounded-3xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden scale-95 opacity-0 transition-all duration-200">
                <div class="p-5 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-orange-50 to-amber-50">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 bg-gradient-to-br from-orange-400 to-amber-500 rounded-xl flex items-center justify-center text-white shadow-lg">
                            <i data-lucide="filter" class="w-5 h-5"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-800">筛选菜谱</h3>
                    </div>
                    <button onclick="app.closeFilterModal()" class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">
                        <i data-lucide="x" class="w-5 h-5"></i>
                    </button>
                </div>
                <div class="p-5 space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">难度</label>
                        <select id="modal-filter-difficulty" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all bg-white">
                            <option value="">不限</option>
                            <option value="简单" ${state.recipeFilters?.difficulty === '简单' ? 'selected' : ''}>简单</option>
                            <option value="中等" ${state.recipeFilters?.difficulty === '中等' ? 'selected' : ''}>中等</option>
                            <option value="困难" ${state.recipeFilters?.difficulty === '困难' ? 'selected' : ''}>困难</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">烹饪时间</label>
                        <select id="modal-filter-time" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all bg-white">
                            <option value="">不限</option>
                            <option value="15" ${state.recipeFilters?.time === '15' ? 'selected' : ''}>15分钟内</option>
                            <option value="30" ${state.recipeFilters?.time === '30' ? 'selected' : ''}>30分钟内</option>
                            <option value="60" ${state.recipeFilters?.time === '60' ? 'selected' : ''}>1小时内</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">类型</label>
                        <select id="modal-filter-category" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all bg-white">
                            <option value="">不限</option>
                            <option value="quick" ${state.recipeFilters?.category === 'quick' ? 'selected' : ''}>快手晚餐</option>
                            <option value="expiring" ${state.recipeFilters?.category === 'expiring' ? 'selected' : ''}>消耗临期</option>
                            <option value="creative" ${state.recipeFilters?.category === 'creative' ? 'selected' : ''}>创意混搭</option>
                            <option value="custom" ${state.recipeFilters?.category === 'custom' ? 'selected' : ''}>自定义</option>
                        </select>
                    </div>
                </div>
                <div class="p-5 border-t border-gray-100 flex gap-3 bg-gray-50">
                    <button onclick="app.clearRecipeFilters()" class="flex-1 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-white hover:shadow-md transition-all font-medium">
                        清除筛选
                    </button>
                    <button onclick="app.applyRecipeFilters()" class="flex-1 py-3 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-xl hover:from-orange-600 hover:to-amber-600 hover:shadow-lg transition-all font-medium shadow-lg shadow-orange-200">
                        应用筛选
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(newModal);
        
        requestAnimationFrame(() => {
            const content = document.getElementById('filter-modal-content');
            content.classList.remove('scale-95', 'opacity-0');
            content.classList.add('scale-100', 'opacity-100');
        });
        
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        newModal.addEventListener('click', (e) => {
            if (e.target === newModal) {
                app.closeFilterModal();
            }
        });
    },

    closeFilterModal() {
        const modal = document.getElementById('filter-modal');
        const content = document.getElementById('filter-modal-content');
        
        if (modal && content) {
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                modal.remove();
            }, 200);
        }
    },

    applyRecipeFilters() {
        state.recipeFilters = {
            difficulty: document.getElementById('modal-filter-difficulty')?.value || '',
            time: document.getElementById('modal-filter-time')?.value || '',
            category: document.getElementById('modal-filter-category')?.value || ''
        };
        
        this.closeFilterModal();
        this.filterRecipes();
    },

    clearRecipeFilters() {
        state.recipeFilters = { difficulty: '', time: '', category: '' };
        this.closeFilterModal();
        this.filterRecipes();
    },

    updateNavState(page) {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            const btnPage = btn.dataset.page;
            if (btnPage === page) {
                btn.classList.remove('text-gray-400');
                btn.classList.add('text-orange-500');
            } else {
                btn.classList.remove('text-orange-500');
                btn.classList.add('text-gray-400');
            }
        });
        document.querySelectorAll('.sidebar-nav-btn').forEach(btn => {
            const btnPage = btn.dataset.page;
            if (btnPage === page) {
                btn.classList.remove('text-gray-600', 'hover:bg-gray-50');
                btn.classList.add('text-orange-500', 'bg-orange-50');
            } else {
                btn.classList.remove('text-orange-500', 'bg-orange-50');
                btn.classList.add('text-gray-600', 'hover:bg-gray-50');
            }
        });
    },

    bindGlobalEvents() {
        // 导航按钮
        document.querySelectorAll('.nav-btn, .sidebar-nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                if (page) this.navigateTo(page);
            });
        });

        // 登出按钮
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) logoutBtn.addEventListener('click', () => this.logout());

        // 添加按钮
        const addBtn = document.getElementById('add-btn');
        const desktopAddBtn = document.getElementById('desktop-add-btn');
        if (addBtn) addBtn.addEventListener('click', () => this.showAddModal());
        if (desktopAddBtn) desktopAddBtn.addEventListener('click', () => this.showAddModal());

        // 关闭模态框
        const closeModalBtn = document.getElementById('close-ai-modal');
        const modalBackdrop = document.getElementById('ai-modal-backdrop');
        if (closeModalBtn) closeModalBtn.addEventListener('click', () => this.hideAddModal());
        if (modalBackdrop) modalBackdrop.addEventListener('click', () => this.hideAddModal());

        // 绑定AI模态框事件（静态元素，只需绑定一次）
        this.bindAIModalEvents();
    },

    bindPageEvents(page) {
        if (page === 'login') {
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleLogin();
                });
            }
        } else if (page === 'login_prompt') {
            const loginBtn = document.getElementById('prompt-login-btn');
            if (loginBtn) {
                loginBtn.addEventListener('click', () => this.navigateTo('login'));
            }
        } else if (page === 'recipes') {
            this.loadRecipes();
        }
    },

    bindAIModalEvents() {
        // 输入方式选择
        document.querySelectorAll('.input-method-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.input-method-btn').forEach(b => {
                    b.classList.remove('active', 'border-orange-200', 'bg-orange-50', 'text-orange-600');
                    b.classList.add('border-gray-200', 'text-gray-600');
                });
                const target = e.currentTarget;
                target.classList.add('active', 'border-orange-200', 'bg-orange-50', 'text-orange-600');
                target.classList.remove('border-gray-200', 'text-gray-600');
                
                const method = target.dataset.method;
                this.handleInputMethodChange(method);
            });
        });

        // 图片上传
        const imageInput = document.getElementById('image-input');
        const uploadZone = document.getElementById('upload-zone');
        
        if (uploadZone) {
            uploadZone.addEventListener('click', () => imageInput?.click());
            uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadZone.classList.add('border-orange-400', 'bg-orange-50');
            });
            uploadZone.addEventListener('dragleave', () => {
                uploadZone.classList.remove('border-orange-400', 'bg-orange-50');
            });
            uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadZone.classList.remove('border-orange-400', 'bg-orange-50');
                const files = e.dataTransfer.files;
                if (files.length > 0) this.handleImageSelect(files[0]);
            });
        }

        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) this.handleImageSelect(e.target.files[0]);
            });
        }

        // 移除图片
        const removeImageBtn = document.getElementById('remove-image');
        if (removeImageBtn) {
            removeImageBtn.addEventListener('click', () => this.handleImageRemove());
        }

        // AI识别按钮
        const recognizeBtn = document.getElementById('ai-recognize-btn');
        if (recognizeBtn) {
            recognizeBtn.addEventListener('click', () => this.handleAIRecognize());
        }

        // 保存按钮
        const confirmSaveBtn = document.getElementById('confirm-save');
        const cancelEditBtn = document.getElementById('cancel-edit');
        
        if (confirmSaveBtn) {
            confirmSaveBtn.addEventListener('click', () => this.handleSaveFood());
        }
        if (cancelEditBtn) {
            cancelEditBtn.addEventListener('click', () => this.hideAddModal());
        }
    },

    handleInputMethodChange(method) {
        const uploadZone = document.getElementById('upload-zone');
        const previewContainer = document.getElementById('preview-container');
        const imageInput = document.getElementById('image-input');
        const aiRecognizeBtn = document.getElementById('ai-recognize-btn');

        if (method === 'camera') {
            imageInput?.setAttribute('capture', 'environment');
            imageInput?.click();
            aiRecognizeBtn?.classList.remove('hidden');
        } else if (method === 'upload') {
            imageInput?.removeAttribute('capture');
            imageInput?.click();
            aiRecognizeBtn?.classList.remove('hidden');
        } else if (method === 'voice') {
            aiRecognizeBtn?.classList.remove('hidden');
            this.handleVoiceInput();
        } else if (method === 'manual') {
            this.hideAddModal();
            this.showManualAddModal();
        }
    },

    async showManualAddModal() {
        const result = await ui.showEditModal({
            title: '添加食材',
            icon: '🍽️',
            fields: [
                { name: 'name', label: '品名', placeholder: '输入食材名称' },
                {
                    name: 'icon',
                    label: '图标',
                    type: 'icon',
                    context: 'food',
                    value: '📦'
                },
                {
                    name: 'category',
                    label: '类别',
                    type: 'select',
                    value: 'other',
                    options: state.categories.map(c => ({value: c.id, label: c.icon + ' ' + c.name}))
                },
                { 
                    name: 'location_id', 
                    label: '存放位置', 
                    type: 'select', 
                    value: '', 
                    options: [{value: '', label: '选择存放位置'}, ...utils.formatLocationOptions(state.locations)] 
                },
                { 
                    name: 'quantity', 
                    label: '数量', 
                    type: 'combined', 
                    value: {value: 1, unit: '个'}, 
                    units: ['个', '克', '千克', '升', '毫升', '盒', '瓶', '包', '袋', '斤'], 
                    unitName: 'unit' 
                },
                { name: 'expiry_date', label: '保质期', type: 'date', defaultRemainingDays: 3 },
                { name: 'is_opened', label: '已开封', type: 'checkbox', value: false },
                { name: 'notes', label: '备注', type: 'textarea' }
            ]
        });

        if (!result) return;

        try {
            await api.post('/food', {
                ...result,
                location_id: result.location_id ? parseInt(result.location_id) : null,
                quantity: parseFloat(result.quantity) || 1,
                icon: result.icon || '📦'
            });
            ui.toast('添加成功！', 'success');
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.toast('添加失败: ' + error.message, 'error');
        }
    },

    async handleVoiceInput() {
        ui.confirm({
            title: '敬请期待',
            message: '语音输入功能正在开发中，敬请期待！',
            type: 'info',
            icon: '🎤'
        });
    },

    async handleVoiceRecognition(text) {
        this.showAILoading('正在理解您的描述...');
        
        try {
            // 模拟AI解析
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // 简单关键词匹配演示
            const foods = [
                { name: '苹果', category: 'fruit', icon: '🍎' },
                { name: '香蕉', category: 'fruit', icon: '🍌' },
                { name: '牛奶', category: 'dairy', icon: '🥛' },
                { name: '鸡蛋', category: 'dairy', icon: '🥚' }
            ];
            
            const matchedFood = foods.find(f => text.includes(f.name));
            
            this.hideAILoading();
            
            if (matchedFood) {
                this.showAIResultEditor({
                    name: matchedFood.name,
                    category: matchedFood.category,
                    icon: matchedFood.icon,
                    quantity: 1,
                    unit: text.includes('盒') ? '盒' : text.includes('瓶') ? '瓶' : '个',
                    expiry_date: null
                });
            } else {
                // 显示空表单让用户填写
                this.showAIResultEditor({
                    name: '',
                    category: 'other',
                    quantity: 1,
                    unit: '个'
                });
                ui.toast('请补充食物信息', 'info');
            }
        } catch (error) {
            this.hideAILoading();
            ui.toast('识别失败，请手动输入', 'error');
        }
    },

    async handleImageSelect(file) {
        if (!file.type.startsWith('image/')) {
            ui.toast('请选择图片文件', 'error');
            return;
        }

        state.selectedImage = file;
        
        // 显示预览
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImage = document.getElementById('preview-image');
            const previewContainer = document.getElementById('preview-container');
            const uploadZone = document.getElementById('upload-zone');
            const recognizeBtn = document.getElementById('ai-recognize-btn');
            
            if (previewImage) previewImage.src = e.target.result;
            if (previewContainer) previewContainer.classList.remove('hidden');
            if (uploadZone) uploadZone.classList.add('hidden');
            if (recognizeBtn) recognizeBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    },

    handleImageRemove() {
        state.selectedImage = null;
        const previewImage = document.getElementById('preview-image');
        const previewContainer = document.getElementById('preview-container');
        const uploadZone = document.getElementById('upload-zone');
        const recognizeBtn = document.getElementById('ai-recognize-btn');
        const imageInput = document.getElementById('image-input');
        
        if (previewImage) previewImage.src = '';
        if (previewContainer) previewContainer.classList.add('hidden');
        if (uploadZone) uploadZone.classList.remove('hidden');
        if (recognizeBtn) recognizeBtn.disabled = true;
        if (imageInput) imageInput.value = '';
    },

    async handleAIRecognize() {
        if (!state.selectedImage) {
            ui.toast('请先选择图片', 'warning');
            return;
        }

        this.showAILoading('正在分析图片...');

        try {
            // 压缩图片
            const compressedImage = await utils.compressImage(state.selectedImage, 1024, 1024, 0.8);
            
            // 创建FormData
            const formData = new FormData();
            formData.append('image', compressedImage, 'food.jpg');

            // 调用AI识别API
            this.updateAILoadingText('识别食物中...');
            
            try {
                const result = await api.upload('/ai/recognize', formData);
                
                this.hideAILoading();
                
                if (result.success && result.results && result.results.length > 0) {
                    const recognition = result.results[0];
                    this.showAIResultEditor({
                        name: recognition.name,
                        category: recognition.category,
                        icon: recognition.icon || utils.getCategoryIcon(recognition.category),
                        quantity: recognition.quantity || 1,
                        unit: recognition.unit || '个',
                        expiry_date: recognition.expiry_days 
                            ? new Date(Date.now() + recognition.expiry_days * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                            : null,
                        storage_advice: recognition.description,
                        ai_confidence: recognition.confidence
                    });
                    ui.toast('识别成功！请确认信息', 'success');
                } else {
                    throw new Error('未能识别食物');
                }
            } catch (apiError) {
                console.warn('API识别失败，使用模拟数据:', apiError);
                
                // 模拟识别结果
                await new Promise(resolve => setTimeout(resolve, 1000));
                this.hideAILoading();
                
                this.showAIResultEditor({
                    name: '新鲜食材',
                    category: 'vegetable',
                    icon: '🥬',
                    quantity: 1,
                    unit: '个',
                    expiry_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                });
                ui.toast('请手动填写食物信息', 'info');
            }
        } catch (error) {
            this.hideAILoading();
            ui.toast('识别失败: ' + error.message, 'error');
        }
    },

    showAIResultEditor(data) {
        const resultEdit = document.getElementById('ai-result-edit');
        if (!resultEdit) return;

        // 填充表单
        document.getElementById('edit-name').value = data.name || '';
        document.getElementById('edit-category').value = data.category || 'other';
        document.getElementById('edit-quantity').value = data.quantity || 1;
        document.getElementById('edit-unit').value = data.unit || '个';
        document.getElementById('edit-expiry').value = data.expiry_date || '';
        document.getElementById('edit-notes').value = data.storage_advice || '';
        document.getElementById('edit-opened').checked = false;
        
        // 设置图标（优先使用AI返回的图标，否则根据类别获取默认图标）
        const iconInput = document.getElementById('edit-icon');
        if (iconInput) {
            iconInput.value = data.icon || utils.getCategoryIcon(data.category) || '📦';
            
            // 图标选择按钮事件
            const iconBtn = document.getElementById('edit-icon-btn');
            if (iconBtn) {
                iconBtn.onclick = async () => {
                    const emoji = await ui.emojiPicker.show({ context: 'food' });
                    if (emoji) iconInput.value = emoji;
                };
            }
        }

        // 填充位置选择
        this.populateLocationSelect();

        // 显示编辑区域
        resultEdit.classList.remove('hidden');
        resultEdit.classList.add('animate-fadeIn');

        // 隐藏识别按钮
        const recognizeBtn = document.getElementById('ai-recognize-btn');
        if (recognizeBtn) recognizeBtn.classList.add('hidden');
    },

    populateLocationSelect() {
        const select = document.getElementById('edit-location');
        if (!select) return;

        select.innerHTML = '<option value="">选择存放位置</option>';
        
        const locationOptions = utils.formatLocationOptions(state.locations);
        locationOptions.forEach(loc => {
            const option = document.createElement('option');
            option.value = loc.value;
            option.textContent = loc.label;
            select.appendChild(option);
        });
    },

    async handleSaveFood() {
        const name = document.getElementById('edit-name')?.value;
        const category = document.getElementById('edit-category')?.value;
        const locationId = document.getElementById('edit-location')?.value;
        const quantity = document.getElementById('edit-quantity')?.value;
        const unit = document.getElementById('edit-unit')?.value;
        const expiryDate = document.getElementById('edit-expiry')?.value;
        const isOpened = document.getElementById('edit-opened')?.checked;
        const notes = document.getElementById('edit-notes')?.value;
        const iconInput = document.getElementById('edit-icon')?.value;

        if (!name) {
            ui.toast('请输入食物名称', 'warning');
            return;
        }
        
        if (!locationId) {
            ui.toast('请选择存放位置', 'warning');
            return;
        }

        const foodData = {
            name,
            category,
            quantity: parseFloat(quantity) || 1,
            unit,
            location_id: locationId ? parseInt(locationId) : null,
            expiry_date: expiryDate || null,
            is_opened: isOpened,
            notes,
            icon: iconInput || utils.getCategoryIcon(category)
        };

        try {
            ui.showLoading('#confirm-save', '保存中...');
            await api.post('/food', foodData);
            ui.hideLoading('#confirm-save');
            
            ui.toast('添加成功！', 'success');
            this.hideAddModal();
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.hideLoading('#confirm-save');
            ui.toast('保存失败: ' + error.message, 'error');
        }
    },

    showAILoading(text = 'AI思考中...') {
        const loading = document.getElementById('ai-loading');
        const loadingText = document.getElementById('ai-loading-text');
        if (loading) loading.classList.remove('hidden');
        if (loadingText) loadingText.textContent = text;
    },

    hideAILoading() {
        const loading = document.getElementById('ai-loading');
        if (loading) loading.classList.add('hidden');
    },

    updateAILoadingText(text) {
        const loadingText = document.getElementById('ai-loading-text');
        if (loadingText) loadingText.textContent = text;
    },

    async handleLogin() {
        const username = document.getElementById('login-username')?.value;
        const password = document.getElementById('login-password')?.value;
        const loginBtn = document.getElementById('login-btn');
        
        if (!username || !password) {
            ui.toast('请输入用户名和密码', 'error');
            return;
        }

        ui.showLoading(loginBtn, '登录中...');
        
        try {
            const data = await api.post('/auth/login', { username, password });
            
            if (data.access_token) {
                api.setToken(data.access_token);
                state.currentUser = data.user;
                localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(data.user));
                
                ui.toast('登录成功！', 'success');
                this.updateUserUI();
                await this.loadInitialData();
                this.navigateTo('home');
            }
        } catch (error) {
            ui.toast(error.message || '登录失败，请检查账号密码', 'error');
        } finally {
            ui.hideLoading(loginBtn);
        }
    },

    async logout() {
        const confirmed = await ui.confirm({
            title: '退出登录',
            message: '确定要退出登录吗？',
            type: 'info',
            icon: '👋'
        });

        if (!confirmed) return;

        api.clearToken();
        state.currentUser = null;
        this.updateUserUI();
        this.navigateTo('home');
        ui.toast('已安全退出');
    },

    async showEditProfileModal() {
        const user = state.currentUser;
        if (!user) return;

        const result = await ui.showEditModal({
            title: '账号设置',
            icon: '⚙️',
            fields: [
                { name: 'nickname', label: '昵称', value: user.nickname || '' },
                { name: 'password', label: '新密码', type: 'password', placeholder: '不修改请留空' }
            ]
        });

        if (!result) return;

        try {
            const updateData = {
                nickname: result.nickname || null,
            };
            
            if (result.password) {
                updateData.password = result.password;
            }

            const updatedUser = await api.put('/auth/me', updateData);
            
            // 更新本地状态
            state.currentUser = updatedUser;
            localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(updatedUser));
            
            ui.toast('个人资料已更新', 'success');
            this.renderPage('profile');
        } catch (error) {
            ui.toast('更新失败: ' + error.message, 'error');
        }
    },

    getLoginPromptHTML() {
        return `
            <div class="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 animate-fadeIn">
                <div class="w-24 h-24 bg-orange-50 rounded-3xl flex items-center justify-center mb-6">
                    <span class="text-5xl">🔒</span>
                </div>
                <h2 class="text-2xl font-bold text-gray-800 mb-2">请先登录</h2>
                <p class="text-gray-500 mb-8 max-w-xs mx-auto">登录后即可使用此功能，管理您的食材和获取灵感</p>
                <button id="prompt-login-btn" class="px-8 py-3 bg-gradient-to-r from-orange-400 to-amber-500 text-white rounded-xl font-semibold shadow-lg shadow-orange-200 hover:shadow-xl transition-all flex items-center gap-2">
                    <span>立即登录</span>
                </button>
            </div>
        `;
    },

    async loadInitialData() {
        if (!state.currentUser) return;
        
        try {
            const [foodsData, locationsData, recipesData] = await Promise.all([
                api.get('/food?include_finished=true&page_size=100').catch(() => ({ items: [] })),
                api.get('/locations').catch(() => ({ items: [] })),
                api.get('/recipes?page=1&page_size=1').catch(() => ({ total: 0 }))
            ]);
            
            state.foods = foodsData?.items || [];
            state.locations = locationsData?.items || [];
            state.currentRecipes = recipesData?.items || [];
            state.recipeCount = recipesData?.total || 0;
            
            const recipeCountEl = document.getElementById('recipe-count');
            if (recipeCountEl) {
                recipeCountEl.textContent = state.recipeCount;
            }
        } catch (error) {
            console.warn('加载初始数据失败:', error);
        }
    },

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            loadingScreen.style.transition = 'opacity 0.5s ease';
            setTimeout(() => { loadingScreen.style.display = 'none'; }, 500);
        }
    },

    showAddModal() {
        if (!state.currentUser) {
            ui.toast('请先登录', 'warning');
            this.navigateTo('login');
            return;
        }

        // 重置模态框状态
        state.selectedImage = null;
        const previewContainer = document.getElementById('preview-container');
        const uploadZone = document.getElementById('upload-zone');
        const resultEdit = document.getElementById('ai-result-edit');
        const recognizeBtn = document.getElementById('ai-recognize-btn');
        const imageInput = document.getElementById('image-input');

        if (previewContainer) previewContainer.classList.add('hidden');
        if (uploadZone) uploadZone.classList.remove('hidden');
        if (resultEdit) resultEdit.classList.add('hidden');
        if (recognizeBtn) {
            recognizeBtn.classList.remove('hidden');
            recognizeBtn.disabled = true;
        }
        if (imageInput) imageInput.value = '';

        // 显示模态框
        const modal = document.getElementById('ai-modal');
        const content = document.getElementById('ai-modal-content');
        
        if (modal && content) {
            modal.classList.remove('hidden');
            setTimeout(() => {
                content.classList.remove('scale-95', 'opacity-0');
                content.classList.add('scale-100', 'opacity-100');
            }, 10);
        }
    },

    hideAddModal() {
        const modal = document.getElementById('ai-modal');
        const content = document.getElementById('ai-modal-content');
        
        if (modal && content) {
            content.classList.remove('scale-100', 'opacity-100');
            content.classList.add('scale-95', 'opacity-0');
            setTimeout(() => { modal.classList.add('hidden'); }, 200);
        }
    },

    showFoodDetail(foodId) {
        const food = state.foods.find(f => f.id === foodId);
        if (!food) return;

        const remainingDays = utils.getRemainingDays(food.expiry_date);
        let statusClass = 'bg-green-100 text-green-700';
        let statusText = '新鲜';
        
        if (remainingDays !== null) {
            if (remainingDays < 0) {
                statusClass = 'bg-red-100 text-red-700';
                statusText = `已过期 ${Math.abs(remainingDays)} 天`;
            } else if (remainingDays <= 3) {
                statusClass = 'bg-amber-100 text-amber-700';
                statusText = `剩余 ${remainingDays} 天`;
            } else {
                statusText = `剩余 ${remainingDays} 天`;
            }
        } else {
            statusText = '未设置期限';
            statusClass = 'bg-gray-100 text-gray-600';
        }

        const locationName = food.location_id 
            ? (state.locations.find(l => l.id === food.location_id)?.name || '未知位置')
            : '未分类';
        
        const locationIcon = food.location_icon || '📦';
        
        let locationDisplay = locationName;
        if (food.parent_location_name) {
            locationDisplay = `${food.parent_location_name} - ${locationName}`;
        }

        const html = `
            <div class="space-y-4">
                <div class="flex items-center justify-between bg-gray-50 p-3 rounded-xl">
                    <div class="flex items-center gap-2">
                        <span class="text-2xl">${food.icon || utils.getCategoryIcon(food.category)}</span>
                        <div>
                            <p class="text-xs text-gray-500">当前状态</p>
                            <span class="text-sm font-bold px-2 py-0.5 rounded-md ${statusClass}">${statusText}</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="text-xs text-gray-500">数量</p>
                        <p class="text-lg font-bold text-gray-800">${Math.round(food.quantity)} <span class="text-sm font-normal text-gray-500">${food.unit}</span></p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-50 p-3 rounded-xl text-center">
                        <p class="text-xs text-gray-500 mb-1">分类</p>
                        <p class="font-medium text-gray-800 flex items-center justify-center gap-1">
                            ${utils.getCategoryIcon(food.category)} ${utils.getCategoryName(food.category)}
                        </p>
                    </div>
                    <div class="bg-gray-50 p-3 rounded-xl text-center">
                        <p class="text-xs text-gray-500 mb-1">存放位置</p>
                        <p class="font-medium text-gray-800 flex items-center justify-center gap-1">
                            ${locationIcon} ${locationDisplay}
                        </p>
                    </div>
                    <div class="bg-gray-50 p-3 rounded-xl text-center">
                        <p class="text-xs text-gray-500 mb-1">保质期至</p>
                        <p class="font-medium text-gray-800">${utils.formatDateFull(food.expiry_date)}</p>
                    </div>
                    <div class="bg-gray-50 p-3 rounded-xl text-center">
                        <p class="text-xs text-gray-500 mb-1">开封状态</p>
                        <p class="font-medium ${food.is_opened ? 'text-orange-600' : 'text-gray-600'}">
                            ${food.is_opened ? '已开封' : '未开封'}
                        </p>
                    </div>
                </div>

                ${food.notes ? `
                    <div class="bg-orange-50 p-3 rounded-xl border border-orange-100">
                        <p class="text-xs text-orange-600 mb-1 font-bold">备注</p>
                        <p class="text-sm text-gray-700">${food.notes}</p>
                    </div>
                ` : ''}
            </div>
        `;

        ui.confirm({
            title: food.name,
            message: html,
            type: 'info',
            icon: food.icon || utils.getCategoryIcon(food.category),
            html: true,
            showEdit: true,
            showDelete: true,
            showCancel: false,
            editBtnClass: 'flex-1 py-3 border border-gray-300 text-gray-700 rounded-xl font-medium hover:bg-gray-50 transition-all',
            onEdit: () => this.editFood(foodId),
            onDelete: () => this.deleteFood(foodId)
        });
    },

    async deleteFood(foodId) {
        // Confirmation is implicit in the delete button click which resolves the promise, 
        // but ui.confirm closes immediately. 
        // We can add a second confirmation if needed, but the delete button in modal is usually intentional.
        // Let's add a quick double-check since it's destructive.
        
        const confirmed = await ui.confirm({
            title: '确认删除',
            message: '确定要删除这个食材吗？此操作不可恢复。',
            type: 'danger',
            icon: '🗑️'
        });

        if (!confirmed) return;

        try {
            await api.delete(`/food/${foodId}`);
            ui.toast('食材已删除', 'success');
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.toast('删除失败: ' + error.message, 'error');
        }
    },

    async consumeFood(foodId) {
        const confirmed = await ui.confirm({
            title: '标记已消耗',
            message: '确定要将这个食材标记为已消耗吗？',
            type: 'info',
            icon: '🔥'
        });

        if (!confirmed) return;

        try {
            await api.post(`/food/${foodId}/consume`, {});
            ui.toast('已标记为已消耗', 'success');
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.toast('操作失败: ' + error.message, 'error');
        }
    },

    async unconsumeFood(foodId) {
        const confirmed = await ui.confirm({
            title: '撤销消耗',
            message: '确定要撤销这个食材的消耗状态吗？',
            type: 'info',
            icon: '↩️'
        });

        if (!confirmed) return;

        try {
            await api.put(`/food/${foodId}`, { is_finished: false, finished_at: null });
            ui.toast('已撤销消耗状态', 'success');
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.toast('操作失败: ' + error.message, 'error');
        }
    },

    async editFood(foodId) {
        const food = state.foods.find(f => f.id === foodId);
        if (!food) return;

        const result = await ui.showEditModal({
            title: '编辑食材',
            icon: food.icon || utils.getCategoryIcon(food.category),
            fields: [
                { name: 'name', label: '品名', value: food.name },
                {
                    name: 'icon',
                    label: '图标',
                    type: 'icon',
                    context: 'food',
                    value: food.icon || utils.getCategoryIcon(food.category)
                },
                {
                    name: 'category',
                    label: '类别',
                    type: 'select',
                    value: food.category,
                    options: state.categories.map(c => ({value: c.id, label: c.icon + ' ' + c.name}))
                },
                { 
                    name: 'location_id', 
                    label: '存放位置', 
                    type: 'select', 
                    value: food.location_id, 
                    options: [{value: '', label: '选择存放位置'}, ...utils.formatLocationOptions(state.locations)] 
                },
                { 
                    name: 'quantity', 
                    label: '数量', 
                    type: 'combined', 
                    value: {value: food.quantity, unit: food.unit}, 
                    units: ['个', '克', '千克', '升', '毫升', '盒', '瓶', '包', '袋', '斤'], 
                    unitName: 'unit' 
                },
                { name: 'expiry_date', label: '保质期', type: 'date', value: food.expiry_date },
                { name: 'is_opened', label: '已开封', type: 'checkbox', value: food.is_opened },
                { name: 'notes', label: '备注', type: 'textarea', value: food.notes }
            ]
        });

        if (!result) return;

        // Auto reduce expiry logic for fresh food
        let expiryDate = result.expiry_date;
        const freshCategories = ['vegetable', 'fruit', 'meat', 'seafood', 'dairy'];
        
        // If opened status changed to true AND it is fresh food
        if (result.is_opened && !food.is_opened && freshCategories.includes(result.category)) {
            const today = new Date();
            const threeDaysLater = new Date(today);
            threeDaysLater.setDate(today.getDate() + 3);
            
            const currentExpiry = expiryDate ? new Date(expiryDate) : null;
            
            // If no expiry or expiry is later than 3 days, shorten it
            if (!currentExpiry || currentExpiry > threeDaysLater) {
                expiryDate = threeDaysLater.toISOString().split('T')[0];
                ui.toast('已自动调整保质期为3天后', 'info');
            }
        }

        try {
            await api.put(`/food/${foodId}`, {
                ...result,
                expiry_date: expiryDate || null,
                location_id: result.location_id ? parseInt(result.location_id) : null
            });
            ui.toast('食材更新成功！', 'success');
            await this.loadInitialData();
            this.renderPage('home');
        } catch (error) {
            ui.toast('更新失败: ' + error.message, 'error');
        }
    },



    async deleteLocation(locationId) {
        const confirmed = await ui.confirm({
            title: '删除空间',
            message: '删除此空间将同时删除其中的所有食材，确定要继续吗？',
            type: 'danger',
            icon: '🗑️'
        });

        if (!confirmed) return;

        try {
            await api.delete(`/locations/${locationId}`);
            ui.toast('空间已删除', 'success');
            await this.loadInitialData();
            this.renderPage('spaces');
        } catch (error) {
            ui.toast('删除失败: ' + error.message, 'error');
        }
    },

    async fetchRecipes(scenario) {
        const foods = state.foods.filter(f => !f.is_finished);
        const expiringFoods = foods.filter(f => {
            const days = utils.getRemainingDays(f.expiry_date);
            return days !== null && days <= 3;
        });

        this.showAILoading('正在生成菜谱...');

        try {
            const result = await api.post('/ai/recipes', {
                scenario,
                foods: foods.map(f => ({ name: f.name, category: f.category, quantity: f.quantity, unit: f.unit })),
                expiringFoods: expiringFoods.map(f => f.name)
            });

            this.hideAILoading();

            if (result.success) {
                state.currentRecipes = result.recipes;
                this.displayRecipes(result);
            }
        } catch (error) {
            this.hideAILoading();
            ui.toast('获取推荐失败: ' + error.message, 'error');
        }
    },

    async fetchRecipesCustom() {
        const customRequirement = await ui.input({
            title: '告诉我您的需求',
            message: '例如：想做一道简单的早餐、想用土豆做一道菜、想吃点清淡的...',
            placeholder: '请输入您的需求',
            icon: '💭'
        });

        if (!customRequirement || !customRequirement.trim()) {
            return;
        }

        const foods = state.foods.filter(f => !f.is_finished);
        const expiringFoods = foods.filter(f => {
            const days = utils.getRemainingDays(f.expiry_date);
            return days !== null && days <= 3;
        });

        this.showAILoading('正在生成菜谱...');

        try {
            const result = await api.post('/ai/recipes', {
                scenario: 'custom',
                custom_requirement: customRequirement.trim(),
                foods: foods.map(f => ({ name: f.name, category: f.category, quantity: f.quantity, unit: f.unit })),
                expiringFoods: expiringFoods.map(f => f.name)
            });

            this.hideAILoading();

            if (result.success) {
                state.currentRecipes = result.recipes;
                this.displayRecipes(result);
            }
        } catch (error) {
            this.hideAILoading();
            ui.toast('获取推荐失败: ' + error.message, 'error');
        }
    },

    displayRecipes(result) {
        const container = document.getElementById('recipe-results');
        if (!container) return;

        const { message, recipes } = result;

        if (!recipes || recipes.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 text-gray-400">
                    <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                        <span class="text-4xl">🤔</span>
                    </div>
                    <p>暂无推荐菜谱</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="animate-fadeIn">
                <div class="bg-white rounded-xl p-4 mb-6 border border-orange-100">
                    <p class="text-gray-700">${message}</p>
                </div>
                <div class="space-y-4">
                    ${recipes.map((recipe, index) => `
                        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
                            <div class="p-5">
                                <div class="flex items-start justify-between mb-3">
                                    <div>
                                        <h3 class="text-lg font-bold text-gray-800">${recipe.name}</h3>
                                        <p class="text-sm text-gray-500 mt-1">${recipe.description}</p>
                                    </div>
                                    <div class="flex gap-2">
                                        ${(recipe.tags || []).map(tag => `<span class="px-2 py-1 bg-orange-100 text-orange-600 rounded-lg text-xs">${tag || ''}</span>`).join('')}
                                    </div>
                                </div>
                                
                                <div class="flex items-center gap-4 text-sm text-gray-500 mb-4">
                                    <span class="flex items-center gap-1">
                                        <i data-lucide="clock" class="w-4 h-4"></i>
                                        ${recipe.cookingTime || recipe.cooking_time || 20}分钟
                                    </span>
                                    <span class="flex items-center gap-1">
                                        <i data-lucide="chef-hat" class="w-4 h-4"></i>
                                        ${recipe.difficulty || '简单'}
                                    </span>
                                    <span class="flex items-center gap-1">
                                        <i data-lucide="users" class="w-4 h-4"></i>
                                        ${recipe.servings || 2}人份
                                    </span>
                                </div>

                                <div class="border-t border-gray-100 pt-4">
                                    <h4 class="font-medium text-gray-700 mb-2">所需食材</h4>
                                    <div class="flex flex-wrap gap-2 mb-4">
                                        ${(recipe.ingredients || []).map(ing => {
                                            let ingText = typeof ing === 'string' ? ing : (ing.name || '未知食材');
                                            let colorClass = utils.getIngredientColorClass(ingText);
                                            
                                            if (typeof ing === 'string') {
                                                return `<span class="px-3 py-1 rounded-full text-sm ${colorClass}">${ing}</span>`;
                                            }
                                            return `<span class="px-3 py-1 rounded-full text-sm ${ing.have ? 'bg-green-50 text-green-700 border border-green-200' : colorClass}">${ing.have ? '✓' : '○'} ${ing.name || '未知食材'}${ing.amount ? ` - ${ing.amount}` : ''}</span>`;
                                        }).join('')}
                                    </div>
                                </div>

                                <div class="border-t border-gray-100 pt-4">
                                    <h4 class="font-medium text-gray-700 mb-2">烹饪步骤</h4>
                                    <ol class="space-y-2 text-sm text-gray-600">
                                        ${(recipe.steps || []).map((step, i) => `
                                            <li class="flex gap-3">
                                                <span class="flex-shrink-0 w-6 h-6 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-xs font-medium">${i + 1}</span>
                                                <span>${step}</span>
                                            </li>
                                        `).join('')}
                                    </ol>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async showAdminPanel() {
        if (!state.currentUser || state.currentUser.role !== 'admin') {
            ui.toast('需要管理员权限', 'error');
            return;
        }

        try {
            const loadingHTML = `
                <div class="p-4 md:p-6">
                    <div class="flex items-center justify-between mb-6">
                        <div>
                            <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2">用户管理</h1>
                            <p class="text-gray-500">管理系统用户账户</p>
                        </div>
                        <button onclick="app.showCreateUserModal()" class="btn btn-primary">
                            <i data-lucide="plus" class="w-4 h-4"></i>
                            新建用户
                        </button>
                    </div>
                    <div class="flex items-center justify-center py-12">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
                    </div>
                </div>
            `;
            document.getElementById('main-content').innerHTML = loadingHTML;
            
            const usersData = await api.get('/admin/admin/users?page=1&page_size=100');

            const users = usersData.items || [];

            const adminPanelHTML = `
                <div class="p-4 md:p-6">
                    <div class="flex items-center justify-between mb-6">
                        <div>
                            <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2">用户管理</h1>
                            <p class="text-gray-500">管理系统用户账户</p>
                        </div>
                        <button onclick="app.showCreateUserModal()" class="btn btn-primary">
                            <i data-lucide="plus" class="w-4 h-4"></i>
                            新建用户
                        </button>
                    </div>

                    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <div class="overflow-x-auto">
                            <table class="w-full">
                                <thead class="bg-gray-50 border-b border-gray-100">
                                    <tr>
                                        <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">用户</th>
                                        <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">角色</th>
                                        <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">状态</th>
                                        <th class="px-4 py-3 text-left text-sm font-medium text-gray-600">创建时间</th>
                                        <th class="px-4 py-3 text-right text-sm font-medium text-gray-600">操作</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-100">
                                    ${users.map(user => `
                                        <tr class="hover:bg-gray-50 transition-colors">
                                            <td class="px-4 py-3">
                                                <div class="flex items-center gap-3">
                                                    <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-300 to-amber-400 flex items-center justify-center text-white font-bold">
                                                        ${user.avatar || user.username[0].toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <p class="font-medium text-gray-800">${user.nickname || user.username}</p>
                                                        <p class="text-sm text-gray-500">${user.email || user.username}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-4 py-3">
                                                <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${user.role === 'admin' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'}">
                                                    ${user.role === 'admin' ? '👑 管理员' : '👤 普通用户'}
                                                </span>
                                            </td>
                                            <td class="px-4 py-3">
                                                <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                                                    ${user.is_active ? '✓ 激活' : '✗ 禁用'}
                                                </span>
                                            </td>
                                            <td class="px-4 py-3 text-sm text-gray-500">
                                                ${new Date(user.created_at).toLocaleDateString('zh-CN')}
                                            </td>
                                            <td class="px-4 py-3 text-right">
                                                <div class="flex items-center justify-end gap-2">
                                                    <button onclick="app.editUser(${user.id})" class="p-2 text-gray-400 hover:text-orange-500 transition-colors" title="编辑">
                                                        <i data-lucide="edit" class="w-4 h-4"></i>
                                                    </button>
                                                    ${user.id !== state.currentUser.id ? `
                                                        <button onclick="app.deleteUser(${user.id})" class="p-2 text-gray-400 hover:text-red-500 transition-colors" title="删除">
                                                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                                                        </button>
                                                    ` : ''}
                                                </div>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                        ${users.length === 0 ? `
                            <div class="text-center py-12 text-gray-400">
                                <div class="w-20 h-20 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                                    <span class="text-4xl">👥</span>
                                </div>
                                <p>暂无用户数据</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;

            document.getElementById('main-content').innerHTML = adminPanelHTML;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (error) {
            ui.hideLoading('#main-content');
            ui.toast('加载用户列表失败: ' + error.message, 'error');
        }
    },

    async showCreateUserModal() {
        const result = await ui.showEditModal({
            title: '创建用户',
            icon: '👤',
            fields: [
                { name: 'username', label: '用户名', placeholder: '输入用户名' },
                { name: 'email', label: '邮箱', placeholder: '输入邮箱（可选）' },
                { name: 'nickname', label: '昵称', placeholder: '输入昵称（可选）' },
                {
                    name: 'password',
                    label: '密码',
                    type: 'password',
                    placeholder: '输入密码（至少6位）'
                },
                {
                    name: 'role',
                    label: '角色',
                    type: 'select',
                    value: 'user',
                    options: [
                        { value: 'user', label: '👤 普通用户' },
                        { value: 'admin', label: '👑 管理员' }
                    ]
                },
                {
                    name: 'is_active',
                    label: '账户状态',
                    type: 'checkbox',
                    value: true
                }
            ]
        });

        if (!result) return;

        try {
            await api.post('/admin/admin/users', {
                username: result.username,
                email: result.email || null,
                password: result.password,
                nickname: result.nickname || result.username,
                role: result.role,
                is_active: result.is_active
            });
            ui.toast('用户创建成功！', 'success');
            await this.showAdminPanel();
        } catch (error) {
            ui.toast('创建失败: ' + error.message, 'error');
        }
    },

    async editUser(userId) {
        try {
            const usersData = await api.get('/admin/admin/users?page=1&page_size=100');
            const user = usersData.items.find(u => u.id === userId);
            if (!user) {
                ui.toast('用户不存在', 'error');
                return;
            }

            const result = await ui.showEditModal({
                title: '编辑用户',
                icon: '✏️',
                fields: [
                    { name: 'username', label: '用户名', value: user.username },
                    { name: 'email', label: '邮箱', value: user.email || '' },
                    { name: 'nickname', label: '昵称', value: user.nickname || '' },
                    {
                        name: 'password',
                        label: '新密码',
                        type: 'password',
                        placeholder: '留空则不修改密码'
                    },
                    {
                        name: 'role',
                        label: '角色',
                        type: 'select',
                        value: user.role,
                        options: [
                            { value: 'user', label: '👤 普通用户' },
                            { value: 'admin', label: '👑 管理员' }
                        ]
                    },
                    {
                        name: 'is_active',
                        label: '账户状态',
                        type: 'checkbox',
                        value: user.is_active
                    }
                ]
            });

            if (!result) return;

            const updateData = {
                username: result.username,
                email: result.email || null,
                nickname: result.nickname || result.username,
                password: result.password || 'password123',
                role: result.role,
                is_active: result.is_active
            };

            await api.put(`/admin/admin/users/${userId}`, updateData);
            ui.toast('用户更新成功！', 'success');
            await this.showAdminPanel();
        } catch (error) {
            ui.toast('更新失败: ' + error.message, 'error');
        }
    },

    async deleteUser(userId) {
        const confirmed = await ui.confirm({
            title: '确认删除',
            message: '确定要删除此用户吗？此操作将永久删除该用户及其所有数据，不可恢复。',
            type: 'danger',
            icon: '🗑️'
        });

        if (!confirmed) return;

        try {
            await api.delete(`/admin/admin/users/${userId}`);
            ui.toast('用户已删除', 'success');
            await this.showAdminPanel();
        } catch (error) {
            ui.toast('删除失败: ' + error.message, 'error');
        }
    },

    showError(message) {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.innerHTML = `
                <div class="text-center p-6">
                    <div class="text-6xl mb-4">⚠️</div>
                    <h2 class="text-xl font-bold text-gray-800 mb-2">出错了</h2>
                    <p class="text-gray-500 mb-4">${message}</p>
                    <button onclick="location.reload()" class="px-6 py-2 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-colors">
                        刷新页面
                    </button>
                </div>
            `;
        }
    }
};

// ============================================
// 初始化应用
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// 导出到全局
window.CONFIG = CONFIG;
window.state = state;
window.utils = utils;
window.api = api;
window.ui = ui;
window.app = app;
