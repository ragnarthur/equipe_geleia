// dateMask.js

document.addEventListener("DOMContentLoaded", function() {
  // Seleciona os inputs de data: data_entrada, data_pagamento e data_nascimento
  const dateInputs = document.querySelectorAll('#data_entrada, #data_pagamento, #data_nascimento');
  
  dateInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
      // Remove caracteres que não sejam dígitos
      let value = e.target.value.replace(/\D/g, '');
      // Limita a 8 dígitos (DDMMYYYY)
      if (value.length > 8) {
        value = value.slice(0, 8);
      }
      
      // Extrai dia, mês e ano
      let day = value.slice(0, 2);
      let month = value.slice(2, 4);
      let year = value.slice(4, 8);
      
      // Monta a string formatada
      let formatted = '';
      if (day) {
        formatted += day;
      }
      if (month) {
        formatted += '/' + month;
      }
      if (year) {
        formatted += '/' + year;
      }
      
      // Atualiza o valor do input
      e.target.value = formatted;
    });
  });
});
