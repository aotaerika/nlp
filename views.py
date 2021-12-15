import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic


from django.shortcuts import render
from django.http import HttpResponse ,QueryDict
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import MeCab
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required


sample_df=pd.read_csv("all_products.csv",header=0)
sample_df=pd.DataFrame(sample_df)

tagger = MeCab.Tagger('-Owakati')
corpus = [tagger.parse(sentence).strip() for sentence in sample_df["品名仕様"]]
vectorizer=TfidfVectorizer()
tf_siyou_vec=vectorizer.fit_transform(corpus)


class IndexView(generic.TemplateView):
    template_name = "nlp/index.html"



@login_required
def index(request):
    if request.method=="GET":
        return render(
            request,
            "nlp/index.html"
        )
    elif request.method=="POST": 
        if 'tf_idf' in request.POST:
            priority_word=request.POST.getlist("level")
            text=" ".join(priority_word)
            text_tf = vectorizer.transform([tagger.parse(text).strip()])
            similarity =cosine_similarity(text_tf, tf_siyou_vec)[0]
            topn_indices = np.argsort(similarity)[::-1][:10]
            title=request.POST.get("input_indno")
            
            topn_df=sample_df.loc[[int(title)]]
            
            cord40=sample_df.at[int(title),"品目コード"]
            print(cord40)
            cord40=cord40.replace(' ', '+')
            print(cord40)
            insert_url="https://www.orange-book.com/ja/c/products/index.html?itemCd="+str(cord40)
            topn_df["リンク"]= insert_url
            
            for i in topn_indices:
                if i == title:
                    next    
                x=sample_df.loc[[i]]
                topn_df=topn_df.append(x)
                cord40=topn_df.at[i,"品目コード"]
                cord40=cord40.replace(' ', '+')
                insert_url="https://www.orange-book.com/ja/c/products/index.html?itemCd="+str(cord40)
                topn_df.at[i,"リンク"]= insert_url
            topn_df=topn_df.drop('品名仕様', axis=1)

            context=topn_df.to_html(render_links=True)
            return render(
                request,
                "nlp/result.html",
                {"products":context}
            )
        else:

            try:
            

                title=request.POST.getlist("title")
                input_indno=sample_df.index[sample_df["発注コード"]==int(title[0])].tolist()
                product_list=sample_df["仕様"][input_indno[0]]
                product_name=sample_df["品名"][input_indno[0]]
                category=sample_df["小小分類テキスト"][input_indno[0]]
                wakati_word=product_list.split()
                #word={"word":(for word in wakati_word)} 
                input_indno=input_indno[0]       

                return render(
                    request,
                    "nlp/response.html",
                    {"product_name":product_name,"title": product_list,"category":category,
                    "wakati_word":wakati_word,"input_indno":input_indno}
                )
            except ValueError as _:
                
                error_word="入力された発注コードは登録されていません。"
                return render(
                    request,
                    "nlp/home.html",
                    {"product_name":error_word}
                )
            except IndexError as _:
                
                error_word="入力された発注コードは登録されていません。"
                return render(
                    request,
                    "nlp/home.html",
                    {"product_name":error_word}
                )

def tf_idf(request):
    if request.method=="GET":
        return render(
            request,
            "nlp/response.html"
        )
    
    else:
        priority_word=[request.POST.getList("level")]
        
        
        return render(
            request,
            "nlp/response.html",
            {"priority_word":priority_word }
        
        )


        

#Create your views here.
