SEED_USERS = [
    {
        "id": "user-alice",
        "full_name": "Alice Smith",
        "email": "alice@example.com",
        "password": "Password123!"
    },
    {
        "id": "user-bob",
        "full_name": "Bob Johnson",
        "email": "bob@example.com",
        "password": "Password123!"
    }
]

SEED_TRIP_USER_ASSIGNMENTS = {
    "trip-1": "user-alice",
    "trip-2": "user-bob",
    "trip-3": "user-alice"
}

SEED_TRIPS = [
    {
        "id": "trip-1",
        "user_id": "user-alice",
        "name": "Vietnam Adventure",
        "destination": "Vietnam",
        "start_date": "2026-10-01",
        "end_date": "2026-10-10",
        "budget": 2000.0,
        "currency": "USD",
        "expenses": [
            {
                "id": "exp-1-1",
                "description": "Hotel Stays (Sofitel, InterContinental, Park Hyatt)",
                "category": "Accommodation",
                "amount": 500.0,
                "currency": "USD",
                "date": "2026-10-01"
            },
            {
                "id": "exp-1-2",
                "description": "Meals & Street Food",
                "category": "Food",
                "amount": 300.0,
                "currency": "USD",
                "date": "2026-10-05"
            },
            {
                "id": "exp-1-3",
                "description": "Domestic Flights & Transfers",
                "category": "Transportation",
                "amount": 200.0,
                "currency": "USD",
                "date": "2026-10-03"
            },
            {
                "id": "exp-1-4",
                "description": "Ha Long Cruise, Cu Chi Tunnels, Mekong Tour",
                "category": "Activities",
                "amount": 250.0,
                "currency": "USD",
                "date": "2026-10-02"
            }
        ],
        "days": [
            {
                "id": "day-1-1",
                "date": "2026-10-01",
                "title": "Arrival in Hanoi",
                "activities": [
                    {
                        "id": "act-1-1-1",
                        "name": "Arrive in Hanoi",
                        "location": "Noi Bai International Airport",
                        "description": "Arrive at 09:30, clear immigration, pick up SIM card at airport"
                    },
                    {
                        "id": "act-1-1-2",
                        "name": "Transfer to hotel",
                        "location": "Old Quarter, Hanoi",
                        "description": "Private taxi to Sofitel Legend Metropole, check in after 14:00"
                    },
                    {
                        "id": "act-1-1-3",
                        "name": "Old Quarter walking tour",
                        "location": "Hanoi Old Quarter",
                        "description": "Explore 36 historic streets — each named for a traditional craft guild"
                    },
                    {
                        "id": "act-1-1-4",
                        "name": "Dinner at Quan An Ngon",
                        "location": "Quan An Ngon Restaurant, 18 Phan Boi Chau",
                        "description": "Street-food style restaurant — try pho bo, banh mi, and cha ca"
                    }
                ]
            },
            {
                "id": "day-1-2",
                "date": "2026-10-02",
                "title": "Ha Long Bay Overnight Cruise",
                "activities": [
                    {
                        "id": "act-1-2-1",
                        "name": "Transfer to Ha Long Bay",
                        "location": "Ha Long City",
                        "description": "Depart hotel at 08:00, 3.5-hour drive with comfort stop midway"
                    },
                    {
                        "id": "act-1-2-2",
                        "name": "Embark Junk Boat",
                        "location": "Ha Long Bay Harbour",
                        "description": "Board Aphrodite Cruise at 12:00, welcome drinks and lunch on board"
                    },
                    {
                        "id": "act-1-2-3",
                        "name": "Kayaking at Luon Cave",
                        "location": "Luon Cave, Ha Long Bay",
                        "description": "Paddle kayak through the sea cave arch to hidden lagoon"
                    },
                    {
                        "id": "act-1-2-4",
                        "name": "Surprise Cave Visit",
                        "location": "Hang Sung Sot (Surprise Cave)",
                        "description": "Largest cave in Ha Long — massive chambers with stalactite formations"
                    },
                    {
                        "id": "act-1-2-5",
                        "name": "Sunset Tai Chi on Deck",
                        "location": "Aphrodite Cruise Sundeck",
                        "description": "Group tai chi session with the cruise instructor at golden hour"
                    },
                    {
                        "id": "act-1-2-6",
                        "name": "Seafood Dinner on Board",
                        "location": "Aphrodite Cruise Dining Room",
                        "description": "Seven-course set menu featuring local seafood paired with Vietnamese wine"
                    }
                ]
            },
            {
                "id": "day-1-3",
                "date": "2026-10-03",
                "title": "Ha Long to Hanoi — Flight to Da Nang",
                "activities": [
                    {
                        "id": "act-1-3-1",
                        "name": "Breakfast and disembark",
                        "location": "Ha Long Bay",
                        "description": "Buffet breakfast on cruise, disembark at 09:30, drive back to Hanoi"
                    },
                    {
                        "id": "act-1-3-2",
                        "name": "Lunch at Highway 4",
                        "location": "Highway 4 Restaurant, 17 Nguyen Hue",
                        "description": "Traditional northern lunch — try bun cha and nem ran"
                    },
                    {
                        "id": "act-1-3-3",
                        "name": "Flight to Da Nang",
                        "location": "Noi Bai (HAN) to Da Nang (DAD)",
                        "description": "Vietnam Airlines VN134 departs 16:00, arrives 17:15. Booked online: confirmation #VN-88210"
                    },
                    {
                        "id": "act-1-3-4",
                        "name": "Check in Da Nang hotel",
                        "location": "InterContinental Danang Sun Peninsula Resort",
                        "description": "Transfer via resort shuttle, beachfront villa with private pool"
                    }
                ]
            },
            {
                "id": "day-1-4",
                "date": "2026-10-04",
                "title": "Hoi An Ancient Town",
                "activities": [
                    {
                        "id": "act-1-4-1",
                        "name": "Private transfer to Hoi An",
                        "location": "Da Nang to Hoi An",
                        "description": "45-minute drive, depart hotel at 09:00"
                    },
                    {
                        "id": "act-1-4-2",
                        "name": "Japanese Covered Bridge",
                        "location": "Hoi An Ancient Town",
                        "description": "Iconic 16th-century wooden bridge built by Japanese trading community"
                    },
                    {
                        "id": "act-1-4-3",
                        "name": "Tan Ky House Tour",
                        "location": "101 Nguyen Thai Hoc",
                        "description": "200-year-old traditional merchant house with Chinese and Japanese architecture"
                    },
                    {
                        "id": "act-1-4-4",
                        "name": "Lunch at Cargo Club",
                        "location": "Cargo Club Restaurant, 100 Nguyen Thai Hoc",
                        "description": "Riverside dining — try cao lau (Hoi An specialty noodles) and white rose dumplings"
                    },
                    {
                        "id": "act-1-4-5",
                        "name": "An Bang Beach Afternoon",
                        "location": "An Bang Beach, Hoi An",
                        "description": "Relax on sand, optional coconut boat tour through water palm forest"
                    },
                    {
                        "id": "act-1-4-6",
                        "name": "Hoi An Night Markets & Lanterns",
                        "location": "Thu Bon Riverfront, Hoi An",
                        "description": "Lantern release ceremony on the river at 20:00, then street food walk"
                    }
                ]
            },
            {
                "id": "day-1-5",
                "date": "2026-10-05",
                "title": "My Son Sanctuary & Da Nang Beach",
                "activities": [
                    {
                        "id": "act-1-5-1",
                        "name": "Day trip to My Son",
                        "location": "My Son Sanctuary, Quang Nam",
                        "description": "Depart 07:30 to beat the heat. Ancient Cham Hindu temple ruins dating from 4th century"
                    },
                    {
                        "id": "act-1-5-2",
                        "name": "Guided temple tour",
                        "location": "Group B & C Temples, My Son",
                        "description": "UNESCO World Heritage site — former royal ceremonial center of Champa kingdom"
                    },
                    {
                        "id": "act-1-5-3",
                        "name": "Return to Da Nang",
                        "location": "Da Nang",
                        "description": "Lunch en route at a countryside restaurant specializing in mi quang noodles"
                    },
                    {
                        "id": "act-1-5-4",
                        "name": "China Beach Afternoon",
                        "location": "My Khe Beach (China Beach)",
                        "description": "Sunbathing and late-afternoon swim at the famous beach featured in 'Apocalypse Now'"
                    },
                    {
                        "id": "act-1-5-5",
                        "name": "Marble Mountains visit",
                        "location": "Ngu Hanh Son (Marble Mountains)",
                        "description": "Climb Thuy Son (Water Mountain) for sunset views over Da Nang Bay"
                    },
                    {
                        "id": "act-1-5-6",
                        "name": "Seafood dinner at Son Tra Night Market",
                        "location": "Son Tra Night Market, Da Nang",
                        "description": "Fresh grilled fish, squid, and tiger prawns picked live from tanks"
                    }
                ]
            },
            {
                "id": "day-1-6",
                "date": "2026-10-06",
                "title": "Ba Na Hills & Golden Bridge",
                "activities": [
                    {
                        "id": "act-1-6-1",
                        "name": "Morning cable car to Ba Na",
                        "location": "Ba Na Hills Mountain Resort",
                        "description": "World's longest non-stop single-track cable car (5.8km). Departs 08:30"
                    },
                    {
                        "id": "act-1-6-2",
                        "name": "Golden Bridge (Cau Vang)",
                        "location": "Ba Na Hills",
                        "description": "Iconic pedestrian bridge held aloft by two giant stone hands"
                    },
                    {
                        "id": "act-1-6-3",
                        "name": "French Village Walk",
                        "location": "Mercure Danang French Village",
                        "description": "Replica European town square with cobblestone streets, cathedral, and vineyard tour"
                    },
                    {
                        "id": "act-1-6-4",
                        "name": "Lunch at Morin Restaurant",
                        "location": "Ba Na Hills",
                        "description": "Formal French set menu at the hillside heritage restaurant"
                    },
                    {
                        "id": "act-1-6-5",
                        "name": "Fantasy Park",
                        "location": "Ba Na Hills Fantasy Park",
                        "description": "Indoor amusement hall with the Alpine Coaster and carousel ride"
                    },
                    {
                        "id": "act-1-6-6",
                        "name": "Return to hotel",
                        "location": "Da Nang",
                        "description": "Cable car descends at 17:00, resort shuttle pickup"
                    }
                ]
            },
            {
                "id": "day-1-7",
                "date": "2026-10-07",
                "title": "Da Nang to Ho Chi Minh City",
                "activities": [
                    {
                        "id": "act-1-7-1",
                        "name": "Check out and airport transfer",
                        "location": "Da Nang International Airport (DAD)",
                        "description": "Leave hotel 10:30 for 13:00 departure"
                    },
                    {
                        "id": "act-1-7-2",
                        "name": "Flight to HCMC",
                        "location": "DAD to SGN (Tan Son Nhat)",
                        "description": "VietJet Air VJ188, arrives 14:25. Seat 14A (window)"
                    },
                    {
                        "id": "act-1-7-3",
                        "name": "Hotel check-in",
                        "location": "Park Hyatt Saigon, District 1",
                        "description": "Luxury colonial-style hotel opposite the Opera House"
                    },
                    {
                        "id": "act-1-7-4",
                        "name": "Notre-Dame Cathedral & Post Office",
                        "location": "District 1, Ho Chi Minh City",
                        "description": "Walking tour of French colonial landmarks — Saigon Notre-Dame Basilica and Central Post Office"
                    },
                    {
                        "id": "act-1-7-5",
                        "name": "Opera House Dinner Show",
                        "location": "Saigon Opera House",
                        "description": "AO Show — a contemporary Vietnamese circus performance at 20:00. Tickets: Orch Row 5"
                    }
                ]
            },
            {
                "id": "day-1-8",
                "date": "2026-10-08",
                "title": "Cu Chi Tunnels & War Remnants",
                "activities": [
                    {
                        "id": "act-1-8-1",
                        "name": "Morning Cu Chi Tunnels tour",
                        "location": "Cu Chi Tunnels, Cu Chi District",
                        "description": "60km NW of HCMC. Visit Ben Dinh section of the 250km Viet Cong tunnel network"
                    },
                    {
                        "id": "act-1-8-2",
                        "name": "Shooting range experience",
                        "location": "Cu Chi Shooting Range",
                        "description": "Optional: fire historic WWII-era rifles (M16, AK-47) at the licensed range"
                    },
                    {
                        "id": "act-1-8-3",
                        "name": "Lunch back in the city",
                        "location": "Secret Garden Restaurant, District 1",
                        "description": "Rooftop garden serving contemporary Vietnamese cuisine"
                    },
                    {
                        "id": "act-1-8-4",
                        "name": "War Remnants Museum",
                        "location": "28 Vo Van Tan, District 3",
                        "description": "Exhibitions documenting the Vietnam/American War. Allow 2-3 hours"
                    },
                    {
                        "id": "act-1-8-5",
                        "name": "Rooftop drinks at Chill Skybar",
                        "location": "AB Tower, 76A Le Lai, District 1",
                        "description": "Sundown cocktails on the 26th floor with panoramic Saigon skyline views"
                    },
                    {
                        "id": "act-1-8-6",
                        "name": "Dinner at Nha Hang Ngon",
                        "location": "160 Pasteur, District 1",
                        "description": "Open-air dining hall — 30+ stalls serving regional specialties from all over Vietnam"
                    }
                ]
            },
            {
                "id": "day-1-9",
                "date": "2026-10-09",
                "title": "Mekong Delta Day Tour",
                "activities": [
                    {
                        "id": "act-1-9-1",
                        "name": "Depart for Cai Be",
                        "location": "Cai Be, Tien Giang Province",
                        "description": "Hotel pickup 07:30, 2-hour drive south to the Mekong Delta"
                    },
                    {
                        "id": "act-1-9-2",
                        "name": "Cai Be Floating Market",
                        "location": "Cai Be Floating Market",
                        "description": "Boat tour of the wholesale floating market — watch boats display produce on tall poles"
                    },
                    {
                        "id": "act-1-9-3",
                        "name": "Coconut candy workshop",
                        "location": "Unicorn Island, Mekong Delta",
                        "description": "Visit a family workshop producing coconut candy and puffed rice cakes"
                    },
                    {
                        "id": "act-1-9-4",
                        "name": "Rowing sampan through canals",
                        "location": "Tan Phong Island",
                        "description": "Narrow palm-shaded canals traversed by traditional 2-person rowing boat"
                    },
                    {
                        "id": "act-1-9-5",
                        "name": "Lunch on the river",
                        "location": "Restaurant on stilts, Mekong River",
                        "description": "Elephant-ear fish deep-fried whole, served with mango salad and tamarind sauce"
                    },
                    {
                        "id": "act-1-9-6",
                        "name": "Return to HCMC",
                        "location": "Ho Chi Minh City",
                        "description": "Depart delta 15:00, arrive city 17:30. Evening at leisure"
                    }
                ]
            },
            {
                "id": "day-1-10",
                "date": "2026-10-10",
                "title": "Departure",
                "activities": [
                    {
                        "id": "act-1-10-1",
                        "name": "Breakfast buffet",
                        "location": "Park Hyatt Saigon",
                        "description": "Last Vietnamese breakfast — banh cuon, pho, fresh tropical fruit plate"
                    },
                    {
                        "id": "act-1-10-2",
                        "name": "Last-minute shopping",
                        "location": "Ben Thanh Market, District 1",
                        "description": "Pick up silk scarves, coffee beans, lacquerware, and fish sauce souvenirs"
                    },
                    {
                        "id": "act-1-10-3",
                        "name": "Airport transfer",
                        "location": "Tan Son Nhat International Airport (SGN)",
                        "description": "Depart hotel 11:30 for 15:00 international flight home. Check in 3 hours early"
                    }
                ]
            }
        ],
        "journal_entries": [
            {
                "id": "je-1-1",
                "title": "Arrival in Hanoi",
                "content": "Arrived in Hanoi today and spent the evening exploring the Old Quarter. The city is much more chaotic than I expected — motorbikes everywhere, street vendors shouting, and the smell of pho drifting from every corner. Had dinner at Quan An Ngon with a group of fellow travellers I met at the hotel. Tried banh mi, cha ca, and a delicious egg coffee. Tomorrow we're heading to Ha Long Bay for an overnight cruise, can't wait!",
                "date": "2026-10-01",
                "created_at": "2026-10-01T15:30:00",
                "updated_at": "2026-10-01T15:30:00"
            },
            {
                "id": "je-1-2",
                "title": "Ha Long Bay Magic",
                "content": "The Ha Long Bay cruise was absolutely breathtaking. Woke up this morning to the sight of thousands of limestone karsts rising from the misty water. We kayaked through Luon Cave and swam in the emerald lagoon — the water was surprisingly warm. The sunset tai chi session on the sundeck with a glass of Vietnamese wine was perfect. Already planning to come back someday.",
                "date": "2026-10-02",
                "created_at": "2026-10-02T20:15:00",
                "updated_at": "2026-10-02T20:15:00"
            },
            {
                "id": "je-1-3",
                "title": "Da Nang Beach Afternoon",
                "content": "Spent the entire day exploring the Old Quarter in Hoi An. The Japanese Covered Bridge was beautiful, but my favourite part was releasing a paper lantern on the river at 8pm. Hundreds of glowing lanterns floating downstream — it felt magical. Ate white rose dumplings and cao lau noodles for lunch at Cargo Club. Tomorrow: My Son Sanctuary temples, then beach time in Da Nang.",
                "date": "2026-10-04",
                "created_at": "2026-10-04T22:00:00",
                "updated_at": "2026-10-04T22:05:00"
            }
        ]
    },
    {
        "id": "trip-2",
        "user_id": "user-bob",
        "name": "Tokyo Discovery",
        "destination": "Japan",
        "start_date": "2026-11-15",
        "end_date": "2026-11-22",
        "budget": 300000.0,
        "currency": "JPY",
        "expenses": [
            {
                "id": "exp-2-1",
                "description": "Shibuya Stream Excel Hotel (8 nights)",
                "category": "Accommodation",
                "amount": 140000.0,
                "currency": "JPY",
                "date": "2026-11-15"
            },
            {
                "id": "exp-2-2",
                "description": "Ramen, Sushi, Izakaya Dining",
                "category": "Food",
                "amount": 65000.0,
                "currency": "JPY",
                "date": "2026-11-18"
            },
            {
                "id": "exp-2-3",
                "description": "Narita Express, Hakone Free Pass, Subway",
                "category": "Transportation",
                "amount": 35000.0,
                "currency": "JPY",
                "date": "2026-11-16"
            },
            {
                "id": "exp-2-4",
                "description": "TeamLab, Skytree, Hakone Ropeway",
                "category": "Activities",
                "amount": 28000.0,
                "currency": "JPY",
                "date": "2026-11-17"
            },
            {
                "id": "exp-2-5",
                "description": "Don Quijote Souvenirs, Ginza Shopping",
                "category": "Shopping",
                "amount": 22000.0,
                "currency": "JPY",
                "date": "2026-11-22"
            }
        ],
        "days": [
            {
                "id": "day-2-1",
                "date": "2026-11-15",
                "title": "Arrival in Shibuya",
                "activities": [
                    {
                        "id": "act-2-1-1",
                        "name": "Arrive at Narita",
                        "location": "Narita International Airport (NRT)",
                        "description": "JL006 arrives 14:40, complete immigration, pick up Suica card at JR East office"
                    },
                    {
                        "id": "act-2-1-2",
                        "name": "Narita Express to Shibuya",
                        "location": "Narita Express → Shibuya Station",
                        "description": "16:00 departure, 1 hr 10 min direct express. Seat reservation confirmed: Car 3 / 12B"
                    },
                    {
                        "id": "act-2-1-3",
                        "name": "Check in hotel",
                        "location": "Shibuya Stream Excel Hotel Tokyu",
                        "description": "Check in after 15:00, corner room on 28F with Shibuya Crossing view"
                    },
                    {
                        "id": "act-2-1-4",
                        "name": "Shibuya Crossing & Hachiko",
                        "location": "Shibuya Scramble Crossing",
                        "description": "Walk through the scramble, visit Hachiko statue outside the station"
                    },
                    {
                        "id": "act-2-1-5",
                        "name": "MAGNET by Shibuya109 Rooftop",
                        "location": "MAGNET by Shibuya109, 7F",
                        "description": "Open-air observation deck 'SHIBUYA SKY HALL' — free, evening views of the crossing"
                    },
                    {
                        "id": "act-2-1-6",
                        "name": "Ramen dinner",
                        "location": "Ichiran Ramen, Shibuya",
                        "description": "Individual booth-style tonkotsu ramen. Order via ticket machine, customize richness and spice"
                    }
                ]
            },
            {
                "id": "day-2-2",
                "date": "2026-11-16",
                "title": "Ancient Asakusa & Akihabara",
                "activities": [
                    {
                        "id": "act-2-2-1",
                        "name": "Senso-ji Temple",
                        "location": "Asakusa, Taito Ward",
                        "description": "Tokyo's oldest Buddhist temple (founded 645 CE). Walk through Kaminarimon (Thunder Gate)"
                    },
                    {
                        "id": "act-2-2-2",
                        "name": "Nakamise Shopping Street",
                        "location": "Senso-ji Approach",
                        "description": "200m-long arcade with 89 traditional shops — buy senbei rice crackers, fans, and wooden dolls"
                    },
                    {
                        "id": "act-2-2-3",
                        "name": "Tokyo Skytree",
                        "location": "Tokyo Skytree, Sumida",
                        "description": "634m tower. Combo ticket: Tembo Deck (350m) + Tembo Galleria (450m). 11:00 entry"
                    },
                    {
                        "id": "act-2-2-4",
                        "name": "Lunch at Solamachi",
                        "location": "Tokyo Solamachi Mall, Skytree",
                        "description": "Rikyu Sushi restaurant — omakase lunch course (10 pieces, 3800 yen)"
                    },
                    {
                        "id": "act-2-2-5",
                        "name": "Akihabara Electric Town",
                        "location": "Chuo Dori, Akihabara",
                        "description": "Retro game arcades (Taito Station, GiGO), anime merchandise stores, and camera shops"
                    },
                    {
                        "id": "act-2-2-6",
                        "name": "Maid Cafe Experience",
                        "location": "@home cafe, Akihabara",
                        "description": "First floor main hall — order omurice (rice omelette) with ketchup art and live mini-show"
                    },
                    {
                        "id": "act-2-2-7",
                        "name": "Yodobashi Camera Akihabara",
                        "location": "Yodobashi-Akiba Multi-storey",
                        "description": "9 floors of electronics, watches, cameras, and hobby toys — tax-free for tourists over 5000 yen"
                    }
                ]
            },
            {
                "id": "day-2-3",
                "date": "2026-11-17",
                "title": "Tsukiji & Ginza Luxury",
                "activities": [
                    {
                        "id": "act-2-3-1",
                        "name": "Toyosu Market Breakfast",
                        "location": "Toyosu Market, Koto Ward",
                        "description": "Open 05:00 — early breakfast of fresh tamagoyaki (sweet rolled egg) and tuna nigiri at a sushi stand"
                    },
                    {
                        "id": "act-2-3-2",
                        "name": "Tsukiji Outer Market",
                        "location": "Tsukiji Jogaii Shijo",
                        "description": "Street food walk — tamagoyaki, grilled scallops, uni shot glasses, and matcha desserts"
                    },
                    {
                        "id": "act-2-3-3",
                        "name": "TeamLab Planets",
                        "location": "Toyosu, teamLab Planets TOKYO",
                        "description": "13:00 ticket — immersive digital art installations, walk barefoot through water rooms. Bring spare socks"
                    },
                    {
                        "id": "act-2-3-4",
                        "name": "Ginza Shopping Street",
                        "location": "Ginza Yon-chome Crossing",
                        "description": "Chuo Dori pedestrian street on Sunday — Wako Clock Tower, Mitsukoshi, Mikimoto flagship"
                    },
                    {
                        "id": "act-2-3-5",
                        "name": "Uniqlo Ginza flagship",
                        "location": "12-2 Ginza 6-chome, Chuo Ward",
                        "description": "12-story Uniqlo store + MUJI next door for Japanese design basics"
                    },
                    {
                        "id": "act-2-3-6",
                        "name": "Sukiyaki Dinner",
                        "location": "Ginza Sukiyaki-ya",
                        "description": "Kansai-style A5 Wagyu beef sukiyaki cooked table-side with warishita broth and raw egg dip"
                    }
                ]
            },
            {
                "id": "day-2-4",
                "date": "2026-11-18",
                "title": "Mt. Fuji Day Trip (Hakone)",
                "activities": [
                    {
                        "id": "act-2-4-1",
                        "name": "Depart Shinjuku for Hakone",
                        "location": "Shinjuku → Hakone-Yumoto",
                        "description": "Odakyu Romancecar 'Super Hakone' 08:00 departure, reserved seats. Use Hakone Free Pass"
                    },
                    {
                        "id": "act-2-4-2",
                        "name": "Hakone Tozan Railway",
                        "location": "Hakone-Yumoto → Gora",
                        "description": "Scenic mountain railway with switchbacks, 40-minute climb through cedar forest"
                    },
                    {
                        "id": "act-2-4-3",
                        "name": "Owakudani Valley",
                        "location": "Owakudani, Hakone",
                        "description": "Volcanic valley with active sulfur vents. Try the black 'kuro-tamago' eggs (said to extend life 7 years)"
                    },
                    {
                        "id": "act-2-4-4",
                        "name": "Hakone Ropeway & Pirate Ship",
                        "location": "Owakudani → Togendai → Moto-Hakone",
                        "description": "Ropeway over crater valley, then pirate-themed cruise ship across Lake Ashi with Mt. Fuji views (weather permitting)"
                    },
                    {
                        "id": "act-2-4-5",
                        "name": "Hakone Shrine",
                        "location": "Hakone-jinja, Moto-Hakone",
                        "description": "Shinto shrine famous for its torii gate rising from the lake. Access via short forest path"
                    },
                    {
                        "id": "act-2-4-6",
                        "name": "Hot Spring Bath (Onsen)",
                        "location": "Hakone-Yumoto Onsen ryokan",
                        "description": "Public onsen experience — wash thoroughly first, soak in hot mineral water (no swimwear)"
                    },
                    {
                        "id": "act-2-4-7",
                        "name": "Return to Tokyo",
                        "location": "Shinjuku, Tokyo",
                        "description": "Romancecar departs 18:30, arrives Shinjuku 20:00. Dinner options in Shinjuku Omoide Yokocho"
                    }
                ]
            },
            {
                "id": "day-2-5",
                "date": "2026-11-19",
                "title": "Traditional Harajuku & Shinjuku",
                "activities": [
                    {
                        "id": "act-2-5-1",
                        "name": "Meiji Shrine",
                        "location": "Meiji Jingu, Shibuya Ward",
                        "description": "Serene Shinto shrine within 170-acre forest in the center of Tokyo. Purify hands at temizuya before entering"
                    },
                    {
                        "id": "act-2-5-2",
                        "name": "Takeshita Street",
                        "location": "Takeshita Dori, Harajuku",
                        "description": "Harajuku fashion street — rainbow cotton candy, crepes, vintage and alternative fashion boutiques"
                    },
                    {
                        "id": "act-2-5-3",
                        "name": "Omotesando Hills Shopping",
                        "location": "Omotesando Avenue",
                        "description": "Champs-Élysées of Tokyo — tree-lined avenue with Prada, Comme des Garcons, and Tod's buildings"
                    },
                    {
                        "id": "act-2-5-4",
                        "name": "Lunch at Afuri",
                        "location": "Afuri Harajuku",
                        "description": "Modern yuzu-shio ramen with roasted chicken and citrus broth — voted one of Tokyo's top 10 ramen chains"
                    },
                    {
                        "id": "act-2-5-5",
                        "name": "Shinjuku Gyoen National Garden",
                        "location": "Sendagaya, Shinjuku",
                        "description": "Late afternoon walk — three garden styles (Japanese traditional, French formal, English landscape). Chrysanthemum displays in November"
                    },
                    {
                        "id": "act-2-5-6",
                        "name": "Shinjuku Golden Gai Izakaya",
                        "location": "Omoide Yokocho (Memory Lane) & Golden Gai",
                        "description": "Alley of 200+ tiny izakayas, each with a theme. Yakitori alley then a hidden bar for shochu flight"
                    },
                    {
                        "id": "act-2-5-7",
                        "name": "Tokyo Metropolitan Government Free Observation",
                        "location": "Tokyo Metropolitan Government Building, 45F",
                        "description": "Free 202m-high night views from both North and South observatories, open until 23:00"
                    }
                ]
            },
            {
                "id": "day-2-6",
                "date": "2026-11-20",
                "title": "Imperial Palace & Ueno Museums",
                "activities": [
                    {
                        "id": "act-2-6-1",
                        "name": "Imperial Palace East Gardens",
                        "location": "Kokyo Higashi Gyoen, Chiyoda",
                        "description": "Free admission, open 09:00. Ruins of Edo Castle keep, Ninomaru traditional garden with stone walls and moats"
                    },
                    {
                        "id": "act-2-6-2",
                        "name": "Tokyo Station & Ramen Street",
                        "location": "Tokyo Station Yaesu Underground, Ramen Street",
                        "description": "4 famous ramen shops in one place. Standby for 'Ramen Street' eel ramen (una-shoyu) at 7th floor too"
                    },
                    {
                        "id": "act-2-6-3",
                        "name": "Ueno Park Museums",
                        "location": "Ueno Park, Taito Ward",
                        "description": "Afternoon at Ueno — Tokyo National Museum (Honkan for Japanese art), National Museum of Nature and Science"
                    },
                    {
                        "id": "act-2-6-4",
                        "name": "Ameya-Yokocho Market",
                        "location": "Ameyoko, Ueno",
                        "description": "Vibrant street market since WWII days — fresh fish, dried snacks, Korean kimchi, discounted Japanese kitkat flavours"
                    },
                    {
                        "id": "act-2-6-5",
                        "name": "Kappabashi Kitchenware Street",
                        "location": "Kappabashi Dori, Asakusa/Ueno",
                        "description": "Everything for the Japanese kitchen — ceramic ramen bowls, wooden sushi rollers, plastic food samples (sampuru)"
                    },
                    {
                        "id": "act-2-6-6",
                        "name": "Tempura Dinner at Narikura",
                        "location": "Narikura, Minato Ward",
                        "description": "Michelin-recommended tempura specialist — seasonal ingredients battered and fried in sesame oil at counter"
                    }
                ]
            },
            {
                "id": "day-2-7",
                "date": "2026-11-21",
                "title": "Odaiba & TeamLab Borderless",
                "activities": [
                    {
                        "id": "act-2-7-1",
                        "name": "Yurikamome Line to Odaiba",
                        "location": "Shimbashi → Odaiba via Yurikamome",
                        "description": "Automated elevated transit system with views over Rainbow Bridge and Tokyo Bay"
                    },
                    {
                        "id": "act-2-7-2",
                        "name": "teamLab Borderless",
                        "location": "MORI Building DIGITAL ART MUSEUM, Azabudai Hills",
                        "description": "10:00 entry — world's first digital art museum without a map, wander through interconnected luminous rooms"
                    },
                    {
                        "id": "act-2-7-3",
                        "name": "Gundam Base & Life-Sized Gundam",
                        "location": "Gundam Front Tokyo, DiverCity Tokyo Plaza",
                        "description": "Life-sized 19.7m Unicorn Gundam statue outside DiverCity — transforms on the hour (12:00, 15:00, 17:00, 19:00 show)"
                    },
                    {
                        "id": "act-2-7-4",
                        "name": "Lunch at DiverCity Food Court",
                        "location": "DiverCity Tokyo Plaza, Odaiba",
                        "description": "Try takoyaki (Osaka octopus balls) and okonomiyaki set from the Osaka food hall"
                    },
                    {
                        "id": "act-2-7-5",
                        "name": "Rainbow Bridge & Odaiba Seaside Park",
                        "location": "Odaiba Kaihin Park",
                        "description": "Beach promenade with Tokyo skyline and Rainbow Bridge views, artificial onsen footbath at beach edge"
                    },
                    {
                        "id": "act-2-7-6",
                        "name": "Onsen Odaiba Odaiba Minato",
                        "location": "Odaiba Oedo Onsen Monogatari",
                        "description": "Large Edo-period themed onsen complex. 10 bath styles, tatami relaxation area, rooftop foot spa with Rainbow Bridge view"
                    },
                    {
                        "id": "act-2-7-7",
                        "name": "Shabu-shabu Farewell Dinner",
                        "location": "Shabu Shabu Onyasai, Shibuya",
                        "description": "All-you-can-eat A5 Wagyu shabu-shabu course with 90-minute time limit"
                    }
                ]
            },
            {
                "id": "day-2-8",
                "date": "2026-11-22",
                "title": "Farewell Tokyo",
                "activities": [
                    {
                        "id": "act-2-8-1",
                        "name": "Shibuya Sky Observation",
                        "location": "Shibuya SKY, Scramble Square 14F-45F",
                        "description": "09:00 entry — skip early crowds. SKY EDGE (230m open-air perimeter walk) + SKY GALLERY museum"
                    },
                    {
                        "id": "act-2-8-2",
                        "name": "Don Quijote Souvenirs",
                        "location": "Don Quijote Shibuya, 24H store",
                        "description": "Tax-free last-minute: Tokyo Banana cakes, matcha KitKats, sheet masks, and Japanese whisky miniatures"
                    },
                    {
                        "id": "act-2-8-3",
                        "name": "Check out & Limousine Bus to Narita",
                        "location": "Shibuya Excel Hotel → Narita Airport (NRT)",
                        "description": "Airport Limousine Bus 12:00 direct to Terminal 1 (90 min), drop in front of hotel door. Ticket booked online"
                    }
                ]
            }
        ]
    },
    {
        "id": "trip-3",
        "user_id": "user-alice",
        "name": "European Backpacking",
        "destination": "Europe (France → Italy → Switzerland → Germany → Netherlands → Belgium)",
        "start_date": "2027-05-01",
        "end_date": "2027-05-14",
        "budget": 5000.0,
        "currency": "EUR",
        "expenses": [
            {
                "id": "exp-3-1",
                "description": "Hostels (Paris, Rome, Florence, Zurich, Munich, Amsterdam)",
                "category": "Accommodation",
                "amount": 1200.0,
                "currency": "EUR",
                "date": "2027-05-01"
            },
            {
                "id": "exp-3-2",
                "description": "Grocery, Trattorias, Street Food",
                "category": "Food",
                "amount": 700.0,
                "currency": "EUR",
                "date": "2027-05-07"
            },
            {
                "id": "exp-3-3",
                "description": "Eurail Pass, Flights, Ferries",
                "category": "Transportation",
                "amount": 950.0,
                "currency": "EUR",
                "date": "2027-05-03"
            },
            {
                "id": "exp-3-4",
                "description": "Louvre, Vatican, Chianti Wine Tour, Van Gogh Museum",
                "category": "Activities",
                "amount": 520.0,
                "currency": "EUR",
                "date": "2027-05-05"
            },
            {
                "id": "exp-3-5",
                "description": "Chocolate, Tulip Bulbs, Souvenirs",
                "category": "Shopping",
                "amount": 230.0,
                "currency": "EUR",
                "date": "2027-05-13"
            },
            {
                "id": "exp-3-6",
                "description": "Laundry, SIM Card, Lockers, Tips",
                "category": "Other",
                "amount": 150.0,
                "currency": "EUR",
                "date": "2027-05-10"
            }
        ],
        "days": [
            {
                "id": "day-3-1",
                "date": "2027-05-01",
                "title": "Arrival in Paris, France",
                "activities": [
                    {
                        "id": "act-3-1-1",
                        "name": "Fly into CDG",
                        "location": "Charles de Gaulle Airport (CDG), Paris",
                        "description": "Air France AF011 lands 08:20 Terminal 2E. RER B express train into city"
                    },
                    {
                        "id": "act-3-1-2",
                        "name": "Check in hostel",
                        "location": "St. Christopher's Inn Paris Gare du Nord",
                        "description": "12-bed mixed dormitory, free breakfast included. 10-min walk from Gare du Nord TGV station"
                    },
                    {
                        "id": "act-3-1-3",
                        "name": "Eiffel Tower Visit",
                        "location": "Champ de Mars, 7th Arrondissement",
                        "description": "Pre-booked online 'Skip the Line' Summit ticket (14:00). Top floor 276m with glass floor on 2nd level"
                    },
                    {
                        "id": "act-3-1-4",
                        "name": "Picnic on Champ de Mars",
                        "description": "Purchase picnic from local fromagerie (camembert, baguette, fresh strawberries) + supermarket wine",
                        "location": "Champ de Mars lawn, below Eiffel Tower"
                    },
                    {
                        "id": "act-3-1-5",
                        "name": "Seine River Cruise Sunset",
                        "location": "Bateaux Mouches, Pont de l'Alma",
                        "description": "1-hour sunset cruise. Buy cheap bottle of rosé at supermarket to bring on board"
                    },
                    {
                        "id": "act-3-1-6",
                        "name": "Dinner in Montmartre",
                        "location": "Le Consulat, Montmartre",
                        "description": "Historic 1908 bistro where Picasso and Van Gogh once ate. Try boeuf bourguignon"
                    }
                ]
            },
            {
                "id": "day-3-2",
                "date": "2027-05-02",
                "title": "Paris Museums & Notre-Dame",
                "activities": [
                    {
                        "id": "act-3-2-1",
                        "name": "Louvre Museum",
                        "location": "Musée du Louvre, 1st Arrondissement",
                        "description": "Free with EU under-26 passport. 09:00 entry, see Mona Lisa, Venus de Milo, Winged Victory. 3-hour highlights route"
                    },
                    {
                        "id": "act-3-2-2",
                        "name": "Notre-Dame Island Walk",
                        "location": "Ile de la Cité, Seine River",
                        "description": "Wander Île de la Cité — view Notre-Dame restoration works outside, visit historic Place Dauphine and Sainte-Chapelle stained glass"
                    },
                    {
                        "id": "act-3-2-3",
                        "name": "Latin Quarter Lunch",
                        "location": "Rue Mouffetard, Latin Quarter",
                        "description": "Falafel sandwich at L'As du Fallafel (closed Saturdays), then pastries at Patisserie Paul"
                    },
                    {
                        "id": "act-3-2-4",
                        "name": "Sacre Coeur Basilica",
                        "location": "Basilique du Sacré-Cœur, Montmartre",
                        "description": "Climb 270 dome steps for panoramic Paris view (tickets 8€). Interior photography not permitted"
                    },
                    {
                        "id": "act-3-2-5",
                        "name": "Place du Tertre Art Market",
                        "location": "Place du Tertre, Montmartre",
                        "description": "Watch artists paint portraits and caricatures — consider a 15-minute caricature souvenir (20-30€)"
                    },
                    {
                        "id": "act-3-2-6",
                        "name": "Rue des Rosiers Dinner",
                        "location": "Le Marais, 4th Arrondissement",
                        "description": "Jewish quarter dining — L'As du Fallafel or Chez l'Ami Jean (Basque classics)"
                    }
                ]
            },
            {
                "id": "day-3-3",
                "date": "2027-05-03",
                "title": "Paris to Rome, Italy",
                "activities": [
                    {
                        "id": "act-3-3-1",
                        "name": "Flight to Rome",
                        "location": "Orly Airport (ORY) → Fiumicino (FCO)",
                        "description": "Ryanair FR3482 departs 07:00. Check in online 48h prior. 2hr flight. Only backpack: 10kg hand luggage"
                    },
                    {
                        "id": "act-3-3-2",
                        "name": "Leonardo Express to Termini",
                        "location": "Fiumicino Airport → Roma Termini",
                        "description": "14€ non-stop train every 15 minutes, 32 min direct. Alternative cheaper FL1 regional train to Tiburtina"
                    },
                    {
                        "id": "act-3-3-3",
                        "name": "Hostel check-in",
                        "location": "YellowSquare Hostel Rome, Testaccio",
                        "description": "Party hostel with rooftop pool. 8-bed ensuite dorm. Welcome Aperitivo on rooftop at 19:00 included"
                    },
                    {
                        "id": "act-3-3-4",
                        "name": "Colosseum Guided Tour",
                        "location": "Colosseo, Rome",
                        "description": "15:00 skip-the-line guided tour with access to underground tunnels and arena floor (Roma Pass accepted for discount)"
                    },
                    {
                        "id": "act-3-3-5",
                        "name": "Roman Forum Walk",
                        "location": "Foro Romano & Palatine Hill",
                        "description": "Combined ticket with Colosseum — walk ancient Roman government buildings and temples. Palatine Hill sunset golden hour"
                    },
                    {
                        "id": "act-3-3-6",
                        "name": "Trastevere Dinner",
                        "location": "Trastevere, Rome",
                        "description": "Da Enzo al 29 — family-run trattoria since 1938. Cacio e pepe and carbonara with house wine (bottiglia 1.5L €12)"
                    }
                ]
            },
            {
                "id": "day-3-4",
                "date": "2027-05-04",
                "title": "Rome Vatican & City",
                "activities": [
                    {
                        "id": "act-3-4-1",
                        "name": "Vatican Museums",
                        "location": "Musei Vaticani, Vatican City",
                        "description": "Pre-booked 09:00 fast-track. Follow signs to Raphael's Rooms then Sistine Chapel. Photography only permitted in most rooms (no flash in Sistine)"
                    },
                    {
                        "id": "act-3-4-2",
                        "name": "Sistine Chapel & St. Peter's Basilica",
                        "location": "Cappella Sistina / Basilica di San Pietro",
                        "description": "Direct link from Sistine Chapel right into the basilica (skips the long queue). Climb 551 dome steps (€10 for stairs only)"
                    },
                    {
                        "id": "act-3-4-3",
                        "name": "Pizza al taglio lunch",
                        "location": "Bonci, Testaccio Market",
                        "description": "Legendary Roman square-cut pizza by weight. Try the potato and rosemary slice, and the signature prosciutto cotto"
                    },
                    {
                        "id": "act-3-4-4",
                        "name": "Pantheon",
                        "location": "Pantheon, Piazza della Rotonda",
                        "description": "126 AD Roman temple turned church. 9m oculus open to sky — rain occasionally falls in. Free entry, always open"
                    },
                    {
                        "id": "act-3-4-5",
                        "name": "Trevi Fountain",
                        "location": "Fontana di Trevi",
                        "description": "Over shoulder coin toss with right hand for 'return to Rome'. Estimated 3,000€ coins collected daily (charity)"
                    },
                    {
                        "id": "act-3-4-6",
                        "name": "Spanish Steps & Night Walk",
                        "location": "Piazza di Spagna & Via Condotti",
                        "description": "Luxury shopping street (Prada, Gucci, Bulgari). Evening gelato at Giolitti — Rome's oldest gelateria since 1900"
                    }
                ]
            },
            {
                "id": "day-3-5",
                "date": "2027-05-05",
                "title": "Day Trip to Pompeii",
                "activities": [
                    {
                        "id": "act-3-5-1",
                        "name": "Trenitalia to Naples",
                        "location": "Roma Termini → Napoli Centrale",
                        "description": "Frecciarossa 07:35 high-speed, 1h10m. Advance ticket €19. Buy Trenitalia app tickets in advance online for best price"
                    },
                    {
                        "id": "act-3-5-2",
                        "name": "Circumvesuviana train to Pompeii",
                        "location": "Napoli Centrale P2 → Pompei Scavi",
                        "description": "40 min suburban train (5€). Get off at 'Pompei Scavi — Villa dei Misteri' stop (closest to ruins entrance)"
                    },
                    {
                        "id": "act-3-5-3",
                        "name": "Pompeii Archaeological Site",
                        "location": "Pompeii Scavi, Parco Archeologico",
                        "description": "Full-day ticket (€18, EU under-25 €2). Recommended route: Forum → Stabian Baths → House of the Vettii → Amphitheatre. Wear sun cream, bring water"
                    },
                    {
                        "id": "act-3-5-4",
                        "name": "Authentic Neapolitan Pizza Lunch",
                        "location": "Pizzeria Da Nino, Pompei town",
                        "description": "15-minute walk outside the Porta Marina gate. DOC Margherita pizza from wood-fired oven, just €5"
                    },
                    {
                        "id": "act-3-5-5",
                        "name": "Mount Vesuvius Hike",
                        "location": "Vesuvio National Park, 1000m",
                        "description": "Bus from Pompeii (€15) + park ticket (€10). 20-min steep hike to crater rim. Views of Naples Bay and Pompeii below"
                    },
                    {
                        "id": "act-3-5-6",
                        "name": "Return to Rome",
                        "location": "Pompei → Napoli → Roma",
                        "description": "Return trains. Arrive Rome 21:00. Late snack at a local forno: pizza bianca with mortadella"
                    }
                ]
            },
            {
                "id": "day-3-6",
                "date": "2027-05-06",
                "title": "Rome → Florence",
                "activities": [
                    {
                        "id": "act-3-6-1",
                        "name": "Frecciarossa to Florence",
                        "location": "Roma Termini → Firenze Santa Maria Novella",
                        "description": "08:35 departure, 1h 45m high speed. Trenitalia Frecciarossa 9500 class 'Frecciarossa 1000'. Corner seats A or D best for view"
                    },
                    {
                        "id": "act-3-6-2",
                        "name": "Hostel Check-in",
                        "location": "Plus Florence Hostel",
                        "description": "Design hostel 15 min walk from station. Rooftop pool, spa, free breakfast. 4-bed female/male dorm options, ensuite"
                    },
                    {
                        "id": "act-3-6-3",
                        "name": "Galleria dell'Accademia",
                        "location": "Via Ricasoli 58, Firenze",
                        "description": "13:00 pre-booked timed ticket (€16). Home of Michelangelo's David (5.17m tall marble statue, carved single block 1501-1504)"
                    },
                    {
                        "id": "act-3-6-4",
                        "name": "Ponte Vecchio",
                        "location": "Ponte Vecchio, Arno River",
                        "description": "Medieval stone bridge with jewellers' shops built on it. Originally butchers and tanners until 1593 when Ferdinando I ordered goldsmiths only"
                    },
                    {
                        "id": "act-3-6-5",
                        "name": "Boboli Gardens Walk",
                        "location": "Giardino di Boboli, Palazzo Pitti",
                        "description": "16th-century Medici garden behind Pitti Palace. Admission €10 includes Pitti galleries. Walk to Porcelain Museum for sunset views"
                    },
                    {
                        "id": "act-3-6-6",
                        "name": "Trattoria Dinner & Gelato",
                        "location": "Trattoria ZaZa, Mercato Centrale area",
                        "description": "Bistecca alla Fiorentina (T-bone steak, shared) with ribollita soup. Then gelato at Vivoli — oldest in Florence (est. 1930)"
                    }
                ]
            },
            {
                "id": "day-3-7",
                "date": "2027-05-07",
                "title": "Tuscany Wine Day (Chianti)",
                "activities": [
                    {
                        "id": "act-3-7-1",
                        "name": "Chianti Wine Tour Bus",
                        "location": "Depart Firenze SMN station 09:00",
                        "description": "Organised backpacker tour €55. 2 wineries, vineyard walk, olive oil tasting, and full Tuscan lunch included"
                    },
                    {
                        "id": "act-3-7-2",
                        "name": "Greve in Chianti Walk",
                        "location": "Greve in Chianti",
                        "description": "Hilltop medieval market town. Walk along the main cobbled street with butcher shops and wine enotecas"
                    },
                    {
                        "id": "act-3-7-3",
                        "name": "Castello di Verrazzano Winery Tour",
                        "location": "Greve in Chianti",
                        "description": "13th-century castle estate. Tour underground cellars, barrel room, and aged 10+ year bottles. Vertical tasting: 3 Chianti Classico vintages + Supertuscan"
                    },
                    {
                        "id": "act-3-7-4",
                        "name": "Traditional Tuscan Lunch",
                        "location": "Osteria di Passignano, Badia a Passignano",
                        "description": "Abbadia San Salvatore monastery restaurant. Pappa al pomodoro, wild boar pappardelle, cantucci biscuits dipped in vin santo"
                    },
                    {
                        "id": "act-3-7-5",
                        "name": "San Gimignano Medieval Town",
                        "location": "San Gimignano, Siena Province",
                        "description": "'Town of Fine Towers' — UNESCO site. Climb Torre Grossa (54m) for views of Tuscany rolling hills and 13 remaining towers"
                    },
                    {
                        "id": "act-3-7-6",
                        "name": "Vernaccia di San Gimignano Wine Tasting",
                        "location": "Enoteca under Torre Grossa",
                        "description": "DOCG white wine made with Vernaccia grapes — first Italian wine to receive DOCG status in 1966. Buy a bottle to take home"
                    }
                ]
            },
            {
                "id": "day-3-8",
                "date": "2027-05-08",
                "title": "Florence → Zurich, Switzerland",
                "activities": [
                    {
                        "id": "act-3-8-1",
                        "name": "Depart to Zurich via Milan",
                        "location": "Firenze SMN → Milano Centrale → Zurich HB",
                        "description": "Frecciarossa 07:30 to Milano (1h45m), then Swiss EuroCity train across Gotthard Base Tunnel (57km, 20 min) to Zurich 3h total. Eurail Global Pass used"
                    },
                    {
                        "id": "act-3-8-2",
                        "name": "Check in Budget Hotel",
                        "location": "Hotel Cristal Zurich, Langstrasse",
                        "description": "Basic private double room, CHF 130/night. Cheapest options near Hauptbahnhof. Use self-catering kitchen to save money on expensive Swiss meals"
                    },
                    {
                        "id": "act-3-8-3",
                        "name": "Old Town (Altstadt) Walk",
                        "location": "Niederdorf & Lindenhof, Zurich",
                        "description": "Limmat River east bank cobbled streets. Follow Marktgasse past fountains to Lindenhof Park (hilltop free views of city and river)"
                    },
                    {
                        "id": "act-3-8-4",
                        "name": "Bahnhofstrasse Shopping",
                        "location": "Bahnhofstrasse, Zurich",
                        "description": "World-famous luxury shopping avenue from Paradeplatz to lakefront. Window-shop watches (Rolex, Patek Philippe) and chocolates (Sprüngli)"
                    },
                    {
                        "id": "act-3-8-5",
                        "name": "Lake Zurich Afternoon",
                        "location": "Zürichsee, Utoquai Promenade",
                        "description": "Free lakefront walking path. Bring supermarket sandwich for picnic. Alternative: public ferry Zürichhorn (4h round-trip with Swiss Pass)"
                    },
                    {
                        "id": "act-3-8-6",
                        "name": "Swiss Cheese Fondue Dinner",
                        "location": "Zeughauskeller, Zurich",
                        "description": "Established 1927 — historic armoury hall. Order half-&-half fondue moitié-moitié (Gruyère + Emmental) with kirsch shot, shared rösti potatoes"
                    }
                ]
            },
            {
                "id": "day-3-9",
                "date": "2027-05-09",
                "title": "Interlaken & Alpine Day",
                "activities": [
                    {
                        "id": "act-3-9-1",
                        "name": "Lucerne & Lake Lucerne Stop",
                        "location": "Zurich → Lucerne (1hr) → Interlaken (2hr)",
                        "description": "GoldenPass line scenic train sections. 2-hour stop in Lucerne: Kapellbrücke wooden bridge (1333) and Lion Monument"
                    },
                    {
                        "id": "act-3-9-2",
                        "name": "Interlaken Arrival & Lunch",
                        "location": "Interlaken Ost Station, Bernese Oberland",
                        "description": "Budget lunch at Husi Bierhaus in Höheweg promenade — shared rösti plate for CHF 18"
                    },
                    {
                        "id": "act-3-9-3",
                        "name": "Harder Kulm Viewpoint",
                        "location": "Harder Kulm, Interlaken",
                        "description": "Funicular (CHF 25 return, Swiss Pass 50%) to 1322m summit. Two Lakes Bridge viewpoint with A-frame glass floor lookout"
                    },
                    {
                        "id": "act-3-9-4",
                        "name": "Paragliding (Optional)",
                        "location": "Interlaken Paragliding",
                        "description": "CHF 130 tandem jump from 2000m. 15-20 min flight landing on Interlaken Höhematte lawn. Book on the day if weather permits"
                    },
                    {
                        "id": "act-3-9-5",
                        "name": "Lake Thun Boat Trip",
                        "location": "Lake Thun Steamship Round Trip",
                        "description": "Short section: Interlaken West → Spiez by historic steamship (Swiss Pass 100% covered). Enjoy mountain reflections at golden hour"
                    },
                    {
                        "id": "act-3-9-6",
                        "name": "Return to Zurich & Dinner",
                        "location": "Zurich HB",
                        "description": "Arrive Zurich 20:30. Cheap dinner at Hiltl oldest vegetarian restaurant in world (est. 1898) — buffet by weight"
                    }
                ]
            },
            {
                "id": "day-3-10",
                "date": "2027-05-10",
                "title": "Zurich → Munich, Germany",
                "activities": [
                    {
                        "id": "act-3-10-1",
                        "name": "ICE Train to Munich",
                        "location": "Zurich HB → München Hbf",
                        "description": "09:04 ICE640 via Lindau & Memmingen, 3h 32 min direct. Deutsche Bahn ICE first class upgrade €30 online (includes free coffee and bigger seats). Eurail pass valid"
                    },
                    {
                        "id": "act-3-10-2",
                        "name": "Wombats Hostel Check-in",
                        "location": "Wombats City Hostel Munich",
                        "description": "Award-winning hostel 5 min from Hauptbahnhof. 6-bed ensuite dorm. Free welcome beer coupon at The Lounge bar, free walking tour daily 11:00"
                    },
                    {
                        "id": "act-3-10-3",
                        "name": "Marienplatz & Glockenspiel",
                        "location": "Marienplatz, Munich Altstadt",
                        "description": "12:00 Glockenspiel performance on the Rathaus (Town Hall) tower. 43 bells and 32 life-sized figures re-create 16th-century tournaments"
                    },
                    {
                        "id": "act-3-10-4",
                        "name": "Frauenkirche Twin Towers",
                        "location": "Frauenkirche, Munich",
                        "description": "Cathedral of Our Lady. Climb south tower 299 steps (€4) for Alps panorama. Look for the 'Devil's Footprint' black mark inside near entrance"
                    },
                    {
                        "id": "act-3-10-5",
                        "name": "Viktualienmarkt Lunch",
                        "location": "Viktualienmarkt, central Munich",
                        "description": "Daily farmers' market since 1807. Buy a Weißwurst (white sausage) with sweet mustard, plus bretzel and radish salad. Sit on market benches"
                    },
                    {
                        "id": "act-3-10-6",
                        "name": "Hofbräuhaus Beer Hall Evening",
                        "location": "Hofbräuhaus am Platzl, Munich",
                        "description": "World-famous royal beer hall (est. 1589). 1-litre Mass of HB Original, roasted half-chicken, live oompah band. Book weekday to avoid weekend crowds"
                    }
                ]
            },
            {
                "id": "day-3-11",
                "date": "2027-05-11",
                "title": "Neuschwanstein & Dachau Day",
                "activities": [
                    {
                        "id": "act-3-11-1",
                        "name": "Regional train to Dachau",
                        "location": "Munich → Dachau Bahnhof",
                        "description": "S-Bahn S2 line towards Petershausen, 25 min. Dachau Concentration Camp memorial: free entrance, 15-min bus from station"
                    },
                    {
                        "id": "act-3-11-2",
                        "description": "Dachau Memorial Site. Free audio guide. Former concentration camp — 41,000 prisoners died. Original barracks, gas chamber, ovens, museum. Allow 3 hours minimum",
                        "location": "KZ-Gedenkstätte Dachau",
                        "name": "Dachau Concentration Camp Memorial"
                    },
                    {
                        "id": "act-3-11-3",
                        "name": "Return and lunch in Munich",
                        "location": "Munich",
                        "description": "S-Bahn returns. Lunch at 'Zum Dürnbräu' Augustiner beer hall, affordable local favourite near main station"
                    },
                    {
                        "id": "act-3-11-4",
                        "name": "Afternoon excursion to Füssen",
                        "location": "Munich → Füssen",
                        "description": "Regional Bayern ticket 25€ group (up to 5 people). Train 2h via Buchloe. Bavarian scenery of rolling hills, lakes, and dairy farms"
                    },
                    {
                        "id": "act-3-11-5",
                        "name": "Neuschwanstein Castle Exterior Walk",
                        "location": "Schloss Neuschwanstein, Hohenschwangau",
                        "description": "Bus from Füssen 10 min. Walk up the Pöllat Gorge road to the castle. Interior tickets 2 weeks in advance sold out, but exterior + Marienbrücke free view point"
                    },
                    {
                        "id": "act-3-11-6",
                        "name": "Marienbrücke Photo Spot",
                        "location": "Marienbrücke (Queen Mary's Bridge)",
                        "description": "10-min steep uphill from castle. The iconic postcard view of Neuschwanstein over waterfall gorge. Sunset lighting best for photos"
                    }
                ]
            },
            {
                "id": "day-3-12",
                "date": "2027-05-12",
                "title": "Munich → Amsterdam, Netherlands",
                "activities": [
                    {
                        "id": "act-3-12-1",
                        "name": "Night Train to Amsterdam",
                        "location": "München Hbf → Amsterdam Centraal",
                        "description": "ÖBB NightJet NJ421 departs 20:18, arrives 09:33 next day. Save one night's accommodation! Couchette 6-berth booked €59 supplement on Eurail. Pack sleeping bag liner for hygiene"
                    },
                    {
                        "id": "act-3-12-2",
                        "name": "Breakfast on the train",
                        "description": "Dining car: Dutch-style broodje haring sandwich or muesli with fresh milk. Breakfast not included with couchette ticket",
                        "location": "NJ421 Restaurant Car"
                    },
                    {
                        "id": "act-3-12-3",
                        "name": "Arrive Amsterdam & Hostel Check-in",
                        "location": "ClinkNOORD Hostel, Amsterdam Noord",
                        "description": "New waterfront hostel. 4-bed mixed dorm, breakfast included. Free ferry from CS behind central library (IJplein) every 6 min 24/7"
                    },
                    {
                        "id": "act-3-12-4",
                        "name": "Dam Square & Royal Palace",
                        "location": "Dam Square, Centrum",
                        "description": "Historical central square. National Monument (WWII), Royal Palace (17th-century). Beware of scammers selling fake cocaine/cannabis on the streets"
                    },
                    {
                        "id": "act-3-12-5",
                        "name": "Anne Frank House Booked Ticket",
                        "location": "Anne Frank Huis, Prinsengracht 263",
                        "description": "Online tickets 15:30 entry (€14). Mandatory booking weeks in advance. Authentic restored Secret Annex. Photography not allowed inside. 80-minute self-guided audio tour"
                    },
                    {
                        "id": "act-3-12-6",
                        "name": "Canal Ring Walk at Golden Hour",
                        "location": "Prinsengracht & Keizersgracht canals",
                        "description": "UNESCO 17th-century canal ring. Walk north to south along the three main canals. Best evening light for photos between 19:00-20:30 in May"
                    },
                    {
                        "id": "act-3-12-7",
                        "name": "Indonesian Rijsttafel Dinner",
                        "location": "Restaurant Blauw, Oude Pijp",
                        "description": "Colonial Dutch-Indonesian rice table. 15+ small dishes shared, €35 prix fixe. Try rendang beef, gado-gado salad, spicy sambal"
                    }
                ]
            },
            {
                "id": "day-3-13",
                "date": "2027-05-13",
                "title": "Amsterdam + Bruges Day Trip (Belgium)",
                "activities": [
                    {
                        "id": "act-3-13-1",
                        "name": "Thalys to Brussels then Bruges",
                        "location": "Amsterdam Centraal → Brussel Zuid → Brugge",
                        "description": "08:03 Thalys to Brussels 1h47m, then local IC train to Bruges (50 min). Eurail Thalys seat reservation €10 compulsory online"
                    },
                    {
                        "id": "act-3-13-2",
                        "name": "Bruges Market Square & Belfry",
                        "location": "Grote Markt (Markt), Bruges",
                        "description": "Medieval square flanked by 12th-century Belfry (climb 366 steps, €12). Provincial Hof and statue of Jan Breydel & Pieter de Coninck"
                    },
                    {
                        "id": "act-3-13-3",
                        "name": "Burg Square & Basilica of Holy Blood",
                        "location": "Burgplein, Brugge",
                        "description": "Town hall, old civil registry. Heilig-Bloedbasiliek: small Gothic chapel housing a vial of Christ's blood (procession every Ascension Day)"
                    },
                    {
                        "id": "act-3-13-4",
                        "name": "Canal Boat Tour Bruges",
                        "location": "Brugge Boottochten, Dijver canal dock",
                        "description": "30-min guided boat ride €12. Explains the UNESCO old town history, gabled houses, and famous Minnewater (Lake of Love) swans"
                    },
                    {
                        "id": "act-3-13-5",
                        "name": "Belgian Lunch Moules-Frites",
                        "location": "Bistro de Eetkamer, Bruges Sint-Anna quarter",
                        "description": "Moules marinières (white wine garlic mussels) with triple-fried frites and Andalouse sauce + a fresh Hoegaarden wheat beer"
                    },
                    {
                        "id": "act-3-13-6",
                        "name": "Belgian Chocolate Tasting",
                        "location": "Dumon Chocolatier, Bruges Simon Stevinplein",
                        "description": "Old family chocolatier. 6-piece praline tasting flight: Gianduja (hazelnut), ganache salted caramel, speculoos, fresh raspberry"
                    },
                    {
                        "id": "act-3-13-7",
                        "name": "Return Amsterdam Night Walk",
                        "location": "Amsterdam Red Light District (De Wallen)",
                        "description": "Evening return + walk through the famous De Wallen district. Observe from public streets, strictly NO photography of workers, coffeeshops smell of cannabis"
                    }
                ]
            },
            {
                "id": "day-3-14",
                "date": "2027-05-14",
                "title": "Departure from Amsterdam",
                "activities": [
                    {
                        "id": "act-3-14-1",
                        "name": "Morning Floating Flower Market",
                        "location": "Bloemenmarkt, Singel Canal",
                        "description": "Floating flower market stalls on Singel canal — buy bulbs for home export (tulip bulbs require phytosanitary certificate boxed for EU export)"
                    },
                    {
                        "id": "act-3-14-2",
                        "name": "Van Gogh Museum",
                        "location": "Museumplein, Van Gogh Museum",
                        "description": "09:00 first entry (€22, book online weeks in advance). World's largest Van Gogh collection: 200 paintings, 500 drawings, 750 personal letters"
                    },
                    {
                        "id": "act-3-14-3",
                        "name": "Lunch: Stroopwafel & Haring",
                        "location": "Albert Cuypstraatmarkt, De Pijp",
                        "description": "Daily street market. Fresh stroopwafel (hot caramel syrup waffle sandwich) at Lanskroon and maatje haring (raw herring with onions, eaten holding tail up)"
                    },
                    {
                        "id": "act-3-14-4",
                        "name": "Vlaams Frites Patat Special",
                        "location": "Vlaams Friteshuis Vleminckx, Voetboogstraat 33",
                        "description": "Legendary Amsterdam fries since 1957. Thick cut double-fried Bintje potatoes, Speciaal sauce (mayo, satesaus, onion, ketchup)"
                    },
                    {
                        "id": "act-3-14-5",
                        "name": "Train to Schiphol Airport",
                        "location": "Amsterdam Centraal → Schiphol Airport (AMS)",
                        "description": "14:00 Intercity train 14 minutes direct. 3rd floor platform 1/2. Reach 3 hours before intercontinental flight due to passport & security queues"
                    }
                ]
            }
        ],
        "journal_entries": [
            {
                "id": "je-3-1",
                "title": "First Night in Paris",
                "content": "Arrived in Paris this morning on the Air France flight. The RER B train into the city was packed, but we finally made it to the hostel around midday. Dropped our backpacks and headed straight to the Eiffel Tower — the pre-booked summit ticket was worth every cent. Glass floor on the second level terrified me at first, but then I got used to it. Had a picnic on the Champ de Mars lawn with baguette, camembert, strawberries, and a cheap bottle of Bordeaux from the supermarket. Ended the day with a sunset Seine cruise. The city of lights really lives up to its name!",
                "date": "2027-05-01",
                "created_at": "2027-05-01T21:40:00",
                "updated_at": "2027-05-01T21:40:00"
            },
            {
                "id": "je-3-2",
                "title": "Rome — Colosseum Underground",
                "content": "Flew from Orly to Fiumicino this morning on a budget Ryanair flight. Backpack barely fit under the seat. The Leonardo Express took us straight to Termini station, then a short walk to the YellowSquare hostel. The Colosseum guided tour in the afternoon was the highlight — we got access to the underground tunnels where gladiators and animals waited before entering the arena. Standing on the arena floor looking up at the tiers, I could almost hear the crowds roaring. Ended the night at Trastevere with cacio e pepe and a 1.5L bottle of house red. Life is good.",
                "date": "2027-05-03",
                "created_at": "2027-05-03T23:10:00",
                "updated_at": "2027-05-03T23:10:00"
            },
            {
                "id": "je-3-3",
                "title": "Chianti Wine Tasting",
                "content": "Took the Chianti wine tour bus today — best decision of the entire trip so far. We visited Castello di Verrazzano, a 13th-century castle estate with underground cellars. The vertical tasting of three Chianti Classico vintages plus a Supertuscan blew my mind. Traditional Tuscan lunch at an osteria in Passignano was incredible — bistecca alla Fiorentina shared with three other backpackers from the tour, paired with a local Chianti. My liver might hate me tomorrow, but my taste buds are in heaven. Two more countries to go: Switzerland and Germany.",
                "date": "2027-05-07",
                "created_at": "2027-05-07T22:25:00",
                "updated_at": "2027-05-07T22:25:00"
            }
        ]
    }
]
