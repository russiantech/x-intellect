class PathList{constructor(){this._initProgress()}_initProgress(){document.querySelectorAll(".progress-bar").forEach((t=>{const r=t.getAttribute("aria-valuenow");t.style.width=r+"%"}))}}