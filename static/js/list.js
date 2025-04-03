document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const menu = document.getElementById("menu");

    menuToggle.addEventListener("click", function () {
        if (menu.style.display === "block") {
            menu.style.display = "none";
        } else {
            menu.style.display = "block";
        }
    });

    // 點擊畫面其他地方時，關閉選單
    document.addEventListener("click", function (event) {
        if (!menu.contains(event.target) && event.target !== menuToggle) {
            menu.style.display = "none";
        }
    });
});
