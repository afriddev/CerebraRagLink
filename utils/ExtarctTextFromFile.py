import fitz
from typing import Any, Dict, List, Tuple, Optional


def extractTextWithMetadata(
    pdfPath: str,
) -> Tuple[str, Dict[str, Dict[str, Any]]]:
    doc: Any = fitz.open(pdfPath)
    imageMap: Dict[str, Dict[str, Any]] = {}
    imageCounter: int = 1
    finalText: List[str] = []

    for pageNum, page in enumerate(doc, start=1):
        blocks: List[Dict[str, Any]] = page.get_text("dict")["blocks"]

        pageItems: List[Tuple[str, float, str]] = []
        for block in blocks:
            if block["type"] == 0:
                for line in block.get("lines", []):
                    y0: float = line["bbox"][1]
                    lineText: str = " ".join(
                        span.get("text", "")
                        for span in line.get("spans", [])
                        if "text" in span
                    ).strip()
                    if lineText:
                        pageItems.append(("text", y0, lineText))
            elif block["type"] == 1:
                y0: float = block["bbox"][1]
                placeholder: str = f"<<IMAGE-{imageCounter}>>"

                xref: Optional[int] = block.get("number")
                baseImage: Optional[Dict[str, Any]] = None
                if xref:
                    try:
                        baseImage = doc.extract_image(xref)
                    except Exception:
                        baseImage = None

                imageMap[placeholder] = {
                    "page": pageNum,
                    "bbox": block["bbox"],
                    "ext": baseImage["ext"] if baseImage else None,
                    "imageBytes": baseImage["image"] if baseImage else None,
                }

                pageItems.append(("image", y0, placeholder))
                imageCounter += 1

        pageItems.sort(key=lambda x: x[1])

        for itemType, _, content in pageItems:
            if itemType == "text":
                finalText.append(content)
            else:
                finalText.append(f"\n{content}\n")

    return "\n".join(finalText), imageMap


def ExtractTextFromDoc(file: str) -> str:
    textWithImages,images = extractTextWithMetadata(file)
    
    return textWithImages

