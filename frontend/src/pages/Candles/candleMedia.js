import hero from "../../assets/candles/velas-hero.jpg";
import manifesto from "../../assets/candles/velas-manifiesto.jpg";
import room from "../../assets/candles/velas-ambiente.jpg";
import gift from "../../assets/candles/velas-regalo.jpg";
import forma from "../../assets/candles/vela-marea.jpg";
import nube from "../../assets/candles/vela-orbe.jpg";
import aurea from "../../assets/candles/vela-espiral.jpg";
import ritual from "../../assets/candles/vela-ambar.jpg";
import seasonal from "../../assets/candles/velas-regalo.jpg";
import pet from "../../assets/candles/cat-mascota.jpg";
import sculptural from "../../assets/candles/cat-escultoricas.jpg";
import organic from "../../assets/candles/cat-organicas.jpg";
import decorative from "../../assets/candles/cat-decorativas.jpg";
import aromatic from "../../assets/candles/cat-aromaticas.jpg";

export const candleImages = { hero, manifesto, room, gift };

// Piezas de demostración. No existen en el catálogo ni se envían al carrito.
// El catálogo real se lee con GET /perfumes/?kind=candle (listPerfumePage).
// Ese endpoint no tiene filtro de estilo. Los estilos solo recortan esta lista.
export const DEMO_CANDLES = [
  { id: "forma-i", style: "sculptural", name: "Forma I", price: "48 USD", image: forma },
  { id: "nube", style: "organic", name: "Nube", price: "52 USD", image: nube },
  { id: "aurea", style: "decorative", name: "Áurea", price: "45 USD", image: aurea },
  { id: "ritual", style: "aromatic", name: "Ritual", price: "50 USD", image: ritual },
];

export const CANDLE_STYLES = [
  { id: "seasonal", image: seasonal },
  { id: "pet", image: pet },
  { id: "sculptural", image: sculptural },
  { id: "organic", image: organic },
  { id: "decorative", image: decorative },
  { id: "aromatic", image: aromatic },
];

export const CANDLE_ROOMS = [
  { id: "bedroom", style: "aromatic" },
  { id: "living", style: "decorative" },
  { id: "spa", style: "organic" },
];
