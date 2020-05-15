
(function ($) {
  "use strict";
  /*================================
  Preloader
  ==================================*/

  var preloader = $('#preloader');
  $(window).on('load', function () {
    preloader.fadeOut('slow', function () { $(this).remove(); });
  });

  /*================================
  sidebar collapsing
  ==================================*/
  $('.nav-btn').on('click', function () {
    $('.page-container').toggleClass('sbar_collapsed');
  });

  /*================================
  Start Footer resizer
  ==================================*/
  var e = function () {
    var e = (window.innerHeight > 0 ? window.innerHeight : this.screen.height) - 5;
    (e -= 67) < 1 && (e = 1), e > 67 && $(".main-content").css("min-height", e + "px")
  };
  $(window).ready(e), $(window).on("resize", e);

  /*================================
  slimscroll activation
  ==================================*/
  $('.menu-inner').slimScroll({
    height: 'auto'
  });
  $('.nofity-list').slimScroll({
    height: '435px'
  });
  $('.timeline-area').slimScroll({
    height: '500px'
  });
  $('.recent-activity').slimScroll({
    height: 'calc(100vh - 114px)'
  });
  $('.settings-list').slimScroll({
    height: 'calc(100vh - 158px)'
  });

  /*================================
  stickey Header
  ==================================*/
  $(window).on('scroll', function () {
    var scroll = $(window).scrollTop(),
      mainHeader = $('#sticky-header'),
      mainHeaderHeight = mainHeader.innerHeight();

    // console.log(mainHeader.innerHeight());
    if (scroll > 1) {
      $("#sticky-header").addClass("sticky-menu");
    } else {
      $("#sticky-header").removeClass("sticky-menu");
    }
  });

  /*================================
  form bootstrap validation
  ==================================*/
  $('[data-toggle="popover"]').popover()

  /*------------- Start form Validation -------------*/
  window.addEventListener('load', function () {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function (form) {
      form.addEventListener('submit', function (event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);

  /*================================
  datatable active
  ==================================*/
  if ($('#dataTable').length) {
    $('#dataTable').DataTable({
      responsive: true
    });
  }
  if ($('#dataTable2').length) {
    $('#dataTable2').DataTable({
      responsive: true
    });
  }
  if ($('#dataTable3').length) {
    $('#dataTable3').DataTable({
      responsive: true
    });
  }

  /*================================
  login form
  ==================================*/
  $('.form-gp input').on('focus', function () {
    $(this).parent('.form-gp').addClass('focused');
  });
  $('.form-gp input').on('focusout', function () {
    if ($(this).val().length === 0) {
      $(this).parent('.form-gp').removeClass('focused');
    }
  });

  /*================================
  slider-area background setting
  ==================================*/
  $('.settings-btn, .offset-close').on('click', function () {
    $('.offset-area').toggleClass('show_hide');
    $('.settings-btn').toggleClass('active');
  });

  /*================================
  Owl Carousel
  ==================================*/
  function slider_area() {
    var owl = $('.testimonial-carousel').owlCarousel({
      margin: 50,
      loop: true,
      autoplay: false,
      nav: false,
      dots: true,
      responsive: {
        0: {
          items: 1
        },
        450: {
          items: 1
        },
        768: {
          items: 2
        },
        1000: {
          items: 2
        },
        1360: {
          items: 1
        },
        1600: {
          items: 2
        }
      }
    });
  }
  slider_area();

  /*================================
  Choose form DATE
  ==================================*/

  //Language Setting - I18N
  $.fn.datepicker.dates['cs'] = {
    days: ["Neděle", "Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota"],
    daysShort: ["Ne", "Po", "Út", "St", "Čt", "Pá", "So"],
    daysMin: ["Ne", "Po", "Út", "St", "Čt", "Pá", "So"],
    months: ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"],
    monthsShort: ["Led", "Úno", "Bře", "Dub", "Kvě", "Čer", "Čer", "Srp", "Zář", "Říj", "Lis", "Pro"],
    today: "Dnes",
    clear: "Vymazat",
    format: "dd/mm/yyyy",
    titleFormat: "MM yyyy",
  };

  //Declaring Variables for elements(ids)
  const fromDateInput = $('#datepicker_from')
  const toDateInput = $('#datepicker_to')
  const fromDate = fromDateInput.val();
  const toDate = fromDateInput.val();

  //Function that sets the options for both datepickers
  $('#datepicker_from, #datepicker_to').datepicker({
    format: 'dd/mm/yyyy',
    todayBtn: true,
    todayBtn: "linked",
    weekStart: 1,
    language: 'cs',
    autoclose: true,
    todayHighlight: true,
    endDate: toDate,
    startDate: fromDate
  })

  //Two functions that helps with validation
  fromDateInput.on("changeDate", function (e) {
    toDateInput.datepicker('setStartDate', e.date);

    toDateInput.on("changeDate", function (e) {
      fromDateInput.datepicker('setEndDate', e.date);
    })
  })
})(jQuery);

/* //Removing and Adding classes on specific viewport
$(document).ready(function () {
    var $window = $(window),
        $crumbs = $('.page-title .pull-left');

    function resize() {
        if ($window.width() < 514) {
            $($crumbs).removeClass('.pull-left')
            return $crumbs
        }

        else {

        }
    }
    //$carousel.trigger('refresh.owl.carousel');

    $window
        .resize(resize)
        .trigger('resize');
}); */


/*================================
Time stamp for file download
==================================*/
function getExportDate() {
  var date = new Date();
  var exportDate = (date.getDate() + '-' + (date.getMonth() + 1) + '-' + date.getFullYear()) + '-' + date.getHours() + '-' + date.getMinutes() + '-' + date.getSeconds();
  var file = 'export' + '-' + exportDate;
  return file
}
/*================================
Selectpicker validation
==================================*/
function selectpickerValidation(e) {
  if (e.target.hasAttribute('required')) {
    if (e.target.selectedIndex > 0) {
      $(e.target.nextElementSibling).removeClass('select-invalid')
    }
    else {
      $(e.target.nextElementSibling).addClass('select-invalid')
    }
  }
}
//Selectpicker validation styling - ON LOAD
$('.selectpicker').on('loaded.bs.select', selectpickerValidation)
//Selectpicker validation styling - ON CHANGE
$('.selectpicker').on('changed.bs.select', selectpickerValidation)


/*================================
Alerts
==================================*/
function createAlert(title, summary, details, severity, dismissible, autoDismiss, appendToId) {
  var iconMap = {
    info: "fa fa-info-circle",
    success: "fa fa-check",
    warning: "fa fa-exclamation-triangle",
    danger: "fa fa-exclamation-circle"
  };

  var iconAdded = false;

  var alertClasses = ["alert", "animated", "slideInRight"];
  alertClasses.push("alert-" + severity.toLowerCase());

  if (dismissible) {
    alertClasses.push("alert-dismissible");
  }

  var msgIcon = $("<i />", {
    "class": iconMap[severity] // you need to quote "class" since it's a reserved keyword
  });

  var msg = $("<div />", {
    "class": alertClasses.join(" ") // you need to quote "class" since it's a reserved keyword
  });

  if (title) {
    var msgTitle = $("<h4 />", {
      html: title
    }).appendTo(msg);

    if (!iconAdded) {
      msgTitle.prepend(msgIcon);
      iconAdded = true;
    }
  }

  if (summary) {
    var msgSummary = $("<strong />", {
      html: summary
    }).appendTo(msg);

    if (!iconAdded) {
      msgSummary.prepend(msgIcon);
      iconAdded = true;
    }
  }

  if (details) {
    var msgDetails = $("<p />", {
      html: details
    }).appendTo(msg);

    if (!iconAdded) {
      msgDetails.prepend(msgIcon);
      iconAdded = true;
    }
  }


  if (dismissible) {
    var msgClose = $("<span />", {
      "class": "close", // you need to quote "class" since it's a reserved keyword
      "data-dismiss": "alert",
      html: "<i class='fa fa-times-circle'></i>"
    }).appendTo(msg);
  }

  $('#' + appendToId).prepend(msg);

  if (autoDismiss) {
    setTimeout(function () {
      msg.addClass("slideOutRight");
      setTimeout(function () {
        msg.remove();
      }, 5000);
    }, 10000);
  }
}
