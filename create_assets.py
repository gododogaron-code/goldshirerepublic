import os

classes_dir = r"d:\сайт\static\images\classes"
avatars_dir = r"d:\сайт\static\images\avatars"

os.makedirs(classes_dir, exist_ok=True)
os.makedirs(avatars_dir, exist_ok=True)

class_svgs = {
    "warrior": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#1e1814" stroke="#c79c6e" stroke-width="2"/>
        <g stroke="#c79c6e" stroke-width="3" stroke-linecap="round" fill="none">
            <line x1="16" y1="48" x2="48" y2="16"/>
            <line x1="12" y1="44" x2="20" y2="52"/>
            <line x1="48" y1="48" x2="16" y2="16"/>
            <line x1="52" y1="44" x2="44" y2="52"/>
        </g>
        <circle cx="32" cy="32" r="7" fill="#855328" stroke="#c79c6e" stroke-width="2"/>
        <circle cx="32" cy="32" r="3" fill="#f5d6ba"/>
    </svg>''',
    
    "paladin": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#20111a" stroke="#f58cba" stroke-width="2"/>
        <g fill="#f58cba">
            <!-- Holy Warhammer -->
            <rect x="22" y="16" width="20" height="12" rx="2" fill="#f58cba" stroke="#fff" stroke-width="1"/>
            <rect x="30" y="28" width="4" height="24" rx="1" fill="#e0629b"/>
            <!-- Holy Aura rays -->
            <polygon points="32,8 30,14 34,14" fill="#fff"/>
            <polygon points="14,22 20,20 20,24" fill="#fff"/>
            <polygon points="50,22 44,20 44,24" fill="#fff"/>
            <circle cx="32" cy="22" r="3" fill="#fff"/>
        </g>
    </svg>''',

    "hunter": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#141c10" stroke="#abd473" stroke-width="2"/>
        <g stroke="#abd473" stroke-width="3" stroke-linecap="round" fill="none">
            <!-- Curved Bow -->
            <path d="M20 16 C36 24 36 40 20 48" stroke="#abd473" stroke-width="4"/>
            <line x1="20" y1="16" x2="20" y2="48" stroke="#e2f5b5" stroke-width="1.5"/>
            <!-- Arrow -->
            <line x1="16" y1="32" x2="48" y2="32" stroke="#fff" stroke-width="2"/>
            <polygon points="48,28 54,32 48,36" fill="#abd473" stroke="none"/>
            <line x1="16" y1="29" x2="19" y2="32" stroke="#abd473" stroke-width="1.5"/>
            <line x1="16" y1="35" x2="19" y2="32" stroke="#abd473" stroke-width="1.5"/>
        </g>
    </svg>''',

    "rogue": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#1c1c0c" stroke="#fff569" stroke-width="2"/>
        <g fill="#fff569">
            <!-- Dagger 1 -->
            <path d="M22 14 L28 20 L24 38 L20 40 L20 34 Z"/>
            <rect x="18" y="38" width="8" height="3" rx="1"/>
            <rect x="21" y="41" width="2" height="9" fill="#eab308"/>
            <circle cx="22" cy="51" r="2" fill="#fff569"/>
            <!-- Dagger 2 -->
            <path d="M42 14 L36 20 L40 38 L44 40 L44 34 Z"/>
            <rect x="38" y="38" width="8" height="3" rx="1"/>
            <rect x="41" y="41" width="2" height="9" fill="#eab308"/>
            <circle cx="42" cy="51" r="2" fill="#fff569"/>
            <!-- Poison Drop -->
            <path d="M32 26 C30 30 30 34 32 36 C34 34 34 30 32 26 Z" fill="#84cc16"/>
        </g>
    </svg>''',

    "priest": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#1e242c" stroke="#ffffff" stroke-width="2"/>
        <g fill="#ffffff">
            <!-- Holy Halo -->
            <ellipse cx="32" cy="18" rx="14" ry="4" fill="none" stroke="#fef08a" stroke-width="2"/>
            <!-- Wings & Ankh / Cross -->
            <path d="M30 22 L34 22 L34 48 L30 48 Z"/>
            <path d="M22 28 L42 28 L42 32 L22 32 Z"/>
            <!-- Wing feathers -->
            <path d="M22 28 C16 30 12 38 16 46 C20 40 24 36 26 34 Z" fill="#e2e8f0"/>
            <path d="M42 28 C48 30 52 38 48 46 C44 40 40 36 38 34 Z" fill="#e2e8f0"/>
            <!-- Center Gem -->
            <circle cx="32" cy="30" r="3" fill="#38bdf8"/>
        </g>
    </svg>''',

    "deathknight": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#1f0a0e" stroke="#c41e3a" stroke-width="2"/>
        <g fill="#c41e3a">
            <!-- Runeblade Skull -->
            <path d="M24 20 C24 14 40 14 40 20 C42 24 42 30 38 34 L38 42 L26 42 L26 34 C22 30 22 24 24 20 Z" fill="#c41e3a"/>
            <!-- Glowing Ice Rune Eyes -->
            <circle cx="29" cy="24" r="2.5" fill="#38bdf8"/>
            <circle cx="35" cy="24" r="2.5" fill="#38bdf8"/>
            <!-- Blade -->
            <polygon points="32,42 28,52 32,58 36,52" fill="#71717a" stroke="#c41e3a" stroke-width="1"/>
            <line x1="32" y1="42" x2="32" y2="54" stroke="#38bdf8" stroke-width="1.5"/>
            <!-- Horns -->
            <path d="M25 18 C20 16 16 20 14 26 C17 25 21 24 23 23 Z" fill="#71717a"/>
            <path d="M39 18 C44 16 48 20 50 26 C47 25 43 24 41 23 Z" fill="#71717a"/>
        </g>
    </svg>''',

    "shaman": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#08182b" stroke="#0070de" stroke-width="2"/>
        <g>
            <!-- Elemental Totem -->
            <rect x="26" y="24" width="12" height="28" rx="2" fill="#78350f" stroke="#0070de" stroke-width="1.5"/>
            <!-- Totem Wings -->
            <rect x="16" y="28" width="32" height="6" rx="2" fill="#92400e"/>
            <!-- Lightning bolts -->
            <polygon points="32,10 27,22 33,22 29,32 37,20 31,20" fill="#38bdf8" stroke="#0070de" stroke-width="1"/>
            <!-- Eyes on totem -->
            <circle cx="29" cy="38" r="1.5" fill="#facc15"/>
            <circle cx="35" cy="38" r="1.5" fill="#facc15"/>
        </g>
    </svg>''',

    "mage": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#0b1e2e" stroke="#3fc7eb" stroke-width="2"/>
        <g>
            <!-- Arcane Orb -->
            <circle cx="32" cy="24" r="10" fill="none" stroke="#3fc7eb" stroke-width="2"/>
            <circle cx="32" cy="24" r="6" fill="#38bdf8" opacity="0.7"/>
            <circle cx="32" cy="24" r="3" fill="#ffffff"/>
            <!-- Staff -->
            <rect x="30" y="34" width="4" height="20" rx="1" fill="#78350f"/>
            <!-- Sparkles -->
            <polygon points="32,10 33,13 36,14 33,15 32,18 31,15 28,14 31,13" fill="#e0f2fe"/>
            <polygon points="18,22 19,24 21,25 19,26 18,28 17,26 15,25 17,24" fill="#e0f2fe"/>
            <polygon points="46,22 47,24 49,25 47,26 46,28 45,26 43,25 45,24" fill="#e0f2fe"/>
        </g>
    </svg>''',

    "warlock": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#180e28" stroke="#8787ed" stroke-width="2"/>
        <g>
            <!-- Demonic Horns & Fel Fire -->
            <path d="M22 28 C20 18 26 14 32 14 C38 14 44 18 42 28 C46 36 40 46 32 46 C24 46 18 36 22 28 Z" fill="#2e1065" stroke="#8787ed" stroke-width="2"/>
            <!-- Horns -->
            <path d="M24 20 C18 12 12 16 10 24 C14 23 18 22 22 22 Z" fill="#8787ed"/>
            <path d="M40 20 C46 12 52 16 54 24 C50 23 46 22 42 22 Z" fill="#8787ed"/>
            <!-- Fel green eyes & soul fire -->
            <circle cx="28" cy="28" r="2.5" fill="#22c55e"/>
            <circle cx="36" cy="28" r="2.5" fill="#22c55e"/>
            <path d="M30 46 C32 54 28 58 32 60 C36 58 32 54 34 46 Z" fill="#a855f7"/>
        </g>
    </svg>''',

    "druid": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect width="64" height="64" rx="8" fill="#241306" stroke="#ff7d0a" stroke-width="2"/>
        <g fill="#ff7d0a">
            <!-- Bear/Cat Paw Print -->
            <ellipse cx="32" cy="40" rx="9" ry="8" fill="#ff7d0a"/>
            <!-- Claws / Toes -->
            <circle cx="20" cy="28" r="4"/>
            <circle cx="28" cy="22" r="4.5"/>
            <circle cx="36" cy="22" r="4.5"/>
            <circle cx="44" cy="28" r="4"/>
            <!-- Nature Leaf overlay in center -->
            <path d="M32 34 C30 38 30 42 32 44 C34 42 34 38 32 34 Z" fill="#4ade80"/>
        </g>
    </svg>'''
}

for name, svg in class_svgs.items():
    with open(os.path.join(classes_dir, f"{name}.svg"), "w", encoding="utf-8") as f:
        f.write(svg.strip())

# Avatars representing WoW races / archetypes
avatar_data = {
    "human_male": ("#1d4ed8", "#fde047", "Human Paladin", '''
        <circle cx="32" cy="24" r="10" fill="#fed7aa"/>
        <path d="M22 20 C22 12 42 12 42 20 C40 18 36 16 32 16 C28 16 24 18 22 20 Z" fill="#78350f"/>
        <!-- Eyes -->
        <circle cx="28" cy="24" r="1.5" fill="#1e3a8a"/>
        <circle cx="36" cy="24" r="1.5" fill="#1e3a8a"/>
        <!-- Armor -->
        <path d="M18 52 C18 38 24 34 32 34 C40 34 46 38 46 52 Z" fill="#3b82f6" stroke="#eab308" stroke-width="2"/>
        <path d="M32 34 L32 52" stroke="#eab308" stroke-width="2"/>
    '''),
    "human_female": ("#2563eb", "#fde047", "Human Mage", '''
        <circle cx="32" cy="24" r="10" fill="#fed7aa"/>
        <!-- Long Hair -->
        <path d="M20 22 C20 12 44 12 44 22 C46 32 44 42 42 46 C38 34 38 20 32 20 C26 20 26 34 22 46 C20 42 18 32 20 22 Z" fill="#b45309"/>
        <!-- Eyes -->
        <circle cx="28" cy="24" r="1.5" fill="#0284c7"/>
        <circle cx="36" cy="24" r="1.5" fill="#0284c7"/>
        <path d="M18 54 C18 42 24 38 32 38 C40 38 46 42 46 54 Z" fill="#818cf8" stroke="#fbbf24" stroke-width="1.5"/>
    '''),
    "dwarf": ("#b45309", "#d97706", "Dwarf Warrior", '''
        <circle cx="32" cy="26" r="11" fill="#fed7aa"/>
        <!-- Big Beard -->
        <path d="M21 28 C21 44 26 50 32 52 C38 50 43 44 43 28 Z" fill="#c2410c"/>
        <path d="M26 36 L32 46 L38 36" stroke="#ea580c" stroke-width="2" fill="none"/>
        <!-- Iron Helmet -->
        <path d="M20 24 C20 14 44 14 44 24 L46 26 L18 26 Z" fill="#475569" stroke="#94a3b8" stroke-width="1.5"/>
        <circle cx="28" cy="24" r="1.5" fill="#0f172a"/>
        <circle cx="36" cy="24" r="1.5" fill="#0f172a"/>
    '''),
    "nightelf": ("#581c87", "#c084fc", "Night Elf Hunter", '''
        <circle cx="32" cy="25" r="9" fill="#c4b5fd"/>
        <!-- Long Ears -->
        <polygon points="23,24 8,14 24,20" fill="#c4b5fd"/>
        <polygon points="41,24 56,14 40,20" fill="#c4b5fd"/>
        <!-- Teal Hair -->
        <path d="M22 22 C22 12 42 12 42 22 C42 34 38 42 36 46 C34 34 36 20 32 20 C28 20 30 34 28 46 C26 42 22 34 22 22 Z" fill="#0d9488"/>
        <!-- Glowing Silver Eyes -->
        <ellipse cx="28" cy="25" rx="2" ry="1" fill="#f8fafc"/>
        <ellipse cx="36" cy="25" rx="2" ry="1" fill="#f8fafc"/>
        <path d="M18 54 C18 40 24 36 32 36 C40 36 46 40 46 54 Z" fill="#15803d" stroke="#a3e635" stroke-width="1.5"/>
    '''),
    "gnome": ("#0284c7", "#38bdf8", "Gnome Warlock", '''
        <circle cx="32" cy="28" r="12" fill="#ffedd5"/>
        <!-- Big Pink/Green Hair -->
        <path d="M18 26 C16 14 48 14 46 26 C50 18 42 10 32 10 C22 10 14 18 18 26 Z" fill="#ec4899"/>
        <!-- Big Curious Eyes -->
        <circle cx="27" cy="28" r="3" fill="#0284c7"/>
        <circle cx="37" cy="28" r="3" fill="#0284c7"/>
        <circle cx="28" cy="27" r="1" fill="#ffffff"/>
        <circle cx="38" cy="27" r="1" fill="#ffffff"/>
        <!-- Goggles -->
        <circle cx="27" cy="20" r="5" fill="none" stroke="#ca8a04" stroke-width="2"/>
        <circle cx="37" cy="20" r="5" fill="none" stroke="#ca8a04" stroke-width="2"/>
        <line x1="32" y1="20" x2="32" y2="20" stroke="#ca8a04" stroke-width="2"/>
        <path d="M20 54 C20 44 26 42 32 42 C38 42 44 44 44 54 Z" fill="#6b21a8"/>
    '''),
    "draenei": ("#1e3a8a", "#60a5fa", "Draenei Shaman", '''
        <circle cx="32" cy="26" r="10" fill="#93c5fd"/>
        <!-- Horns -->
        <path d="M22 22 C16 14 20 8 28 14 Z" fill="#3b82f6"/>
        <path d="M42 22 C48 14 44 8 36 14 Z" fill="#3b82f6"/>
        <!-- Tentacles / Tendrils -->
        <path d="M26 34 C24 42 22 46 24 50" stroke="#60a5fa" stroke-width="3" fill="none" stroke-linecap="round"/>
        <path d="M38 34 C40 42 42 46 40 50" stroke="#60a5fa" stroke-width="3" fill="none" stroke-linecap="round"/>
        <!-- Glowing blue eyes -->
        <ellipse cx="28" cy="25" rx="2" ry="1.2" fill="#eff6ff"/>
        <ellipse cx="36" cy="25" rx="2" ry="1.2" fill="#eff6ff"/>
        <!-- Naaru Crest forehead mark -->
        <polygon points="32,17 31,19 33,19" fill="#93c5fd"/>
        <path d="M18 54 C18 42 24 38 32 38 C40 38 46 42 46 54 Z" fill="#1e40af" stroke="#93c5fd" stroke-width="1.5"/>
    '''),
    "orc": ("#991b1b", "#dc2626", "Orc Warrior", '''
        <circle cx="32" cy="26" r="11" fill="#4ade80"/>
        <!-- Tusks -->
        <polygon points="26,35 24,28 28,34" fill="#fef08a"/>
        <polygon points="38,35 40,28 36,34" fill="#fef08a"/>
        <!-- Brow & Piercing Red Eyes -->
        <path d="M22 23 L32 26 L42 23" stroke="#166534" stroke-width="3" fill="none"/>
        <circle cx="27" cy="25" r="1.5" fill="#ef4444"/>
        <circle cx="37" cy="25" r="1.5" fill="#ef4444"/>
        <!-- Topknot Hair -->
        <circle cx="32" cy="14" r="4" fill="#18181b"/>
        <path d="M16 54 C16 40 22 36 32 36 C42 36 48 40 48 54 Z" fill="#7f1d1d" stroke="#e11d48" stroke-width="2"/>
    '''),
    "undead": ("#4c0519", "#9f1239", "Undead Rogue", '''
        <circle cx="32" cy="26" r="10" fill="#a1a1aa"/>
        <!-- Sunken Eyes & Glowing yellow pinpoints -->
        <circle cx="27" cy="24" r="3" fill="#18181b"/>
        <circle cx="37" cy="24" r="3" fill="#18181b"/>
        <circle cx="27" cy="24" r="1" fill="#facc15"/>
        <circle cx="37" cy="24" r="1" fill="#facc15"/>
        <!-- Stitched mouth / jaw metal straps -->
        <path d="M26 34 L38 34" stroke="#52525b" stroke-width="2"/>
        <line x1="28" y1="32" x2="28" y2="36" stroke="#71717a" stroke-width="1.5"/>
        <line x1="32" y1="32" x2="32" y2="36" stroke="#71717a" stroke-width="1.5"/>
        <line x1="36" y1="32" x2="36" y2="36" stroke="#71717a" stroke-width="1.5"/>
        <!-- Ragged Cloak -->
        <path d="M18 54 C18 42 24 38 32 38 C40 38 46 42 46 54 Z" fill="#27272a" stroke="#881337" stroke-width="1.5"/>
    '''),
    "tauren": ("#78350f", "#b45309", "Tauren Druid", '''
        <!-- Big Tauren Head & Snout -->
        <ellipse cx="32" cy="28" rx="12" ry="11" fill="#92400e"/>
        <!-- Large Horns -->
        <path d="M21 24 C10 16 10 6 18 10 C22 12 24 18 24 22 Z" fill="#fef08a"/>
        <path d="M43 24 C54 16 54 6 46 10 C42 12 40 18 40 22 Z" fill="#fef08a"/>
        <!-- Nose Ring -->
        <ellipse cx="32" cy="33" rx="5" ry="4" fill="#78350f"/>
        <circle cx="32" cy="37" r="3.5" fill="none" stroke="#eab308" stroke-width="1.5"/>
        <!-- Eyes -->
        <circle cx="26" cy="25" r="1.5" fill="#fef3c7"/>
        <circle cx="38" cy="25" r="1.5" fill="#fef3c7"/>
        <!-- Leather armor -->
        <path d="M14 54 C14 38 20 34 32 34 C44 34 50 38 50 54 Z" fill="#451a03" stroke="#d97706" stroke-width="2"/>
    '''),
    "troll": ("#065f46", "#10b981", "Troll Shaman", '''
        <circle cx="32" cy="26" r="10" fill="#2dd4bf"/>
        <!-- Long Upward Tusks -->
        <path d="M24 34 C20 30 18 20 20 16 C22 22 24 28 26 32 Z" fill="#fef9c3"/>
        <path d="M40 34 C44 30 46 20 44 16 C42 22 40 28 38 32 Z" fill="#fef9c3"/>
        <!-- Long Ears -->
        <polygon points="23,26 12,20 24,22" fill="#2dd4bf"/>
        <polygon points="41,26 52,20 40,22" fill="#2dd4bf"/>
        <!-- Mohawk -->
        <path d="M29 18 C28 8 36 8 35 18 Z" fill="#ef4444"/>
        <!-- Yellow glowing eyes -->
        <circle cx="28" cy="24" r="1.5" fill="#eab308"/>
        <circle cx="36" cy="24" r="1.5" fill="#eab308"/>
        <path d="M18 54 C18 42 24 38 32 38 C40 38 46 42 46 54 Z" fill="#0f766e" stroke="#2dd4bf" stroke-width="1.5"/>
    '''),
    "bloodelf": ("#991b1b", "#f59e0b", "Blood Elf Mage", '''
        <circle cx="32" cy="25" r="9" fill="#fde68a"/>
        <!-- Long Pointy Ears -->
        <polygon points="23,24 10,16 24,20" fill="#fde68a"/>
        <polygon points="41,24 54,16 40,20" fill="#fde68a"/>
        <!-- Golden / Blonde Hair -->
        <path d="M21 21 C21 11 43 11 43 21 C45 32 43 42 41 46 C37 32 38 19 32 19 C26 19 27 32 23 46 C21 42 19 32 21 21 Z" fill="#eab308"/>
        <!-- Glowing Emerald Green Eyes -->
        <ellipse cx="28" cy="25" rx="2" ry="1.2" fill="#22c55e"/>
        <ellipse cx="36" cy="25" rx="2" ry="1.2" fill="#22c55e"/>
        <circle cx="28" cy="25" r="0.8" fill="#ecfdf5"/>
        <circle cx="36" cy="25" r="0.8" fill="#ecfdf5"/>
        <!-- Regal Crimson Robe -->
        <path d="M18 54 C18 40 24 36 32 36 C40 36 46 40 46 54 Z" fill="#991b1b" stroke="#f59e0b" stroke-width="1.5"/>
    '''),
    "innkeeper": ("#78350f", "#f59e0b", "Innkeeper Farley", '''
        <circle cx="32" cy="25" r="11" fill="#fed7aa"/>
        <!-- Friendly Brown Beard & Mustache -->
        <path d="M23 28 C23 42 28 48 32 48 C36 48 41 42 41 28 Z" fill="#78350f"/>
        <path d="M26 31 C28 34 36 34 38 31" stroke="#451a03" stroke-width="2" fill="none"/>
        <!-- Balding brown hair -->
        <path d="M20 24 C19 18 23 14 32 14 C41 14 45 18 44 24 Z" fill="#451a03"/>
        <circle cx="32" cy="20" r="8" fill="#fed7aa"/>
        <!-- Kind eyes and smile -->
        <circle cx="28" cy="24" r="1.5" fill="#3b2413"/>
        <circle cx="36" cy="24" r="1.5" fill="#3b2413"/>
        <!-- Tavern Apron & Mug -->
        <path d="M16 54 C16 40 22 36 32 36 C42 36 48 40 48 54 Z" fill="#f8fafc" stroke="#b45309" stroke-width="2"/>
        <rect x="26" y="38" width="12" height="16" fill="#b45309" rx="1"/>
    ''')
}

for avatar_id, (bg_color, border_color, title, inner_svg) in avatar_data.items():
    full_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
    <defs>
        <radialGradient id="grad_{avatar_id}" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="{border_color}" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="{bg_color}" stop-opacity="0.8"/>
        </radialGradient>
    </defs>
    <rect width="64" height="64" rx="32" fill="url(#grad_{avatar_id})" stroke="{border_color}" stroke-width="2.5"/>
    <g>
        {inner_svg}
    </g>
</svg>'''
    with open(os.path.join(avatars_dir, f"{avatar_id}.svg"), "w", encoding="utf-8") as f:
        f.write(full_svg.strip())

print("Created 10 class icons and 12 avatar icons successfully!")
