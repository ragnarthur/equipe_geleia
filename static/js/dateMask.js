// dateMask.js

document.addEventListener("DOMContentLoaded", function() {
    // Seleciona os inputs de data (ajuste os IDs conforme seu HTML)
    const dateInputs = document.querySelectorAll('#data_entrada, #data_pagamento');
  
    dateInputs.forEach(function(input) {
      input.addEventListener('input', function(e) {
        // Remove tudo que não for dígito
        let value = e.target.value.replace(/\D/g, '');
        // Limita o máximo a 8 dígitos (DDMMYYYY)
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
  
        // Atribui ao input
        e.target.value = formatted;
      });
    });
  });
  