import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt

with st.echo(code_location='below'):
    SpotifyData = pd.read_csv('Spotify_data.csv')
    df = SpotifyData
    st.sidebar.title("🎶 Музыка 2010-х")
    visualization = st.sidebar.radio("Выберите визуализацию:", ["Тренды в музыке", "Особенности песен", "Топ жанров",
                                                                "Топ артистов", "Датасет"])

    charact_codes = ["bpm", "nrgy", "dnce", "dB", "dur", "live", "val", "acous", "spch"]
    charact_list = ["Темп (bpm)", "Энергия", "Танцевальность", "Громкость", "Длительность (в секундах)",
                    "Живое исполнение", "Жизнерадостность", "Акустичность", "Речитативность"]
    df = df.rename(columns=dict(zip(charact_codes, charact_list)))
    for ch in ["Энергия", "Танцевальность", "Громкость",       # нормализация характеристик
                    "Живое исполнение", "Жизнерадостность", "Акустичность", "Речитативность"]:
        df[ch] = 100 * (df[ch] - df[ch].quantile(0.1)) / (df[ch].quantile(0.9) - df[ch].quantile(0.1))


    match visualization:

        case "Тренды в музыке":
            st.markdown("# Тренды в музыке")
            st.markdown("### В течение 2010-х годов слушатели стали выше ценить как танцевальные и "
                        "речитативные, так и акустические композиции, а средняя длительность и энергичность популярных "
                        "песен сократилась.")
            st.write("Ежегодно стриминговая платформа Spotify определяет 100 наиболее прослушиваемых песен. "
                     "Визуализация показывает, как на протяжении 2010–2019 годов изменялись их средние характеристики. "
                     "Музыкальные особенности, такие как энергия и танцевальность, определены алгоритмами Spotify и "
                     "приведены к шкалам, в которых большинство песен характеризуется значениями от 0 до 100. "
                     )

            characteristics = np.array(st.multiselect("Выберите одну или несколько характеристик:", charact_list,
                                                      default=["Танцевальность", "Акустичность",
                                                               "Длительность (в секундах)"]))
            source = pd.DataFrame()
            for ch in characteristics:
                source[ch] = df.groupby("top year")[ch].mean()
            try:
                source = pd.melt(source.reset_index(), "top year")
                highlight = alt.selection(type='single', on='mouseover',
                                          fields=['variable'], nearest=True)
                base = alt.Chart(source).encode(
                    alt.X("top year:O", title="Год"),
                    alt.Y("value:Q", title="Среднее значение"),
                    alt.Color("variable", title="Характеристика")
                )
                ### FROM: https://altair-viz.github.io/gallery/multiline_highlight.html
                points = base.mark_circle().encode(
                    opacity=alt.value(0)
                ).add_selection(
                    highlight
                ).properties(
                    width=800,
                    height=500
                )
                lines = base.mark_line(interpolate="basis").encode(
                    size=alt.condition(~highlight, alt.value(2), alt.value(4))
                )
                ### END FROM
                st.altair_chart((points + lines).interactive())
            except:
                st.write("Выберите хотя бы одну характеристку.")



        case "Датасет":
            st.write(SpotifyData)

    st.markdown("***")
    """
    Автор базы данных — [Michael Morris](https://www.kaggle.com/datasets/muhmores/spotify-top-100-songs-of-20152019).
    
    Исходный код:
    """