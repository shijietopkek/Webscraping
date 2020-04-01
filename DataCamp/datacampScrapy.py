import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd

class dcSpider(scrapy.Spider):
    name = "dcSpider"
    
    def start_requests(self):
        url = "https://www.datacamp.com/courses/all"
        yield scrapy.Request(url=url,callback=self.parse_front)
        
    def parse_front(self,response):
        urls = response.xpath("//a[contains(@class,'course-block__link')]/@href").extract()
        main_url = "https://www.datacamp.com"
        for i in range(len(urls)):
            urls[i] = main_url+urls[i]
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse_content)
            
    def parse_content(self,response):
        global df
        global df2
        container = response.xpath("//div[contains(@class, 'home-header__intro')]")
        title = container.xpath("./h1/text()").extract()[0]
        desc = container.xpath("./p/text()").extract()[0]
        stats = container.xpath("./ul")
        duration = stats.xpath("./li[1]/text()").extract()[0]
        video_count=stats.xpath("./li[2]/text()").extract()[0].split(" ")[0]
        exercise_count=stats.xpath("./li[3]/text()").extract()[0].split(" ")[0]
        no_of_participants=stats.xpath("./li[4]/text()").extract()[0].split(" ")[0]
        xp_count = stats.xpath("./li[5]/text()").extract()[0].split(" ")[0]
        
        chapter_titles = response.xpath("//ol[@class='chapters']//h4[@class='chapter__title']/text()").extract()
        chapter_descs = response.xpath("//ol[@class='chapters']//p[contains(@class,'chapter__description')]").extract()
        for i in range(len(chapter_titles)):
            chapter_titles[i]=chapter_titles[i].strip("\n").strip()
        for i in range(len(chapter_descs)):
            chapter_descs[i] = chapter_descs[i].split("\n")[1].strip()
        chapter_nums = [i+1 for i in range(len(chapter_titles))]
        df3 = pd.DataFrame({"Course":[title]*len(chapter_titles),
                            "Chapter No.":chapter_nums,
                            "Chapter Title": chapter_titles,
                            "Chapter Description": chapter_descs
            })
        
        df4 = pd.DataFrame({"Course":[title],
                            "Description":[desc],
                            "Duration":[duration],
                            "No. of Chapters":[len(chapter_nums)],
                            "No. of Videos":[int(video_count.replace(",",""))],
                            "No. of Exercises":[int(exercise_count.replace(",",""))],
                            "No. of Participants":[int(no_of_participants.replace(",",""))],
                            "No. of XPs": [int(xp_count.replace(",",""))],          
            })
        df = df.append(df4)
        df2 = df2.append(df3)
    
        
df = pd.DataFrame(data=None, columns=["Course","Description","Duration","No. of Chapters","No. of Videos","No. of Exercises","No. of Participants","No. of XPs"])
df2 = pd.DataFrame(data=None, columns=["Course","Chapter No.","Chapter Title","Chapter Description"])
#main
process = CrawlerProcess()
process.crawl(dcSpider)
process.start()




path = r"C:\Users\sj\Desktop\DC_courses.xlsx"
writer=pd.ExcelWriter(path, engine='xlsxwriter')
df.to_excel(writer, sheet_name = 'Courses',index=False)
df2.to_excel(writer, sheet_name = 'Course Chapters',index=False)
writer.save()
writer.close()