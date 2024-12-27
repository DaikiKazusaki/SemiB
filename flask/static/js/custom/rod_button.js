class RodButton extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    static observedAttributes = ['x', 'z'];

    attributeChangedCallback(name, oldValue, newValue) {
        this.render();  // 値が変われば再描画
    }

    get x() {
        return this.getAttribute('x');
    }
    set x(value) {
        this.setAttribute('name', value);
    }
    get z() {
        return this.getAttribute('z');
    }
    set z(value) {
        this.setAttribute('z', value);
    }

    // 初期化時のイベント
    connectedCallback() {
        this.render();
    }

    // レンダリング処理
    render() {
        const x = this.x || 'null';
        const z = this.z || 'null';
        this.shadowRoot.innerHTML = `
        <button>(${x}, ${z})</button>
        `;
    }
}

customElements.define('custom-rod-button', RodButton);