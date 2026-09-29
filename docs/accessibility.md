# Accessibility

The semantic shortcode is the safest authored representation because the source
text remains readable if the font is missing. Direct PUA characters are not
official Unicode names and must never be exposed without a label.

```html
<span class="bones" role="img" aria-label="Femur">:femur:</span>
<span class="bones-emoji" role="img" aria-label="Left kidney">&#xE01C;</span>
```

Do not rely on the visual color palette to distinguish structures. The
monochrome font, SVG assets, and accessible label all carry the meaning.

