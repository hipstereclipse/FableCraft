# Library Arcanum original-game reference review

Reviewed 2026-09-12. A limited direct image comparison is now available for the
Guild pilot. This is a visual reference review, not a Bedrock engine test or an
exact reconstruction sign-off. No external image is embedded here or reused in
the pack.

## Source and provenance

Casey Loe / Kaizen Media Group, **Fable: The Lost Chapters, Prima Official Game
Guide**, Prima Games, 2005, ISBN 0-7615-5180-8. The copyright and contents page
(PDF page 2) identifies the 2005 TLC edition. The screen in **PDF page 38,
printed page 37**, under *New Opportunities at the Heroes' Guild / Opening the
Demon Door*, visibly displays the location name **The Library Arcanum**. This
contemporary guide establishes original-era game imagery; it predates
Anniversary. It does not identify the platform/build used for that particular
screen.
[Source PDF hosted by OGXbox](https://www.ogxbox.co.uk/media/com_eshop/attachments/Fable_The_Lost_Chapters_Strategy_Guide_Book.pdf).

The complete relevant page and copyright page were rendered with Poppler and
visually inspected. The embedded gameplay image was also extracted directly
with `pdfimages`; its native resolution is only **207 x 153 pixels**. Enlarging
the page adds no original detail. All downloaded and extracted material remains
in ignored scratch, confirmed with `git check-ignore`:

- PDF: `tmp/conformance/reference-arcanum/prima-tlc-guide.pdf`
- Copyright page: `tmp/conformance/reference-arcanum/prima-tlc-page-02.png`
- Relevant full page: `tmp/conformance/reference-arcanum/prima-tlc-page-38.png`
- Native gameplay image: `tmp/conformance/reference-arcanum/guide-p38-img-009.png`

SHA-256 of the source PDF:
`0872726adb299a10c94b31d482aecb540d740bf61fab1f22cb08cdcf81ae1a2b`.
SHA-256 of the extracted gameplay PNG:
`3171577a9503e2188aace301c9dcae8ba34803c592149e61c3fc156e109caacf`.

## Bounded comparison

Compared against the project's original generated overview
`screenshots/validation/DP1/geometry/arcanum-library-view.png`. That image is an
isometric voxel preview with invisible barriers omitted. Its camera and lighting
are not equivalent to the original gameplay camera.

| Visible original evidence | Current preview and implication |
| --- | --- |
| The Hero stands on earthy ground in a green clearing, framed by textured upright edges in the foreground and dark vertical forms behind. | Trees, grass and enclosing rock give the pilot the relevant outdoor setting. Exact cliff profiles, shelf heights and distances cannot be recovered from this small view. |
| Bright and shaded areas break up the ground; the visible edge/path through the clearing is irregular. | The pilot's long straight paved axis and rectangular joins read as a more formal garden. A future pass should soften the visible ground transitions while retaining safe traversable paths. |
| An orange/gold chest is clearly visible to the right of the Hero in this camera, on a bright patch of grass. | The pilot places its main reward on the central route with a distinct approach. Compare from a matching player-height view before deciding whether the chest should move; the screenshot does not establish a compass direction or complete reward layout. |
| Much of the background is dark beneath vegetation. | The preview's bright overhead view cannot validate the original enclosed, shaded mood. This needs an in-game player-height capture and lighting review. |

The image does **not** independently establish the complete pond outline,
butterflies, both book locations, the reading table, the return portal, room
dimensions or all boundary geometry. Those remain supported by the separate
written references or unverified. Do not infer absence from the camera crop.

## Next review actions

DP2 applies the bounded ground-treatment finding: 426 y2 surface blocks become
irregular earth/grass patches; other geometry and all persistent room anchors
remain unchanged. Its inspected overview is
`screenshots/validation/DP2/arcanum-earth-overview.png`. This addresses the formal
paving appearance only. The comparison above records the original DP1 baseline.

1. Capture the pilot in Bedrock from player height at its arrival and near its
   chest; compare vegetation enclosure, ground transitions and reward visibility.
2. Seek an original TLC traversal or a higher-resolution original screenshot
   before changing unseen topology or claiming close dimensional fidelity.
3. Keep all external reference pixels in ignored scratch. Any geometry and
   textures shipped by the project must remain original.

Local architecture notes were checked first and contained prose, not an
inspectable original room image. Web image/video searches mostly returned other
locations, Anniversary, or unrelated games. The Fandom page could not be opened
directly in this session; the web PDF viewer rejected the guide's size. A direct
download followed by local Poppler inspection produced the verified view above.
