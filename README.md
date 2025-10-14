# PDF Scraper Tool (v1.0.0)

Hey!

Thank you for installing, some important information is listed below please read before using, so you don't get lost! Or do it's part of the fun!:

---

## 📑 Table of Contents
- [Preambles](#-preambles)
- [What Is This Tool For?](#-what-is-this-tool-for)
- [How to Use the Tool](#-how-to-use-the-tool)
  - [Loading PDFs](#-loading-a-pdf-or-pdfs)
  - [Scraping Tools](#-scraping-tools)
- [Important Note](#-important-note)
- [Upcoming Updates](#-upcoming-updates-in-order-of-priority)
- [Later Updates](#-later-updates)
- [Requirements](#-requirements)
- [Developer](#-developer)

---

## ⚙️ Preambles

> **Note:** This tool is a **Work in Progress (WIP)** — Current release = `V1.0.0`.

You may encounter some bugs or glitches — if you do, please **reach out** to me and I can revise them for the next version.

- I’m working on this tool in the background, so updates may be slow.  
- If issues are urgent/tool-breaking, I’ll fix them ASAP.  
- I’m planning to update the tool to include **OCR detection** so it’s more usable across older PDF types.

---

## 📘 What Is This Tool For?

The primary focus of this tool is to **eliminate the manual task** of extracting and interpreting information from PDFs.  

In my role, I often have to look at tons of PDFs, take values/info from them, and compile them in Excel.  
This tool helps cut down the manual effort of that process.

> When booting the app for the first time, it may take a moment to build the libraries and initialize the script — please be patient!

---

## 🧭 How to Use the Tool

### 📂 Loading a PDF or PDFs

1. Open the **“PDF Manager”** at the top ribbon.  
2. Click **“Import PDF”**, this allows you to select one or more PDFs from a folder.  
3. The selected PDFs will appear in the window below **“Selected PDFs.”**  
4. Double-click or select a PDF to show it in the main UI.  
5. You’re now ready to scrape!

---

### 🧰 Scraping Tools

There are currently two scraping tools (more coming soon!).  
Below is a description of how they work:

#### ⚠️ Important
What the program sees and what text/values are selectable, is visible on the right next to the **Export Order**.  
Hover over a word in a PDF to check what the tool can “see.”

---

#### ✏️ Word Selector
**TL;DR:** Select a specific word or value.

Example:  
If a PDF contains the sentence **“The Boy Ran Away”** and you only want the word **“Ran,”** click it — the rest of the sentence will be ignored.

---

#### 🧱 Box Selector
**TL;DR:** Select a full sentence or area to reduce exclusion errors.

⚠️ Be careful not to accidentally include extra text, as it may affect your results.

Example:  
If you want a sentence like *“The Boy Ran away”* instead of just the word "Ran", when using the Word Selector, this is the tool for you. Instead use the **Box Selector** to draw a box around the whole sentence for full extraction.

---

#### 🔲 Resize Mode
**TL;DR:** Resize a drawn **Box Selector** area.

Example:  
If the box is misplaced or too small, select **Resize Mode** and use the green corner points to reshape it.

---

## ❗ Important Note

Do **not** rely on this tool for scraping highly sensitive or critical data.  
It can make mistakes — always check the output, as it may miss or misinterpret information.

---

## 🚀 Upcoming Updates (in order of priority)

Here’s what you can expect in future updates:

- Add an option to align all PDFs to the same position as the main PDF (auto-apply to all or single).  
- Allow individual box area updates on any PDF.  
- Add a feature to delete all items in the export order.  
- Add a quick preview pane for choosing which page to select from (still limited to one page max).  
- Fix resize mode visibility (only appears when selected).  
- Improve extraction accuracy and build better QA options.  
- Add a **loading bar** when exporting (to avoid looking like it froze).  
- Simplify and clarify button wording.  
- Add a new tab for exported results with options to:
  - Save as `.xlsx`
  - Save as `.txt`
  - Copy to clipboard

---

## 🧩 Later Updates

These will come after the above improvements:

- Improve the UI (move away from Tkinter-based models).  
- Implement OCR for better data reading and exporting.  
- Add an **advanced filtering or fallback option** when data looks incorrect (e.g., garbled letters/numbers).

---

## 📦 Requirements

If you are a dev looking to adapt or use the tool. Use the `requirements.txt` file from the source code and run:

`pip install -r requirements.txt`

Failing that run:

`pip install PyMuPDF tkinter pandas openpyxl pillow`

---

## Developer

**Created and Designed By:** [Ksquizz] (https://github.com/Ksquizz)

If you have feedback or find a bug, please open and **issue** at: (https://github.com/Ksquizz/PDF-Extractor/issues)

*Like this project, feel free to leave it a star!!* ⭐
