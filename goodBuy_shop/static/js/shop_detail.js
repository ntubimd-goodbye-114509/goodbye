window.addEventListener("DOMContentLoaded", () => {
  // 動態設定內容區 margin-top
  const header = document.querySelector('.header');
  const content = document.querySelector('.main-content');
  if (header && content) {
    content.style.marginTop = header.offsetHeight + 'px';
  }

  // 阻止 quantity-input 的上下鍵改變數值
  document.querySelectorAll('.quantity-input').forEach((input) => {
    input.addEventListener('keydown', (e) => {
      if (e.key === "ArrowUp" || e.key === "ArrowDown") {
        e.preventDefault();
      }
    });
  });
});

// 增加數量
function increaseQty(btn) {
  const input = btn.parentNode.querySelector('input[name="quantity"]');
  let current = parseInt(input.value) || 1;
  input.value = current + 1;
}

// 減少數量（不能小於 1）
function decreaseQty(btn) {
  const input = btn.parentNode.querySelector('input[name="quantity"]');
  let current = parseInt(input.value) || 1;
  if (current > 1) {
    input.value = current - 1;
  }
}
