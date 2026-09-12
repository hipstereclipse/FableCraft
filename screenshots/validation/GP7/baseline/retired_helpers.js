function clearGuildRingScarecrows(dim, base) {
  if (world.getDynamicProperty("fc_guild_ring_scarecrows_removed")) return;
  const columns = [
    { x: GUILD.dueling.x - 2, z: GUILD.dueling.z - 2 },
    { x: GUILD.dueling.x + 2, z: GUILD.dueling.z + 2 },
    { x: GUILD.dueling.x + 2, z: GUILD.dueling.z - 2 },
  ];
  for (const column of columns) {
    for (let y = 1; y <= 3; y++) {
      try {
        const block = dim.getBlock({
          x: base.x + column.x,
          y: base.y + y,
          z: base.z + column.z,
        });
        if (block?.typeId === "minecraft:hay_block"
          || block?.typeId === "minecraft:carved_pumpkin") {
          block.setType("minecraft:air");
        }
      } catch { }
    }
  }
  world.setDynamicProperty("fc_guild_ring_scarecrows_removed", true);
}

function repairGuildDemonApproach(dim, base) {
  if (world.getDynamicProperty("fc_guild_demon_approach_v2")) return;
  let complete = true;
  const setCobble = (x, z, clearHeadroom) => {
    try {
      const ground = dim.getBlock({
        x: base.x + x,
        y: base.y,
        z: base.z + z,
      });
      if (!ground) {
        complete = false;
        return;
      }
      ground.setType((x + z) % 4 === 0
        ? "minecraft:mossy_cobblestone"
        : "minecraft:cobblestone");
      if (!clearHeadroom) return;
      const headroom = dim.getBlock({
        x: base.x + x,
        y: base.y + 1,
        z: base.z + z,
      });
      if (headroom) headroom.setType("minecraft:air");
      else complete = false;
    } catch { complete = false; }
  };

  const bridgeX = GUILD.demon.x - 1;
  const bridgeZ = 84;
  const pathLength = GUILD.demon.z - 1 - bridgeZ;
  for (let z = bridgeZ; z < GUILD.demon.z; z++) {
    const x = Math.round(bridgeX
      + (GUILD.demon.x - bridgeX) * (z - bridgeZ) / pathLength);
    for (const pathX of [x, x + 1]) {
      setCobble(pathX, z, z > bridgeZ + 1);
    }
  }

  // Join the east-bank cobblestone network to the bridge's bank-side apron.
  const bankX = GUILD.demon.x + 9;
  const bankZ = 76;
  const eastPathX = GUILD.demon.x + 16;
  const eastPathZ = 80;
  const eastSteps = Math.max(Math.abs(eastPathX - (bankX + 2)),
    Math.abs(eastPathZ - bankZ), 1);
  for (let i = 0; i <= eastSteps; i++) {
    const x = Math.round(eastPathX + (bankX + 2 - eastPathX) * i / eastSteps);
    const z = Math.round(eastPathZ + (bankZ - eastPathZ) * i / eastSteps);
    for (let dx = 0; dx <= 1; dx++) {
      for (let dz = 0; dz <= 1; dz++) {
        setCobble(x + dx, z + dz, true);
      }
    }
  }

  // Remove only the island scarecrow closest to the Demon Door.
  const scarecrowX = GUILD.demon.x - 3;
  const scarecrowZ = GUILD.demon.z - 9;
  const parts = [
    { x: scarecrowX, y: 1, z: scarecrowZ, type: "minecraft:oak_fence" },
    { x: scarecrowX, y: 2, z: scarecrowZ, type: "minecraft:hay_block" },
    { x: scarecrowX, y: 3, z: scarecrowZ, type: "minecraft:carved_pumpkin" },
    { x: scarecrowX, y: 2, z: scarecrowZ - 1, type: "minecraft:oak_fence" },
    { x: scarecrowX, y: 2, z: scarecrowZ + 1, type: "minecraft:oak_fence" },
  ];
  for (const part of parts) {
    try {
      const block = dim.getBlock({
        x: base.x + part.x,
        y: base.y + part.y,
        z: base.z + part.z,
      });
      if (!block) {
        complete = false;
        continue;
      }
      if (block?.typeId === part.type) block.setType("minecraft:air");
    } catch { complete = false; }
  }
  if (complete) world.setDynamicProperty("fc_guild_demon_approach_v2", true);
}

