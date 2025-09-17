function formatName(name, output = "markdown") {
    // 中文名不斜体
    if (/[\u4e00-\u9fa5]/.test(name)) return name;

    // 科名不斜体
    if (name.endsWith("aceae")) return name;

    // 属/种/亚种名
    const parts = name.split(/\s+/);
    return parts.map(p => {
        const lower = p.toLowerCase();
        if (["subsp.", "var.", "f."].includes(lower)) {
            return p; // 标记不斜体
        } else {
            if (output === "markdown") return `*${p}*`;
            if (output === "html") return `<i>${p}</i>`;
            return p;
        }
    }).join(" ");
}

// 页面加载后自动替换所有 raw-name 类的字段
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".scientific_name").forEach(el => {
        const raw = el.textContent.trim();
        el.innerHTML = formatName(raw, "html");
    });
});

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM加载完成");
    
    var toggleButton = document.getElementById('toggle-sensitive-info');
    console.log("找到按钮:", !!toggleButton);
    
    if (toggleButton) {
        var isSensitiveVisible = false;
        
        toggleButton.addEventListener('click', function() {
            console.log("按钮被点击");
            
            var sensitiveElements = document.querySelectorAll('.sensitive-info');
            console.log("找到敏感元素:", sensitiveElements.length);
            
            if (isSensitiveVisible) {
                // 隐藏所有敏感信息
                sensitiveElements.forEach(function(element) {
                    element.style.display = 'none';
                });
                toggleButton.textContent = '显示敏感信息';
                toggleButton.classList.remove('btn-danger');
                toggleButton.classList.add('btn-outline-secondary');
            } else {
                // 显示所有敏感信息
                sensitiveElements.forEach(function(element) {
                    element.style.display = 'table-row';
                });
                toggleButton.textContent = '隐藏敏感信息';
                toggleButton.classList.remove('btn-outline-secondary');
                toggleButton.classList.add('btn-danger');
            }
            
            isSensitiveVisible = !isSensitiveVisible;
        });
    }
});
