# Bounded third-door reference follow-up

Scratch only, 2026-09-13. No production file or source/room asset changed. Seven distinct external candidate URLs were attempted, plus two pages of the already retained TLC guide. Search results for Anniversary, later games, mixed Reddit accounts and modding were excluded. The extra proposed Steam follow-up script was never run.

## Confirmed guide detail

The retained original **Fable: The Lost Chapters Prima guide** was not downloaded again. Its SHA256 is `0872726adb299a10c94b31d482aecb540d740bf61fab1f22cb08cdcf81ae1a2b`; original URL is in `manifest.json`.

I visually inspected the complete `prima-p110.png` (PDF110, printed109) and `prima-p108.png` (PDF108, printed107). The Cutlass Bluetane row identifies a legendary light cleaver, damage165, value40425 and the Greatwood Caves Demon Door. It shows **one filled Lightning augmentation and no empty socket rings**. The symbol matches the labeled Lightning key on PDF108. Adjacent ordinary cleavers visibly use empty rings, so the row does not support an extra free slot. The guide’s weapon icon is only71×71 pixels; its installed-augmentation icon is35×35. Rendering the full page larger adds no source detail.

## Retrieved pixels and limitations

Both direct mirror images were downloaded, hashed and viewed at their actual sizes. `mirror-greatwood-caves.jpg` is280×210: a pointed inset stone doorway, surrounding curved stonework, rocky sides, twin warm lights and a Hero obscuring its lower center. `mirror-cutlass-bluetane.jpg` is250×257: a broad dark cleaver with an irregular notched edge, pointed upper corner, wrapped narrow grip and one Lightning emblem in the inventory panel.

Their actual parent page was read through the web tool under the title *Fable: The Lost Chapters Game Guide & Walkthrough*, with corresponding Greatwood Caves and Cutlass Bluetane image links. Its raw HTML fetch returned403; that failure is retained. The classic UI and the weapon silhouette’s agreement with the retained guide support provisional reference use, but this mirror has no verified original capture date/build/mod history. Do not count either image as a newly accepted original-edition corpus source yet.

Steam app204030 `butterfly` and `greatwood` listing HTML was retained and inspected. The former returned seven cards about Hero butterflies; the latter returned two cards for Greatwood Forest/Lake. `steam-card-inventory.json` records exact IDs, app IDs, titles and direct image links. Individual Steam images were not downloaded or visually inspected; their unseen contents are not claimed as evidence.

## Remaining gap

No new larger original-edition verified **Butterfly House interior** was recovered. The retained guide’s PDF174214×123 dark interior frame still does not settle the complete room shape, walls, roof, route, chest/end placement, furniture or metric dimensions. The name alone cannot justify greenhouse or Arboretum architecture.

`manifest.json` records exact source/direct URLs, all file hashes, dimensions, attempted failures and edition limits. `fetch-results.json` preserves the initial sandbox DNS failure; `fetch-network-results.json` preserves the successful public retrievals and mirror403. An attempted optional PyMuPDF inventory helper found the module unavailable; the successful `pdfimages -list` inventory is retained as `prima-image-inventory.txt`.
