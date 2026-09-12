// The only saved-Guild geometry migration in the portal pilot. A frozen legacy
// fingerprint authorizes exactly the mouth's 3 x 4 x 9 cells; never the campus.
export function createGuildDoorAperture({ world, fingerprint, report = () => {} }) {
  const key = "fc_guild_door_aperture_v1";
  const finite = (p) => p && [p.x,p.y,p.z].every(Number.isFinite);
  let nextAttempt = 0;
  function ready(source, tick = 0) {
    if (!finite(source) || !fingerprint || fingerprint.version !== 1) return false;
    let record;
    try { record = JSON.parse(world.getDynamicProperty(key) ?? "null"); } catch { return false; }
    const origin = { x: Math.floor(source.x), y: Math.floor(source.y), z: Math.floor(source.z) };
    const signature = `${source.dimension ?? "minecraft:overworld"}|${origin.x}|${origin.y}|${origin.z}`;
    if (record && (record.schema !== 1 || record.source !== signature || !["clearing","ready"].includes(record.phase))) return false;
    if (tick < nextAttempt) return false;
    const dim = world.getDimension(source.dimension ?? "minecraft:overworld");
    const cells = [];
    let i = 0;
    const [sx,sy,sz] = fingerprint.size;
    const [ox,oy,oz] = fingerprint.min;
    if (sx !== 3 || sy !== 4 || sz !== 9 || fingerprint.indices.length !== sx*sy*sz) return false;
    try {
      for (let x=0;x<sx;x++) for (let y=0;y<sy;y++) for (let z=0;z<sz;z++) {
        const at = {x:origin.x+ox+x,y:origin.y+oy+y,z:origin.z+oz+z};
        const block = dim.getBlock(at);
        const expected = fingerprint.palette[fingerprint.indices[i++]];
        if (!block) return false;
        // Fully generated new throat is air; a partial authorized clear resumes.
        // A foreign block aborts before ANY mutation, preserving player work.
        if (block.typeId !== "minecraft:air" && block.typeId !== expected) {
          nextAttempt = tick + 200;
          report("Guild doorway differs from its recorded geometry; portal waits for a clear mouth.");
          return false;
        }
        cells.push(block);
      }
      // Verify usable floor through the whole tunnel, without placing any floor
      // over player edits, liquids or lost blocks in an existing world.
      const floors = new Set(["minecraft:cobblestone","minecraft:mossy_cobblestone", "minecraft:grass_block", "minecraft:stone_bricks"]);
      for (let x=-1;x<=1;x++) for (let z=0;z<9;z++) {
        if (!floors.has(dim.getBlock({x:origin.x+x,y:origin.y-1,z:origin.z+z})?.typeId)) return false;
      }
      if (record?.phase === "ready") return cells.every((b)=>b.typeId === "minecraft:air");
      world.setDynamicProperty(key,JSON.stringify({schema:1,source:signature,phase:"clearing"}));
      for (const b of cells) if (b.typeId !== "minecraft:air") b.setType("minecraft:air");
      if (!cells.every((b)=>b.typeId === "minecraft:air")) return false;
      world.setDynamicProperty(key,JSON.stringify({schema:1,source:signature,phase:"ready"}));
      return true;
    } catch { return false; }
  }
  return { ready };
}
