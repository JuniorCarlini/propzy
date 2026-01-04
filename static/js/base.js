/* ============================================================================
 * propzy - JavaScript Base do Sistema
 * ============================================================================ */

// Toast notifications
document.addEventListener("DOMContentLoaded", () => {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach((toastEl) => {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
    });
});

// Menu Off-Canvas para Mobile
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function openSidebar() {
        if (sidebar) sidebar.classList.add('show');
        if (sidebarOverlay) sidebarOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (sidebarOverlay) sidebarOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    if (menuToggle) {
        menuToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (sidebar && sidebar.classList.contains('show')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Fechar menu ao clicar em um link do menu
    const menuLinks = document.querySelectorAll('.menu-link');
    menuLinks.forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });

    // Fechar menu ao redimensionar a janela para desktop
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    });

    // User Menu Dropdown
    const userAvatar = document.getElementById('userAvatar');
    const userMenuDropdown = document.getElementById('userMenuDropdown');

    function toggleUserMenu() {
        if (userMenuDropdown) {
            userMenuDropdown.classList.toggle('show');
        }
    }

    function closeUserMenu() {
        if (userMenuDropdown) {
            userMenuDropdown.classList.remove('show');
        }
    }

    if (userAvatar && userMenuDropdown) {
        userAvatar.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleUserMenu();
        });

        // Fechar menu ao clicar fora
        document.addEventListener('click', function (e) {
            if (userMenuDropdown && !userMenuDropdown.contains(e.target) && !userAvatar.contains(e.target)) {
                closeUserMenu();
            }
        });

        // Fechar menu ao pressionar ESC
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && userMenuDropdown && userMenuDropdown.classList.contains('show')) {
                closeUserMenu();
            }
        });
    }

    // Seletor de Idioma
    function initLanguageSelector() {
        const languageSelect = document.getElementById('language-select');
        const languageForm = document.getElementById('language-form');
        const nextInput = document.getElementById('language-next') || languageForm?.querySelector('input[name="next"]');

        if (languageSelect && languageForm) {
            languageSelect.addEventListener('change', function (e) {
                e.stopPropagation();

                // Remove o prefixo de idioma atual da URL antes de submeter
                if (nextInput) {
                    let currentPath = window.location.pathname;
                    // Remove prefixos de idioma conhecidos
                    currentPath = currentPath.replace(/^\/(pt-br|pt_BR|en|es)\//, '/');
                    // Se ficou vazio, usa /
                    if (!currentPath || currentPath === '') {
                        currentPath = '/';
                    }
                    // Garante que comece com /
                    if (!currentPath.startsWith('/')) {
                        currentPath = '/' + currentPath;
                    }
                    // Adiciona query string se existir
                    nextInput.value = currentPath + window.location.search;
                }

                // Atualiza a bandeira visualmente
                const selectedValue = this.value;
                const languageIcon = document.getElementById('language-icon') || document.querySelector('.language-selector-icon');
                if (languageIcon) {
                    let flagCode = selectedValue;
                    if (selectedValue === 'pt-br' || selectedValue === 'pt_BR') {
                        flagCode = 'br';
                    } else if (selectedValue === 'en') {
                        flagCode = 'us';
                    } else if (selectedValue === 'es') {
                        flagCode = 'es';
                    }
                    languageIcon.className = 'language-selector-icon fi fi-' + flagCode;
                }

                // Submete o formulário
                languageForm.submit();
            });
        }
    }

    // Inicializa quando o DOM estiver pronto
    initLanguageSelector();
});


