document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('menu-toggle');
  const menu = document.getElementById('menu');

  menuBtn.addEventListener('click', () => {
      menu.classList.toggle('active'); // 切換 .active 樣式
  });
});

