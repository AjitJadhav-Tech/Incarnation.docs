"""PDF date + password engine used by the desktop app."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

import pikepdf
from pikepdf import Name

IST = timezone(timedelta(hours=5, minutes=30))
PDF_DATE_IN = re.compile(
    r"^D:(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?(\d{2})?"
)


def _to_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=IST)
        return value
    text = str(value).strip()
    if not text:
        return None
    match = PDF_DATE_IN.match(text)
    if match:
        y, mo, d, h, mi, s = match.groups()
        return datetime(
            int(y),
            int(mo),
            int(d),
            int(h or 0),
            int(mi or 0),
            int(s or 0),
            tzinfo=IST,
        )
    for fmt in ("%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=IST)
        except ValueError:
            continue
    return None


def format_display(dt: Optional[datetime]) -> str:
    if not dt:
        return "—"
    return dt.strftime("%d-%m-%Y %H:%M:%S")


def format_pdf_date(dt: datetime) -> str:
    local = dt.astimezone(IST) if dt.tzinfo else dt.replace(tzinfo=IST)
    return local.strftime("D:%Y%m%d%H%M%S+05'30'")


def format_xmp_date(dt: datetime) -> str:
    local = dt.astimezone(IST) if dt.tzinfo else dt.replace(tzinfo=IST)
    return local.strftime("%Y-%m-%dT%H:%M:%S+05:30")


@dataclass
class PdfInfo:
    path: str
    pages: int
    encrypted: bool
    size_kb: float
    pdf_version: str
    creation: Optional[datetime] = None
    modification: Optional[datetime] = None
    title: str = ""
    author: str = ""
    producer: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class ProcessOptions:
    input_path: str
    output_path: str
    open_password: str = ""
    new_password: str = ""
    lock: bool = True
    creation: Optional[datetime] = None
    modification: Optional[datetime] = None
    compress: bool = True
    wipe_other_metadata: bool = True
    strip_producer: bool = True
    blank_modified: bool = True


def inspect_pdf(path: str, password: str = "") -> PdfInfo:
    kwargs = {}
    if password:
        kwargs["password"] = password
    try:
        pdf_ctx = pikepdf.open(path, **kwargs)
    except pikepdf.PasswordError as exc:
        raise pikepdf.PasswordError(
            "This PDF is locked. Enter the current password and click Inspect."
        ) from exc
    with pdf_ctx as pdf:
        info = PdfInfo(
            path=path,
            pages=len(pdf.pages),
            encrypted=bool(pdf.is_encrypted),
            size_kb=os.path.getsize(path) / 1024,
            pdf_version=str(pdf.pdf_version),
        )
        doc = pdf.docinfo
        info.creation = _to_datetime(doc.get("/CreationDate"))
        info.modification = _to_datetime(doc.get("/ModDate"))
        info.title = str(doc.get("/Title") or "")
        info.author = str(doc.get("/Author") or "")
        info.producer = str(doc.get("/Producer") or "")
        extra = {}
        for key in doc.keys():
            extra[str(key)] = str(doc.get(key))
        info.extra = extra
        return info


def _clear_docinfo(pdf: pikepdf.Pdf) -> None:
    for key in list(pdf.docinfo.keys()):
        del pdf.docinfo[key]


def _clear_xmp(pdf: pikepdf.Pdf) -> None:
    with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
        for key in list(meta.keys()):
            try:
                del meta[key]
            except Exception:
                pass


def _drop_mod_keys(pdf: pikepdf.Pdf) -> None:
    for key in list(pdf.docinfo.keys()):
        if str(key) in ("/ModDate", "/ModificationDate"):
            del pdf.docinfo[key]


def _apply_dates(
    pdf: pikepdf.Pdf,
    created: datetime,
    modified: Optional[datetime],
    wipe: bool,
    blank_modified: bool,
) -> None:
    if wipe:
        _clear_docinfo(pdf)
        _clear_xmp(pdf)

    # This pikepdf build cannot encode datetime objects into docinfo.
    pdf.docinfo[Name.CreationDate] = format_pdf_date(created)
    if blank_modified:
        _drop_mod_keys(pdf)
    elif modified:
        pdf.docinfo[Name.ModDate] = format_pdf_date(modified)

    with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
        meta["xmp:CreateDate"] = format_xmp_date(created)
        if blank_modified:
            for key in (
                "xmp:ModifyDate",
                "xmp:MetadataDate",
                "xmpMM:ModifyDate",
                "pdf:ModDate",
            ):
                if key in meta:
                    try:
                        del meta[key]
                    except Exception:
                        pass
        elif modified:
            meta["xmp:ModifyDate"] = format_xmp_date(modified)
            meta["xmp:MetadataDate"] = format_xmp_date(modified)
        if wipe:
            for key in (
                "pdf:Producer",
                "xmp:CreatorTool",
                "dc:creator",
                "dc:title",
                "pdf:Keywords",
            ):
                if key in meta:
                    try:
                        del meta[key]
                    except Exception:
                        pass


def _patch_info_bytes(path: str, strip_producer: bool, blank_modified: bool) -> None:
    with open(path, "rb") as fh:
        data = fh.read()
    patched = data
    if strip_producer:
        patched = re.sub(rb"/Producer\s*\([^)]*\)", b"", patched)
        patched = re.sub(rb"/Producer\s*<[0-9a-fA-F\s]*>", b"", patched)
    if blank_modified:
        patched = re.sub(rb"/ModDate\s*\([^)]*\)", b"", patched)
        patched = re.sub(rb"/ModDate\s*<[0-9a-fA-F\s]*>", b"", patched)
        patched = re.sub(rb"/ModDate\s*/", b"/", patched)
        patched = re.sub(rb"<xmp:ModifyDate>[^<]*</xmp:ModifyDate>", b"", patched)
        patched = re.sub(rb"<xmp:MetadataDate>[^<]*</xmp:MetadataDate>", b"", patched)
        patched = re.sub(rb"<pdfx:ModDate>[^<]*</pdfx:ModDate>", b"", patched)
    if patched != data:
        with open(path, "wb") as fh:
            fh.write(patched)


def process_pdf(options: ProcessOptions) -> dict:
    if not os.path.isfile(options.input_path):
        raise FileNotFoundError(options.input_path)
    if not options.creation:
        raise ValueError("Creation date is required.")
    if not options.blank_modified and not options.modification:
        raise ValueError("Modification date is required, or enable blank Modified.")

    out_dir = os.path.dirname(os.path.abspath(options.output_path))
    os.makedirs(out_dir, exist_ok=True)

    open_kwargs = {}
    if options.open_password:
        open_kwargs["password"] = options.open_password

    temps = []

    def _temp() -> str:
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        temps.append(path)
        return path

    try:
        mid = _temp()
        try:
            pdf_in = pikepdf.open(options.input_path, **open_kwargs)
        except pikepdf.PasswordError as exc:
            raise pikepdf.PasswordError(
                "Could not open the source PDF. Check the open password."
            ) from exc
        with pdf_in as pdf:
            _apply_dates(
                pdf,
                options.creation,
                options.modification,
                options.wipe_other_metadata,
                options.blank_modified,
            )
            save_kwargs = {"object_stream_mode": pikepdf.ObjectStreamMode.disable}
            if options.compress:
                save_kwargs.update(
                    compress_streams=True,
                    recompress_flate=True,
                    normalize_content=True,
                )
            pdf.save(mid, **save_kwargs)

        final = _temp()
        with pikepdf.open(mid) as pdf:
            _apply_dates(
                pdf,
                options.creation,
                options.modification,
                wipe=False,
                blank_modified=options.blank_modified,
            )
            save_kwargs = {"object_stream_mode": pikepdf.ObjectStreamMode.disable}
            if options.lock and options.new_password:
                save_kwargs["encryption"] = pikepdf.Encryption(
                    user=options.new_password,
                    owner=options.new_password,
                    R=4,
                )
            pdf.save(final, **save_kwargs)

        if options.strip_producer or options.blank_modified:
            _patch_info_bytes(final, options.strip_producer, options.blank_modified)

        os.replace(final, options.output_path)
        temps.remove(final)
    finally:
        for path in temps:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    return {
        "output": options.output_path,
        "size_kb": os.path.getsize(options.output_path) / 1024,
        "creation": format_display(options.creation),
        "modification": "blank" if options.blank_modified else format_display(options.modification),
        "locked": bool(options.lock and options.new_password),
    }
