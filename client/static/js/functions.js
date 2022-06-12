// 获取cookie中name的信息
function get_cookie(name) {
    const strCookie = document.cookie;
    const arrCookie = strCookie.split("; ");
    for (let i = 0; i < arrCookie.length; ++i) {
        let arr = arrCookie[i].split("=");
        if (arr[0] === name)
            return arr[1];
    }
    return "";
}

// 格式化输出整型数据，在num前面补0到n位
function PrefixInteger(num, n) {
    return (Array(n).join(0) + num).slice(-n);
}

// 下载功能封装
function download(href, title) {
    const a = document.createElement('a');
    a.setAttribute('href', href);
    // 添加download属性，防止打开文件
    a.setAttribute('download', title);
    a.click();
}