import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import altair as alt
import plotly.express as px

with st.echo(code_location='below'):
    df = pd.read_csv('Spotify_data.csv')
    wide_genres = ["country", "folk", "rock", "rap", "pop", "hip hop"]
    wide_genres_ru = ["кантри", "фолк", "рок", "рэп", "поп", "хип-хоп"]

    def detect_genre(top_genre):
        for genre in wide_genres:
            if top_genre.find(genre) >= 0:
                return wide_genres_ru[wide_genres.index(genre)]
        return "другой жанр"

    df["wide_genre"] = df["top genre"].dropna().map(detect_genre)
    st.sidebar.title("🎶 Музыка 2010-х")
    visualization = st.sidebar.radio("Выберите визуализацию:", ["Тренды в музыке", "Особенности песен",
                                                                "Топ артистов", "Датасет"])
    charact_codes = ["bpm", "nrgy", "dnce", "dB", "dur", "live", "val", "acous", "spch"]
    charact_list = ["Темп (bpm)", "Энергия", "Танцевальность", "Громкость", "Длительность (в секундах)",
                    "Живое исполнение", "Жизнерадостность", "Акустичность", "Речитативность"]
    df = df.rename(columns=dict(zip(charact_codes, charact_list)))
    for ch in ["Энергия", "Танцевальность", "Громкость",       # нормализация характеристик
                    "Живое исполнение", "Жизнерадостность", "Акустичность", "Речитативность"]:
        df[ch] = 100 * (df[ch] - df[ch].quantile(0.05)) / (df[ch].quantile(0.95) - df[ch].quantile(0.05))

    if visualization == "Тренды в музыке":
        st.markdown("# Тренды в музыке")
        st.markdown("В течение 2010-х годов слушатели стали выше ценить как танцевальные и "
                    "речитативные, так и акустические композиции, а средняя длительность и энергичность популярных "
                    "песен сократилась.")

        st.write("Ежегодно стриминговая платформа Spotify определяет 100 наиболее прослушиваемых песен. "
                 "Визуализация с использованием `altair` показывает, как на протяжении 2010–2019 годов изменялись "
                 "их средние характеристики. Музыкальные особенности, такие как энергия и танцевальность, определены "
                 "алгоритмами Spotify и приведены к шкалам, в которых 90 % песен характеризуется значениями от 0 до "
                 "100. ")

        characteristics = np.array(st.multiselect("Выберите одну или несколько характеристик:", sorted(charact_list),
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

    elif visualization == "Особенности песен":
        st.markdown("# Особенности песен")
        st.markdown("Визуализация с использованием `plotly` позволяет оценить характеристики конкретных песен в "
                    "сравнении с другими популярными композициями. Например, график показывает, что песня Билли Айлиш "
                    "*when the party's over*, попавшая в чарт в 2019 году, — это "
                    "самая акустичная и одна из наименее танцевальных популярных песен 2010-х годов.")
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Ось Х", sorted(charact_list), index=0)
        with col2:
            y_axis = st.selectbox("Ось Y", sorted(charact_list), index=6)
        year = st.slider("Год попадания песни в топ", min_value=2010, value=(2018, 2019), max_value=2019)
        yearly_data = df[(df["top year"] >= year[0]) & (df["top year"] <= year[1])]
        fig = px.scatter(yearly_data,
                         x=x_axis,
                         y=y_axis,
                         size=yearly_data["pop"] - 35,
                         color="wide_genre",
                         color_discrete_sequence=px.colors.qualitative.Pastel,
                         width=800,
                         height=600,
                         category_orders={"wide_genre": sorted(wide_genres_ru) + ["другой жанр"]},
                         custom_data=["artist", "year released", "title", "pop"],
                         labels=dict(wide_genre="Жанр"),
                         size_max=15,
                         template="simple_white")
        fig.update_traces(
            hovertemplate="<br>".join([
                "<b>%{customdata[2]}</b>",
                "%{customdata[0]}",
                "",
                x_axis + ": %{x:.2f}",
                y_axis + ": %{y:.2f}",
                "Популярность: %{customdata[3]}",
                "Год релиза: %{customdata[1]}"
            ])
        )
        st.plotly_chart(fig)

    elif visualization == "Топ артистов":
        st.markdown("# Топ артистов")
        st.markdown("Интерактивный топ артистов позволяет увидеть, какие исполнители выпустили больше всего хитов, "
                    "попавших в чарт Spotify, в течение произвольного отрезка времени в 2010-х годах. Цвет столбца"
                    "соответствует жанру, к которому относится больше всего композиций исполнителя, попавших в топ. "
                    "Визуализация выполнена с помощью пакета `seaborn`.")
        year = st.slider("Построить топ за период:", min_value=2010, value=(2018, 2019), max_value=2019)
        yearly_data = df[(df["top year"] >= year[0]) & (df["top year"] <= year[1])]
        col1, col2, col3 = st.columns(3)
        chart = pd.DataFrame(yearly_data["artist"].value_counts()).reset_index().rename(columns={
            'index': 'Artist',
            'artist': 'Hits'
        }).sort_values(by=["Hits", "Artist"], ascending=[False, True])

        chart["Основной жанр"] = chart["Artist"].map(
            lambda art: yearly_data.query("artist == @art").loc[:, "wide_genre"].mode()[0])
        sns.set(font_scale=0.7)
        plot = sns.catplot(data=chart.head(10), x="Hits", y="Artist", hue="Основной жанр",
                           kind="bar", hue_order=sorted(wide_genres_ru) + ["другой жанр"],
                           palette=sns.color_palette("Set2"), dodge=False)
        plt.xlabel("Количество песен в топе")
        plt.ylabel("Исполнитель")
        st.pyplot(plot)

    elif visualization == "Датасет":
        st.markdown("# Датасет")
        st.write(df)

    st.markdown("***")
    """
    Автор базы данных — [Michael Morris](https://www.kaggle.com/datasets/muhmores/spotify-top-100-songs-of-20152019).
    
    Исходный код:
    """