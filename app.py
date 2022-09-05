import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st


st.title('LIXIL vs Competitor Stock Viewer')

st.sidebar.write("""
# 製造業売上高Top10 株価
以下のオプションから表示日数を指定してください。
""")

st.sidebar.write("""
## 表示日数選択    
""")

days = st.sidebar.slider('日数', 1, 90, 30)

st.write(f"""
### 過去 {days}日間 のLIXILおよび、競合他社の株価
""")

# Tickerリスト分の会社の株価を取得する関数を定義する
# 入力の引数は、取得日数と取得した会社が格納されたTickerリスト

@st.cache #取得したデータをキャッシュに保存する
def get_data(days,tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        # 取得日数分の株価の情報を取得する
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        # 日付のフォーマットを変更する
        hist.index = hist.index.strftime('%d %B %Y')
        # 株価の終値のみを取得する
        hist = hist[['Close']]
        # カラム名をCloseからCompanyNameに変更する
        hist.columns = [company]
        # 日付と社名の列と行を入れ替える
        hist = hist.T
        # indexのカラム名をNameにする
        hist.index.name = 'Company_Name'
        # 各社のデータをデータフレームに結合していく
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """
    )

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 12000.0, (0.0, 12000.0)  
    )

    # 株価を取得する会社のTickerリストを作成する。
    # 住宅設備業界売上Top10 ※YKKAP,伊藤忠建材,SMB建材は非上場のため除く
    tickers = {
        'LIXIL': '5938.T',
        'Panasonic': '6752.T',
        'TOTO': '5332.T',
        '三和シヤッター工業': '5929.T',
        'リンナイ': '5947.T',
        'JKホールディングス': '9896.T',
        '三協立山': '5932.T',
        'タカラスタンダード': '7981.T'
    }

    # 株価を取得
    df = get_data(days, tickers)

    # 会社を選択するセレクトボックスを作成する。
    companies = st.multiselect(
        '企業名を選択してください。',
        list(df.index),
        ['LIXIL', 'Panasonic', 'TOTO']
    )


    if not companies:
        st.error('少なくとも１社は選択してください。') # 企業が１社も選択されていない場合、エラーを表示する。
    else:
        data = df.loc[companies]
        # data = data.sort_index()
        st.write("### 株価（JPY）", data.style.format('{:.1f}'))
        # dataを転置して、日付データをインデックスからデータに変更する
        data = data.T.reset_index()
        # melt関数によって、dataを生データライクに展開する
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(JPY)'}
        )

        # 表を作成する
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(JPY):Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
                color="Company_Name:N"
            )
        )

        # 表を表示する
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "おっと！何かエラーが起きているようです。"
    )