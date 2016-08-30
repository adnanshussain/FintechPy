//semantic modules
//dropdown
$('.ui.dropdown').dropdown();

//fintech modules
$(".filter .text").click(function() {
    $(this).parent().toggleClass("opened");
});
$(".collapse-btn").click(function() {
    $(".ui.content.container").toggleClass("expand-content");
});
$(".top .menu").click(function() {
    $(".ui.content.container").toggleClass("expand-content");
});

$(window).scroll(function() {
    var scroll = $(window).scrollTop();
    var topheight = $(".question.page").height() + 90;
    var topheight2 = $(".main > .top").height();
    var toptotalheight = topheight + topheight2;
    $(".page.filters .scroll").css("padding-bottom", toptotalheight - scroll);
    if (scroll >= 146) {
        $(".page.filters").addClass("fixed");
        $(".page.filters").css("top", "0");
    } else {
        $(".page.filters").removeClass("fixed");
    }
});