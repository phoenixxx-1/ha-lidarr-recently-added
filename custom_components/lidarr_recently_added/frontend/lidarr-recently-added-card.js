/* Lidarr Recently Added card 0.3.0 - built from frontend/src, do not edit. */
var I=globalThis,$=I.ShadowRoot&&(I.ShadyCSS===void 0||I.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,e1=Symbol(),h1=new WeakMap,P=class{constructor(H,C,V){if(this._$cssResult$=!0,V!==e1)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=H,this.t=C}get styleSheet(){let H=this.o,C=this.t;if($&&H===void 0){let V=C!==void 0&&C.length===1;V&&(H=h1.get(C)),H===void 0&&((this.o=H=new CSSStyleSheet).replaceSync(this.cssText),V&&h1.set(C,H))}return H}toString(){return this.cssText}},g1=M=>new P(typeof M=="string"?M:M+"",void 0,e1),w=(M,...H)=>{let C=M.length===1?M[0]:H.reduce((V,L,r)=>V+(e=>{if(e._$cssResult$===!0)return e.cssText;if(typeof e=="number")return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(L)+M[r+1],M[0]);return new P(C,M,e1)},f1=(M,H)=>{if($)M.adoptedStyleSheets=H.map(C=>C instanceof CSSStyleSheet?C:C.styleSheet);else for(let C of H){let V=document.createElement("style"),L=I.litNonce;L!==void 0&&V.setAttribute("nonce",L),V.textContent=C.cssText,M.appendChild(V)}},t1=$?M=>M:M=>M instanceof CSSStyleSheet?(H=>{let C="";for(let V of H.cssRules)C+=V.cssText;return g1(C)})(M):M;var{is:i2,defineProperty:A2,getOwnPropertyDescriptor:o2,getOwnPropertyNames:a2,getOwnPropertySymbols:d2,getPrototypeOf:p2}=Object,U=globalThis,k1=U.trustedTypes,m2=k1?k1.emptyScript:"",v2=U.reactiveElementPolyfillSupport,b=(M,H)=>M,i1={toAttribute(M,H){switch(H){case Boolean:M=M?m2:null;break;case Object:case Array:M=M==null?M:JSON.stringify(M)}return M},fromAttribute(M,H){let C=M;switch(H){case Boolean:C=M!==null;break;case Number:C=M===null?null:Number(M);break;case Object:case Array:try{C=JSON.parse(M)}catch{C=null}}return C}},y1=(M,H)=>!i2(M,H),B1={attribute:!0,type:String,converter:i1,reflect:!1,useDefault:!1,hasChanged:y1};Symbol.metadata??=Symbol("metadata"),U.litPropertyMetadata??=new WeakMap;var Z=class extends HTMLElement{static addInitializer(H){this._$Ei(),(this.l??=[]).push(H)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(H,C=B1){if(C.state&&(C.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(H)&&((C=Object.create(C)).wrapped=!0),this.elementProperties.set(H,C),!C.noAccessor){let V=Symbol(),L=this.getPropertyDescriptor(H,V,C);L!==void 0&&A2(this.prototype,H,L)}}static getPropertyDescriptor(H,C,V){let{get:L,set:r}=o2(this.prototype,H)??{get(){return this[C]},set(e){this[C]=e}};return{get:L,set(e){let i=L?.call(this);r?.call(this,e),this.requestUpdate(H,i,V)},configurable:!0,enumerable:!0}}static getPropertyOptions(H){return this.elementProperties.get(H)??B1}static _$Ei(){if(this.hasOwnProperty(b("elementProperties")))return;let H=p2(this);H.finalize(),H.l!==void 0&&(this.l=[...H.l]),this.elementProperties=new Map(H.elementProperties)}static finalize(){if(this.hasOwnProperty(b("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(b("properties"))){let C=this.properties,V=[...a2(C),...d2(C)];for(let L of V)this.createProperty(L,C[L])}let H=this[Symbol.metadata];if(H!==null){let C=litPropertyMetadata.get(H);if(C!==void 0)for(let[V,L]of C)this.elementProperties.set(V,L)}this._$Eh=new Map;for(let[C,V]of this.elementProperties){let L=this._$Eu(C,V);L!==void 0&&this._$Eh.set(L,C)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(H){let C=[];if(Array.isArray(H)){let V=new Set(H.flat(1/0).reverse());for(let L of V)C.unshift(t1(L))}else H!==void 0&&C.push(t1(H));return C}static _$Eu(H,C){let V=C.attribute;return V===!1?void 0:typeof V=="string"?V:typeof H=="string"?H.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(H=>this.enableUpdating=H),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(H=>H(this))}addController(H){(this._$EO??=new Set).add(H),this.renderRoot!==void 0&&this.isConnected&&H.hostConnected?.()}removeController(H){this._$EO?.delete(H)}_$E_(){let H=new Map,C=this.constructor.elementProperties;for(let V of C.keys())this.hasOwnProperty(V)&&(H.set(V,this[V]),delete this[V]);H.size>0&&(this._$Ep=H)}createRenderRoot(){let H=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return f1(H,this.constructor.elementStyles),H}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(H=>H.hostConnected?.())}enableUpdating(H){}disconnectedCallback(){this._$EO?.forEach(H=>H.hostDisconnected?.())}attributeChangedCallback(H,C,V){this._$AK(H,V)}_$ET(H,C){let V=this.constructor.elementProperties.get(H),L=this.constructor._$Eu(H,V);if(L!==void 0&&V.reflect===!0){let r=(V.converter?.toAttribute!==void 0?V.converter:i1).toAttribute(C,V.type);this._$Em=H,r==null?this.removeAttribute(L):this.setAttribute(L,r),this._$Em=null}}_$AK(H,C){let V=this.constructor,L=V._$Eh.get(H);if(L!==void 0&&this._$Em!==L){let r=V.getPropertyOptions(L),e=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:i1;this._$Em=L;let i=e.fromAttribute(C,r.type);this[L]=i??this._$Ej?.get(L)??i,this._$Em=null}}requestUpdate(H,C,V,L=!1,r){if(H!==void 0){let e=this.constructor;if(L===!1&&(r=this[H]),V??=e.getPropertyOptions(H),!((V.hasChanged??y1)(r,C)||V.useDefault&&V.reflect&&r===this._$Ej?.get(H)&&!this.hasAttribute(e._$Eu(H,V))))return;this.C(H,C,V)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(H,C,{useDefault:V,reflect:L,wrapped:r},e){V&&!(this._$Ej??=new Map).has(H)&&(this._$Ej.set(H,e??C??this[H]),r!==!0||e!==void 0)||(this._$AL.has(H)||(this.hasUpdated||V||(C=void 0),this._$AL.set(H,C)),L===!0&&this._$Em!==H&&(this._$Eq??=new Set).add(H))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(C){Promise.reject(C)}let H=this.scheduleUpdate();return H!=null&&await H,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[L,r]of this._$Ep)this[L]=r;this._$Ep=void 0}let V=this.constructor.elementProperties;if(V.size>0)for(let[L,r]of V){let{wrapped:e}=r,i=this[L];e!==!0||this._$AL.has(L)||i===void 0||this.C(L,void 0,r,i)}}let H=!1,C=this._$AL;try{H=this.shouldUpdate(C),H?(this.willUpdate(C),this._$EO?.forEach(V=>V.hostUpdate?.()),this.update(C)):this._$EM()}catch(V){throw H=!1,this._$EM(),V}H&&this._$AE(C)}willUpdate(H){}_$AE(H){this._$EO?.forEach(C=>C.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(H)),this.updated(H)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(H){return!0}update(H){this._$Eq&&=this._$Eq.forEach(C=>this._$ET(C,this[C])),this._$EM()}updated(H){}firstUpdated(H){}};Z.elementStyles=[],Z.shadowRootOptions={mode:"open"},Z[b("elementProperties")]=new Map,Z[b("finalized")]=new Map,v2?.({ReactiveElement:Z}),(U.reactiveElementVersions??=[]).push("2.1.2");var o1=globalThis,P1=M=>M,Q=o1.trustedTypes,w1=Q?Q.createPolicy("lit-html",{createHTML:M=>M}):void 0,a1="$lit$",S=`lit$${Math.random().toFixed(9).slice(2)}$`,d1="?"+S,x2=`<${d1}>`,h=document,F=()=>h.createComment(""),R=M=>M===null||typeof M!="object"&&typeof M!="function",p1=Array.isArray,E1=M=>p1(M)||typeof M?.[Symbol.iterator]=="function",A1=`[ 	
\f\r]`,T=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,b1=/-->/g,T1=/>/g,c=RegExp(`>|${A1}(?:([^\\s"'>=/]+)(${A1}*=${A1}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),F1=/'/g,R1=/"/g,N1=/^(?:script|style|textarea|title)$/i,m1=M=>(H,...C)=>({_$litType$:M,strings:H,values:C}),v=m1(1),E=m1(2),w2=m1(3),u=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),D1=new WeakMap,O=h.createTreeWalker(h,129);function W1(M,H){if(!p1(M)||!M.hasOwnProperty("raw"))throw Error("invalid template strings array");return w1!==void 0?w1.createHTML(H):H}var _1=(M,H)=>{let C=M.length-1,V=[],L,r=H===2?"<svg>":H===3?"<math>":"",e=T;for(let i=0;i<C;i++){let t=M[i],o,a,A=-1,p=0;for(;p<t.length&&(e.lastIndex=p,a=e.exec(t),a!==null);)p=e.lastIndex,e===T?a[1]==="!--"?e=b1:a[1]!==void 0?e=T1:a[2]!==void 0?(N1.test(a[2])&&(L=RegExp("</"+a[2],"g")),e=c):a[3]!==void 0&&(e=c):e===c?a[0]===">"?(e=L??T,A=-1):a[1]===void 0?A=-2:(A=e.lastIndex-a[2].length,o=a[1],e=a[3]===void 0?c:a[3]==='"'?R1:F1):e===R1||e===F1?e=c:e===b1||e===T1?e=T:(e=c,L=void 0);let m=e===c&&M[i+1].startsWith("/>")?" ":"";r+=e===T?t+x2:A>=0?(V.push(o),t.slice(0,A)+a1+t.slice(A)+S+m):t+S+(A===-2?i:m)}return[W1(M,r+(M[C]||"<?>")+(H===2?"</svg>":H===3?"</math>":"")),V]},D=class M{constructor({strings:H,_$litType$:C},V){let L;this.parts=[];let r=0,e=0,i=H.length-1,t=this.parts,[o,a]=_1(H,C);if(this.el=M.createElement(o,V),O.currentNode=this.el.content,C===2||C===3){let A=this.el.content.firstChild;A.replaceWith(...A.childNodes)}for(;(L=O.nextNode())!==null&&t.length<i;){if(L.nodeType===1){if(L.hasAttributes())for(let A of L.getAttributeNames())if(A.endsWith(a1)){let p=a[e++],m=L.getAttribute(A).split(S),x=/([.?@])?(.*)/.exec(p);t.push({type:1,index:r,name:x[2],strings:m,ctor:x[1]==="."?z:x[1]==="?"?K:x[1]==="@"?q:f}),L.removeAttribute(A)}else A.startsWith(S)&&(t.push({type:6,index:r}),L.removeAttribute(A));if(N1.test(L.tagName)){let A=L.textContent.split(S),p=A.length-1;if(p>0){L.textContent=Q?Q.emptyScript:"";for(let m=0;m<p;m++)L.append(A[m],F()),O.nextNode(),t.push({type:2,index:++r});L.append(A[p],F())}}}else if(L.nodeType===8)if(L.data===d1)t.push({type:2,index:r});else{let A=-1;for(;(A=L.data.indexOf(S,A+1))!==-1;)t.push({type:7,index:r}),A+=S.length-1}r++}}static createElement(H,C){let V=h.createElement("template");return V.innerHTML=H,V}};function g(M,H,C=M,V){if(H===u)return H;let L=V!==void 0?C._$Co?.[V]:C._$Cl,r=R(H)?void 0:H._$litDirective$;return L?.constructor!==r&&(L?._$AO?.(!1),r===void 0?L=void 0:(L=new r(M),L._$AT(M,C,V)),V!==void 0?(C._$Co??=[])[V]=L:C._$Cl=L),L!==void 0&&(H=g(M,L._$AS(M,H.values),L,V)),H}var G=class{constructor(H,C){this._$AV=[],this._$AN=void 0,this._$AD=H,this._$AM=C}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(H){let{el:{content:C},parts:V}=this._$AD,L=(H?.creationScope??h).importNode(C,!0);O.currentNode=L;let r=O.nextNode(),e=0,i=0,t=V[0];for(;t!==void 0;){if(e===t.index){let o;t.type===2?o=new B(r,r.nextSibling,this,H):t.type===1?o=new t.ctor(r,t.name,t.strings,this,H):t.type===6&&(o=new j(r,this,H)),this._$AV.push(o),t=V[++i]}e!==t?.index&&(r=O.nextNode(),e++)}return O.currentNode=h,L}p(H){let C=0;for(let V of this._$AV)V!==void 0&&(V.strings!==void 0?(V._$AI(H,V,C),C+=V.strings.length-2):V._$AI(H[C])),C++}},B=class M{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(H,C,V,L){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=H,this._$AB=C,this._$AM=V,this.options=L,this._$Cv=L?.isConnected??!0}get parentNode(){let H=this._$AA.parentNode,C=this._$AM;return C!==void 0&&H?.nodeType===11&&(H=C.parentNode),H}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(H,C=this){H=g(this,H,C),R(H)?H===d||H==null||H===""?(this._$AH!==d&&this._$AR(),this._$AH=d):H!==this._$AH&&H!==u&&this._(H):H._$litType$!==void 0?this.$(H):H.nodeType!==void 0?this.T(H):E1(H)?this.k(H):this._(H)}O(H){return this._$AA.parentNode.insertBefore(H,this._$AB)}T(H){this._$AH!==H&&(this._$AR(),this._$AH=this.O(H))}_(H){this._$AH!==d&&R(this._$AH)?this._$AA.nextSibling.data=H:this.T(h.createTextNode(H)),this._$AH=H}$(H){let{values:C,_$litType$:V}=H,L=typeof V=="number"?this._$AC(H):(V.el===void 0&&(V.el=D.createElement(W1(V.h,V.h[0]),this.options)),V);if(this._$AH?._$AD===L)this._$AH.p(C);else{let r=new G(L,this),e=r.u(this.options);r.p(C),this.T(e),this._$AH=r}}_$AC(H){let C=D1.get(H.strings);return C===void 0&&D1.set(H.strings,C=new D(H)),C}k(H){p1(this._$AH)||(this._$AH=[],this._$AR());let C=this._$AH,V,L=0;for(let r of H)L===C.length?C.push(V=new M(this.O(F()),this.O(F()),this,this.options)):V=C[L],V._$AI(r),L++;L<C.length&&(this._$AR(V&&V._$AB.nextSibling,L),C.length=L)}_$AR(H=this._$AA.nextSibling,C){for(this._$AP?.(!1,!0,C);H!==this._$AB;){let V=P1(H).nextSibling;P1(H).remove(),H=V}}setConnected(H){this._$AM===void 0&&(this._$Cv=H,this._$AP?.(H))}},f=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(H,C,V,L,r){this.type=1,this._$AH=d,this._$AN=void 0,this.element=H,this.name=C,this._$AM=L,this.options=r,V.length>2||V[0]!==""||V[1]!==""?(this._$AH=Array(V.length-1).fill(new String),this.strings=V):this._$AH=d}_$AI(H,C=this,V,L){let r=this.strings,e=!1;if(r===void 0)H=g(this,H,C,0),e=!R(H)||H!==this._$AH&&H!==u,e&&(this._$AH=H);else{let i=H,t,o;for(H=r[0],t=0;t<r.length-1;t++)o=g(this,i[V+t],C,t),o===u&&(o=this._$AH[t]),e||=!R(o)||o!==this._$AH[t],o===d?H=d:H!==d&&(H+=(o??"")+r[t+1]),this._$AH[t]=o}e&&!L&&this.j(H)}j(H){H===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,H??"")}},z=class extends f{constructor(){super(...arguments),this.type=3}j(H){this.element[this.name]=H===d?void 0:H}},K=class extends f{constructor(){super(...arguments),this.type=4}j(H){this.element.toggleAttribute(this.name,!!H&&H!==d)}},q=class extends f{constructor(H,C,V,L,r){super(H,C,V,L,r),this.type=5}_$AI(H,C=this){if((H=g(this,H,C,0)??d)===u)return;let V=this._$AH,L=H===d&&V!==d||H.capture!==V.capture||H.once!==V.once||H.passive!==V.passive,r=H!==d&&(V===d||L);L&&this.element.removeEventListener(this.name,this,V),r&&this.element.addEventListener(this.name,this,H),this._$AH=H}handleEvent(H){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,H):this._$AH.handleEvent(H)}},j=class{constructor(H,C,V){this.element=H,this.type=6,this._$AN=void 0,this._$AM=C,this.options=V}get _$AU(){return this._$AM._$AU}_$AI(H){g(this,H)}},I1={M:a1,P:S,A:d1,C:1,L:_1,R:G,D:E1,V:g,I:B,H:f,N:K,U:q,B:z,F:j},n2=o1.litHtmlPolyfillSupport;n2?.(D,B),(o1.litHtmlVersions??=[]).push("3.3.3");var $1=(M,H,C)=>{let V=C?.renderBefore??H,L=V._$litPart$;if(L===void 0){let r=C?.renderBefore??null;V._$litPart$=L=new B(H.insertBefore(F(),r),r,void 0,C??{})}return L._$AI(M),L};var v1=globalThis,n=class extends Z{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let H=super.createRenderRoot();return this.renderOptions.renderBefore??=H.firstChild,H}update(H){let C=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(H),this._$Do=$1(C,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return u}};n._$litElement$=!0,n.finalized=!0,v1.litElementHydrateSupport?.({LitElement:n});var l2=v1.litElementPolyfillSupport;l2?.({LitElement:n});(v1.litElementVersions??=[]).push("4.2.2");var U1={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Q1=M=>(...H)=>({_$litDirective$:M,values:H}),X=class{constructor(H){}get _$AU(){return this._$AM._$AU}_$AT(H,C,V){this._$Ct=H,this._$AM=C,this._$Ci=V}_$AS(H,C){return this.update(H,C)}update(H,C){return this.render(...C)}};var{I:Z2}=I1,G1=M=>M;var z1=()=>document.createComment(""),y=(M,H,C)=>{let V=M._$AA.parentNode,L=H===void 0?M._$AB:H._$AA;if(C===void 0){let r=V.insertBefore(z1(),L),e=V.insertBefore(z1(),L);C=new Z2(r,e,M,M.options)}else{let r=C._$AB.nextSibling,e=C._$AM,i=e!==M;if(i){let t;C._$AQ?.(M),C._$AM=M,C._$AP!==void 0&&(t=M._$AU)!==e._$AU&&C._$AP(t)}if(r!==L||i){let t=C._$AA;for(;t!==r;){let o=G1(t).nextSibling;G1(V).insertBefore(t,L),t=o}}}return C},s=(M,H,C=M)=>(M._$AI(H,C),M),S2={},K1=(M,H=S2)=>M._$AH=H,q1=M=>M._$AH,Y=M=>{M._$AR(),M._$AA.remove()};var j1=(M,H,C)=>{let V=new Map;for(let L=H;L<=C;L++)V.set(M[L],L);return V},x1=Q1(class extends X{constructor(M){if(super(M),M.type!==U1.CHILD)throw Error("repeat() can only be used in text expressions")}dt(M,H,C){let V;C===void 0?C=H:H!==void 0&&(V=H);let L=[],r=[],e=0;for(let i of M)L[e]=V?V(i,e):e,r[e]=C(i,e),e++;return{values:r,keys:L}}render(M,H,C){return this.dt(M,H,C).values}update(M,[H,C,V]){let L=q1(M),{values:r,keys:e}=this.dt(H,C,V);if(!Array.isArray(L))return this.ut=e,r;let i=this.ut??=[],t=[],o,a,A=0,p=L.length-1,m=0,x=r.length-1;for(;A<=p&&m<=x;)if(L[A]===null)A++;else if(L[p]===null)p--;else if(i[A]===e[m])t[m]=s(L[A],r[m]),A++,m++;else if(i[p]===e[x])t[x]=s(L[p],r[x]),p--,x--;else if(i[A]===e[x])t[x]=s(L[A],r[x]),y(M,t[x+1],L[A]),A++,x--;else if(i[p]===e[m])t[m]=s(L[p],r[m]),y(M,L[A],L[p]),p--,m++;else if(o===void 0&&(o=j1(e,m,x),a=j1(i,A,p)),o.has(i[A]))if(o.has(i[p])){let l=a.get(e[m]),r1=l!==void 0?L[l]:null;if(r1===null){let O1=y(M,L[A]);s(O1,r[m]),t[m]=O1}else t[m]=s(r1,r[m]),y(M,L[A],r1),L[l]=null;m++}else Y(L[p]),p--;else Y(L[A]),A++;for(;m<=x;){let l=y(M,t[x+1]);s(l,r[m]),t[m++]=l}for(;A<=p;){let l=L[A++];l!==null&&Y(l)}return this.ut=e,K1(M,t),u}});var X1="M12,11A1,1 0 0,0 11,12A1,1 0 0,0 12,13A1,1 0 0,0 13,12A1,1 0 0,0 12,11M12,16.5C9.5,16.5 7.5,14.5 7.5,12C7.5,9.5 9.5,7.5 12,7.5C14.5,7.5 16.5,9.5 16.5,12C16.5,14.5 14.5,16.5 12,16.5M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z";var Y1="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z";var n1="M8,5.14V19.14L19,12.14L8,5.14Z";var J1="M3 10H14V12H3V10M3 6H14V8H3V6M3 14H10V16H3V14M16 13V21L22 17L16 13Z",C2="M3 16H10V14H3M18 14V10H16V14H12V16H16V20H18V16H22V14M14 6H3V8H14M14 10H3V12H14V10Z";var H2="M20,6A2,2 0 0,1 22,8V20A2,2 0 0,1 20,22H4A2,2 0 0,1 2,20V8C2,7.15 2.53,6.42 3.28,6.13L15.71,1L16.47,2.83L8.83,6H20M20,8H4V12H16V10H18V12H20V8M7,14A3,3 0 0,0 4,17A3,3 0 0,0 7,20A3,3 0 0,0 10,17A3,3 0 0,0 7,14Z";var l1="M12,12A3,3 0 0,0 9,15A3,3 0 0,0 12,18A3,3 0 0,0 15,15A3,3 0 0,0 12,12M12,20A5,5 0 0,1 7,15A5,5 0 0,1 12,10A5,5 0 0,1 17,15A5,5 0 0,1 12,20M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8C10.89,8 10,7.1 10,6C10,4.89 10.89,4 12,4M17,2H7C5.89,2 5,2.89 5,4V20A2,2 0 0,0 7,22H17A2,2 0 0,0 19,20V4C19,2.89 18.1,2 17,2Z";var N="music_assistant";function J(M){return Object.values(M.entities??{}).filter(H=>H!==void 0&&H.platform===N&&H.entity_id.startsWith("media_player.")&&M.states[H.entity_id]!==void 0).map(H=>H.entity_id).sort((H,C)=>k(M,H).localeCompare(k(M,C)))}function V2(M,H){let C=M.states[H]?.attributes.group_members;if(!Array.isArray(C))return[];let V=C.filter(L=>typeof L=="string");return V.length>1&&V.includes(H)?V:[]}function L2(M,H){let C=V2(M,H);return C.length&&C[0]!==H?C[0]:void 0}function C1(M,H){let C=k(M,H),V=V2(M,H);if(!V.length||V[0]!==H)return C;let L=C.split(" ")[0],r=V.slice(1).map(e=>{let i=k(M,e),t=i.split(" ");return t.length>1&&t[0]===L?t.slice(1).join(" "):i});return[C,...r].join(" + ")}function H1(M){return M.services?.[N]?.play_media!==void 0}function k(M,H){let C=M.states[H]?.attributes.friendly_name;return typeof C=="string"&&C?C:H}function V1(M,H){if(H.player_entity){let C=M.states[H.player_entity]?.state?.trim();if(C&&C!=="unknown"&&C!=="unavailable"){if(C.startsWith("media_player.")&&M.states[C])return C;let V=J(M).find(L=>k(M,L).toLowerCase()===C.toLowerCase());if(V)return V}}if(H.player&&M.states[H.player])return H.player}function Z1(M,H,C){if(!H)return;let V=M.states[H]?.attributes.items;if(Array.isArray(V))return C?V.slice(0,C):V}var u2=[["year",365*24*3600],["month",720*3600],["week",168*3600],["day",24*3600],["hour",3600],["minute",60]];function S1(M,H,C=Date.now()){if(!M)return"";let V=Date.parse(M);if(Number.isNaN(V))return"";let L=Math.max(0,(C-V)/1e3),r;try{r=new Intl.RelativeTimeFormat(H,{numeric:"auto",style:"narrow"})}catch{r=new Intl.RelativeTimeFormat("en",{numeric:"auto",style:"narrow"})}for(let[e,i]of u2)if(L>=i)return r.format(-Math.floor(L/i),e);return r.format(0,"minute")}function M2(M){return(M??"").replace(/^the\s+/i,"").split(/[\s\-_/&+]+/u).filter(V=>/[\p{L}\p{N}]/u.test(V)).slice(0,2).map(V=>[...V.replace(/[^\p{L}\p{N}]/gu,"")][0]??"").join("").toUpperCase()||"?"}function r2(M){return M&&typeof M=="object"&&"message"in M&&typeof M.message=="string"?M.message:String(M)}function e2(){return document.querySelector("home-assistant")===null||customElements.get("home-assistant")!==void 0}function L1(M,H){let C=()=>{customElements.get(M)||customElements.define(M,H)};if(e2()){C();return}let V=Date.now(),L=()=>{e2()||Date.now()-V>3e4?C():window.setTimeout(L,25)};L()}var u1="lidarr-recently-added-popup",s2=600,W=class extends n{constructor(){super(...arguments);this.heading="";this.entries=[];this.x=0;this.y=0;this.onKeydown=C=>this.handleKeydown(C)}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this.onKeydown,!0)}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.onKeydown,!0)}close(){this.remove(),this.returnFocus?.focus({preventScroll:!0})}get sheet(){return window.innerWidth<s2}firstUpdated(){let C=this.renderRoot.querySelector(".panel");if(C&&!this.sheet){let{width:L,height:r}=C.getBoundingClientRect(),e=Math.min(Math.max(this.x,8),window.innerWidth-L-8),i=this.y+r+8>window.innerHeight?Math.max(8,this.y-r):this.y;C.style.left=`${e}px`,C.style.top=`${i}px`}C?.classList.add("open"),this.items()[0]?.focus({preventScroll:!0})}items(){return[...this.renderRoot.querySelectorAll(".item")]}handleKeydown(C){let V=this.items(),L=V.indexOf(this.renderRoot.activeElement);if(C.key==="Escape")C.stopPropagation(),C.preventDefault(),this.close();else if(C.key==="ArrowDown"||C.key==="ArrowUp"){C.preventDefault();let r=C.key==="ArrowDown"?1:-1;V[(L+r+V.length)%V.length]?.focus()}else if(C.key==="Tab"){C.preventDefault();let r=C.shiftKey?-1:1;V[(L+r+V.length)%V.length]?.focus()}}choose(C){this.close(),C.action()}render(){return v`
      <div class="backdrop" @click=${()=>this.close()}></div>
      <div
        class="panel ${this.sheet?"sheet":"menu"}"
        role="menu"
        aria-label=${this.heading}
      >
        <div class="heading">
          <div class="title">${this.heading}</div>
          ${this.subheading?v`<div class="subtitle">${this.subheading}</div>`:d}
        </div>
        ${this.entries.map(C=>v`
            <button
              class="item"
              role=${C.checked===void 0?"menuitem":"menuitemradio"}
              aria-checked=${C.checked===void 0?d:String(C.checked)}
              @click=${()=>this.choose(C)}
            >
              ${C.icon?v`<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
                    ${E`<path d=${C.icon}></path>`}
                  </svg>`:d}
              <span class="label">
                <span>${C.label}</span>
                ${C.secondary?v`<span class="secondary">${C.secondary}</span>`:d}
              </span>
            </button>
          `)}
      </div>
    `}};W.properties={heading:{type:String},subheading:{type:String},entries:{attribute:!1},x:{type:Number},y:{type:Number}},W.styles=w`
    :host {
      position: fixed;
      inset: 0;
      z-index: 10;
      font-family: var(--ha-font-family-body, var(--paper-font-body1_-_font-family, inherit));
      -webkit-font-smoothing: antialiased;
    }
    .backdrop {
      position: absolute;
      inset: 0;
      background: transparent;
    }
    .panel {
      position: absolute;
      box-sizing: border-box;
      min-width: 220px;
      max-width: min(320px, calc(100vw - 16px));
      padding: 6px 0;
      background: var(--card-background-color, var(--ha-card-background, #fff));
      color: var(--primary-text-color);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
      opacity: 0;
      transform: scale(0.96);
      transform-origin: top left;
      transition:
        opacity 120ms ease-out,
        transform 120ms ease-out;
    }
    .panel.open {
      opacity: 1;
      transform: none;
    }
    .sheet {
      left: 8px;
      right: 8px;
      bottom: 8px;
      max-width: none;
      padding-bottom: calc(6px + env(safe-area-inset-bottom, 0px));
      transform: translateY(16px);
    }
    .backdrop:has(+ .sheet) {
      background: rgba(0, 0, 0, 0.32);
    }
    .heading {
      padding: 8px 16px 6px;
    }
    .title {
      font-size: 14px;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .subtitle {
      font-size: 12px;
      color: var(--secondary-text-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .item {
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
      min-height: 44px;
      padding: 6px 16px;
      border: 0;
      background: none;
      color: inherit;
      font: inherit;
      font-size: 14px;
      text-align: start;
      cursor: pointer;
    }
    .item:hover,
    .item:focus-visible {
      background: color-mix(in srgb, var(--primary-text-color) 8%, transparent);
      outline: none;
    }
    .item[aria-checked="true"] {
      color: var(--primary-color);
    }
    .icon {
      flex: none;
      width: 22px;
      height: 22px;
      fill: var(--secondary-text-color);
    }
    .item[aria-checked="true"] .icon {
      fill: var(--primary-color);
    }
    .label {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .label > span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .secondary {
      font-size: 12px;
      color: var(--secondary-text-color);
    }
    @media (prefers-reduced-motion: reduce) {
      .panel {
        transition: none;
      }
    }
  `;L1(u1,W);function s1(M){document.querySelectorAll(u1).forEach(C=>C.remove());let H=document.createElement(u1);return H.heading=M.heading,H.subheading=M.subheading,H.entries=M.entries,H.x=M.x,H.y=M.y,H.returnFocus=M.returnFocus,document.body.appendChild(H),H}var M1="lidarr-recently-added-card",t2="lidarr_recently_added",c2=500,O2=10,h2={title:"Title",albums_entity:"Recently added albums sensor",artists_entity:"Recently added artists sensor",layout:"Layout",max_items:"Maximum items",show_artists:"Show artists",show_added:"Show when added",player:"Music Assistant player",player_entity:"Player helper",artist_radio:"Artist tap starts radio",lidarr_link:"Show \u201COpen in Lidarr\u201D in the hold menu"},g2={player:"Tapping a cover plays it here.",player_entity:"Optional. An input_select or text helper holding a player's entity ID or name. Takes priority over the fixed player.",lidarr_link:"Only turn on if the Lidarr address works from the devices that show this dashboard."},_=class extends n{constructor(){super(...arguments);this.now=Date.now();this.failedImages=new Set;this.albums=[];this.artists=[];this.suppressClick=!1;this.lastMenuAt=0;this.onPointerDown=C=>{if(C.button!==0)return;let V=this.targetFrom(C);V&&(this.cancelHold(),this.suppressClick=!1,this.pendingHold={pointerId:C.pointerId,x:C.clientX,y:C.clientY,target:V,timer:window.setTimeout(()=>{let L=this.pendingHold;this.pendingHold=void 0,L&&(this.suppressClick=!0,this.openMenu(L.target,L.x,L.y))},c2)})};this.onPointerMove=C=>{let V=this.pendingHold;V&&C.pointerId===V.pointerId&&Math.hypot(C.clientX-V.x,C.clientY-V.y)>O2&&this.cancelHold()};this.cancelHold=()=>{this.pendingHold&&(window.clearTimeout(this.pendingHold.timer),this.pendingHold=void 0)};this.onClick=C=>{let V=this.targetFrom(C);if(!V)return;if(this.suppressClick){this.suppressClick=!1;return}let L=V.element.getBoundingClientRect();this.tap(V,C.clientX||L.left+L.width/2,C.clientY||L.top+L.height/2)};this.onContextMenu=C=>{let V=this.targetFrom(C);V&&(C.preventDefault(),this.cancelHold(),Date.now()-this.lastMenuAt>800&&(this.suppressClick=!0,this.openMenu(V,C.clientX,C.clientY)))};this.onKeyDown=C=>{if(C.key==="ContextMenu"||C.key==="F10"&&C.shiftKey){let V=this.targetFrom(C);if(V){C.preventDefault();let L=V.element.getBoundingClientRect();this.openMenu(V,L.left+L.width/2,L.top+L.height/2)}}}}setConfig(C){if(!C.albums_entity&&!C.artists_entity)throw new Error("Set albums_entity, artists_entity, or both.");if(C.layout&&!["strip","wall"].includes(C.layout))throw new Error('layout must be "strip" or "wall".');this.config={layout:"strip",show_artists:!0,show_added:!0,artist_radio:!0,lidarr_link:!1,...C}}getCardSize(){let C=this.config?.layout==="wall"?8:4;return(this.config?.albums_entity?C:0)+(this.showArtists?2:0)+1}getGridOptions(){return{columns:12,min_columns:6,rows:"auto"}}static getConfigForm(){let C={entity:{filter:{integration:t2,domain:"sensor"}}};return{schema:[{name:"title",selector:{text:{}}},{name:"albums_entity",selector:C},{name:"artists_entity",selector:C},{type:"grid",name:"",schema:[{name:"layout",selector:{select:{mode:"dropdown",options:[{value:"strip",label:"Strip (one scrolling row)"},{value:"wall",label:"Wall (grid)"}]}}},{name:"max_items",selector:{number:{min:1,max:25,mode:"box"}}}]},{type:"grid",name:"",schema:[{name:"show_artists",selector:{boolean:{}}},{name:"show_added",selector:{boolean:{}}}]},{type:"expandable",name:"",flatten:!0,title:"Playback (Music Assistant)",schema:[{name:"player",selector:{entity:{filter:{integration:N,domain:"media_player"}}}},{name:"player_entity",selector:{entity:{filter:[{domain:"input_select"},{domain:"select"},{domain:"input_text"},{domain:"text"}]}}},{name:"artist_radio",selector:{boolean:{}}}]},{name:"lidarr_link",selector:{boolean:{}}}],computeLabel:V=>h2[V.name],computeHelper:V=>g2[V.name]}}static getStubConfig(C){let V=r=>{let e=Object.values(C.entities??{}).filter(i=>i?.platform===t2).map(i=>i.entity_id);return(e.length?e:Object.keys(C.states)).find(i=>i.endsWith(r))},L=J(C)[0];return{type:`custom:${M1}`,albums_entity:V("recently_added_albums")??"sensor.lidarr_recently_added_albums",artists_entity:V("recently_added_artists")??"sensor.lidarr_recently_added_artists",layout:"strip",...L?{player:L}:{}}}connectedCallback(){super.connectedCallback(),this.ticker=window.setInterval(()=>{this.now=Date.now()},6e4)}disconnectedCallback(){super.disconnectedCallback(),window.clearInterval(this.ticker),this.cancelHold()}shouldUpdate(C){if(!this.config)return!1;if(C.size>1||!C.has("hass"))return!0;let V=C.get("hass");if(!V||!this.hass)return!0;let{albums_entity:L,artists_entity:r,player_entity:e,player:i}=this.config;return[L,r,e,i].some(t=>t!==void 0&&V.states[t]!==this.hass.states[t])||V.entities!==this.hass.entities||V.services!==this.hass.services||V.locale!==this.hass.locale}get showArtists(){return!!(this.config?.show_artists&&this.config.artists_entity)}get language(){return this.hass?.locale?.language??this.hass?.language??navigator.language}render(){if(!this.config||!this.hass)return d;let C=this.config,V=H1(this.hass);this.albums=Z1(this.hass,C.albums_entity,C.max_items)??[],this.artists=this.showArtists?Z1(this.hass,C.artists_entity,C.max_items)??[]:[];let L=!!C.albums_entity&&this.showArtists;return v`
      <ha-card>
        ${C.title?v`<h1 class="card-header">${C.title}</h1>`:d}
        <div
          class="content ${C.title?"":"no-title"} ${V?"can-play":""}"
          @pointerdown=${this.onPointerDown}
          @pointermove=${this.onPointerMove}
          @pointerup=${this.cancelHold}
          @pointercancel=${this.cancelHold}
          @click=${this.onClick}
          @contextmenu=${this.onContextMenu}
          @keydown=${this.onKeyDown}
        >
          ${C.albums_entity?this.renderSection(C.albums_entity,L?"Albums":void 0,this.albums.length?v`<div class="albums ${C.layout}">
                      ${x1(this.albums,(r,e)=>r.musicbrainz_id??`${r.artist}|${r.album}|${e}`,(r,e)=>this.renderAlbum(r,e,V))}
                    </div>`:v`<div class="empty">No albums imported yet.</div>`):d}
          ${this.showArtists?this.renderSection(C.artists_entity,L?"Artists":void 0,this.artists.length?v`<div class="artists">
                      ${x1(this.artists,(r,e)=>r.musicbrainz_id??`${r.artist}|${e}`,(r,e)=>this.renderArtist(r,e,V))}
                    </div>`:v`<div class="empty">No artists added yet.</div>`):d}
        </div>
      </ha-card>
    `}renderSection(C,V,L){let r=this.hass.states[C],e=L;return r?r.state==="unavailable"&&(e=v`<div class="empty">Lidarr is unavailable.</div>`):e=v`<div class="warning">Entity not found: ${C}</div>`,v`
      <section>
        ${V?v`<h2 class="section-label">${V}</h2>`:d}
        ${e}
      </section>
    `}renderAlbum(C,V,L){let r=C.album??"Unknown album",e=C.artist??"",i=L?"Tap to play, hold for options":"";return v`
      <button
        class="tile album"
        data-kind="album"
        data-index=${V}
        aria-label=${[r,e&&`by ${e}`,i].filter(Boolean).join(", ")}
        aria-haspopup="menu"
      >
        <div class="cover">
          ${this.renderImage(C.cover_url,v`<svg viewBox="0 0 24 24" aria-hidden="true">
            ${E`<path d=${X1}></path>`}
          </svg>`)}
          ${L?v`<span class="play" aria-hidden="true"
                ><svg viewBox="0 0 24 24">${E`<path d=${n1}></path>`}</svg
              ></span>`:d}
        </div>
        <div class="title">${r}</div>
        ${e?v`<div class="subtitle">${e}</div>`:d}
        ${this.config.show_added&&C.added?v`<div class="added">Added ${S1(C.added,this.language,this.now)}</div>`:d}
      </button>
    `}renderArtist(C,V,L){let r=C.artist??"Unknown artist";return v`
      <button
        class="tile artist"
        data-kind="artist"
        data-index=${V}
        aria-label=${[r,L?"Tap to play, hold for options":""].filter(Boolean).join(", ")}
        aria-haspopup="menu"
      >
        <div class="avatar">
          ${this.renderImage(C.image_url,v`<span class="initials">${M2(C.artist)}</span>`)}
        </div>
        <div class="name">${r}</div>
        ${this.config.show_added&&C.added?v`<div class="added">${S1(C.added,this.language,this.now)}</div>`:d}
      </button>
    `}renderImage(C,V){return!C||this.failedImages.has(C)?v`<div class="placeholder">${V}</div>`:v`<img
      src=${C}
      alt=""
      loading="lazy"
      decoding="async"
      draggable="false"
      @error=${()=>{this.failedImages=new Set(this.failedImages).add(C)}}
    />`}targetFrom(C){let V=C.target?.closest(".tile");if(!V)return;let L=Number(V.dataset.index);if(V.dataset.kind==="album"&&this.albums[L])return{kind:"album",item:this.albums[L],element:V};if(V.dataset.kind==="artist"&&this.artists[L])return{kind:"artist",item:this.artists[L],element:V}}tap(C,V,L){if(!this.hass||!H1(this.hass)||!this.mediaName(C))return;let r=V1(this.hass,this.config);r?this.play(C,r,"replace"):this.choosePlayer(C,V,L)}mediaName(C){return(C.kind==="album"?C.item.album:C.item.artist)??void 0}openMenu(C,V,L){let r=this.hass;if(!r)return;let e=[],i=this.mediaName(C);if(H1(r)&&i){let o=V1(r,this.config),a=p=>()=>o?void this.play(C,o,p):this.choosePlayer(C,V,L,p),A=C.kind==="artist"&&this.config.artist_radio;e.push({label:A?"Start radio":"Play now",icon:A?H2:n1,secondary:o?`on ${C1(r,o)}`:void 0,action:a("replace")},{label:"Play next",icon:J1,action:a("next")},{label:"Add to queue",icon:C2,action:a("add")},{label:"Choose player\u2026",icon:l1,action:()=>this.choosePlayer(C,V,L)})}let t=C.item.lidarr_url;this.config.lidarr_link&&t&&e.push({label:"Open in Lidarr",icon:Y1,action:()=>window.open(t,"_blank","noopener")}),e.length&&(this.lastMenuAt=Date.now(),s1({heading:i??"",subheading:C.kind==="album"?C.item.artist??void 0:"Artist",entries:e,x:V,y:L,returnFocus:C.element}))}choosePlayer(C,V,L,r="replace"){let e=this.hass,i=J(e);if(!i.length){this.toast("No Music Assistant players found.");return}let t=V1(e,this.config),o=new Map(i.map(A=>[A,C1(e,A)])),a=new Map;o.forEach(A=>a.set(A,(a.get(A)??0)+1)),this.lastMenuAt=Date.now(),s1({heading:"Play on\u2026",subheading:this.mediaName(C),entries:i.map(A=>{let p=o.get(A),m=L2(e,A),x=[f2(e.states[A]?.state),m?`grouped with ${k(e,m)}`:void 0,(a.get(p)??0)>1?A:void 0].filter(Boolean).join(" \xB7 ");return{label:p,secondary:x||void 0,icon:l1,checked:A===t,action:()=>{this.play(C,A,r)}}}),x:V,y:L,returnFocus:C.element})}async play(C,V,L){let r=this.hass,e=this.mediaName(C),i=C.kind==="artist"&&this.config.artist_radio,t=C.kind==="album"?{media_id:e,media_type:"album",enqueue:L}:{media_id:e,media_type:"artist",enqueue:L};C.kind==="album"&&C.item.artist&&(t.artist=C.item.artist),i&&(t.radio_mode=!0);let o=C1(r,V);try{await r.callService(N,"play_media",t,{entity_id:V},!1);let a=i?`${e} radio`:e;this.toast(L==="next"?`${a} will play next on ${o}`:L==="add"?`Added ${a} to the queue on ${o}`:`Playing ${a} on ${o}`)}catch(a){this.toast(`Couldn't play ${e} on ${o}: ${r2(a)}`)}}toast(C){this.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:C},bubbles:!0,composed:!0}))}};_.properties={hass:{attribute:!1},config:{state:!0},now:{state:!0},failedImages:{state:!0}},_.styles=w`
    :host {
      --lra-cover-size: 132px;
      --lra-wall-min: 96px;
      --lra-avatar-size: 72px;
      --lra-radius: 10px;
      --lra-gap: 12px;
      --lra-tint: color-mix(
        in srgb,
        var(--primary-color) 16%,
        var(--card-background-color, var(--ha-card-background, #fff))
      );
    }
    ha-card {
      height: 100%;
      overflow: hidden;
    }
    .card-header {
      margin: 0;
      padding: 16px 16px 0;
      font-family: inherit;
      font-size: var(--ha-card-header-font-size, 20px);
      font-weight: var(--ha-font-weight-normal, 400);
      line-height: 1.3;
      color: var(--ha-card-header-color, var(--primary-text-color));
    }
    .content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 12px 0 16px;
    }
    .content.no-title {
      padding-top: 16px;
    }
    section {
      min-width: 0;
    }
    .section-label {
      margin: 0 16px 8px;
      font-size: 13px;
      font-weight: var(--ha-font-weight-medium, 500);
      letter-spacing: 0.02em;
      color: var(--secondary-text-color);
    }
    .empty,
    .warning {
      margin: 0 16px;
      font-size: 14px;
      color: var(--secondary-text-color);
    }
    .warning {
      color: var(--warning-color, #ff9800);
    }

    /* Rows that scroll sideways, snapping to whole items. */
    .albums.strip,
    .artists {
      display: flex;
      gap: var(--lra-gap);
      overflow-x: auto;
      overscroll-behavior-x: contain;
      scroll-snap-type: x mandatory;
      scroll-padding-inline: 16px;
      padding: 0 16px 4px;
      scrollbar-width: thin;
      scrollbar-color: var(--divider-color, rgba(127, 127, 127, 0.3)) transparent;
    }
    .albums.strip .tile {
      flex: none;
      width: var(--lra-cover-size);
    }
    .albums.wall {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(var(--lra-wall-min), 1fr));
      gap: 16px var(--lra-gap);
      padding: 0 16px;
    }

    .tile {
      display: flex;
      flex-direction: column;
      min-width: 0;
      margin: 0;
      padding: 0;
      border: 0;
      background: none;
      color: inherit;
      font: inherit;
      text-align: start;
      scroll-snap-align: start;
      -webkit-tap-highlight-color: transparent;
      -webkit-touch-callout: none;
      user-select: none;
      -webkit-user-select: none;
      touch-action: manipulation;
      cursor: default;
    }
    .can-play .tile {
      cursor: pointer;
    }
    .tile:focus-visible {
      outline: none;
    }
    .tile:focus-visible .cover,
    .tile:focus-visible .avatar {
      outline: 2px solid var(--primary-color);
      outline-offset: 2px;
    }

    .cover {
      position: relative;
      width: 100%;
      aspect-ratio: 1;
      border-radius: var(--lra-radius);
      overflow: hidden;
      background: var(--lra-tint);
      transition: transform 150ms ease-out;
    }
    .can-play .tile:active .cover,
    .can-play .tile:active .avatar {
      transform: scale(0.97);
    }
    img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      -webkit-user-drag: none;
    }
    .placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      background: var(--lra-tint);
      color: var(--primary-color);
    }
    .placeholder svg {
      width: 42%;
      height: 42%;
      fill: currentColor;
      opacity: 0.55;
    }
    .play {
      position: absolute;
      right: 8px;
      bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      opacity: 0;
      transform: translateY(4px);
      transition:
        opacity 150ms ease-out,
        transform 150ms ease-out;
      pointer-events: none;
    }
    .play svg {
      width: 22px;
      height: 22px;
      fill: currentColor;
    }
    @media (hover: hover) {
      .tile:hover .play,
      .tile:focus-visible .play {
        opacity: 1;
        transform: none;
      }
    }

    .title,
    .name {
      margin-top: 8px;
      font-size: 14px;
      font-weight: var(--ha-font-weight-medium, 500);
      line-height: 1.3;
      color: var(--primary-text-color);
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      overflow: hidden;
      overflow-wrap: anywhere;
    }
    .subtitle {
      margin-top: 2px;
      font-size: 13px;
      line-height: 1.3;
      color: var(--secondary-text-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .added {
      margin-top: 2px;
      font-size: 12px;
      line-height: 1.3;
      color: var(--secondary-text-color);
      opacity: 0.8;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .artist {
      flex: none;
      align-items: center;
      width: calc(var(--lra-avatar-size) + 16px);
      text-align: center;
    }
    .avatar {
      width: var(--lra-avatar-size);
      height: var(--lra-avatar-size);
      border-radius: 50%;
      overflow: hidden;
      background: var(--lra-tint);
      transition: transform 150ms ease-out;
    }
    .artist .name {
      font-size: 13px;
      text-align: center;
    }
    .initials {
      font-size: calc(var(--lra-avatar-size) * 0.36);
      font-weight: var(--ha-font-weight-medium, 500);
      letter-spacing: 0.02em;
      color: var(--primary-color);
    }

    @media (prefers-reduced-motion: reduce) {
      .cover,
      .avatar,
      .play {
        transition: none;
      }
    }
  `;function f2(M){if(M)return M.charAt(0).toUpperCase()+M.slice(1).replace(/_/g," ")}L1(M1,_);var c1=window;c1.customCards??=[];c1.customCards.some(M=>M.type===M1)||c1.customCards.push({type:M1,name:"Lidarr Recently Added",description:"Cover art for recently added albums and artists, with tap to play.",preview:!0,documentationURL:"https://github.com/phoenixxx-1/ha-lidarr-recently-added"});console.info("%c LIDARR-RECENTLY-ADDED-CARD %c 0.3.0 ","font-weight:600","");export{_ as LidarrRecentlyAddedCard};
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
lit-html/directive.js:
lit-html/directives/repeat.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/directive-helpers.js:
  (**
   * @license
   * Copyright 2020 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
