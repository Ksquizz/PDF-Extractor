Hey! 

Thank you for installing some important information is listed below:

=== Preambles ===

This tool is a WIP this is the V1.0.0 release. You may encounter some bugs and glitches - if you do please reach out to me and I can revise it for the next version
I am working on this tool in the background so updates may be slow but if they are urgent, I will fix ASAP.
I am planning on updating the tool to include OCR detection so it's more usable across other older PDF types.

== What is this tool for? ==

The primary focus of this tool is to cut that damn manual task of interpreting information off a PDF. In my role I have to look at tons of PDF's take values/info from them and compile them, typically in excel. So, this tool helps cut down the manual-ness of it.

When booting the app up for the first time, it may take a moment to build the libraries and initiate the script so please be patient.

== How to use the tool == 

 -- Loading a PDF or PDF's --

    To import PDF(s) please find the "PDF manager" at the top ribbon. Open it and click "import PDF". This will allow you to select the PDF(s) in a folder and import them to the tool.

    Following this the selected PDF's can be seen in the window below the "Selected PDFs" window.

    Double click or select a PDF to show it in your main UI. You're now ready to scrape!!

-- Scraping Tools --

    There are currently only two scraping tools (this is set to change in upcoming updates)
    Below is a description of they work

        IMPORTANT!!

    What the programme sees and what text/values are selectable is visible on the right next to the Export Order - hover over a word in a PDF to check out what it can see.

     --- "Word Selector" ---
     TLDR: Select a certain word or value.

        Certainly, needs a rename (thanks future me)!
        Example Application: This tool can select a certain word on a PDF e.g "The Boy Ran Away" = I want to select "Ran" so I click on ran and the rest of the sentence is ignored.

    --- "Box Selector" --- 
        TLDR: Select a whole sentence or an area where values/words may appear to limit exclusion error.

        This is the main tool (the tool I use most). Use it for long form sentences or values that can vary in place of a PDF to select a total area to scan.

        BE CAREFUL not to accidentally highlight another sentence/value as it can pick it up and mess with your results

        Example Application: If you have a sentence and the tool cuts it off e.g "The Boy Ran away" using the "Word Selector Tool" I can only select "Ran" :'(). If I want to select the whole sentence, I can use the "Box Selector" to drag and draw a box around my area to extract the whole sentence!

    --- "Resize Mode" ---
        TLDR: Resize a drawn "Box Selector" area.

        Example Application: If I have accidentally drawn the box in the wrong place or it does not fit the area, I want it to scan I can select this tool using the green corner points to reshape it!

== Important Note == 
    Do not rely on this tool to scrape really really important data, it can make mistakes and you should always check the output as it can miss things and make errors

=== Upcoming Updates in order of priority ===

What you can expect in the next few updates..:

-Work in an option to fit all PDF's to the exact same place that the main PDF is in as auto tool/application to all PDF's button (have an option to move one PDF to align with the boxes) or crop PDF's and option to apply to all or just one.
-Have the option to individually update the box areas on any specific PDF.
-Have an option to delete all items in the export order.
-Have an option to choose what page you want to select from (gives a quick preview pane so you can easily identify). Still sticking to 1 page max.
-Fix the resize option so it only appears when selecting the resize option and everything else disappears if you click off it.
-Fix the accuracy of the extraction, giving an option for easy QA - similar to what we already have need to build off it.
-Create a loading bar when exporting due to it seeming like it just freezes
-Change the wording of the buttons to something clearer as it's rather confusing
-Produce a new tab with the exported results from the programme have the option to save as excel or txt or copy to clipboard depending on usage

=== Later Updates (once above are fixed): ===

-Make the UI more pretty and easier to use (move away from tkinter base models).
-Upgrade to implement OCR and try the best to make it accurate at exporting and reading data (should be good when fixing the PDF alignment/cropping).
-Maybe implement a fallback option if the data doesn't look right (jumple of letter and numbers) give an option to turn this off or give an advanced filtering option e.g if something has a unique ID which may be confused

Anyways enough waffling... please enjoy.

Developer/Creator - Ksquizz
