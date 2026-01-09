/**
 * propzy - Scripts de Autenticação
 * Gerencia funcionalidades JavaScript das páginas de autenticação
 */

(function () {
    'use strict';

    /**
     * Atualiza a bandeira do idioma quando selecionado
     * @param {string} languageCode - Código do idioma selecionado
     */
    function updateLanguageFlag(languageCode) {
        const icon = document.querySelector('.language-selector-icon');
        if (icon) {
            let flagCode = languageCode;
            if (languageCode === 'pt-br') {
                flagCode = 'br';
            } else if (languageCode === 'en') {
                flagCode = 'us';
            } else if (languageCode === 'es') {
                flagCode = 'es';
            }
            icon.className = 'language-selector-icon fi fi-' + flagCode;
        }
    }

    /**
     * Inicializa o toggle de mostrar/ocultar senha
     * Funciona para todos os campos de senha na página
     */
    function initPasswordToggle() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');

        passwordInputs.forEach(passwordInput => {
            // Procura pelo botão toggle existente ou cria um novo
            let toggleBtn = passwordInput.parentElement.querySelector('.password-toggle-btn');

            // Se não existe botão, cria um
            if (!toggleBtn) {
                // Cria wrapper se não existir
                let wrapper = passwordInput.parentElement;
                if (!wrapper.classList.contains('password-input-wrapper')) {
                    wrapper = document.createElement('div');
                    wrapper.className = 'password-input-wrapper';
                    passwordInput.parentNode.insertBefore(wrapper, passwordInput);
                    wrapper.appendChild(passwordInput);
                }

                // Cria botão toggle
                toggleBtn = document.createElement('button');
                toggleBtn.type = 'button';
                toggleBtn.className = 'password-toggle-btn';
                toggleBtn.setAttribute('aria-label', 'Mostrar senha');
                toggleBtn.innerHTML = '<i class="fa fa-eye"></i>';

                wrapper.appendChild(toggleBtn);
            }

            // Adiciona evento de clique
            toggleBtn.addEventListener('click', function () {
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);

                const icon = toggleBtn.querySelector('i');
                if (type === 'password') {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                    toggleBtn.setAttribute('aria-label', 'Mostrar senha');
                } else {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                    toggleBtn.setAttribute('aria-label', 'Ocultar senha');
                }
            });
        });
    }

    /**
     * Inicializa o seletor de idioma
     */
    function initLanguageSelector() {
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', function () {
                updateLanguageFlag(this.value);
                document.getElementById('language-form').submit();
            });
        }
    }

    // Inicializa quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function () {
        initPasswordToggle();
        initLanguageSelector();
    });

    // Expõe função globalmente para uso inline (se necessário)
    window.updateLanguageFlag = updateLanguageFlag;
})();
























