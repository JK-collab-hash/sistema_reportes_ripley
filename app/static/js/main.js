let contadorProductos = 1;

function agregarProducto() {
    contadorProductos++;
    const contenedor = document.getElementById("productos-container");
    if (!contenedor) return;

    const primero = contenedor.querySelector(".product-box");
    const nuevo = primero.cloneNode(true);
    nuevo.querySelector("strong").textContent = `Producto ${contadorProductos}`;
    nuevo.querySelectorAll("input").forEach(input => input.value = "");
    nuevo.querySelectorAll("select").forEach(select => select.selectedIndex = 0);
    contenedor.appendChild(nuevo);
}
