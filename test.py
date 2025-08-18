import fitz  # PyMuPDF


def extract_text_with_inline_images(pdf_path):
    doc = fitz.open(pdf_path)
    image_map = {}
    image_counter = 1
    final_text = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]

        # Collect items with positions
        page_items = []
        for block in blocks:
            if block["type"] == 0:  # text block
                for line in block.get("lines", []):
                    y0 = line["bbox"][1]  # top y of line
                    line_text = " ".join(
                        span.get("text", "")
                        for span in line.get("spans", [])
                        if "text" in span
                    ).strip()
                    if line_text:
                        page_items.append(("text", y0, line_text))

            elif block["type"] == 1:  # image block
                y0 = block["bbox"][1]  # top y of image
                placeholder = f"<<IMAGE-{image_counter}>>"

                # try extracting image
                xref = block.get("number")
                base_image = None
                if xref:
                    try:
                        base_image = doc.extract_image(xref)
                    except Exception:
                        base_image = None

                image_map[placeholder] = {
                    "page": page_num,
                    "bbox": block["bbox"],
                    "ext": base_image["ext"] if base_image else None,
                    "image_bytes": base_image["image"] if base_image else None,
                }

                page_items.append(("image", y0, placeholder))
                image_counter += 1

        # Sort by vertical position (y0)
        page_items.sort(key=lambda x: x[1])

        # Append to final text
        for item_type, _, content in page_items:
            if item_type == "text":
                final_text.append(content)
            else:
                final_text.append(f"\n{content}\n")

        final_text.append(f"\n--- End of Page {page_num} ---\n")

    return "\n".join(final_text), image_map


# Example usage
if __name__ == "__main__":
    text_with_images, image_map = extract_text_with_inline_images("OPD_Doctor_desk_User_Manual[1].pdf")

    print(text_with_images)   # Preview first portion
    print(list(image_map.keys()))
