class Search {
    get options() {
        return {
            searchModalId: "searchPagesModal",
            searchInputId: "searchPagesInput",
            searchResultsId: "searchPagesResults",
            placeholder: "Search", 
            loading: "Loading",
            //jsonPath: Helpers.UrlFix("json/search.json") 
            //jsonPath: Helpers.UrlFix("{{ url_for('main.search') }}")
            jsonPath: Helpers.UrlFix(window.search_url) 
            //jsonPath: Helpers.UrlFix("http://localhost:5000/json/search.json") 
        }
    }
    constructor(t = {}) {
        return this.settings = Object.assign(this.options, t),
            document.getElementById(this.settings.searchInputId) ? (this._addListeners(), this._init(), this._autoComplete) : null
    }

    _init() {
        const t = document.getElementById(this.settings.searchInputId);
        this._autoComplete = new autoComplete({
            data: {
                src: async () => {
                    t.setAttribute("placeholder", this.settings.loading);
                    const e = await fetch(this.settings.jsonPath), 
                    s = await e.json();
                    return t.setAttribute("placeholder", this.settings.placeholder), 
                    s
                }, 
                
                key: ["label"], 
                cache: !0
            },

            sort: (t, e) => t.match < e.match ? -1 : t.match > e.match ? 1 : 0,
            placeHolder: this.settings.placeholder,
            selector: "#" + this.settings.searchInputId,
            threshold: 1,
            debounce: 0,
            searchEngine: "loose",
            highlight: !0,
            maxResults: 10,

            resultsList: {

                render: !0,
                container: t => {
                    t.setAttribute("id", this.settings.searchResultsId),
                    t.setAttribute("class", "auto-complete-result")
                },

                destination: document.getElementById(this.settings.searchInputId),
                position: "afterend",
                element: "ul"
            },
            
            resultItem: {
                content: (t, e) => {
                    e.innerHTML = '<p class="mb-0">' + t.match + '</p><p class="text-small text-muted mb-0">' + Helpers.UrlFix(t.value.url) + "</p>",
                    e.setAttribute("class", "auto-complete-result-item")
                }, 
                
                element: "li"
            },

            noResults: () => {
                const t = document.createElement("li");
                t.setAttribute("class", "no_resulst"), 
                t.setAttribute("tabindex", "1"),
                t.innerHTML = "No Results",
                document.getElementById(this.settings.searchResultsId).appendChild(t)
            },
            
            onSelection: e => {
                window.location.href = Helpers.UrlFix(e.selection.value.url),
                    t.value = "",
                    t.setAttribute("placeholder", "Search")
            }
        })
    }

    _addListeners() {
        document.getElementById(this.settings.searchModalId).addEventListener("shown.bs.modal", this._onSearchModalShown.bind(this)),
        document.getElementById(this.settings.searchModalId).addEventListener("hidden.bs.modal", this._onSearchModalHidden.bind(this)),
        document.getElementById(this.settings.searchInputId).addEventListener("focus", this._onInputFocus.bind(this)),
        document.getElementById(this.settings.searchInputId).addEventListener("focusout", this._onInputFocusOut.bind(this))
    }

    _onSearchModalShown() { document.getElementById(this.settings.searchInputId).focus() }

    _onSearchModalHidden() {
        document.getElementById(this.settings.searchInputId).value = "";
        const t = document.getElementById(this.settings.searchResultsId);
        for (; t.firstChild;)t.removeChild(t.firstChild)
    }

    _onInputFocus() { document.getElementById(this.settings.searchInputId).addEventListener("keydown", this._onKeyDown.bind(this)) }

    _onInputFocusOut() { document.getElementById(this.settings.searchInputId).removeEventListener("keydown", this._onKeyDown.bind(this)) }

    _onKeyDown(t) { 38 !== t.which && 40 !== t.which || t.preventDefault() }
    
}