from dataclasses import dataclass
from typing import Literal

type HAlign = Literal["left", "center", "right", "fill", "justify", "center_across", "distributed"]
type VAlign = Literal["top", "vcenter", "center", "bottom", "justify", "distributed"]

@dataclass(kw_only=True)
class ExcelOptions:
    aline: HAlign | None = None
    vAlign: VAlign | None = None
    fontName: str | None = None
    fontSize: float | int | None = None
    bold: bool | None = None
    italic: bool | None = None
    fontColor: str | None = None   # Color name or HEX -> "red", "#FF0000"
    underline: bool | None = None
    bgColor: str | None = None
    border: int | None = None
    rotation: int | None = None
    textWrap: bool | None = None
    shrink: bool | None = None
    numberFormat: str | None = None

    def toXlsWriter(self) -> dict:
        options = {}
        if self.fontName:
            options["font_name"] = self.fontName

        if self.fontSize:
            options["font_size"] = self.fontSize

        if self.bold is not None:
            options["bold"] = self.bold

        if self.italic is not None:
            options["italic"] = self.italic

        if self.fontColor:
            options["font_color"] = self.fontColor

        if self.underline:
            options["underline"] = 1

        if self.bgColor:
            options["bg_color"] = self.bgColor

        if self.border is not None:
            options["border"] = self.border

        if self.aline:
            options["align"] = self.aline

        if self.vAlign:
            options["valign"] = self.vAlign

        if self.rotation:
            options["rotation"] = self.rotation

        if self.shrink is not None:
            options["shrink"] = self.shrink

        if self.numberFormat:
            options["num_format"] = self.numberFormat

        if self.textWrap is not None:
            options["text_wrap"] = self.textWrap
        return options
