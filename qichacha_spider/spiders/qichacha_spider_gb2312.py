# -*- coding:utf-8 -*-
__author__ = 'zhaojm'

import scrapy

from ..items import CompanyInfoItem

import urllib
import json
import time

from ..utils import get_gb2312_txt


class QichachaSpider(scrapy.Spider):
    name = "qichacha_spider_gb2312"

    def start_requests(self):

        txt = get_gb2312_txt()
        for i in range(len(txt)):
            for j in range(len(txt)):
                search_key = txt[i] + txt[j]
                # search_key = u'一三'
                print "++++++gb2312+++++++: %s %d %d %d %s" % (
                time.strftime('%Y-%m-%d', time.localtime(time.time())), i, j, len(
                    txt), search_key)
                url = "http://www.qichacha.com/search?key=" + urllib.quote(search_key.encode('utf-8')) + "&index=0"
                print url
                request = scrapy.Request(
                    url,
                    callback=self.parse
                )
                # request.meta['item_category'] = item['category']
                # request.meta['item_category_num'] = item['category'][0:1]
                yield request
                # break
                # break

    def parse(self, response):
        # print response.body
        search_list = response.xpath('//tbody/tr')
        for sel in search_list:
            companyInfoItem = CompanyInfoItem()

            # companyInfoItem['item_category'] = response.meta['item_category']
            # companyInfoItem['item_category_num'] = response.meta['item_category_num']
            companyInfoItem['item_from_gb2312'] = u'gb2312'
            companyInfoItem['item_update_time'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            # companyInfoItem['province'] = sel.xpath(
            #     './span[@class="clear"]/span[@class="btn btn-link pull-right"]/text()').extract_first()
            # companyInfoItem['phone'] = sel.xpath('./span[@class="clear"]/small[2]/span[1]/text()').extract_first()
            # companyInfoItem['email'] = sel.xpath('./span[@class="clear"]/small[2]/span[2]/text()').extract_first()

            url = sel.xpath('./td[@class="tp1"]/a/@href').extract_first()
            url = response.urljoin(url)
            print "url: ", url

            request = scrapy.Request(
                url,
                callback=self.parse_company
            )
            request.meta['item'] = companyInfoItem
            yield request
            # break  # 只要第一个,有分类的

    def parse_company(self, response):
        # print "parse_company", response.body
        companyInfoItem = response.meta['item']

        companyInfoItem['company_name'] = response.xpath('//span[@class="text-big font-bold"]/text()').extract_first()

        small_sel = response.xpath(
            '//div[@id="company-top"]/div[@class="row"]/div[@class="col-md-9 m-b m-t"]/span[@class="clear"]/small[@class="clear text-ellipsis m-t-xs text-md text-black"]')
        try:
            companyInfoItem['phone'] = small_sel.xpath('./text()')[1].extract().strip()
        except:
            pass
        try:
            companyInfoItem['email'] = small_sel.xpath('./a/text()').extract_first()
        except:
            pass

        li_list = response.xpath('//ul[@class="company-base"]/li')
        for li_sel in li_list:
            label = li_sel.xpath('./label/text()').extract_first()
            # print label.encode('utf8')
            if u'统一社会信用代码' in label:
                companyInfoItem['unified_social_credit_code'] = li_sel.xpath('./text()').extract_first()
            elif u'注册号' in label:
                companyInfoItem['registration_number'] = li_sel.xpath('./text()').extract_first()
            elif u'组织机构代码' in label:
                companyInfoItem['organization_registration_code'] = li_sel.xpath('./text()').extract_first()
            elif u'经营状态' in label:
                companyInfoItem['business_status'] = li_sel.xpath('./text()').extract_first()
            elif u'公司类型' in label:
                companyInfoItem['business_type'] = li_sel.xpath('./text()').extract_first()
            elif u'成立日期' in label:
                companyInfoItem['register_date'] = li_sel.xpath('./text()').extract_first()
            elif u'法定代表' in label:
                companyInfoItem['legal_representative'] = li_sel.xpath('./a/text()').extract_first()
            elif u'注册资本' in label:
                companyInfoItem['registered_capital'] = li_sel.xpath('./text()').extract_first()
            elif u'营业期限' in label:
                companyInfoItem['operating_period'] = li_sel.xpath('./text()').extract_first()
            elif u'登记机关' in label:
                companyInfoItem['registration_authority'] = li_sel.xpath('./text()').extract_first()
            elif u'发照日期' in label:
                companyInfoItem['date_of_issue'] = li_sel.xpath('./text()').extract_first()
            elif u'企业地址' in label:
                companyInfoItem['business_address'] = li_sel.xpath('./text()')[1].extract()
            elif u'英文名' in label:
                companyInfoItem['english_name'] = li_sel.xpath('./text()')[1].extract()
            elif u'经营范围' in label:
                companyInfoItem['business_scope'] = li_sel.xpath('./text()')[1].extract()
            else:
                print "unknown li label: ", label.encode('utf8')
        # print companyInfoItem
        yield companyInfoItem
