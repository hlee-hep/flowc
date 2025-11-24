def markdown_to_rich_text(md: str):
    """
    Super-minimal Markdown → Notion rich_text converter.
    Supports:
      - **bold**
      - *italic*
      - `code`
      - bullet list (- item → • item)
    """

    def inline_parse(text: str):
        tokens = []
        i = 0
        n = len(text)
        buf = []

        def flush_plain():
            if buf:
                tokens.append({"text": {"content": "".join(buf)}})
                buf.clear()

        while i < n:
            ch = text[i]

            # inline code: `code`
            if ch == "`":
                end = text.find("`", i + 1)
                if end != -1:
                    flush_plain()
                    content = text[i + 1:end]
                    tokens.append({
                        "text": {"content": content},
                        "annotations": {"code": True}
                    })
                    i = end + 1
                    continue

            # bold: **text**
            if text.startswith("**", i):
                end = text.find("**", i + 2)
                if end != -1:
                    flush_plain()
                    content = text[i + 2:end]
                    tokens.append({
                        "text": {"content": content},
                        "annotations": {"bold": True}
                    })
                    i = end + 2
                    continue

            # italic *text*
            if ch == "*":
                end = text.find("*", i + 1)
                if end != -1:
                    flush_plain()
                    content = text[i + 1:end]
                    tokens.append({
                        "text": {"content": content},
                        "annotations": {"italic": True}
                    })
                    i = end + 1
                    continue

            # plain char
            buf.append(ch)
            i += 1

        flush_plain()
        return tokens

    # ------------------------
    # block-level parsing (bullet list)
    # ------------------------
    lines = md.split("\n")
    output = []

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # bullet: "- text" → "• text"
        if stripped.startswith("- "):
            bullet_text = "• " + stripped[2:]
            output.extend(inline_parse(bullet_text))
        else:
            output.extend(inline_parse(line))

        # add newline unless it's the last line
        if idx != len(lines) - 1:
            output.append({"text": {"content": "\n"}})

    if not output:
        output = [{"text": {"content": ""}}]

    return output
