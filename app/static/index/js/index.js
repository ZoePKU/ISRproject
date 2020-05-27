function getObjectURL(file) {
    let url = null ;
    // 下面函数执行的效果是一样的，只是需要针对不同的浏览器执行不同的 js 函数而已
    if (window.createObjectURL!=undefined) { // basic
        url = window.createObjectURL(file) ;
    } else if (window.URL!=undefined) { // mozilla(firefox)
        url = window.URL.createObjectURL(file) ;
    } else if (window.webkitURL!=undefined) { // webkit or chrome
        url = window.webkitURL.createObjectURL(file) ;
    }
    return url ;
}

// 上传图片
$(function () {
    $('#img-upload').click(function () {
        $('#query-img').click();
    });
})

function upload(obj) {
    let new_src=getObjectURL(obj.files[0]);
    document.getElementById('img-preview').src=new_src;
}

//图片大小自动调整
function adapt() {
    let tableWidth = $("#image_show").width(); //表格宽度
    let img = new Image();
    img.src = $('#img-preview').attr("src");
    let imgWidth = img.width; //图片实际宽度
    if (imgWidth < tableWidth) {
        $('#img-preview').attr("style", "width: auto");
    } else {
        $('#img-preview').attr("style", "width: 100%");
    }
}
