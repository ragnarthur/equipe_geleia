// tableHover.js

console.log("tableHover.js foi carregado!");

document.addEventListener("DOMContentLoaded", function() {
  console.log("DOM totalmente carregado!");

  const tableRows = document.querySelectorAll('.table tbody tr');
  console.log("Linhas encontradas:", tableRows);

  tableRows.forEach(function(row) {
    // Adiciona transição suave
    row.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';

    row.addEventListener('mouseover', function() {
      console.log("Mouseover na linha:", row);
      row.style.transform = 'scale(1.02)';
      row.style.boxShadow = '0 0 10px rgba(255, 0, 0, 0.2)'; 
    });
    row.addEventListener('mouseout', function() {
      row.style.transform = 'none';
      row.style.boxShadow = 'none';
    });
  });
});
