import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Deterministic Seed
SEED = 42

SOURCES = [
    "Deccan Business Wire",
    "South Asia Technology Review",
    "Metro Press Network",
    "Capital Markets Daily",
    "Pacific Rim Dispatch",
    "Global Tech Pulse",
    "Urban Transport Weekly",
    "Financial Chronicle Direct",
    "Apex Energy Journal",
    "National News Syndicate",
    "Indo-Pacific Observer",
    "State Commerce Gazette",
    "Healthcare & Biotech Digest",
    "Sports Horizon Media"
]

# Ground Truth Events definition (24 Events, 81 Raw Items)
EVENT_DEFINITIONS = [
    # ----------------------------------------------------
    # Pair 1: Semiconductor Facilities (Tech) - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-TECH-001",
        "title": "Government clearance for $2 Billion Semiconductor Manufacturing Facility in Hyderabad",
        "category": "Technology",
        "false_match_pair": "EVT-TECH-002",
        "facts": {"location": "Hyderabad", "type": "Manufacturing Facility", "value": "$2 Billion"},
        "items": [
            {
                "source": "Deccan Business Wire",
                "headline": "Hyderabad semiconductor manufacturing facility receives government clearance",
                "body": "Authorities have cleared a proposed $2 billion semiconductor manufacturing facility in Hyderabad. The project is expected to create thousands of direct tech and engineering jobs once construction begins."
            },
            {
                "source": "South Asia Technology Review",
                "headline": "Government clears $2bn chip plant planned for Hyderabad",
                "body": "A major chip manufacturing project planned for Hyderabad has received final government approval, according to officials familiar with the decision. Total capital outlay is estimated at $2 billion."
            },
            {
                "source": "Metro Press Network",
                "headline": "Hyderabad set for major semiconductor investment after project approval",
                "body": "Hyderabad is set to receive a large semiconductor investment after authorities cleared plans for a fabrication facility worth about $2 billion."
            },
            {
                "source": "Global Tech Pulse",
                "headline": "Telangana capital secures $2B chip manufacturing plant approval",
                "body": "The union government has officially greenlit a $2 billion semiconductor production unit in Hyderabad, boosting India's domestic hardware manufacturing push."
            }
        ]
    },
    {
        "event_id": "EVT-TECH-002",
        "title": "$800 Million Semiconductor R&D Center Commitment in Bengaluru",
        "category": "Technology",
        "false_match_pair": "EVT-TECH-001",
        "facts": {"location": "Bengaluru", "type": "R&D Center", "value": "$800 Million"},
        "items": [
            {
                "source": "Capital Markets Daily",
                "headline": "Bengaluru technology research center gets $800m semiconductor commitment",
                "body": "A separate technology research center planned in Bengaluru has secured an $800 million investment commitment. The project focuses strictly on semiconductor R&D and chip architecture design rather than mass production."
            },
            {
                "source": "South Asia Technology Review",
                "headline": "Karnataka capital attracts $800M chip R&D hub investment",
                "body": "Investors have committed $800 million to establish an advanced semiconductor research facility in Bengaluru, highlighting the city's leadership in chip design talent."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "New $800 million semiconductor R&D complex approved for Bengaluru",
                "body": "State authorities in Karnataka have sanctioned an $800 million semiconductor technology lab in Bengaluru focused on next-generation microarchitecture."
            },
            {
                "source": "Global Tech Pulse",
                "headline": "Bengaluru secures $800M semiconductor research lab commitment",
                "body": "A major consortium of technology firms has pledged $800 million for a semiconductor research and development center situated in Bengaluru."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 2: Central Bank Interest Rate Decisions - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-BIZ-001",
        "title": "RBI cuts repo rate by 25 basis points to 6.25%",
        "category": "Business",
        "false_match_pair": "EVT-BIZ-002",
        "facts": {"institution": "RBI (Reserve Bank of India)", "action": "Rate Cut 25bps", "new_rate": "6.25%"},
        "items": [
            {
                "source": "Financial Chronicle Direct",
                "headline": "RBI cuts benchmark repo rate by 25 bps to 6.25% in surprise policy move",
                "body": "The Monetary Policy Committee of the Reserve Bank of India voted to lower the key repo rate by 25 basis points to 6.25%, citing easing headline inflation pressures."
            },
            {
                "source": "Capital Markets Daily",
                "headline": "Reserve Bank lowers repo rate to 6.25 percent to spur economic growth",
                "body": "In a monetary policy shift, India's central bank reduced the benchmark lending rate by 25 basis points to 6.25%, aiming to support credit demand."
            },
            {
                "source": "National News Syndicate",
                "headline": "RBI lowers interest rates: Repo rate trimmed to 6.25%",
                "body": "India's central bank has cut its key repo rate by 0.25 percentage points to 6.25%, providing relief for commercial borrowers and home loan seekers."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Monetary Policy Committee cuts RBI repo rate to 6.25%",
                "body": "Following its bi-monthly review, the RBI Monetary Policy Committee announced a 25 basis point cut in the repo rate, bringing it down to 6.25%."
            }
        ]
    },
    {
        "event_id": "EVT-BIZ-002",
        "title": "US Federal Reserve holds benchmark interest rate steady at 5.25%",
        "category": "Business",
        "false_match_pair": "EVT-BIZ-001",
        "facts": {"institution": "US Federal Reserve", "action": "Rate Hold", "rate": "5.25%"},
        "items": [
            {
                "source": "Pacific Rim Dispatch",
                "headline": "Federal Reserve maintains US interest rates at 5.25% amid sticky inflation",
                "body": "The US Federal Reserve held its benchmark interest rate target steady at 5.25% to 5.50%, noting that while economic activity continues to expand, inflation remains elevated."
            },
            {
                "source": "Financial Chronicle Direct",
                "headline": "US Fed leaves interest rates unchanged at 5.25% baseline",
                "body": "American central bankers opted to keep key borrowing costs untouched at 5.25%, signaling patience before considering any monetary policy easing."
            },
            {
                "source": "Global Tech Pulse",
                "headline": "Fed pauses rate changes, keeping key benchmark at 5.25%",
                "body": "In line with market expectations, the Federal Reserve kept interest rates frozen at 5.25%, reiterating its commitment to returning inflation to target levels."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "US central bank holds monetary policy rate steady at 5.25%",
                "body": "The US Federal Reserve concluded its policy meeting by leaving key benchmark interest rates unchanged at 5.25%."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 3: Urban Metro Railway Projects - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-TRN-001",
        "title": "Mumbai Metro Line 3 Underground Corridor Commercial Commissioning",
        "category": "Transport",
        "false_match_pair": "EVT-TRN-002",
        "facts": {"city": "Mumbai", "line": "Line 3 (Aqua Line)", "type": "Underground Metro"},
        "items": [
            {
                "source": "Urban Transport Weekly",
                "headline": "Mumbai Metro Line 3 underground Aqua Line opens for commercial passenger service",
                "body": "Mumbai's first fully underground metro corridor, Line 3 connecting Colaba to SEEPZ, commenced passenger operations today following safety clearance."
            },
            {
                "source": "Metro Press Network",
                "headline": "Passengers ride Mumbai Aqua Line 3 as underground metro opens",
                "body": "Commuters in Mumbai turned out in large numbers as the long-awaited Line 3 underground metro line officially launched passenger runs between South Mumbai and key commercial hubs."
            },
            {
                "source": "Deccan Business Wire",
                "headline": "Mumbai Line 3 underground metro line flags off first passenger trains",
                "body": "Urban transit authorities in Mumbai inaugurated revenue operations on the Line 3 Aqua Line corridor, bringing seamless underground transit to the financial capital."
            },
            {
                "source": "National News Syndicate",
                "headline": "Underground transit era begins in Mumbai with Line 3 inauguration",
                "body": "Commercial services officially began on Mumbai Metro Line 3 today, cutting commute times across densely populated urban centers."
            }
        ]
    },
    {
        "event_id": "EVT-TRN-002",
        "title": "Delhi Metro Phase 4 Silver Line Tunneling Completion",
        "category": "Transport",
        "false_match_pair": "EVT-TRN-001",
        "facts": {"city": "Delhi", "line": "Phase 4 Silver Line", "type": "Tunneling Completion"},
        "items": [
            {
                "source": "Urban Transport Weekly",
                "headline": "Delhi Metro Phase 4 Silver Line completes final underground tunnel breakthrough",
                "body": "Engineers on the Delhi Metro Phase 4 Silver Line project achieved a major milestone today by completing tunneling work on the Aerocity-Tughlakabad underground section."
            },
            {
                "source": "Metro Press Network",
                "headline": "Tunnel breakthrough achieved for Delhi Metro Silver Line Phase 4",
                "body": "DMRC announced the completion of underground tunneling for a critical segment of the Phase 4 Silver Line connecting Aerocity with Tughlakabad."
            },
            {
                "source": "Pacific Rim Dispatch",
                "headline": "Delhi Metro achieves Phase 4 underground tunneling milestone",
                "body": "Construction teams finished excavation work on the Delhi Metro Phase 4 Silver Line underground tunnel using tunnel boring machines."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Silver Line tunneling completed for Delhi Metro expansion",
                "body": "The Delhi Metro Rail Corporation reported successful breakthrough of the last tunnel boring machine working on the Phase 4 Silver Line route."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 4: Renewable Energy Projects - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-NRG-001",
        "title": "Reliance $10 Billion Solar Gigafactory Commissioning in Kutch, Gujarat",
        "category": "Energy",
        "false_match_pair": "EVT-NRG-002",
        "facts": {"company": "Reliance Industries", "location": "Kutch, Gujarat", "tech": "Solar Gigafactory", "value": "$10 Billion"},
        "items": [
            {
                "source": "Apex Energy Journal",
                "headline": "Reliance commissions $10B solar PV manufacturing gigafactory in Kutch",
                "body": "Reliance Industries has officially commissioned the first phase of its $10 billion solar photovoltaic manufacturing gigafactory in Kutch, Gujarat."
            },
            {
                "source": "Deccan Business Wire",
                "headline": "Giant $10 billion solar panel factory opens in Kutch district",
                "body": "Operations have started at a massive $10 billion solar equipment manufacturing plant located in Kutch, Gujarat, aimed at supplying domestic solar projects."
            },
            {
                "source": "Financial Chronicle Direct",
                "headline": "Kutch solar gigafactory begins commercial production following $10B outlay",
                "body": "Production lines for high-efficiency solar modules went live today at the new $10 billion solar gigafactory facility in Gujarat's Kutch region."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Gujarat solar manufacturing gigafactory backed by $10B investment launches",
                "body": "A landmark $10 billion solar PV manufacturing complex in Kutch has begun commercial operations, marking a giant step for green energy independence."
            }
        ]
    },
    {
        "event_id": "EVT-NRG-002",
        "title": "Adani $5 Billion Wind Energy Park Inauguration in Jaisalmer, Rajasthan",
        "category": "Energy",
        "false_match_pair": "EVT-NRG-001",
        "facts": {"company": "Adani Green Energy", "location": "Jaisalmer, Rajasthan", "tech": "Wind Energy Park", "value": "$5 Billion"},
        "items": [
            {
                "source": "Apex Energy Journal",
                "headline": "Adani Green inaugurates $5B wind power plant complex in Jaisalmer",
                "body": "Adani Green Energy has inaugurated a $5 billion utility-scale wind power park in Jaisalmer, Rajasthan, adding 3,000 MW of renewable generation capacity."
            },
            {
                "source": "Capital Markets Daily",
                "headline": "Jaisalmer wind energy project launches after $5 billion investment",
                "body": "A $5 billion wind farm complex in Rajasthan's Jaisalmer district has commenced feeding power into the national grid following official commissioning."
            },
            {
                "source": "National News Syndicate",
                "headline": "$5B Rajasthan wind energy park begins feeding power to grid",
                "body": "The newly completed $5 billion wind turbine facility in Jaisalmer has officially begun commercial electricity generation in western Rajasthan."
            },
            {
                "source": "Pacific Rim Dispatch",
                "headline": "Wind power park near Jaisalmer goes live following $5B project rollout",
                "body": "Clean energy developer Adani Green completed the installation of heavy wind turbine generators at its $5 billion Jaisalmer clean power hub."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 5: Healthcare & Medical Innovations - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-HLT-001",
        "title": "AIIMS New Delhi Breakthrough in Phase-3 mRNA Cancer Vaccine Trials",
        "category": "Healthcare",
        "false_match_pair": "EVT-HLT-002",
        "facts": {"institution": "AIIMS New Delhi", "field": "Cancer Vaccine", "tech": "mRNA Phase-3"},
        "items": [
            {
                "source": "Healthcare & Biotech Digest",
                "headline": "AIIMS New Delhi reports promising Phase-3 results for indigenous mRNA cancer vaccine",
                "body": "Researchers at AIIMS New Delhi announced groundbreaking Phase-3 clinical trial data showing strong efficacy for an indigenous mRNA therapeutic cancer vaccine."
            },
            {
                "source": "National News Syndicate",
                "headline": "Indigenous mRNA cancer vaccine shows high efficacy in AIIMS trial",
                "body": "Clinical trials conducted at AIIMS Delhi revealed encouraging immunogenicity and safety metrics for a newly developed mRNA vaccine targeting solid tumors."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "AIIMS researchers achieve Phase-3 success with mRNA oncology vaccine",
                "body": "Medical scientists at AIIMS in New Delhi have successfully completed Phase-3 human trials for a novel mRNA-based cancer immunotherapy product."
            },
            {
                "source": "Global Tech Pulse",
                "headline": "Phase-3 clinical data validates AIIMS Delhi mRNA cancer vaccine candidate",
                "body": "A clinical study led by AIIMS New Delhi confirmed high response rates among patients participating in the trial for India's first mRNA cancer shot."
            }
        ]
    },
    {
        "event_id": "EVT-HLT-002",
        "title": "NIMHANS Bengaluru Study on AI-Assisted Early Alzheimer Detection",
        "category": "Healthcare",
        "false_match_pair": "EVT-HLT-001",
        "facts": {"institution": "NIMHANS Bengaluru", "field": "Alzheimer Detection", "tech": "AI Brain Scans"},
        "items": [
            {
                "source": "Healthcare & Biotech Digest",
                "headline": "NIMHANS Bengaluru unveils AI diagnostic model for early Alzheimer detection",
                "body": "Scientists at NIMHANS Bengaluru have published a milestone study detailing an artificial intelligence model that identifies early biomarkers of Alzheimer's disease from neuroimaging."
            },
            {
                "source": "South Asia Technology Review",
                "headline": "Bengaluru institute NIMHANS uses AI algorithms to detect Alzheimer's early",
                "body": "Researchers at NIMHANS in Bengaluru developed a deep-learning algorithm capable of predicting cognitive decline up to five years before symptom onset."
            },
            {
                "source": "Global Tech Pulse",
                "headline": "NIMHANS study demonstrates AI precision in diagnosing neurodegenerative conditions",
                "body": "A collaborative study conducted by NIMHANS Bengaluru demonstrated 94% accuracy in detecting early stage Alzheimer's disease using AI analysis of MRI scans."
            },
            {
                "source": "Pacific Rim Dispatch",
                "headline": "AI brain scan model created at NIMHANS catches early Alzheimer's signs",
                "body": "Medical researchers in Bengaluru at NIMHANS showcased an AI platform trained on brain scan datasets to diagnose early Alzheimer's disease."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 6: Airport Infrastructure - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-AVN-001",
        "title": "Noida International Airport at Jewar Completes Inaugural Trial Flights",
        "category": "Transport",
        "false_match_pair": "EVT-AVN-002",
        "facts": {"location": "Jewar, Noida (UP)", "airport": "Noida International Airport", "status": "Calibration Flights Complete"},
        "items": [
            {
                "source": "Urban Transport Weekly",
                "headline": "Noida International Airport at Jewar completes inaugural flight calibration trials",
                "body": "The upcoming Noida International Airport at Jewar successfully concluded its first round of calibration flight trials for instrument landing systems."
            },
            {
                "source": "Metro Press Network",
                "headline": "Calibration aircraft land at Jewar Noida airport in successful test run",
                "body": "Aviation authorities reported flawless execution of trial flight landings at the new Jewar airport site in Greater Noida."
            },
            {
                "source": "Deccan Business Wire",
                "headline": "Jewar airport marks milestone with successful trial flight operations",
                "body": "Flight calibration tests were completed at Noida International Airport in Jewar, clearing the runway for upcoming commercial operationalization."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Noida airport at Jewar passes key flight calibration inspection",
                "body": "Test aircraft completed multiple approaches and touch-and-go landings at the Jewar international airport greenfield project."
            }
        ]
    },
    {
        "event_id": "EVT-AVN-002",
        "title": "Navi Mumbai International Airport Receives DGCA Aerodrome License",
        "category": "Transport",
        "false_match_pair": "EVT-AVN-001",
        "facts": {"location": "Navi Mumbai (Maharashtra)", "airport": "Navi Mumbai International Airport", "status": "Aerodrome License Sanctioned"},
        "items": [
            {
                "source": "Urban Transport Weekly",
                "headline": "Navi Mumbai International Airport granted formal DGCA aerodrome license",
                "body": "Aviation regulator DGCA has granted the official aerodrome license to Navi Mumbai International Airport, paving the way for commercial flight operations."
            },
            {
                "source": "Financial Chronicle Direct",
                "headline": "DGCA issues operational license for Navi Mumbai greenfield airport",
                "body": "The Directorate General of Civil Aviation issued the aerodrome license for Navi Mumbai International Airport after inspecting infrastructure safety."
            },
            {
                "source": "Metro Press Network",
                "headline": "Navi Mumbai airport secures regulatory license for commercial flights",
                "body": "Project developers at Navi Mumbai International Airport received final regulatory licensing approval from civil aviation authorities."
            },
            {
                "source": "Pacific Rim Dispatch",
                "headline": "Aviation regulator approves aerodrome license for Navi Mumbai airport",
                "body": "DGCA inspectors formally signed off on safety and security protocols, issuing the aerodrome license for Navi Mumbai's new airport facility."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 7: EV Automotive Manufacturing - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-AUTO-001",
        "title": "Tata Motors $1.5 Billion EV Assembly Mega-Plant in Sanand, Gujarat",
        "category": "Business",
        "false_match_pair": "EVT-AUTO-002",
        "facts": {"company": "Tata Motors", "location": "Sanand, Gujarat", "facility": "EV Vehicle Assembly", "value": "$1.5 Billion"},
        "items": [
            {
                "source": "State Commerce Gazette",
                "headline": "Tata Motors opens $1.5B electric vehicle assembly mega-plant in Sanand",
                "body": "Tata Motors inaugurated a $1.5 billion manufacturing plant dedicated exclusively to passenger electric vehicle assembly in Sanand, Gujarat."
            },
            {
                "source": "Deccan Business Wire",
                "headline": "$1.5 billion Tata EV factory begins car production in Sanand",
                "body": "Commercial production of electric SUVs began today at Tata Motors' new $1.5 billion vehicle manufacturing hub located in Sanand."
            },
            {
                "source": "Capital Markets Daily",
                "headline": "Tata Motors expands Sanand footprint with $1.5B electric car facility",
                "body": "Automaker Tata Motors expanded its EV manufacturing footprint after commissioning a $1.5 billion vehicle plant in Sanand, Gujarat."
            },
            {
                "source": "National News Syndicate",
                "headline": "Sanand EV factory launched by Tata Motors following $1.5B investment",
                "body": "Tata Motors formally rolled out the first batch of electric vehicles from its newly constructed $1.5 billion assembly plant in Sanand."
            }
        ]
    },
    {
        "event_id": "EVT-AUTO-002",
        "title": "Mahindra $900 Million EV Battery Cell Giga-facility in Pune, Maharashtra",
        "category": "Business",
        "false_match_pair": "EVT-AUTO-001",
        "facts": {"company": "Mahindra & Mahindra", "location": "Pune, Maharashtra", "facility": "Battery Cell Manufacturing", "value": "$900 Million"},
        "items": [
            {
                "source": "State Commerce Gazette",
                "headline": "Mahindra commits $900M for EV battery cell gigafactory near Pune",
                "body": "Mahindra & Mahindra announced a $900 million investment to establish an advanced battery cell manufacturing gigafactory located near Pune, Maharashtra."
            },
            {
                "source": "Financial Chronicle Direct",
                "headline": "Pune selected for Mahindra's new $900 million EV battery plant",
                "body": "Mahindra secured regulatory approval for a $900 million EV battery pack assembly and cell chemistry manufacturing complex in the Pune industrial belt."
            },
            {
                "source": "South Asia Technology Review",
                "headline": "Mahindra breaks ground on $900M battery manufacturing facility in Pune",
                "body": "Construction commenced on Mahindra's $900 million EV battery plant near Pune, designed to supply power packs for upcoming electric SUV models."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "Mahindra invests $900M in Pune electric vehicle battery factory",
                "body": "Mahindra & Mahindra broke ground on a $900 million specialized facility for manufacturing electric vehicle battery modules in Pune."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 8: River Environmental Directives - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-ENV-001",
        "title": "NGT Sanctions ₹500 Crore Penalty on Yamuna River Toxic Foam Polluters",
        "category": "Environment",
        "false_match_pair": "EVT-ENV-002",
        "facts": {"court": "NGT (National Green Tribunal)", "target": "Yamuna River", "city": "Delhi", "penalty": "₹500 Crore"},
        "items": [
            {
                "source": "National News Syndicate",
                "headline": "National Green Tribunal slaps ₹500 crore penalty over Yamuna River toxic foam",
                "body": "The National Green Tribunal imposed an environmental compensation penalty of ₹500 crore on industrial units polluting the Yamuna river in Delhi."
            },
            {
                "source": "Metro Press Network",
                "headline": "NGT orders ₹500 crore fine for industrial effluent discharge into Yamuna",
                "body": "Observing severe toxic froth formation on the Yamuna, the Green Tribunal penalized defaulting civic agencies and industrial clusters ₹500 crore."
            },
            {
                "source": "Urban Transport Weekly",
                "headline": "Yamuna river pollution: NGT slaps ₹500 crore environmental compensation fine",
                "body": "The NGT directed authorities to collect ₹500 crore in environmental damages from entities responsible for dumping untreated industrial waste into the Yamuna."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Tribunal imposes ₹500 cr fine over untreated sewage waste in Yamuna",
                "body": "A principal bench of the NGT issued strict directions and a ₹500 crore fine targeting toxic effluent discharges corrupting the Yamuna river."
            }
        ]
    },
    {
        "event_id": "EVT-ENV-002",
        "title": "High Court Directs Action Plan for Mula-Mutha River Cleanup in Pune",
        "category": "Environment",
        "false_match_pair": "EVT-ENV-001",
        "facts": {"court": "Bombay High Court", "target": "Mula-Mutha River", "city": "Pune", "action": "STP Action Plan"},
        "items": [
            {
                "source": "National News Syndicate",
                "headline": "High Court demands immediate action plan to clean Pune's Mula-Mutha river",
                "body": "The Bombay High Court directed municipal authorities in Pune to submit a comprehensive blueprint for stopping raw sewage disposal into the Mula-Mutha river."
            },
            {
                "source": "Metro Press Network",
                "headline": "Pune municipal body reprimanded by High Court over Mula-Mutha river pollution",
                "body": "Hearing a public interest litigation, the High Court warned civic officials in Pune over delays in constructing sewage treatment plants along the Mula-Mutha river."
            },
            {
                "source": "Pacific Rim Dispatch",
                "headline": "High Court orders strict monitoring of sewage treatment plants in Pune",
                "body": "Judicial bench issued orders requiring weekly water quality testing and compliance reports for all sewage treatment plants along Pune's Mula-Mutha river."
            },
            {
                "source": "Urban Transport Weekly",
                "headline": "Court mandates time-bound cleanup strategy for Mula-Mutha river in Pune",
                "body": "The High Court instructed environmental officers in Pune to shut down non-compliant industrial units discharging heavy metals into Mula-Mutha."
            }
        ]
    },

    # ----------------------------------------------------
    # Pair 9: Sports Achievements - FALSE MATCH PAIR
    # ----------------------------------------------------
    {
        "event_id": "EVT-SPT-001",
        "title": "India Wins T20 Cricket World Cup Final Victory Against South Africa",
        "category": "Sports",
        "false_match_pair": "EVT-SPT-002",
        "facts": {"sport": "Cricket", "tournament": "T20 World Cup", "opponent": "South Africa", "venue": "Barbados"},
        "items": [
            {
                "source": "Sports Horizon Media",
                "headline": "India crowned T20 World Cup champions after thrilling 7-run victory over South Africa",
                "body": "India clinched the T20 Cricket World Cup trophy in Barbados, holding off South Africa by 7 runs in a dramatic final over finish."
            },
            {
                "source": "National News Syndicate",
                "headline": "India wins T20 Cricket World Cup in Barbados final thriller",
                "body": "Sensational death bowling sealed a historic T20 World Cup triumph for India as they defeated South Africa in the final match."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "India lifts T20 World Cup trophy after beating South Africa in finals",
                "body": "Celebrations erupted across India following the national cricket team's T20 World Cup victory against South Africa in the Bridgetown final."
            },
            {
                "source": "Metro Press Network",
                "headline": "T20 World Cup victory: India edge past South Africa in Barbados final",
                "body": "India secured its second T20 Cricket World Cup title after overcoming South Africa by 7 runs in an intense final showdown."
            }
        ]
    },
    {
        "event_id": "EVT-SPT-002",
        "title": "India Men's Hockey Team Wins Asian Champions Trophy Gold in Inner Mongolia",
        "category": "Sports",
        "false_match_pair": "EVT-SPT-001",
        "facts": {"sport": "Field Hockey", "tournament": "Asian Champions Trophy", "opponent": "China", "venue": "Hulunbuir"},
        "items": [
            {
                "source": "Sports Horizon Media",
                "headline": "India Men's Hockey team defeats China 1-0 to win Asian Champions Trophy",
                "body": "The Indian men's field hockey team defended its Asian Champions Trophy title with a hard-fought 1-0 victory over host nation China in the final."
            },
            {
                "source": "National News Syndicate",
                "headline": "Indian hockey team claims Asian Champions Trophy gold medal",
                "body": "A late fourth-quarter field goal secured gold for the Indian hockey squad at the Asian Champions Trophy tournament held in Hulunbuir."
            },
            {
                "source": "Indo-Pacific Observer",
                "headline": "India retains Asian Hockey Champions Trophy title with victory over China",
                "body": "Indian men's hockey team recorded an unbeaten campaign to lift the Asian Champions Trophy trophy in Inner Mongolia."
            },
            {
                "source": "Metro Press Network",
                "headline": "Gold for India in Asian Hockey Champions Trophy final against China",
                "body": "India's field hockey squad concluded an impressive tournament performance, clinching the Asian Champions Trophy gold medal."
            }
        ]
    },

    # ----------------------------------------------------
    # Multi-source Non-paired Events
    # ----------------------------------------------------
    {
        "event_id": "EVT-ECO-001",
        "title": "India Q1 GDP Growth Accelerates to 7.8% Beating Consensus",
        "category": "Economy",
        "false_match_pair": None,
        "facts": {"indicator": "GDP Growth", "value": "7.8%", "period": "Q1"},
        "items": [
            {
                "source": "Financial Chronicle Direct",
                "headline": "India Q1 GDP growth surges to 7.8% on robust manufacturing and investment",
                "body": "Gross Domestic Product expanded by 7.8% in the first quarter of the fiscal year, exceeding economic forecasts driven by strong capital expenditure."
            },
            {
                "source": "Capital Markets Daily",
                "headline": "Q1 GDP growth hits 7.8 percent as industrial output gains momentum",
                "body": "Official government data revealed India's economy grew at a brisk 7.8% pace in Q1, reflecting resilient domestic consumer demand."
            },
            {
                "source": "State Commerce Gazette",
                "headline": "Economic growth speeds up: Q1 GDP prints at 7.8%",
                "body": "India maintained its position as the fastest-growing major economy after registering 7.8% GDP expansion for the April-June quarter."
            },
            {
                "source": "Deccan Business Wire",
                "headline": "India reports 7.8% economic expansion in first quarter earnings data",
                "body": "Manufacturing and construction activity powered India's quarterly GDP growth to 7.8%, beating analyst projections."
            }
        ]
    },

    # ----------------------------------------------------
    # Single-source Events (Isolated Wire Stories)
    # ----------------------------------------------------
    {
        "event_id": "EVT-SCI-001",
        "title": "ISRO Successfully Launches EOS-08 Earth Observation Satellite",
        "category": "Science",
        "false_match_pair": None,
        "facts": {"agency": "ISRO", "mission": "EOS-08 Satellite", "launcher": "SSLV-D3"},
        "items": [
            {
                "source": "Pacific Rim Dispatch",
                "headline": "ISRO successfully places EOS-08 Earth Observation Satellite into orbit via SSLV-D3",
                "body": "The Indian Space Research Organisation successfully deployed the EOS-08 satellite into intended orbit from Sriharikota using its SSLV-D3 rocket."
            }
        ]
    },
    {
        "event_id": "EVT-LOC-001",
        "title": "Greater Chennai Corporation Opens 50 Urban Micro-Parks with Rainwater Harvesting",
        "category": "Local",
        "false_match_pair": None,
        "facts": {"city": "Chennai", "project": "50 Sponge Micro-Parks", "focus": "Flood Mitigation"},
        "items": [
            {
                "source": "Metro Press Network",
                "headline": "Chennai inaugurates 50 eco-friendly urban micro-parks designed to absorb rainwater",
                "body": "The Greater Chennai Corporation opened 50 newly developed micro-parks equipped with underground rainwater harvesting recharge wells to prevent monsoon flooding."
            }
        ]
    },
    {
        "event_id": "EVT-ECO-002",
        "title": "Retail Inflation Drops to 3.54% Hitting 5-Year Record Low",
        "category": "Economy",
        "false_match_pair": None,
        "facts": {"indicator": "Consumer Price Index (CPI)", "value": "3.54%", "period": "July"},
        "items": [
            {
                "source": "Financial Chronicle Direct",
                "headline": "India July CPI retail inflation drops to 3.54%, lowest level in 5 years",
                "body": "Consumer price index inflation slowed sharply to 3.54% in July, falling below the central bank's medium-term target of 4.0%."
            }
        ]
    },
    {
        "event_id": "EVT-FIN-001",
        "title": "SEBI Issues Revised Regulatory Framework for Algorithmic Trading",
        "category": "Business",
        "false_match_pair": None,
        "facts": {"regulator": "SEBI", "subject": "Algorithmic Trading", "rule": "API Audit Requirements"},
        "items": [
            {
                "source": "Capital Markets Daily",
                "headline": "SEBI mandates enhanced API security and annual audits for algorithmic trading brokers",
                "body": "Markets regulator SEBI published updated guidelines requiring stockbrokers offering algo-trading facilities to undergo mandatory annual cybersecurity audits."
            }
        ]
    },
    {
        "event_id": "EVT-TOU-001",
        "title": "Kerala Announces ₹250 Crore Eco-Tourism Infrastructure Revamp Plan in Wayanad",
        "category": "Local",
        "false_match_pair": None,
        "facts": {"state": "Kerala", "district": "Wayanad", "funding": "₹250 Crore"},
        "items": [
            {
                "source": "National News Syndicate",
                "headline": "Kerala government sanctions ₹250 crore eco-tourism restoration package for Wayanad",
                "body": "Kerala state authorities approved a ₹250 crore infrastructure rejuvenation project aimed at promoting sustainable eco-tourism in Wayanad."
            }
        ]
    }
]


def generate_synthetic_dataset():
    random.seed(SEED)
    base_time = datetime.now(timezone.utc) - timedelta(days=2)

    raw_items = []
    ground_truth_events = []

    item_counter = 0

    for evt in EVENT_DEFINITIONS:
        event_id = evt["event_id"]
        event_raw_item_ids = []

        # Generate timestamps spread over the last 48 hours
        time_offset_hours = random.uniform(2, 44)
        event_time = base_time + timedelta(hours=time_offset_hours)

        for item_def in evt["items"]:
            item_counter += 1
            item_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{event_id}-item-{item_counter}"))

            # Slight variation in publication time between different sources reporting same event
            pub_offset_minutes = random.randint(-120, 120)
            source_published_at = event_time + timedelta(minutes=pub_offset_minutes)
            ingested_at = source_published_at + timedelta(minutes=random.randint(5, 30))

            raw_item = {
                "id": item_uuid,
                "source_name": item_def["source"],
                "headline": item_def["headline"],
                "body": item_def["body"],
                "category": evt["category"],
                "source_published_at": source_published_at.isoformat(),
                "ingested_at": ingested_at.isoformat(),
                "embedding_status": "PENDING"
            }
            raw_items.append(raw_item)
            event_raw_item_ids.append(item_uuid)

        ground_truth_events.append({
            "event_id": event_id,
            "title": evt["title"],
            "category": evt["category"],
            "false_match_pair_event_id": evt["false_match_pair"],
            "key_facts": evt["facts"],
            "raw_item_ids": event_raw_item_ids,
            "source_count": len(event_raw_item_ids)
        })

    # Save to data directory
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    items_file = data_dir / "synthetic_raw_items.json"
    ground_truth_file = data_dir / "ground_truth_events.json"

    with open(items_file, "w", encoding="utf-8") as f:
        json.dump(raw_items, f, indent=2)

    with open(ground_truth_file, "w", encoding="utf-8") as f:
        json.dump(ground_truth_events, f, indent=2)

    print(f"[SUCCESS] Dataset generated successfully!")
    print(f" -> Raw Items: {len(raw_items)} saved to {items_file}")
    print(f" -> Underlying Events: {len(ground_truth_events)} saved to {ground_truth_file}")


if __name__ == "__main__":
    generate_synthetic_dataset()
