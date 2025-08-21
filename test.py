


if __name__ == "__main__":
    textWithImages, imageMap = extractTextWithMetadata(
        "OPD_Doctor_desk_User_Manual.pdf"
    )
    print(textWithImages)
    print(list(imageMap.keys()))
