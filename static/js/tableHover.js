// tableHover.js

console.log("tableHover.js foi carregado!");

document.addEventListener("DOMContentLoaded", function() {
  console.log("DOM totalmente carregado!");

  const tableRows = document.querySelectorAll('.table tbody tr');
  console.log("Linhas encontradas:", tableRows);

  tableRows.forEach(function(row) {
    // Adiciona transição suave para transform e box-shadow
    row.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';

    row.addEventListener('mouseover', function() {
      console.log("Mouseover na linha:", row);
      // Define position relative e z-index para que o dropdown apareça por cima
      row.style.position = 'relative';
      row.style.zIndex = '999';
      row.style.transform = 'scale(1.02)';
      row.style.boxShadow = '0 0 10px rgba(255, 0, 0, 0.2)'; 
    });
    row.addEventListener('mouseout', function() {
      row.style.transform = 'none';
      row.style.boxShadow = 'none';
      // Restaura a posição e o z-index padrão
      row.style.position = 'static';
      row.style.zIndex = 'auto';
    });
  });
});
