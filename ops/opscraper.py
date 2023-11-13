import os
import sys
import time

import numpy as np
import pandas as pd
from selenium import webdriver

from config import Config


# For Prediction

class DataromaScraper():
    save_file = 'Agg-SuperInvestorPortfolio.csv'
    cols = ['%portfolio' ,'action' ,'report_price' ,'current_price', 'change_from_report', '1_year_low', '1_year_high']
    score_cols = ['Frequency_Score', '%HoldingSum_Score', 'Action_Score', 'Price_Score', 'Dataroma_Total_Score']
    buy_words = ['Add', 'Buy']
    sell_words = ['Sell', 'Reduce']

    def get_super_portfolio_links(self, invpart, driver):
        try:
            inv_list_body = driver.find_element('xpath' ,invpart)
            inv_list_text = driver.find_element('xpath' ,invpart).text
            sup_names_list =[]
            for inv in inv_list_text.split('\n'):
                if 'Updated' in inv:
                    sep =' Updated'
                else:
                    sep =' - '
                sup_names_list.append(inv.split(sep)[0])
            link_list = driver.find_elements('xpath' ,invpart +'/ul/li/a')
            investor_elem_dict = {}
            for e in link_list:
                investor_elem_dict[e.text] = {'link': e.get_attribute("href")}

            return investor_elem_dict
        except:
            print(sys.exc_info())

        driver.quit()



    def read_portfolio(self, name, link, elem, driver):
        driver.get(link)
        important_keys = {2: '%portfolio', 3: 'action', 5 :'report_price', 8 :'current_price', 9 :'change_from_report', 10 :'1_year_low', 11 :'1_year_high'}
        try:
            time.sleep(2)
            found = len(driver.find_elements('xpath' ,elem.replace('{num}' ,'')))
            print("Reading the portfolio of " ,name, ":: stocks found ::", str(found))
            if found >0:
                portfolio_data = {}
                for i in range(1, found +1):
                    num_replace = "[ " +str(i ) +"]"
                    ticker = driver.find_element('xpath' ,elem.replace('{num}' ,num_replace ) +'/td[2]').text
                    portfolio_data[ticker] = [x.text for x in driver.find_elements('xpath' ,elem.replace('{num}' ,num_replace ) +'/td')]
                result = pd.DataFrame(portfolio_data)
                result = result[result.index.isin(important_keys.keys())]
                result = result.T.reset_index()
                result['Symbol'] = result['index'].apply(lambda x : x.split('-')[0].strip())
                result['TickerName'] = result['index'].apply(lambda x : x.split('-')[1].strip())
                result.drop('index', axis=1, inplace=True)
                result.rename(columns=important_keys, inplace=True)
                result['Investor'] = name.split('Updated')[0].strip()
                result.sort_values('Investor', inplace=True)
                size = driver.find_element('xpath' ,'//*[@id="p2"]/span[4]').text if driver.find_element('xpath'
                                                                                                         ,'//*[@id="p2"]/span[4]') else 0
                result['InvestorPortfolioSize'] = size
                result['UpdateTime'] = name.split('Updated')[1].strip()
                print(str(result.shape[0] ) +" stocks loaded into portfolio.")
                return result
        except:
            print(sys.exc_info())
            return
        return

    def action_analysis(self, df):
        ac_score = 0
        for i, row in df.iterrows():
            action = row[self.cols[1]]
            percent = float(action.split('%')[0].split(' ')[1] if '%' in action else 1)
            for b in self.buy_words:
                if b in row[self.cols[1]]:
                    ac_score+=percent
            for s in self.sell_words:
                if s in row[self.cols[1]]:
                    ac_score-=percent

        return ac_score


    def price_analysis(self, df, ac_score):
        diff_sums = 0
        df[self.cols[3]].fillna('0', inplace=True)
        df[self.cols[2]].fillna('0', inplace=True)
        for i, row in df.iterrows():
            cur =0
            if row[self.cols[3] ]=='' or row[self.cols[3]] is None or row[self.cols[3 ]==np.nan or self.cols[2]] is None or row[self.cols[2] ]==np.nan:
                continue
            cur = float(row[self.cols[3]].split('$')[1]) if '$' in row[self.cols[3]] else float(row[self.cols[3]])
            rep = float(row[self.cols[2]].split('$')[1]) if '$' in row[self.cols[2]] else float(row[self.cols[2]])
            diff_sums+=(cur - rep)
            if diff_sums *ac_score < 0:
                diff_sums = - diff_sums
        return diff_sums / (i+1)


    def growth_analysis(self, df):
        gr_score = 0
        for i, row in df.iterrows():
            gr_score+=(row[self.cols[3]] - row[self.cols[2]])
        return gr_score / i


    def stock_analysis(self, df):
        results ={}
        all_stocks = list(df['Symbol'].unique())
        df[self.cols[1]].fillna('', inplace=True)
        for stock in all_stocks:
            results[stock] = {}
            this_stock = df[df['Symbol' ]==stock]
            results[stock]['Frequency_Score'] = this_stock[self.cols[0]].count().sum()
            results[stock]['%HoldingSum_Score'] = this_stock[self.cols[0]].sum()
            results[stock]['Action_Score'] = self.action_analysis(this_stock)
            results[stock]['Price_Score'] = self.price_analysis(this_stock, results[stock]['Action_Score'])
        resdf = pd.DataFrame(results).T
        resdf['Action_Score'] = 1.5 *resdf['Action_Score']
        resdf['Frequency_Score'] = 1.5 *resdf['Frequency_Score']
        resdf[self.score_cols[-1]] = resdf[self.score_cols[0]] + resdf[self.score_cols[1]] + resdf[self.score_cols[2]]
        mn, mx = resdf.min(), resdf.max()
        resdf_scaled = (resdf - mn) / (mx - mn)
        resdf_scaled.sort_values(self.score_cols[-1], ascending=False, inplace=True)
        resdf_scaled.index.name=Config.symbol
        return all_stocks, resdf_scaled







    def scanDataroma(self, latest):

        if latest or not os.path.isfile('Agg-SuperInvestorPortfolio.csv'):
            driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
            url = "https://www.dataroma.com/m/home.php"
            driver.get(url)

            # investors
            agg_df = None
            super_portfolio_links = self.get_super_portfolio_links('//*[@id="port_body"]', driver)
            print("Portfolio links fetched.")
            print("Total Investors:  " +str(len(super_portfolio_links.keys())))
            start = round(time.time())
            elem = '//*[@id="grid"]/tbody/tr{num}'
            combined_portfolios = []
            for si in list(super_portfolio_links.keys()):
                x = self.read_portfolio(si, super_portfolio_links[si]['link'], elem, driver)
                combined_portfolios.append(x)
            agg_df = pd.concat(combined_portfolios)
            agg_df.to_csv(self.save_file)
            print("Portfolios read done.")
            print(str(round(time.time()) - start) + " seconds taken to read portfolios.")
            driver.quit()
        else:
            agg_df = pd.read_csv(self.save_file, header=0)
            stock_list, results = self.stock_analysis(agg_df)
            results = round(results,2).reset_index()



        # top 10 most owned stocks
        # top 10 stocks by %

        # top big bets

        # top buys last qtr

        # top buys last 2 qtrs



        return stock_list, results


class YahooScraper():
    all_links = []
    yahoo_file = 'Agg-yahoo-lists.csv'

    def get_links(self, master_link, element, n=10):
        driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
        url = master_link
        driver.get(url)
        link_dict = {}
        time.sleep(2)
        suffix = "//section//div[2]"
        count = len(driver.find_elements('xpath', element + suffix))
        print(str(count) + " lists found from master link: " + master_link + ".\n")

        for i in range(1, count):
            try:
                list_elem_suffix = '/div[' + str(i) + ']/div[1]/div/a'
                link_text = driver.find_element('xpath', element + suffix + list_elem_suffix).text
                link_url = driver.find_element('xpath', element + suffix + list_elem_suffix).get_attribute('href')
                link_dict[link_text] = link_url
            except:
                print(element + suffix + list_elem_suffix)
                print(sys.exc_info())
        driver.quit()
        return link_dict

    def save_list_data(self, links, elements):
        driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
        list_data = {}
        for name in list(links.keys()):
            if not name in list_data or len(list_data[name]['list']) == 0:
                try:
                    driver.get(links[name])
                    time.sleep(2)
                    stock_list = {}
                    suffix = '/tr'

                    for elem in elements:
                        found_stocks = len(driver.find_elements('xpath', elem.replace('{num}', '')))
                        if found_stocks == 0:
                            continue
                        else:
                            break

                    headers = driver.find_elements('xpath', elem.split('table/')[0] + "/table/thead/tr[1]/th")
                    h_keys = [h.text for h in headers]
                    print(str(found_stocks) + " stocks found in list: " + links[name])
                    for i in range(1, found_stocks + 1):
                        num_replace = "[" + str(i) + "]"
                        for ind, h in enumerate(h_keys):
                            if len(driver.find_elements('xpath', elem.replace('{num}', num_replace) + '/td')):
                                value = driver.find_element('xpath', elem.replace('{num}', num_replace) + '/td[' + str(
                                    ind + 1) + ']').text
                                if h not in stock_list:
                                    stock_list[h] = []
                                stock_list[h].append(value)
                            else:
                                continue
                except:
                    print(sys.exc_info())
                list_data[name] = pd.DataFrame(stock_list)
                list_data[name]['List'] = name
        resdf = pd.concat([ln for ln in list_data.values()], axis=0)
        if resdf.shape[0] > 0:
            resdf.to_csv(self.yahoo_file)
        df = resdf
        driver.quit()

    def score_analysis(self, df):
        print("Scoring Yahoo Lists")
        res = df[['Symbol', 'Name', 'List']].drop_duplicates()
        print("Total symbols found: " + str(len(df['Symbol'].unique())))
        cats = ['Undervalue','Growth','High','Gain','Dividend']
        for cat in cats:
            res[cat] = 0
        for i, row in res.iterrows():
            for cat in cats:
                if cat in row['List']:
                    res.at[i, cat] += 0.5
        res.groupby('Symbol').sum()
        res['Yahoo_Score'] = res.loc[:, 'Undervalue':'Dividend'].sum(axis=1)
        res = res[['Symbol']+cats+['Yahoo_Score']]
        return res.sort_values('Yahoo_Score', ascending=False)

    def scanYahooLists(self, links, elements, latest=False, stock_limit=10):

        if latest or not os.path.isfile(self.yahoo_file):
            self.save_list_data(links, elements)
        df = pd.read_csv(self.yahoo_file)
        result = self.score_analysis(df)

        return result





class MarketBeatScraper():
    all_links = []
    mkb_file = 'Agg-marketbeat-lists.csv'

    def get_price_symbol(self, fund):
        driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
        link = "https://www.marketbeat.com/stocks/NASDAQ/"+fund
        element = '//*[@id="cphPrimaryContent_pnlCompany"]/div[1]/div[1]/div/div[1]/div/div/strong'
        last_close=np.nan
        try:
            driver.get(link)
            last_close = driver.find_element('xpath', element).text
            last_close = float(last_close.replace('$','') if '$' in last_close else last_close)
            driver.close()
        except:
            driver.close()
            print(fund + " not found for price.")
        return last_close

    def get_links(self, master_link, element, n=10):
        driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
        url = master_link
        driver.get(url)
        link_dict = {}
        time.sleep(2)
        suffix = "//section//div[2]"
        count = len(driver.find_elements('xpath', element + suffix))
        print(str(count) + " lists found from master link: " + master_link + ".\n")

        for i in range(1, count):
            try:
                list_elem_suffix = '/div[' + str(i) + ']/div[1]/div/a'
                link_text = driver.find_element('xpath', element + suffix + list_elem_suffix).text
                link_url = driver.find_element('xpath', element + suffix + list_elem_suffix).get_attribute('href')
                link_dict[link_text] = link_url
            except:
                print(element + suffix + list_elem_suffix)
                print(sys.exc_info())
        driver.quit()
        return link_dict

    def save_list_data(self, links, elements):
        driver = webdriver.Chrome(executable_path='/Users/subhayuchakravarty/Downloads/chromedriver')
        list_data = {}
        for name in list(links.keys()):
            if not name in list_data or len(list_data[name]['list']) == 0:
                try:
                    driver.get(links[name])
                    time.sleep(2)
                    stock_list = {}
                    suffix = '/tr'

                    for elem in elements:
                        found_stocks = len(driver.find_elements('xpath', elem.replace('{num}', '')))
                        if found_stocks == 0:
                            continue
                        else:
                            break

                    headers = driver.find_elements('xpath', elem.split('table/')[0] + "/table/thead/tr[1]/th")
                    h_keys = [h.text for h in headers]
                    print(str(found_stocks) + " stocks found in list: " + links[name])
                    for i in range(1, found_stocks + 1):
                        num_replace = "[" + str(i) + "]"
                        symbol = driver.find_element('xpath', elem.replace('{num}', num_replace) + '/td[1]').text
                        symbol = symbol.split('\n')[0] if '\n' in symbol else symbol
                        if len(symbol) > 20:
                            continue
                        for ind, h in enumerate(h_keys):
                            value = driver.find_element('xpath', elem.replace('{num}', num_replace) + '/td[' + str(ind + 1) + ']').text
                            if h != 'Consensus Analyst Rating':
                                value = value.split('\n')[0] if '\n' in value else value
                            if h not in stock_list:
                                stock_list[h] = []
                            stock_list[h].append(value)
                except:
                    print(sys.exc_info())
                list_data[name] = pd.DataFrame(stock_list)
                list_data[name]['List'] = name
        lc = list_data['Large Caps']
        lc = lc.rename(columns={'Consensus Analyst Rating': 'Rating', 'Company':'Symbol'})
        lc['Score'] = lc['Rating'].apply(lambda x: float(x.split('Score:')[1].split(')')[0].strip()))
        lc['Rating'] = lc['Rating'].apply(lambda x: x.split('(')[0].strip())
        lc = lc[['Symbol','Rating', 'Score']]
        ratings = list_data['All Ratings']
        ratings = ratings.rename(columns={'Company': 'Symbol'})
        ratings['Rating'] = ratings['Action'] + ratings['Rating']
        ratings=ratings[['Symbol', 'Rating']]
        resdf = pd.concat([lc, ratings], axis=0)
        if resdf.shape[0] > 0:
            resdf.to_csv(self.mkb_file)
        driver.quit()

    def score_analysis(self, df):
        print("Scoring Market Beat")
        res = df[['Symbol', 'Score', 'Rating']].drop_duplicates()
        res['Score'].fillna(0, inplace=True)
        print("Total symbols found: " + str(len(df['Symbol'].unique())))
        cats = ['Buy','Outperform','Reiterated','Initiated','Positive','Sector Perform','Upgraded','Target Raised', 'Hold']
        for cat in cats:
            res[cat] = 0
        for i, row in res.iterrows():
            for cat in cats:
                add = 0.5
                if row['Rating'] is not np.nan and row['Rating'] is not None:
                    if 'Moderate' in row['Rating']:
                        add-=0.25
                    if 'Downgraded' in row['Rating']:
                        add-=0.5
                    if 'Target Lowered' in row['Rating']:
                        add-=0.5
                    if cat in row['Rating']:
                        res.at[i, cat] += add
        res = res.groupby('Symbol').sum()
        res['MarketBeat_Score'] = res.loc[:, 'Buy':'Hold'].sum(axis=1) + res['Score']
        mn, mx = res.min(), res.max()
        resdf_scaled = (res - mn) / (mx - mn)
        return resdf_scaled.sort_values('MarketBeat_Score', ascending=False).reset_index()

    def scanMarketBeatLists(self, links, elements, latest=False, stock_limit=10):

        if latest or not os.path.isfile(self.mkb_file):
            self.save_list_data(links, elements)
        df = pd.read_csv(self.mkb_file)
        result = self.score_analysis(df)

        return result
