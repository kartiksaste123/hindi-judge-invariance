import re, pathlib, shutil, zipfile, pypandoc
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parents[1]
M = ROOT / "results" / "metrics"; F = ROOT / "results" / "figures"
R = ROOT / "results" / "report"; R.mkdir(exist_ok=True)
E = ROOT / "build" / "export"; shutil.rmtree(E, ignore_errors=True); (E / "images_png").mkdir(parents=True); (E / "images_jpeg").mkdir()
h = (ROOT / "build" / "report.html").read_text()
h = re.sub(r"<script.*?</script>", "", h, flags=re.S)
import html as H
def mml(tex, disp):
    t = H.unescape(tex).replace(r"\mathbb{1}", r"\mathbf{1}")
    out = pypandoc.convert_text(("$$%s$$" if disp else "$%s$") % t, "html", format="markdown", extra_args=["--mathml"])
    return re.search(r"<math.*?</math>", out, re.S).group(0)
h = re.sub(r"\\\[(.+?)\\\]", lambda m: mml(m.group(1), True), h, flags=re.S)
h = re.sub(r"\\\((.+?)\\\)", lambda m: mml(m.group(1), False), h, flags=re.S)
pypandoc.convert_text(h, "docx", format="html", outputfile=str(R / "results_report.docx"))
for p in sorted(F.glob("fig*.png")):
    shutil.copy(p, E / "images_png" / p.name)
    Image.open(p).convert("RGB").save(E / "images_jpeg" / (p.stem + ".jpg"), quality=95)
shutil.copy(R / "results_report.pdf", E); shutil.copy(M / "metrics_main.csv", E)
z = ROOT / "build" / "Step4_Results_Package.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in sorted(E.rglob("*")):
        if f.is_file(): zf.write(f, "Step4_Results/" + str(f.relative_to(E)))
print(z, z.stat().st_size)
