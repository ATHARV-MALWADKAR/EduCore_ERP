// Theme management system
class ThemeManager {
    constructor() {
        this.currentTheme = this.getSavedTheme();
        this.listeners = [];
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.updateThemeIcon();
    }

    getSavedTheme() {
        try {
            const saved = localStorage.getItem('theme');
            if (saved && (saved === 'light' || saved === 'dark')) {
                return saved;
            }
            // Check system preference
            return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        } catch (e) {
            return 'light';
        }
    }

    setTheme(theme) {
        this.currentTheme = theme;
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            // localStorage not available
        }
        this.applyTheme(theme);
        this.notifyListeners();
    }

    applyTheme(theme) {
        const html = document.documentElement;
        if (theme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
        this.updateThemeIcon();
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    updateThemeIcon() {
        // This will be handled by individual pages if needed
    }

    onThemeChange(callback) {
        this.listeners.push(callback);
    }

    notifyListeners() {
        this.listeners.forEach(callback => callback());
    }
}

// Create global theme manager instance
window.themeManager = new ThemeManager();

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    if (window.themeManager) {
        window.themeManager.init();
    }
});