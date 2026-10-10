import re, pathlib, shutil, zipfile, pypandoc
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]; O = ROOT / "results" / "step5"
E = O / "export"; shutil.rmtree(E, ignore_errors=True); (E / "images_png").mkdir(parents=True); (E / "images_jpeg").mkdir()
h = (O / "report.html").read_text()
h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
import html as H
def mml(tex, disp):
    t = H.unescape(tex).replace(r"\mathbb{1}", r"\mathbf{1}")
    out = pypandoc.convert_text(("$$%s$$" if disp else "$%s$") % t, "html", format="markdown", extra_args=["--mathml"])
    return re.search(r"<math.*?</math>", out, re.S).group(0)
h = re.sub(r"\\\[(.+?)\\\]", lambda m: mml(m.group(1), True), h, flags=re.S)
h = re.sub(r"\\\((.+?)\\\)", lambda m: mml(m.group(1), False), h, flags=re.S)
pypandoc.convert_text(h, "docx", format="html", outputfile=str(E / "Step4_Results_Report.docx"))
for p in sorted(O.glob("fig*.png")):
    shutil.copy(p, E / "images_png" / p.name)
    Image.open(p).convert("RGB").save(E / "images_jpeg" / (p.stem + ".jpg"), quality=95)
shutil.copy(O / "Step4_Results_Report.pdf", E); shutil.copy(O / "metrics_main.csv", E)
z = O / "Step4_Results_Package.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(E.rglob("*")):
        if f.is_file(): zf.write(f, "Step4_Results/" + str(f.relative_to(E)))
print(z, z.stat().st_size)
