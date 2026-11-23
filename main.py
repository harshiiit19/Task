"""Compounding Quest - a gamified explainer of compounding (FastAPI)."""
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Compounding Quest", description="Gamified compounding explainer")
BASE_DIR = Path(__file__).resolve().parent
# app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

PROFILES = [
    {
        "id": "young", "name": "Time Travellers", "ages": "Ages 18-30", "emoji": "🚀",
        "story": "You have time on your side. Change the sliders to see how saving earlier could affect your future total.",
        "goal": 10000000, "goal_text": "Save ₹1 crore",
        "defaults": {"principal": 0, "monthly": 5000, "rate": 10, "years": 25, "fee": 0},
        "tip": "Starting earlier gives your money more time to grow.",
    },
    {
        "id": "mid", "name": "Builders", "ages": "Ages 31-50", "emoji": "🏗️",
        "story": "You may be balancing loan payments, family costs, and savings. Try changing the fee to see how costs can affect your total.",
        "goal": 20000000, "goal_text": "Save ₹2 crore",
        "defaults": {"principal": 500000, "monthly": 20000, "rate": 10, "years": 20, "fee": 1},
        "tip": "When you can, increase your savings as your income grows. Keep an eye on fees.",
    },
    {
        "id": "senior", "name": "Final Stretch", "ages": "Ages 51+", "emoji": "🏔️",
        "story": "With fewer years to save, your starting amount, monthly savings, and costs all matter. Adjust them to explore different outcomes.",
        "goal": 12500000, "goal_text": "Save ₹1.25 crore for retirement",
        "defaults": {"principal": 2500000, "monthly": 30000, "rate": 8, "years": 10, "fee": 0.5},
        "tip": "You can still build savings. Contributing more and keeping fees low may help.",
    },
]

MYTHS = [
    ("Compounding makes money grow fast right away.",
     "Growth can feel slow at first. Given more time, returns may also earn returns and help the total grow faster."),
    ("I need a lot of money to start saving.",
     "You can begin with a small amount. Saving regularly can add up over time."),
    ("Investment returns are guaranteed.",
     "They are not. The rates in this tool are examples; real investment values can rise or fall."),
    ("If I start late, there is no point saving.",
     "Starting earlier gives money more time to grow, but saving later can still help you reach your goals."),
    ("Compounding only affects investments.",
     "Loan interest can also build up over time. If you do not repay it, you may owe more."),
    ("A 1% yearly fee is too small to matter.",
     "Fees can add up over many years and leave you with less money. Try changing the fee in the calculator."),
]

BENEFITS = [
    ("More time to grow", "Money has more time to earn returns when you start saving earlier."),
    ("Small savings add up", "Regular contributions can build into a larger total over time."),
    ("A steady habit helps", "Saving regularly can help you stay focused on your goals."),
    ("Think about rising prices", "Prices often go up over time, so consider how that may affect what your savings can buy."),
    ("Make a plan that fits", "Your savings plan can change as your goals and circumstances change."),
]

QUIZ = [
    {"q": "What does compounding mean?", "o": ["Earning returns only on your original savings",
     "Earning returns on your savings and on earlier returns", "Paying a fee every year", "Saving the same amount each month"], "a": 1},
    {"q": "Using the Rule of 72, about how long could it take money to double at 8% a year?", "o": ["6 years", "9 years", "12 years", "72 years"], "a": 1},
    {"q": "What can give savings more time to grow?", "o": ["Starting earlier", "Checking the balance every day",
     "Changing investments often", "Waiting until you have a large amount"], "a": 0},
    {"q": "If interest is added to a loan and you do not repay it, what can happen?", "o": ["The amount stays the same",
     "The amount gets smaller", "The amount you owe can grow", "Interest stops"], "a": 2},
    {"q": "Ria starts saving at 25. Sam saves the same amount each month but starts at 35. Who has more time for their savings to grow?", "o": ["Sam",
     "Ria", "They have the same amount of time", "It depends only on luck"], "a": 1},
]


def project(principal: float, monthly: float, rate: float, years: int, fee: float = 0.0) -> dict:
    """Month-by-month growth. Returns yearly series for compound, simple, and contributed."""
    r = max(rate - fee, 0) / 100 / 12
    bal, contributed, simple_interest = principal, principal, 0.0
    out = {"year": [0], "compound": [round(principal, 2)], "simple": [round(principal, 2)],
           "contributed": [round(principal, 2)]}
    for y in range(1, years + 1):
        # simple interest: interest is earned on money put in, but never reinvested
        simple_interest += (rate - fee) / 100 * max(contributed + monthly * 6, 0)
        for _ in range(12):
            bal = bal * (1 + r) + monthly
            contributed += monthly
        out["year"].append(y)
        out["compound"].append(round(bal, 2))
        out["contributed"].append(round(contributed, 2))
        out["simple"].append(round(contributed + simple_interest, 2))
    out["final"] = out["compound"][-1]
    return out


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"api_urls": {
            "projection": str(request.url_for("projection")),
            "profiles": str(request.url_for("profiles")),
            "content": str(request.url_for("content")),
        }},
    )


@app.get("/api/profiles")
async def profiles():
    return PROFILES


@app.get("/api/content")
async def content():
    return {"myths": MYTHS, "benefits": BENEFITS, "quiz": QUIZ}


@app.get("/api/projection")
async def projection(
    principal: float = Query(0, ge=0, le=100_000_000),
    monthly: float = Query(0, ge=0, le=10_000_000),
    rate: float = Query(8, ge=0, le=30),
    years: int = Query(10, ge=0, le=60),
    fee: float = Query(0, ge=0, le=10),
):
    return project(principal, monthly, rate, years, fee)
