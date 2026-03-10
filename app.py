"""Gradio UI for PDF to multiple formats converter."""

from pathlib import Path

import gradio as gr

from converters import (
    convert_to_docx,
    convert_to_html,
    convert_to_images,
    convert_to_markdown,
    convert_to_svg,
    convert_to_text,
)

FORMAT_CHOICES = [
    "Text (.txt)",
    "Images (PNG)",
    "Images (JPEG)",
    "DOCX",
    "Markdown",
    "SVG",
    "HTML",
]


def convert(
    uploaded_file: str | gr.File | None,
    format_choice: str,
    dpi: int,
) -> tuple[str | None, str]:
    """Run the selected conversion and return (output path, status message)."""
    path_str = (
        uploaded_file
        if isinstance(uploaded_file, str)
        else (getattr(uploaded_file, "name", None) if uploaded_file else None)
    )
    if not path_str:
        return None, "Please select a PDF file."

    pdf_path = Path(path_str)
    if not pdf_path.suffix.lower() == ".pdf":
        return None, "Please select a valid PDF file."

    try:
        if format_choice == "Text (.txt)":
            out_path = convert_to_text(pdf_path)
            msg = "Conversion completed. Download your file below."
        elif format_choice == "Images (PNG)":
            out_path = convert_to_images(pdf_path, dpi=dpi, image_fmt="png")
            msg = "Conversion completed. Download the ZIP of page images below."
        elif format_choice == "Images (JPEG)":
            out_path = convert_to_images(pdf_path, dpi=dpi, image_fmt="jpg")
            msg = "Conversion completed. Download the ZIP of page images below."
        elif format_choice == "DOCX":
            out_path = convert_to_docx(pdf_path)
            msg = "Conversion completed. Download your file below."
        elif format_choice == "Markdown":
            out_path = convert_to_markdown(pdf_path)
            msg = "Conversion completed. Download your file below."
        elif format_choice == "SVG":
            out_path = convert_to_svg(pdf_path)
            msg = "Conversion completed. Download the ZIP of SVG pages below."
        elif format_choice == "HTML":
            out_path = convert_to_html(pdf_path)
            msg = "Conversion completed. Download your file below."
        else:
            return None, "Please select an output format."

        return str(out_path), msg
    except (ValueError, RuntimeError) as e:
        return None, f"Could not open the file. Make sure it is a valid PDF. ({e!s})"
    except OSError as e:
        return None, "Could not write the output. Try again or free some disk space."
    except Exception as e:
        return None, f"Conversion failed: {e!s}"


def build_ui() -> gr.Blocks:
    theme = gr.themes.Soft(
        primary_hue="slate",
        secondary_hue="blue",
    ).set(
        body_background_fill="*neutral_50",
        block_background_fill="*neutral_0",
    )

    with gr.Blocks(theme=theme, title="PDF Converter", css="footer {visibility: hidden}") as demo:
        gr.Markdown(
            """
            # PDF to Multiple Formats
            Convert a PDF to text, images, DOCX, Markdown, SVG, or HTML. Upload a file, choose a format, and download.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                file_in = gr.File(
                    file_types=[".pdf"],
                    label="Choose PDF",
                    type="filepath",
                )
                format_radio = gr.Radio(
                    FORMAT_CHOICES,
                    value="Text (.txt)",
                    label="Output format",
                )
                dpi_slider = gr.Slider(
                    minimum=72,
                    maximum=300,
                    value=150,
                    step=1,
                    label="Resolution (DPI) — for Images only",
                )
                convert_btn = gr.Button("Convert", variant="primary")

            with gr.Column(scale=1):
                file_out = gr.File(label="Download result")
                status = gr.Markdown(value="Upload a PDF and click Convert.")

        gr.Markdown(
            "*For PDFs with many pages, image or SVG conversion may take a moment.*",
            elem_classes=["small"],
        )

        def on_convert(uploaded_file, format_choice, dpi):
            path, message = convert(uploaded_file, format_choice, int(dpi))
            return path, message

        convert_btn.click(
            fn=on_convert,
            inputs=[file_in, format_radio, dpi_slider],
            outputs=[file_out, status],
        )

        def on_file_change(files):
            if files and getattr(files, "name", None):
                return gr.update(interactive=True)
            return gr.update(interactive=False)

        def enable_convert(x):
            if x is None:
                return gr.update(interactive=False)
            path = x if isinstance(x, str) else getattr(x, "name", None)
            return gr.update(interactive=bool(path))

        file_in.change(
            fn=enable_convert,
            inputs=[file_in],
            outputs=[convert_btn],
        )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.launch()