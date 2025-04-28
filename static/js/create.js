// 封面圖選擇
document.getElementById('cover-image').addEventListener('change', function(event) {
    const label = document.querySelector('.cover-placeholder');
    const file = event.target.files[0];
    if (file) {
        label.textContent = file.name;
    }
});

// 動態新增標籤
document.getElementById('add-tag-btn').addEventListener('click', function() {
    const newTagInput = document.getElementById('new-tag');
    const tagContainer = document.getElementById('tag-container');

    const tagValue = newTagInput.value.trim();
    if (tagValue !== '') {
        const tagSpan = document.createElement('span');
        tagSpan.textContent = `#${tagValue}`;
        tagContainer.appendChild(tagSpan);
        newTagInput.value = '';
    }
});
