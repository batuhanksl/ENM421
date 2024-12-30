import pandas as pd
import asyncio
from playwright.async_api import async_playwright

df = pd.read_excel('hepsiemlaklink.xlsx')



newlist = []

async def extract_val_attributes(myurl,counter):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(myurl)
        await asyncio.sleep(5)

        # Desired fields to extract
        desired_fields = [
            "Son Güncelleme Tarihi", "Konut Tipi", "Oda + Salon Sayısı",
            "Banyo Sayısı", "Brüt M2", "Kat Sayısı", "Bulunduğu Kat",
            "Bina Yaşı", "Isınma Tipi", "Eşya Durumu", "Kullanım Durumu", "Cephe"
        ]

        # Extract relevant data
        data = await page.evaluate(f'''() => {{
            const items = document.querySelectorAll("li.spec-item");
            const fieldValues = Array.from(items)
                .map(item => {{
                    const field = item.querySelector("span.txt")?.textContent.trim();
                    const valueElement = item.querySelector("span:not(.txt), a");
                    const value = valueElement?.textContent.trim();
                    return {{ field, value }};
                }})
                .filter(item => item.field && {desired_fields}?.includes(item.field));

            // Extract price value
            const priceElement = document.querySelector("p.fz24-text.price");
            const price = priceElement?.textContent.trim();

            // Extract title value
            const titleElement = document.querySelector("h1.fontRB");
            const title = titleElement?.textContent.trim();

            return {{ fieldValues, price, title }};
        }}''')


        newlist.append(data)

        print(f"Counter: {counter}, Extracted data: {data}")
        
        if counter % 75 == 0:
            df_newList = pd.DataFrame(newlist)
            df_newList.to_excel(f"Emlak{counter}.xlsx", index=False)

        await browser.close()

async def main():
  # Iterate over each row in the dataframe and extract data
    idlecount = 0
    for index,row in df.iloc[1299:,:].iterrows():
        idlecount += 1
        url = row['Link']
        await extract_val_attributes(url,idlecount)

if __name__ == "__main__":
    asyncio.run(main())