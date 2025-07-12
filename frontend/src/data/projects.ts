export const projects = [
  {
    title: "Bilik Persalinan",
    genre: "Feature Film • Drama",
    status: "ACTIVE",
    statusColor: "bg-yellow-400 text-black",
    budget: "$850K",
    dueDate: "Dec 15, 2024",
    team: "12 members",
    createdAt: "2024-11-15T08:00:00.000Z", // Older project
    // --- Script Breakdown Data ---
    scriptBreakdown: {
      scenes: [
        {
          number: 1,
          heading: "INT. HOSPITAL LOBBY - DAY",
          location: "Hospital Lobby",
          time: "Day",
          characters: ["NURUL", "RECEPTIONIST"],
          props: ["Reception desk", "Chairs", "Files"],
          wardrobe: ["Nurse uniform", "Casual"],
          sfx: [],
          notes: "Establishing scene",
          budget: "RM 2,000",
          dialogues: [
            {
              character: "NURUL",
              text: "Excuse me, I have an appointment with Dr. Amir at 2 PM."
            },
            {
              character: "RECEPTIONIST",
              text: "Of course, Mrs. Nurul. Please take a seat, the doctor will see you shortly."
            }
          ]
        },
        {
          number: 2,
          heading: "INT. BILIK PERSALINAN - DAY",
          location: "Delivery Room",
          time: "Day",
          characters: ["NURUL", "DR. AMIR", "MIDWIFE", "HUSBAND"],
          props: ["Hospital bed", "IV stand", "Baby cot", "Medical tools"],
          wardrobe: ["Scrubs", "Patient gown", "Blood makeup"],
          sfx: ["Baby cry SFX", "Heart monitor SFX"],
          notes: "Main delivery scene, emotional climax",
          budget: "RM 5,000",
          dialogues: [
            {
              character: "DR. AMIR",
              text: "Alright Nurul, you're doing great. Just a few more pushes."
            },
            {
              character: "NURUL",
              text: "I can't... it hurts so much!"
            },
            {
              character: "HUSBAND",
              text: "You're the strongest person I know. You can do this, sayang."
            },
            {
              character: "MIDWIFE",
              text: "The baby's head is crowning! One more big push!"
            }
          ]
        },
        {
          number: 3,
          heading: "INT. HOSPITAL CORRIDOR - DAY",
          location: "Hospital Corridor",
          time: "Day",
          characters: ["HUSBAND", "NURUL"],
          props: ["Wheelchair", "Signage", "Flowers"],
          wardrobe: ["Casual", "Nurse uniform"],
          sfx: [],
          notes: "",
          budget: "RM 1,500"
        },
        {
          number: 4,
          heading: "INT. DOCTOR'S OFFICE - DAY",
          location: "Doctor's Office",
          time: "Day",
          characters: ["DR. AMIR", "NURUL"],
          props: ["Desk", "Computer", "Medical charts"],
          wardrobe: ["Doctor's coat", "Nurse uniform"],
          sfx: [],
          notes: "",
          budget: "RM 1,000"
        },
        {
          number: 5,
          heading: "INT. BILIK PERSALINAN - NIGHT",
          location: "Delivery Room",
          time: "Night",
          characters: ["NURUL", "MIDWIFE", "BABY"],
          props: ["Hospital bed", "Baby blanket", "Oxygen mask"],
          wardrobe: ["Scrubs", "Newborn makeup"],
          sfx: ["Heart monitor SFX", "Lullaby music"],
          notes: "Quiet, intimate moment post-delivery",
          budget: "RM 3,000"
        },
        {
          number: 6,
          heading: "EXT. HOSPITAL PARKING - DAY",
          location: "Hospital Parking",
          time: "Day",
          characters: ["HUSBAND", "NURUL"],
          props: ["Car", "Parking signage", "Bag"],
          wardrobe: ["Casual", "Nurse uniform"],
          sfx: [],
          notes: "",
          budget: "RM 1,000"
        }
      ],
      elements: {
        characters: [
          { name: "NURUL", description: "Young nurse, empathetic, main protagonist. Age 28." },
          { name: "DR. AMIR", description: "Senior doctor, calm, experienced. Age 45." },
          { name: "MIDWIFE (PUAN SITI)", description: "Supportive, motherly. Age 50." },
          { name: "HUSBAND (FAIZAL)", description: "Anxious, supportive partner. Age 32." },
          { name: "RECEPTIONIST", description: "Minor role, friendly. Age 25." },
          { name: "BABY", description: "Newborn, female." }
        ],
        locations: [
          "Hospital Lobby",
          "Delivery Room (Bilik Persalinan)",
          "Hospital Corridor",
          "Doctor's Office",
          "Hospital Parking Lot"
        ],
        props: [
          "Hospital bed",
          "IV stand",
          "Baby cot",
          "Medical tools",
          "Wheelchair",
          "Flowers",
          "Computer",
          "Desk",
          "Baby blanket",
          "Oxygen mask",
          "Car"
        ],
        wardrobe: [
          "Nurse uniforms (blue/white)",
          "Doctor's coat",
          "Patient gown",
          "Casual wear (for husband)",
          "Blood and sweat makeup (for delivery)",
          "Newborn makeup (for baby)"
        ],
        sfx: [
          "Baby crying (SFX)",
          "Heart monitor beeping (SFX)",
          "Ambient hospital sounds (SFX)"
        ]
      },
      budget: {
        talent: "RM 8,000",
        location: "RM 5,000",
        propsSet: "RM 4,000",
        wardrobeMakeup: "RM 2,000",
        sfxVfx: "RM 1,000",
        crew: "RM 7,000",
        miscellaneous: "RM 3,000"
      },
      crew: [
        { role: "Director", name: "Dr. Farhan Azimi" },
        { role: "Producer", name: "Aznir Rahman" },
        { role: "DOP", name: "Siti Zainab" },
        { role: "Sound", name: "Hafizul Rahman" },
        { role: "Art Director", name: "Lim Wei Ling" },
        { role: "Wardrobe", name: "Aina Syahirah" },
        { role: "Makeup", name: "Nurul Izzah" }
      ],
      shootingSchedule: [
        { day: 1, scenes: [1, 3], location: "Hospital Lobby/Corridor", notes: "Establishing shots" },
        { day: 2, scenes: [2, 5], location: "Delivery Room", notes: "Main delivery scenes" },
        { day: 3, scenes: [4, 6], location: "Doctor's Office/Parking", notes: "Wrap-up scenes" }
      ]
    }
  },
  {
    title: "Urban Legends",
    genre: "Short Film • Horror",
    status: "REVIEW",
    statusColor: "bg-[#232733] text-white",
    budget: "$120K",
    dueDate: "Jan 20, 2025",
    team: "8 members",
    createdAt: "2024-12-01T10:30:00.000Z", // More recent than first project
    // --- Script Breakdown Data ---
    scriptBreakdown: {
      scenes: [
        {
          number: 1,
          heading: "EXT. ABANDONED SCHOOL - NIGHT",
          location: "Abandoned School",
          time: "Night",
          characters: ["AMIR", "LISA", "FARID"],
          props: ["Flashlight", "Old notebook", "Camera"],
          wardrobe: ["Casual", "Jacket"],
          sfx: ["Wind howling", "Distant footsteps"],
          notes: "Teens arrive at the haunted school.",
          budget: "RM 1,500"
        },
        {
          number: 2,
          heading: "INT. SCHOOL HALLWAY - NIGHT",
          location: "School Hallway",
          time: "Night",
          characters: ["LISA", "FARID"],
          props: ["Broken desk", "Graffiti", "Cell phone"],
          wardrobe: ["Casual"],
          sfx: ["Creaking door", "Phone vibration"],
          notes: "Lisa and Farid split up to explore.",
          budget: "RM 2,000"
        },
        {
          number: 3,
          heading: "INT. CLASSROOM - NIGHT",
          location: "Classroom",
          time: "Night",
          characters: ["AMIR"],
          props: ["Chalk", "Old map"],
          wardrobe: ["Casual"],
          sfx: ["Chalk screech", "Heartbeat"],
          notes: "Amir finds a clue on the blackboard.",
          budget: "RM 1,200"
        }
      ],
      elements: {
        characters: [
          { name: "AMIR", description: "Curious, brave teen. Age 17." },
          { name: "LISA", description: "Skeptical, witty. Age 16." },
          { name: "FARID", description: "Easily frightened, loyal friend. Age 17." }
        ],
        locations: [
          "Abandoned School",
          "School Hallway",
          "Classroom"
        ],
        props: [
          "Flashlight",
          "Old notebook",
          "Camera",
          "Broken desk",
          "Cell phone",
          "Chalk",
          "Old map"
        ],
        wardrobe: [
          "Casual wear",
          "Jacket"
        ],
        sfx: [
          "Wind howling",
          "Distant footsteps",
          "Creaking door",
          "Phone vibration",
          "Chalk screech",
          "Heartbeat"
        ]
      },
      budget: {
        talent: "RM 3,000",
        location: "RM 2,000",
        propsSet: "RM 1,500",
        wardrobeMakeup: "RM 1,000",
        sfxVfx: "RM 2,000",
        crew: "RM 3,500",
        miscellaneous: "RM 1,000"
      },
      crew: [
        { role: "Director", name: "Azlan Mokhtar" },
        { role: "Producer", name: "Siti Rahmah" },
        { role: "DOP", name: "Lim Wei Jian" },
        { role: "Sound", name: "Hafizul Rahman" },
        { role: "Art Director", name: "Noraini Zain" }
      ],
      shootingSchedule: [
        { day: 1, scenes: [1], location: "Abandoned School", notes: "Exterior shots" },
        { day: 2, scenes: [2], location: "School Hallway", notes: "Hallway exploration" },
        { day: 3, scenes: [3], location: "Classroom", notes: "Climax and clue discovery" }
      ]
    }
  },
  {
    title: "Summer Nights",
    genre: "Documentary • Nature",
    status: "COMPLETED",
    statusColor: "bg-green-400 text-black",
    budget: "$450K",
    dueDate: "Mar 10, 2025",
    team: "15 members",
    createdAt: "2024-10-20T14:15:00.000Z", // Oldest project (completed)
    // --- Script Breakdown Data ---
    scriptBreakdown: {
      scenes: [
        {
          number: 1,
          heading: "EXT. RAINFOREST EDGE - SUNSET",
          location: "Rainforest Edge",
          time: "Sunset",
          characters: ["NARRATOR", "CAMERA CREW"],
          props: ["Camera", "Tripod", "Microphone"],
          wardrobe: ["Outdoor wear", "Boots"],
          sfx: ["Bird calls", "Wind in trees"],
          notes: "Opening narration, setting the scene.",
          budget: "RM 2,500"
        },
        {
          number: 2,
          heading: "EXT. RIVERBANK - NIGHT",
          location: "Riverbank",
          time: "Night",
          characters: ["NARRATOR", "BIOLOGIST"],
          props: ["Notebook", "Lantern", "Insect net"],
          wardrobe: ["Outdoor wear", "Raincoat"],
          sfx: ["Frogs croaking", "Water flowing"],
          notes: "Interview with biologist about nocturnal wildlife.",
          budget: "RM 3,000"
        },
        {
          number: 3,
          heading: "EXT. FOREST CLEARING - DAWN",
          location: "Forest Clearing",
          time: "Dawn",
          characters: ["NARRATOR"],
          props: ["Camera drone"],
          wardrobe: ["Outdoor wear"],
          sfx: ["Morning birds", "Insects buzzing"],
          notes: "Drone shots of sunrise and closing remarks.",
          budget: "RM 2,000"
        }
      ],
      elements: {
        characters: [
          { name: "NARRATOR", description: "Voiceover, guides the story. Age 35." },
          { name: "BIOLOGIST", description: "Expert on rainforest wildlife. Age 40." },
          { name: "CAMERA CREW", description: "Support, behind the scenes." }
        ],
        locations: [
          "Rainforest Edge",
          "Riverbank",
          "Forest Clearing"
        ],
        props: [
          "Camera",
          "Tripod",
          "Microphone",
          "Notebook",
          "Lantern",
          "Insect net",
          "Camera drone"
        ],
        wardrobe: [
          "Outdoor wear",
          "Boots",
          "Raincoat"
        ],
        sfx: [
          "Bird calls",
          "Wind in trees",
          "Frogs croaking",
          "Water flowing",
          "Morning birds",
          "Insects buzzing"
        ]
      },
      budget: {
        talent: "RM 10,000",
        location: "RM 8,000",
        propsSet: "RM 5,000",
        wardrobeMakeup: "RM 2,500",
        sfxVfx: "RM 3,000",
        crew: "RM 12,000",
        miscellaneous: "RM 4,000"
      },
      crew: [
        { role: "Director", name: "Faridah Hassan" },
        { role: "Producer", name: "James Lee" },
        { role: "DOP", name: "Chong Wei" },
        { role: "Sound", name: "Aina Syahirah" },
        { role: "Biologist", name: "Dr. Nor Azman" }
      ],
      shootingSchedule: [
        { day: 1, scenes: [1], location: "Rainforest Edge", notes: "Opening shots" },
        { day: 2, scenes: [2], location: "Riverbank", notes: "Night wildlife" },
        { day: 3, scenes: [3], location: "Forest Clearing", notes: "Sunrise and wrap-up" }
      ]
    }
  }
  // ...add more projects as needed
]