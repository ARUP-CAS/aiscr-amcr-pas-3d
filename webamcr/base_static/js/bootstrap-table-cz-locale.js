/* 
  /*===============================
  Bootstrap-table Locale CZ
  ===============================*/
  $.fn.bootstrapTable.locales['cs'] = {
    formatLoadingMessage() {
      return 'Čekejte, prosím'
    },
    formatRecordsPerPage(pageNumber) {
      return `${pageNumber}  \xa0 řádků na stránce`
    },
    formatShowingRows(pageFrom, pageTo, totalRows, totalNotFiltered) {
      if (totalNotFiltered !== undefined && totalNotFiltered > 0 && totalNotFiltered > totalRows) {
        return `Zobrazen ${pageFrom} až ${pageTo} řádek z celkových ${totalRows} výsledků. (filtered from ${totalNotFiltered} total rows)`
      }

      return `Zobrazen ${pageFrom} až ${pageTo} řádek z celkových ${totalRows} výsledků.`
    },
    formatSRPaginationPreText() {
      return 'Předchozí'
    },
    formatSRPaginationPageText(page) {
      return `to page ${page}`
    },
    formatSRPaginationNextText() {
      return 'Další'
    },
    formatDetailPagination(totalRows) {
      return `Zobrazeno ${totalRows} výsledků`
    },
    formatClearSearch() {
      return 'Vymazat vyhledávání'
    },
    formatSearch() {
      return 'Vyhledávání'
    },
    formatNoMatches() {
      return 'Nenalezena žádná vyhovující položka'
    },
    formatPaginationSwitch() {
      return 'Skrýt/Zobrazit stránkování'
    },
    formatPaginationSwitchDown() {
      return 'Zobrazit stránkování'
    },
    formatPaginationSwitchUp() {
      return 'Schovat stránkování'
    },
    formatRefresh() {
      return 'Aktualizovat'
    },
    formatToggle() {
      return 'Přepni'
    },
    formatToggleOn() {
      return 'Show card view'
    },
    formatToggleOff() {
      return 'Hide card view'
    },
    formatColumns() {
      return 'Sloupce'
    },
    formatColumnsToggleAll() {
      return 'Přepnout vše'
    },
    formatFullscreen() {
      return 'Celá obrazovka'
    },
    formatAllRows() {
      return 'Vše'
    },
    formatAutoRefresh() {
      return 'Auto Refresh'
    },
    formatExport() {
      return 'Export dat'
    },
    formatJumpTo() {
      return 'Přejít'
    },
    formatAdvancedSearch() {
      return 'Pokročilé vyhledávání'
    },
    formatAdvancedCloseButton() {
      return 'Zavřít'
    }
  }

  $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['cs'])
 