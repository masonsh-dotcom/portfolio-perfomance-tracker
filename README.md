# Portfolio Performance Tracker

CISC106 Drafter project by Mason Shimp. Add holdings with manually entered USD prices, update prices or remove holdings, and see the cost basis, current value, gain or loss, and return. In Settings, name the portfolio, set a goal, and record cash deposits.

Holdings and settings last for the current session. Reloading the site resets the portfolio. Goal progress uses stock value plus cash. Stock return is the gain or loss divided by the cost basis of the currently tracked holdings.

## Run locally

In Thonny, open `main.py`, install Drafter 2.1.2 under **Tools → Manage packages** if needed, and choose **Run**. With Python 3.10 or later, you can also run these commands from the project folder.

```text
python -m pip install -r requirements.txt
python -m unittest -v
python main.py
```

The unit tests cover all 11 routes, including the root alias, and check valid and invalid input. To build the static site locally, run `python -m drafter main.py --compile` from this folder. Serve it with `python -m http.server 8000 --directory dist` and open `http://localhost:8000/`.

## Publish on GitHub Pages

1. Complete the disclosure review below. Create a public GitHub repository named `portfolio-performance-tracker`. A default branch named `main` matches the included workflow.
2. Put the contents of this folder at the repository root, including `.github/workflows/pages.yml`, `main.py`, `test_tracker.py`, `requirements.txt`, both worksheet files, and the complete AI transcript. If you upload files through GitHub's website, create `.github/workflows/pages.yml` by entering that full path under **Add file → Create new file** and pasting the included workflow. Use a commit message such as **Add portfolio tracker and course materials**.
3. Open **Settings → Pages**. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Open **Actions → Publish portfolio tracker → Run workflow**, select `main`, and run it. It installs Drafter, runs the tests, compiles the app, and deploys only the built site. The course materials are in the public repository.
5. After the run turns green, copy the URL from the `github-pages` deployment or **Settings → Pages**. It typically looks like `https://YOUR-USERNAME.github.io/portfolio-performance-tracker/`. Open it in a private browser window, complete the check below, and submit the working website URL to Canvas.

If the first run failed before Pages was enabled, set the Pages source and run the workflow again. For later source changes on `main`, the workflow runs automatically. Open the failed step in **Actions** for any error details.

[Drafter publishing guide](https://drafter-edu.github.io/drafter/your-project/deploy/github-pages/) · [GitHub Pages workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

## Check the published site

1. Add `AAPL` with 10 shares, a purchase price of 150, and a current price of 175. Holdings should show a value of **$1,750.00** and a gain of **$250.00 (+16.67%)**.
2. Edit the holding to 180. In Settings, enter a portfolio name, a goal of 2,000, and a cash deposit of 100. Home should show **$1,900.00**. Summary should show a **$300.00 (+20.00%)** stock gain and **95.0%** goal progress.
3. Try adding a holding with zero shares and check for the validation message. Remove AAPL and confirm the cash balance is still **$100.00** and the stock return is unavailable.

The course's overall project requirements also call for a linked video showing and explaining the live site. Add the video link here when you record it.

## Review the course materials before uploading

- The two original worksheets are in `worksheets/`. The brainstorming worksheet includes a school email address. Review both files, including images and document properties, for any information you want to keep private. Ask course staff how to handle any privacy edits to materials they require in the public repository.
- The design worksheet currently says no LLM was used. The earlier project chat contains design assistance. Review that statement and make sure your disclosure reflects the assistance you used.
- `AI-CONVERSATION.md` contains the retrieved planning and development conversations. Include every project-related user message and assistant reply from any other AI chats you used. The assignment requires the conversations themselves. If private details such as grades or school contact information appear, ask course staff how they want those handled while preserving the required record.
