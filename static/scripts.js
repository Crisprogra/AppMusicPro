// Agregar clase 'active' a la card cuando se hace clic en ella
const cards = document.querySelectorAll('.card');
cards.forEach(card => {
  card.addEventListener('click', () => {
    card.classList.toggle('active');
  });
});
