// $(function() {
//     $(".cuadrado-container").on("mouseover", function() {
//         $(this).slideUp();  // Desvanecer lentamente
//     });

//     $(".cuadrado-container").on("mouseout", function() {
//         $(this).slideDown();  // Aparecer lentamente
//     });
// });


// gsap.from(".cuadrado-container", {
//     duration: 2.5,
//     opacity: 0,
//     y: -50,
//     ease: "elastic.out(1, 0.3)"
//   });



gsap.to(".img-x", {
  duration: 2,  // Duración de la animación en segundos
  x: "100%",   // Mueve el elemento a lo largo del eje X al 100% de su ancho
  ease: "elastic.out" // Tipo de suavizado para la animación
});
  