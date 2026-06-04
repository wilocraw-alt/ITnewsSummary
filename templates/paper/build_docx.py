#!/usr/bin/env python3
"""main.tex -> main.docx (pandoc). pandoc<2.11은 citeproc 내장이 없어,
latexmk가 만든 main.bbl을 인라인하고 \\cite{key}를 [n]으로 치환해
본문 인용 표시와 참고문헌 목록이 Word에도 렌더되도록 한다.
사용: python3 build_docx.py  (paper/ 디렉터리에서, 먼저 `make pdf`로 main.bbl 생성)
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

if not os.path.exists("main.bbl"):
    sys.exit("main.bbl 없음 — 먼저 `make pdf`로 참고문헌을 생성하세요.")

src = open("main.tex", encoding="utf-8").read()
bbl = open("main.bbl", encoding="utf-8").read()

# \input{path}/\include{path}를 파일 내용으로 펼친다(섹션 안의 \cite까지 치환 대상에 포함).
def expand_inputs(text):
    def repl(m):
        p = m.group(1).strip()
        if not os.path.splitext(p)[1]:
            p += ".tex"
        return open(p, encoding="utf-8").read() if os.path.exists(p) else m.group(0)
    for _ in range(6):  # 중첩 \input 대비 반복
        new = re.sub(r"\\(?:input|include)\{([^}]*)\}", repl, text)
        if new == text:
            break
        text = new
    return text

src = expand_inputs(src)

# bbl의 \bibitem 순서에서 key -> 번호 매핑 (thebibliography 번호 규칙과 동일)
keys = re.findall(r"\\bibitem\{([^}]*)\}", bbl)
num = {k: str(i + 1) for i, k in enumerate(keys)}

# 본문 \cite{a,b} -> [1, 2]
def repl_cite(m):
    cited = [c.strip() for c in m.group(1).split(",")]
    nums = [num.get(c, "?") for c in cited]
    return "[" + ", ".join(nums) + "]"

src = re.sub(r"\\cite\{([^}]*)\}", repl_cite, src)

# \includegraphics{figures/foo} (확장자 없음) → .png 명시: pandoc이 docx에 래스터 임베드.
src = re.sub(
    r"(\\includegraphics(?:\[[^\]]*\])?\{figures/[^}.]+)\}",
    r"\1.png}",
    src,
)
# \bibliographystyle 제거, \bibliography{...} -> bbl 인라인
src = re.sub(r"\\bibliographystyle\{[^}]*\}\s*", "", src)
# bbl에 \newblock 등 역슬래시가 있어 치환문자열로 쓰면 escape 오류 → 람다로 그대로 삽입
src = re.sub(r"\\bibliography\{[^}]*\}", lambda m: bbl, src)

tmp = ".main_docx.tex"
open(tmp, "w", encoding="utf-8").write(src)
try:
    subprocess.run(
        ["pandoc", tmp, "--resource-path=.:sections", "-o", "main.docx"],
        check=True,
    )
    print("main.docx 생성 완료 (인용", len(keys), "건 인라인).")
finally:
    if os.path.exists(tmp):
        os.remove(tmp)
