document.addEventListener('DOMContentLoaded', function() {
    // 切換圖片
    const mainImage = document.getElementById('main-image');
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        item.addEventListener('click', function() {
            // 更新主圖片
            mainImage.src = this.dataset.src;
            
            // 更新選取狀態
            galleryItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
});