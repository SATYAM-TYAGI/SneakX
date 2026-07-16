# User Manual

I built the SneakX interface to be clean and easy to use. Here is how you can search and find sneakers.

---

## 1. How to Search
When you open the page, you will see a search bar at the top.
* You can search using normal, natural sentences.
* For example, you can type: `red jordan shoes` or `comfortable running sneakers`.
* The search engine will understand what you mean even if the words do not match the shoe name exactly.

---

## 2. How the Filters Work
Under the search bar, there are filters you can use to narrow down your search:
* **Brand**: Choose a specific brand (like Nike, Jordan, or adidas).
* **Type**: Choose a category (like Running or Basketball).
* **Gender**: Filter by men, women, or all.
* **Material**: Filter by material (like Leather or Canvas).
* **Color**: Choose a specific colorway (like Black, White, or Red).

After setting your search text and filters, click the **Find Sneakers** button. The top 10 recommendations will appear below.

---

## 3. How the Recommendations Work
* **Query Parser**: Extracts Brand, Type, Gender, and Primary Color from your query.
* **Search Strategies**: If you search by traits only (e.g. *"Nike Running Shoes Black"*), it runs a structured search. If you search using general descriptions (e.g. *"comfortable"*), it performs semantic search on the filtered subset (hybrid) or the entire dataset.
* **Fallback Logic**: If there are fewer than 10 matches, the app automatically finds similar shoes to the top recommendation and appends them until 10 products are returned.

---

## 4. How to Open a Shoe (Details Screen)
* If you see a shoe you like, you can click on its card or click the **View Details** button.
* This opens a dedicated page showing:
  * A large image of the shoe.
  * Full specifications (Model, Type, Gender, Colorway, Materials, and Retail Price).
  * A detailed description of the design.
  * A **View on StockX** button, which will open the shoe's StockX listing in a new browser tab.

---

## 5. How Similar Products Work
At the bottom of the details page, you will see a section called **Check Out Similar Sneakers**.
* I built this to show 20 shoes that look or perform like the one you are viewing.
* It uses Brand, Type, Gender, Material, Colors, and vector embeddings (Identity & Description) to calculate a unified similarity score.
* If you click on any of these similar shoes, the page will update instantly to show that shoe's details.

---

## 6. Example Searches to Try
Here are some search terms you can type to test the system:
* `nike running shoes`
* `black canvas skate shoes`
* `retro basketball high tops for men`
* `comfortable casual sneakers`
