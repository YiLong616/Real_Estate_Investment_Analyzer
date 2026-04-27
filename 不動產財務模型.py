import streamlit as st
import numpy_financial as npf
import pandas as pd 

st.set_page_config(
    page_title = "不動產財務計算機",
    layout = "centered"
)

st.title("不動產財務計算機")
st.caption("參考與應用《張金鶚的房產七堂課》的量化模型")
with st.expander("點此查看：計算機使用說明與指標判斷依據", expanded=False):
    st.markdown("""
    ### 系統作用與使用方法
    本計算機基於《張金鶚的房產七堂課》之理論，結合傳統財務分析與現代現金流折現模型。幫助購屋者在買房前，同時做好**檢測負擔能力**與**評估投資效益**。
    
    * **使用步驟：**
        1. 於左側邊欄輸入您心儀物件的「房屋與市場參數」。
        2. 接著輸入您的「貸款與個人財務參數」。
        3. 主畫面將自動即時為您試算結果，並給出紅黃綠燈的具體建議。
        4. 觀察最下方的「利率敏感度折線圖」，評估未來若央行升降息對您財務的影響。

    ---

    ### 核心財務指標計算方式
    * **營運淨收入 (NOI)：** 預估年租金收入 - 預估年營運支出（含空置期損失、管理費、稅賦等）。
    * **資產總報酬率 (ROR)：** NOI ÷ 房屋總價。代表房子純靠租金，不依賴貸款的真實賺錢能力。
    * **貸款常數 (K)：** 每年應繳房貸本利和 ÷ 貸款總額。代表您向銀行借錢的實質年化成本。
    * **自有資金報酬率 (ROE)：** (NOI - 每年應繳房貸本利和) ÷ 自備款金額。代表您拿出的現金，實際獲得的投資報酬率。

    ---

    ### 分析結果與紅綠燈判斷依據
    
    #### 1. 負擔能力檢測
    * **安全綠燈：** 房價所得比 < 5倍 且 房貸收支比 < 33%。財務相對健康，有餘裕維持生活品質。
    * **警戒黃燈：** 房價所得比 5 ~ 7倍 或 房貸收支比 33 ~ 50%。現金流有壓力，需確保收入穩定並預留緊急預備金。
    * **危險紅燈：** 房價所得比 > 7倍 或 房貸收支比 > 50%。極易成為屋奴，強烈建議改採「先租屋、後買房」策略。

    #### 2. 財務槓桿評估
    * **正槓桿：** ROR > K。房子賺錢速度大於銀行利息，借錢能放大真實獲利，您的 ROE 將大於 ROR。
    * **負槓桿：** ROR < K。房屋收益不足以支付利息，借貸將拖垮獲利，您的 ROE 將小於 ROR。

    #### 3. 現代財務分析（長期投資評估）
    * **淨現值 (NPV)：** 將未來持有期間的淨租金收益，加上期末售屋所得，扣除房貸後，以您的「折現率」回推成今天的價值。
        * **NPV > 0：** 代表該筆投資的真實回報大於您設定的期望報酬率，**具備投資價值**。
        * **NPV < 0：** 代表該筆投資無法滿足您的預期回報。
    * **內部報酬率 (IRR)：** 考慮資金進出時間點後，這筆不動產投資的「真實年化報酬率」。
    """)

st.divider()

# 輸入數值
st.sidebar.header("參數設定")
st.sidebar.subheader("房屋與市場參數")
house_price = st.sidebar.number_input("房屋總價 (萬元)", min_value=0, value=1500, step=100)
monthly_rent = st.sidebar.number_input("預估月租金 (元)", min_value=0, value=30000, step=1000)
expense_rate = st.sidebar.number_input("營運支出比例 (%)", min_value=0, value=15, help="含空置損失、房屋稅、管理費等")
holding_years = st.sidebar.number_input("預計持有年限 (年)", min_value=0, value=10, step=5)
appreciation_rate = st.sidebar.number_input("預估房價年增值率 (%)", min_value=0.0, value=5.0, step=0.1)
rent_growth_rate = st.sidebar.number_input("預估租金年漲幅 (%)", min_value=0.0, value=1.0, step=0.1)

st.sidebar.divider()

st.sidebar.subheader("貸款與個人財務參數")
down_payment = st.sidebar.number_input("自備款金額 (萬元)", min_value=0, value=300, step=50)
interest_rate = st.sidebar.number_input("房貸年利率 (%)", min_value=0.0, value=2.4, step=0.1)
loan_term = st.sidebar.selectbox("貸款年限 (年)", options=[20, 30, 40], index=1)
annual_income = st.sidebar.number_input("家庭年所得 (萬元)", min_value=10, value=150, step=10)
discount_rate = st.sidebar.number_input("折現率 (%)", min_value=0.0, value=2.4, step=0.1)

# 計算部分
loan_amount = house_price - down_payment
annual_rent_w = (monthly_rent * 12) / 10000 # w代表轉為萬元
annual_expense_w = annual_rent_w * (expense_rate / 100)
noi_w = annual_rent_w - annual_expense_w # 營運淨收入
monthly_rate = (interest_rate / 100) / 12
total_months = loan_term * 12
if monthly_rate > 0:
    monthly_payment_w = loan_amount * (monthly_rate * (1 + monthly_rate)**total_months) / ((1 + monthly_rate)**total_months - 1) # PMT
else:
    monthly_payment_w = loan_amount / total_months
annual_ds_w = monthly_payment_w * 12

# 財務指標
ror = noi_w / house_price * 100 if house_price > 0 else 0
k = annual_ds_w / loan_amount * 100 if loan_amount > 0 else 0
roe = (noi_w - annual_ds_w) / down_payment * 100 if down_payment > 0 else 0
price_income_ratio = house_price / annual_income if annual_income > 0 else 0
loan_income_ratio = (monthly_payment_w / (annual_income / 12)) * 100 if annual_income > 0 else 0

# 分析結果
st.header("投資報酬率法")
st.subheader("負擔能力檢測")
col_a1, col_a2 = st.columns(2)
col_a1.metric("房價所得比", f"{price_income_ratio:.1f} 倍")
col_a2.metric("房貸收支比", f"{loan_income_ratio:.1f} %")
if price_income_ratio > 7 or loan_income_ratio > 50:
    st.error("目前房價遠超出您的負擔能力，強烈建議暫緩購屋，改採「先租屋、後買房」策略。")
elif price_income_ratio > 5 or loan_income_ratio > 33:
    st.warning("購屋將對現金流造成一定壓力，請確保未來工作收入穩定，並預留至少半年的緊急預備金。")
else:
    st.success("財務相對健康，購屋後仍能維持良好生活品質，可積極尋找符合「心中之尺」的物件。")

st.subheader("財務槓桿與投資效益")
col_b1, col_b2, col_b3 = st.columns(3)
col_b1.metric("資產總報酬率 (ROR)", f"{ror:.2f} %")
col_b2.metric("貸款常數 (K)", f"{k:.2f} %")
col_b3.metric("自有資金報酬率 (ROE)", f"{roe:.2f} %")
if ror > k + 0.01:
    st.success(f"正槓桿效應：對購屋者有利，房屋收益 ({ror:.2f}%) 大於借貸成本 ({k:.2f}%)，ROE 被放大至 {roe:.2f}%。")
elif ror < k - 0.01:
    st.error(f"負槓桿效應：對銀行有利，房屋收益 ({ror:.2f}%) 小於借貸成本 ({k:.2f}%)，ROE 被拖垮至 {roe:.2f}%。")
else:
    st.info("槓桿不正不負：資產報酬率與借款成本打平。")

# 現代財務分析
st.divider()
st.header("現代財務分析法")

cash_flows = [-down_payment] # 第一筆現金流為負的自備款

for year in range(1, int(holding_years) + 1):
    yearly_rent = annual_rent_w * ((1 + rent_growth_rate / 100) ** (year - 1)) # 租金成長
    yearly_noi = yearly_rent * (1 - expense_rate / 100)
    yearly_cf = yearly_noi - annual_ds_w
    if year < holding_years:
        cash_flows.append(yearly_cf)
    else:
        final_house_value = house_price * ((1 + appreciation_rate / 100) ** holding_years)
        current_month = year * 12
        if current_month >= total_months:
            remaining_loan = 0
        else:
            if monthly_rate > 0:
                remaining_loan = loan_amount * (((1 + monthly_rate)**total_months - (1 + monthly_rate)**current_month) / ((1 + monthly_rate)**total_months - 1))
            else:
                remaining_loan = loan_amount - (monthly_payment_w * current_month)
        terminal_cf = yearly_cf + (final_house_value - remaining_loan)
        cash_flows.append(terminal_cf)

# 計算NPV
npv = 0
for i, cf in enumerate(cash_flows):
    npv += cf / ((1 + discount_rate / 100) ** i)

# 計算IRR (增加防呆機制：攔截 nan)
try:
    calculated_irr = npf.irr(cash_flows)
    # 檢查是否算不出 IRR (產生 nan)
    if pd.isna(calculated_irr):
        irr = 0.0
    else:
        irr = calculated_irr * 100
except:
    irr = 0.0

# 顯示結果
st.markdown(f"考慮未來 **{int(holding_years)}** 年的現金流，並以折現率 **{discount_rate:.2f}%** 進行評估：")
col_c1, col_c2 = st.columns(2)
col_c1.metric("淨現值 (NPV)", f"{npv:.2f} 萬元")
col_c2.metric("內部報酬率 (IRR)", f"{irr:.2f} %")

# 決策判定
if npv > 0:
    st.success(f"具備投資價值：NPV 大於 0，代表此不動產的真實回報 (IRR {irr:.2f}%) 高於您要求的折現率 ({discount_rate:.2f}%)。")
else:
    st.error(f"報酬未達標：NPV 小於 0，代表此投資無法滿足您 {discount_rate:.2f}% 的預期報酬率。")

# 利率敏感度測試
st.divider()
st.header("利率敏感度測試")
st.markdown("觀察如果未來央行升降息，房貸利率變動對您「自有資金報酬率 (ROE)」的影響。")
rate_list = []
roe_list = []
start_rate = max(0.5, round(interest_rate - 1.0, 1)) # 確保利率不小於 0.5%
end_rate = round(interest_rate + 1.0, 1)
current_test_rate = start_rate
while current_test_rate <= end_rate + 0.01: # 每次增加 0.1%，模擬不同利率下的結果
    test_monthly_rate = (current_test_rate / 100) / 12
    if test_monthly_rate > 0 and loan_amount > 0:
        test_pmt = loan_amount * (test_monthly_rate * (1 + test_monthly_rate)**total_months) / ((1 + test_monthly_rate)**total_months - 1) # PMT
    else:
        test_pmt = loan_amount / total_months if loan_amount > 0 else 0
    test_annual_ds = test_pmt * 12
    test_roe = ((noi_w - test_annual_ds) / down_payment) * 100 if down_payment > 0 else 0
    rate_list.append(round(current_test_rate, 2))
    roe_list.append(round(test_roe, 2))
    current_test_rate = round(current_test_rate + 0.1, 1)

chart_data = {"房貸利率(%)": rate_list, "自有資金報酬率(ROE) %": roe_list}
df = pd.DataFrame(chart_data) # 轉換為 DataFrame 表格

st.line_chart(df.set_index("房貸利率(%)")) # X 軸為房貸利率的摺線圖
st.caption(f"當利率上升到某個臨界點時，ROE 將會跌破資產報酬率 ROR ({ror:.2f}%)，代表從那一刻起，投資將轉為負槓桿。")
