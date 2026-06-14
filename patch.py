import pathlib

p = pathlib.Path('packs/Fablecraft_BP/scripts/main.js')
c = p.read_text('utf-8')

# 1. Add call to placeGuildNear when join_guild quest is accepted
c = c.replace(
    '        p.sendMessage(`§e✦ Quest accepted: ${q.name}`);\n      });',
    '        p.sendMessage(`§e✦ Quest accepted: ${q.name}`);\n        if (q.id === "join_guild") placeGuildNear(p);\n      });'
)

# 2. Fix double const y
c = c.replace(
    '  const y = sampleGroundY(dim, base.x, base.z, 92, 100);\n  // Be lenient with ground sampling for the initial Guild placement (allow liquid).\n  const y = sampleGroundY(dim, base.x, base.z, 92, 100, true);',
    '  // Be lenient with ground sampling for the initial Guild placement (allow liquid).\n  const y = sampleGroundY(dim, base.x, base.z, 92, 100, true);'
)

# 3. Add loading screen wrapper
# Find the start of the try block and replace it
orig_try = '''  if (y === null) return;
  try {
    // The Heroes' Guild is ONE connected 92x30x100 structure on a single floor'''
new_try = '''  if (y === null) return;
  
  p.onScreenDisplay.setTitle("§6Founding Guild...", { fadeInDuration: 0, stayDuration: 200, fadeOutDuration: 0, subtitle: "§ePlease wait..." });
  
  system.runTimeout(() => {
  try {
    // The Heroes' Guild is ONE connected 92x30x100 structure on a single floor'''
c = c.replace(orig_try, new_try)

# 4. Close the wrapper at the end of the placeGuildNear function
# We need to find the end of the try block. It looks like:
orig_end = '''      } catch { }
    }, 10);
  } catch { /* chunk not ready; retried by the structure sweep */ }
}'''

new_end = '''      } catch { }
    }, 10);
  } catch { /* chunk not ready; retried by the structure sweep */ }
  }, 5);
}'''
c = c.replace(orig_end, new_end)

p.write_text(c, 'utf-8')
print("Patched main.js")
