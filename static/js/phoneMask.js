// phoneMask.js

document.addEventListener("DOMContentLoaded", function() {
    const phoneInput = document.getElementById('telefone');
    if (phoneInput) {
      phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        // Limita a 11 dígitos (ex: 2 para DDD + 9 para número)
        if (value.length > 11) {
          value = value.slice(0, 11);
        }
        
        // Formata o telefone: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
        let formatted = '';
        if (value.length > 0) {
          formatted += '(' + value.substring(0, 2) + ') ';
        }
        if (value.length >= 7) {
          // Se tiver 11 dígitos, assume 9 dígitos para o número
          if (value.length === 11) {
            formatted += value.substring(2, 7) + '-' + value.substring(7, 11);
          } else {
            // Caso contrário, assume 8 dígitos
            formatted += value.substring(2, 6) + '-' + value.substring(6, 10);
          }
        } else if (value.length > 2) {
          formatted += value.substring(2);
        }
        
        e.target.value = formatted;
      });
    }
  });
  