/**
 * Funcionalidades JavaScript para gerenciamento de romaneios
 */

// Validação da chave de acesso em tempo real
document.addEventListener('DOMContentLoaded', function() {
    const chaveInput = document.getElementById('chave_acesso');
    const chaveCounter = document.getElementById('chave-counter');
    
    if (chaveInput && chaveCounter) {
        chaveInput.addEventListener('input', function() {
            const chave = this.value.replace(/\D/g, ''); // Remove não-numéricos
            this.value = chave; // Atualiza o valor
            
            const length = chave.length;
            
            if (length === 44) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                chaveCounter.className = 'form-text text-success';
                chaveCounter.innerHTML = '<i class="fas fa-check-circle me-1"></i>Chave de acesso válida!';
            } else if (length > 0) {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                chaveCounter.className = 'form-text text-danger';
                chaveCounter.innerHTML = `<i class="fas fa-exclamation-circle me-1"></i>Faltam ${44 - length} caracteres (${length}/44)`;
            } else {
                this.classList.remove('is-valid', 'is-invalid');
                chaveCounter.className = 'form-text text-muted';
                chaveCounter.innerHTML = 'A chave deve conter exatamente 44 caracteres numéricos';
            }
        });
    }
});

// Verificar romaneio
document.querySelectorAll('.btn-verificar').forEach(btn => {
    btn.addEventListener('click', async function() {
        const romaneioId = this.dataset.id;
        
        if (!confirm('Deseja verificar este romaneio agora?')) {
            return;
        }
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            const response = await fetch(`/api/romaneios/${romaneioId}/verificar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Verificação realizada com sucesso!\n\n' + data.resultado.mensagem);
                location.reload();
            } else {
                alert('Erro ao verificar: ' + data.error);
            }
        } catch (error) {
            alert('Erro ao verificar romaneio: ' + error.message);
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-sync"></i>';
        }
    });
});

// Excluir romaneio
document.querySelectorAll('.btn-excluir').forEach(btn => {
    btn.addEventListener('click', async function() {
        const romaneioId = this.dataset.id;
        
        if (!confirm('Tem certeza que deseja excluir este romaneio?\n\nEsta ação não pode ser desfeita.')) {
            return;
        }
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            const response = await fetch(`/api/romaneios/${romaneioId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Romaneio excluído com sucesso!');
                location.reload();
            } else {
                alert('Erro ao excluir: ' + data.error);
            }
        } catch (error) {
            alert('Erro ao excluir romaneio: ' + error.message);
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-trash"></i>';
        }
    });
});

// Validação de chave de acesso (apenas números)
document.getElementById('chave_acesso')?.addEventListener('input', function(e) {
    this.value = this.value.replace(/\D/g, '').substring(0, 44);
});

// Contador de caracteres para chave de acesso
document.getElementById('chave_acesso')?.addEventListener('keyup', function() {
    const length = this.value.length;
    const small = this.parentElement.querySelector('small');
    if (small) {
        small.textContent = `${length}/44 dígitos`;
        if (length === 44) {
            small.classList.add('text-success');
            small.classList.remove('text-muted');
        } else {
            small.classList.add('text-muted');
            small.classList.remove('text-success');
        }
    }
});

