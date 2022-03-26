import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.chrome.options import Options


class Scraping:
    """ dentro de init, farei as perguntas das quais serão utilizadas no site 
    da amazon e na configuração do arquivo."""

    def __init__(self):
        self.abrir_chrome = input(
            'Deseja visualizar o Chrome? [S/N] ').strip().upper()
        self.item = input('O que deseja pesquisar? ')
        self.valores = input(
            'Deseja adicionar valor mínimo e maxímo de busca? [S/N] ').strip().upper()
        if self.valores == 'S' or self.valores == 'SIM':
            self.valor_min = int(input('Qual valor mínimo de busca? '))
            self.valor_max = int(input('Qual valor maxímo de busca? '))
        self.lista_de_dados = []
        self.nome_arquivo = input('Nome para o arquivo: ')
        self.index = input(
            'Deseja o index no documento? [S/N] ').strip().upper()

    # Sequencia de iciazilação para o funcionamento do sistema.
    def iniciar(self):
        self.config_web()
        self.acessar_pagina()
        self.raspagem_de_dados()
        self.arquivar_dados()
        self.criar_documento()

    # Configuração da web
    def config_web(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option(
            'excludeSwitches', ['load-extension', 'enable-automation'])
        self.chrome_options.add_argument('--lang=pt-BR')
        self.chrome_options.add_argument('--disable-notifications')
        if self.abrir_chrome == 'N' or self.abrir_chrome == 'NAO':
            self.chrome_options.add_argument('--headless')

    # Acessar pagina do item escolhido pelo usuário.
    def acessar_pagina(self):
        self.navegador = webdriver.Chrome(options=self.chrome_options)
        self.navegador.get('https://www.amazon.com.br/')
        sleep(0.5)

        self.barra_pesquisa = self.navegador.find_element_by_css_selector(
            'input[id="twotabsearchtextbox"]')
        self.barra_pesquisa.send_keys(self.item)
        self.barra_pesquisa.submit()
        sleep(1)

        if self.valores == 'S' or self.valores == 'SIM':
            self.valor_minimo = self.navegador.find_element_by_css_selector(
                'input[placeholder="Min."]')
            self.valor_minimo.send_keys(self.valor_min)
            sleep(0.5)

            self.valor_maximo = self.navegador.find_element_by_css_selector(
                'input[placeholder="Máx."]')
            self.valor_maximo.send_keys(self.valor_max)
            self.valor_maximo.submit()
            sleep(3)

    # Coletar os dados da pagina da pagina.
    def raspagem_de_dados(self):
        self.site = BeautifulSoup(self.navegador.page_source, 'html.parser')
        self.itens = self.site.findAll('div', attrs={
            'class': 'a-section a-spacing-small s-padding-left-small s-padding-right-small'})
        
        for self.item in self.itens:
            self.titulo = self.item.find(
                'span', attrs={'class': 'a-size-base-plus a-color-base a-text-normal'})
            self.titulo = self.titulo.text
            
            self.preco = self.item.find(
                'span', attrs={'class': 'a-offscreen'})
            
            if self.preco:
                self.preco = self.preco.text

            self.parcelas = self.item.find(
                'span', attrs={'class': 'a-size-base a-color-secondary'})
            
            if self.parcelas:
                self.parcelas = self.parcelas.text

            if not self.parcelas:
                self.outra_parcela = self.item.findAll(
                    'span', attrs={'class': 'a-color-secondary'})
                if self.outra_parcela:
                    self.outra_parcela = ''.join(
                        [parcelas.text for parcelas in self.outra_parcela])

            self.url = self.item.find('a', attrs={
                'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
            self.url = 'https://www.amazon.com.br/' + self.url['href']

            self.lista_de_dados.append(
                [self.titulo, self.preco, self.parcelas, self.url])

        self.passar_pagina()

    # Tentar passar a pagina, se conseguir, ira coletar mais dados.
    def passar_pagina(self):
        try:
            self.passar_a_pagina = self.navegador.find_element_by_css_selector(
                'a[class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]')
            self.passar_a_pagina.click()
            sleep(3)

            self.raspagem_de_dados()

        except:
            pass

    # Salvando os dados em um DataFrame.
    def arquivar_dados(self):
        self.dados = pd.DataFrame(self.lista_de_dados, columns=[
            'Titulo', 'Preço Total', 'Parcelado', 'Link'])

    # Criar um documento excel, com ou sem index.
    def criar_documento(self):
        if self.index == 'N' or self.index == 'NAO':
            self.dados.to_excel(f'{self.nome_arquivo}.xlsx', index=False)

        else:
            self.dados.to_excel(f'{self.nome_arquivo}.xlsx')


amazon = Scraping()
amazon.iniciar()
