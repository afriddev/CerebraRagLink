import base64
import fitz
from typing import Any, List, Tuple, Optional

def ExtractTextAndImagesFromDoc(pdfPath: str) -> Tuple[str, List[str]]:
    doc: Any = fitz.open(pdfPath)
    imagesB64: List[str] = []
    imageCounter: int = 1
    finalTextParts: List[str] = []

    for _, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        pageItems: List[Tuple[str, float, str]] = []

        for block in blocks:
            if block["type"] == 0:
                for line in block.get("lines", []):
                    y0 = line["bbox"][1]
                    lineText = " ".join(
                        span.get("text", "")
                        for span in line.get("spans", [])
                        if "text" in span
                    ).strip()
                    if lineText:
                        pageItems.append(("text", y0, lineText))
            elif block["type"] == 1:
                y0 = block["bbox"][1]
                imgId = f"image-{imageCounter}"
                placeholder = f"<<{imgId}>>"

                xref: Optional[int] = block.get("image") or block.get("number")
                baseImage = None
                if isinstance(xref, int) and xref > 0:
                    try:
                        baseImage = doc.extract_image(xref)
                    except Exception:
                        baseImage = None

                if baseImage and baseImage.get("image"):
                    data = baseImage["image"]
                else:
                    try:
                        rect = fitz.Rect(block["bbox"])
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect, alpha=False)
                        data = pix.tobytes("png")
                    except Exception:
                        data = b""

                b64Str = base64.b64encode(data).decode("utf-8") if data else ""
                imagesB64.append(b64Str)
                pageItems.append(("image", y0, placeholder))
                imageCounter += 1

        pageItems.sort(key=lambda x: x[1])
        for itemType, _, content in pageItems:
            if itemType == "text":
                finalTextParts.append(content)
            else:
                finalTextParts.append(f"\n{content}\n")

    return "\n".join(finalTextParts), imagesB64


def ExtractTextFromDoc_Rag(file: str) -> Tuple[str, List[str]]:
    textWithImages, imagesB64 = ExtractTextAndImagesFromDoc(file)
    return textWithImages, imagesB64
