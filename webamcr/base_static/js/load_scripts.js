/*================================
Tooltip - Custom functions
==================================*/
    //Dynamic function for tooltips
    function customTooltip(id, placement, title){
        $(id).tooltip({placement:placement, title:title})
    };
    //Dynamic function for tooltips in selectpickers
    function customSelectpickerTooltip (id, placement, title){
        $(id).on('loaded.bs.select', function (e) {
        selectTooltip_wrapper = e.currentTarget.parentElement;
        selectTooltip_button = e.currentTarget.nextElementSibling;
        selectTooltip_button.removeAttribute("title")
        $(selectTooltip_wrapper).tooltip({placement: placement, title: title});
    });
    };
/*================================
 Owl carousel initialization
==================================*/
function create_slider(){
    $('.owl-carousel').owlCarousel({
      loop: false,
      margin: 15,
      dots: true,
      navigation: false,
      responsiveClass: true,
      onDragged: function () {
          $('body').css('overflow', 'auto');
      },
      onDrag: function () {
          $('body').css('overflow', 'hidden');
      },
      responsive: {
          0: {
              items: 2,
              nav: false,
              mergeFit: true
          },
          600: {
              items: 3,
              nav: false
          },
          1000: {
              items: 6,
              nav: false,
              loop: false
          }
      }
    })
  }
/*================================
Cards - text on hover
==================================*/
  function card_text(){
      $(".amcr-card").hover(
          function (e) {
            var hoveredElement = "." + e.currentTarget.classList[2]
            $(hoveredElement).toggleClass('open');
    });
  }
/*================================
Google Analytics - GTAG
==================================*/
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  gtag('js', new Date());
  gtag('config', 'UA-79200582-5');