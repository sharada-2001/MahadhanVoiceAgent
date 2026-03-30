"""
Onboarding Recovery Tools - Tools for diagnosing and resolving farmer app onboarding drop-offs.
"""

from tools.tool_registry import registry


# ============================================================================
# DROP-OFF DIAGNOSIS TOOLS
# ============================================================================

@registry.register(
    name="diagnose_dropoff",
    description="Diagnose why the farmer stopped during app onboarding. Call this when farmer mentions they couldn't complete registration, app registration, sign up, or had problems with OTP, profile, photo, or crop details.",
    parameters={
        "type": "object",
        "properties": {
            "stage": {
                "type": "string",
                "enum": ["otp_issue", "profile_not_started", "photo_not_uploaded", "crop_details_missing", "partial_crop_details", "unknown"],
                "description": "The stage where farmer stopped: otp_issue (OTP not entered), profile_not_started (after OTP but didn't start profile), photo_not_uploaded (profile started but no photo), crop_details_missing (profile done but no crop info), partial_crop_details (started crops but didn't finish), unknown (not clear)"
            },
            "specific_problem": {
                "type": "string",
                "description": "Specific problem mentioned by farmer like 'OTP nahi aaya', 'photo nahi lag raha', 'time nahi tha'"
            }
        },
        "required": ["stage"]
    }
)
def diagnose_dropoff(stage: str, specific_problem: str = None) -> dict:
    """Diagnose drop-off and provide stage-specific guidance."""
    
    diagnoses = {
        "otp_issue": {
            "stage": "B.1 - OTP Not Entered",
            "common_causes": [
                "OTP message delayed or not received",
                "Network connectivity issues", 
                "App was closed before entering OTP",
                "Confusion about where to enter OTP"
            ],
            "guidance": {
                "hindi": [
                    "Pehle apna network check karein - WiFi ya mobile data on hai?",
                    "SMS inbox mein OTP dekhein, kabhi kabhi 1-2 minute lag jaata hai",
                    "Agar OTP nahi aaya, 'Resend OTP' button dabayein",
                    "OTP 6 digit ka number hota hai, use app mein enter karein"
                ],
                "steps": [
                    "Check network connectivity",
                    "Wait 1-2 minutes for SMS",
                    "Use Resend OTP if not received",
                    "Enter 6-digit code in app"
                ]
            },
            "encouragement": "Yeh bahut aasan hai, bas 1 minute lagega!"
        },
        
        "profile_not_started": {
            "stage": "B.2 - Profiling Not Started",
            "common_causes": [
                "User felt tired after OTP verification",
                "Unclear why profile details are needed",
                "Perceived as time-consuming"
            ],
            "guidance": {
                "hindi": [
                    "Profile bharne mein sirf 2-3 minute lagte hain",
                    "Aapka profile hone ke baad aapko personalized farming tips milenge",
                    "Mahadhan ki special offers bhi profile complete karne par milti hain",
                    "Abhi complete kar lein, baad mein yaad nahi rahega"
                ],
                "steps": [
                    "Open app and go to Profile section",
                    "Fill basic details - Name, Village, District",
                    "Takes only 2-3 minutes"
                ]
            },
            "encouragement": "Sirf 2 minute mein complete ho jayega, shuru karein?"
        },
        
        "photo_not_uploaded": {
            "stage": "B.3 - Profile Photo Not Uploaded", 
            "common_causes": [
                "Camera permission not given",
                "Poor lighting conditions",
                "User uncomfortable with selfie",
                "Device camera issues"
            ],
            "guidance": {
                "hindi": [
                    "Photo se aapki pehchaan hoti hai aur account safe rehta hai",
                    "Camera permission dene ke liye 'Allow' button dabayein",
                    "Achhi roshni mein photo lein, din ki roshni best hai",
                    "Simple photo chalega, studio jaisi zaroorat nahi",
                    "Agar camera nahi chal raha, gallery se bhi photo le sakte hain"
                ],
                "steps": [
                    "Allow camera permission when asked",
                    "Take photo in good daylight",
                    "Simple clear face photo is enough",
                    "Can also upload from gallery"
                ]
            },
            "encouragement": "Bas ek photo, aur profile complete!"
        },
        
        "crop_details_missing": {
            "stage": "B.4 - Crop Details Not Entered (CRITICAL)",
            "common_causes": [
                "Crop section seems complex",
                "User interrupted by external factors",
                "Unclear immediate benefit",
                "User fatigue"
            ],
            "guidance": {
                "hindi": [
                    "IMPORTANT: Profile tab tak save nahi hota jab tak crop details na ho",
                    "Crop details dene se aapko sahi samay par sahi salah milegi",
                    "Bas 3 cheezein batani hain: Fasal naam, area, aur buwai date",
                    "Agar exact area nahi pata, approximate bata dein, baad mein change kar sakte hain",
                    "Yeh karne se Mahadhan ka free expert advice milega"
                ],
                "steps": [
                    "Select your main crop from list",
                    "Enter approximate land area in acres",
                    "Select sowing date (approximate is fine)",
                    "Press Save - Done!"
                ]
            },
            "encouragement": "Sirf 3 cheezein batayein aur expert advice free mein paayein!"
        },
        
        "partial_crop_details": {
            "stage": "B.5 - Partial Crop Details Entered",
            "common_causes": [
                "Uncertainty about exact crop data",
                "Time constraints interrupted user",
                "Confusion about farming terminology"
            ],
            "guidance": {
                "hindi": [
                    "Jo bhi pata hai wo bharna kaafi hai, exact data zaruri nahi",
                    "Galat answer dene ka darr mat rakhiye, baad mein edit kar sakte hain",
                    "Agar area andaza se bhi bhar dein toh chalega",
                    "Buwai date yaad nahi hai? Mahina select kar lein, date baad mein change karein",
                    "Main WhatsApp par step-by-step guide bhej sakta hoon"
                ],
                "steps": [
                    "Open app - your partial data is saved",
                    "Fill remaining fields with best estimate",
                    "You can always edit later",
                    "Press Submit to complete"
                ]
            },
            "encouragement": "Aapne shuru kar diya hai, bas thoda sa baaki hai!"
        },
        
        "unknown": {
            "stage": "Unknown - Need More Information",
            "common_causes": ["Unable to determine specific issue"],
            "guidance": {
                "hindi": [
                    "Kripya bataiye app mein kahan tak pahunche the?",
                    "Kya OTP enter hua tha?",
                    "Kya profile photo daali thi?",
                    "Kya fasal ki jaankari daali thi?"
                ],
                "questions_to_ask": [
                    "Did you enter OTP successfully?",
                    "Did you add your profile photo?", 
                    "Did you enter crop information?"
                ]
            },
            "encouragement": "Main aapki madad karunga, bas bataiye kahan ruke the"
        }
    }
    
    diagnosis = diagnoses.get(stage, diagnoses["unknown"])
    
    if specific_problem:
        diagnosis["farmer_mentioned"] = specific_problem
    
    return {
        "status": "diagnosed",
        "diagnosis": diagnosis
    }


@registry.register(
    name="get_otp_help",
    description="Provide specific help for OTP-related issues. Call when farmer says OTP didn't come, OTP expired, wrong OTP, network problem during OTP.",
    parameters={
        "type": "object",
        "properties": {
            "problem_type": {
                "type": "string",
                "enum": ["not_received", "expired", "wrong_number", "network_issue", "where_to_enter"],
                "description": "Type of OTP problem: not_received, expired (time out), wrong_number (sent to different number), network_issue, where_to_enter (doesn't know where to put OTP)"
            }
        },
        "required": ["problem_type"]
    }
)
def get_otp_help(problem_type: str) -> dict:
    """Provide OTP-specific troubleshooting."""
    
    solutions = {
        "not_received": {
            "problem": "OTP SMS not received",
            "hindi_solution": "OTP nahi aaya? Yeh karein: 1) 2 minute wait karein, 2) Apna phone number check karein - sahi daala tha?, 3) 'Resend OTP' button dabayein, 4) DND service on hai toh usse off karein, 5) Phone restart karke try karein",
            "immediate_action": "Resend OTP button dabayein"
        },
        "expired": {
            "problem": "OTP expired / timed out",
            "hindi_solution": "OTP expire ho gaya? Koi baat nahi! 'Resend OTP' dabayein aur naya OTP aayega. Naya OTP aate hi turant enter kar dein, sirf 5 minute valid hota hai.",
            "immediate_action": "Resend OTP for new code"
        },
        "wrong_number": {
            "problem": "OTP sent to wrong number",
            "hindi_solution": "Galat number par gaya? Pehle wale screen par jayein aur sahi mobile number enter karein. Phir naya OTP aayega sahi number par.",
            "immediate_action": "Go back and correct mobile number"
        },
        "network_issue": {
            "problem": "Network connectivity issue",
            "hindi_solution": "Network problem? Yeh try karein: 1) WiFi se mobile data ya mobile data se WiFi switch karein, 2) Airplane mode on-off karein, 3) Bahar khule mein jaakar try karein, 4) 5 minute baad dobara try karein",
            "immediate_action": "Switch network or try in open area"  
        },
        "where_to_enter": {
            "problem": "Don't know where to enter OTP",
            "hindi_solution": "OTP kahan daalna hai? App mein ek box dikhega jisme 6 number daalne hain. SMS mein jo 6 digit number aaya hai, wo wahan type karein aur 'Verify' ya 'Submit' button dabayein.",
            "immediate_action": "Enter 6 digits in the OTP box on screen"
        }
    }
    
    return {
        "status": "help_provided",
        "solution": solutions.get(problem_type, solutions["not_received"])
    }


@registry.register(
    name="get_profile_help",
    description="Help farmer complete their profile. Call when farmer asks about profile, photo upload, or filling personal details.",
    parameters={
        "type": "object",
        "properties": {
            "section": {
                "type": "string", 
                "enum": ["personal_details", "photo_upload", "address", "general"],
                "description": "Which profile section needs help"
            }
        },
        "required": ["section"]
    }
)
def get_profile_help(section: str) -> dict:
    """Provide profile completion guidance."""
    
    help_content = {
        "personal_details": {
            "fields": ["Naam", "Umar", "Gender"],
            "hindi_guide": "Apna poora naam type karein jaise Aadhaar mein hai. Umar mein apni age number mein daalein. Gender mein Purush ya Mahila select karein.",
            "time_estimate": "1 minute"
        },
        "photo_upload": {
            "fields": ["Profile Photo"],
            "hindi_guide": "Camera icon par click karein. 'Allow' button dabayein agar permission maange. Seedha camera ki taraf dekhein aur photo lein. Agar camera nahi chal raha toh 'Gallery' se pehle ki photo bhi daal sakte hain.",
            "time_estimate": "30 seconds",
            "tips": "Din ki roshni mein photo lein, andhere mein mat lein"
        },
        "address": {
            "fields": ["Village", "Taluka", "District", "State"],
            "hindi_guide": "Apna gaon ka naam type karein. List mein se apna taluka select karein. District automatically aa jayega. State bhi select karein.",
            "time_estimate": "1 minute"
        },
        "general": {
            "hindi_guide": "Profile bharna bahut aasan hai. Bas apna naam, photo, aur gaon ki jaankari daalni hai. Total 2-3 minute lagte hain. Profile complete karne par Mahadhan ki special offers milti hain!",
            "time_estimate": "2-3 minutes total"
        }
    }
    
    return {
        "status": "guide_provided",
        "help": help_content.get(section, help_content["general"])
    }


@registry.register(
    name="get_crop_entry_help",
    description="Help farmer enter crop details in the app. Call when farmer asks about adding crops, fasal details, land area, or sowing date.",
    parameters={
        "type": "object",
        "properties": {
            "confusion_area": {
                "type": "string",
                "enum": ["which_crop", "land_area", "sowing_date", "multiple_crops", "general"],
                "description": "What the farmer is confused about"
            }
        },
        "required": ["confusion_area"]
    }
)
def get_crop_entry_help(confusion_area: str) -> dict:
    """Help with crop detail entry."""
    
    help_content = {
        "which_crop": {
            "hindi_guide": "Jo fasal abhi khadi hai ya jo aap bona chahte hain wo select karein. List mein se apni fasal dhundhein. Agar exact naam nahi dikh raha toh nearest option select karein.",
            "examples": "Gehun, Dhan/Chawal, Kapas, Soybean, Ganna, Chana"
        },
        "land_area": {
            "hindi_guide": "Apni zameen ka area acre ya hectare mein daalein. Exact nahi pata toh andaza se daal dein - 1 acre mein lagbhag ek football ground aata hai. Baad mein change kar sakte hain.",
            "conversion": "1 Hectare = 2.5 Acre, 1 Acre = 4 Bigha (approximate)"
        },
        "sowing_date": {
            "hindi_guide": "Jab boya tha ya bona hai wo date select karein. Exact date yaad nahi hai toh koi baat nahi - mahina select kar lein, date baad mein edit kar sakte hain.",
            "tip": "Approximate date dalna kaafi hai"
        },
        "multiple_crops": {
            "hindi_guide": "Pehle ek fasal add karein aur save karein. Phir 'Add Crop' button se doosri fasal add kar sakte hain. Jitni fasal hain utni baar add karein.",
            "tip": "Ek ek karke add karein"
        },
        "general": {
            "hindi_guide": "Crop details bharna bahut simple hai. Bas 3 cheezein: 1) Fasal ka naam select karein, 2) Kitne acre/hectare mein hai, 3) Kab boya ya boenge. Exact info zaruri nahi, andaza bhi chalega!",
            "time_estimate": "1-2 minutes per crop",
            "benefit": "Crop details se aapko sahi samay par spray, paani, aur khad ki yaad dilaayi jayegi"
        }
    }
    
    return {
        "status": "guide_provided", 
        "help": help_content.get(confusion_area, help_content["general"])
    }


@registry.register(
    name="send_help_via_whatsapp",
    description="Offer to send step-by-step help via WhatsApp or SMS. Call when farmer seems to need visual guidance or wants help later.",
    parameters={
        "type": "object",
        "properties": {
            "help_topic": {
                "type": "string",
                "enum": ["otp_steps", "profile_steps", "crop_entry_steps", "complete_guide"],
                "description": "What help content to send"
            },
            "farmer_phone": {
                "type": "string",
                "description": "Farmer's phone number if provided"
            }
        },
        "required": ["help_topic"]
    }
)
def send_help_via_whatsapp(help_topic: str, farmer_phone: str = None) -> dict:
    """Queue help content to be sent via WhatsApp/SMS."""
    
    # In production, this would integrate with WhatsApp Business API or SMS gateway
    help_content = {
        "otp_steps": "OTP Help Guide - 4 simple steps with images",
        "profile_steps": "Profile Completion Guide - step by step screenshots", 
        "crop_entry_steps": "Crop Entry Guide - visual walkthrough",
        "complete_guide": "Complete Mahadhan App Guide - full registration process"
    }
    
    return {
        "status": "queued",
        "message_hindi": f"Main aapko WhatsApp par {help_content[help_topic]} bhej dunga. Kripya thodi der mein check karein.",
        "help_topic": help_topic,
        "phone": farmer_phone or "registered_number"
    }


@registry.register(
    name="end_conversation",
    description="End the conversation gracefully. Call when: farmer says goodbye (bas, nahi chahiye, ho gaya, shukriya, alvida), farmer has completed all tasks, or farmer wants to end the call.",
    parameters={
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "enum": ["farmer_goodbye", "task_completed", "will_do_later", "transferred_to_human"],
                "description": "Why the conversation is ending"
            },
            "tasks_completed": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tasks that were completed during the call"
            },
            "pending_tasks": {
                "type": "array", 
                "items": {"type": "string"},
                "description": "List of tasks farmer said they will do later"
            }
        },
        "required": ["reason"]
    }
)
def end_conversation(reason: str, tasks_completed: list = None, pending_tasks: list = None) -> dict:
    """End the conversation and log the outcome."""
    
    closing_messages = {
        "farmer_goodbye": {
            "hindi": "Dhanyavaad! Mahadhan Kisan Saathi se baat karke accha laga. Kheti mein koi bhi madad chahiye toh zarur call karein. Jai Jawan, Jai Kisan!",
            "marathi": "Dhanyavaad! Mahadhan Kisan Saathi shi bolun bara vatla. Shetit kaahi madad pahije tar nakki call kara. Jai Jawan, Jai Kisan!"
        },
        "task_completed": {
            "hindi": "Bahut badiya! Registration complete ho gaya. Ab aap Mahadhan app ka poora faayda utha sakte hain. Koi sawaal ho toh zarur call karein. Dhanyavaad!",
            "marathi": "Khup chhan! Registration zala. Ata tumhi Mahadhan app cha purn faayda gheu shakta. Kaahi prashna asel tar nakki call kara. Dhanyavaad!"
        },
        "will_do_later": {
            "hindi": "Theek hai, jab time mile tab kar lena. Main WhatsApp par steps bhej dunga. Koi problem ho toh wapas call kar lena. Dhanyavaad!",
            "marathi": "Theek ahe, jeva vel milel teva kara. Mi WhatsApp var steps pathvin. Kaahi problem asel tar parat call kara. Dhanyavaad!"
        },
        "transferred_to_human": {
            "hindi": "Main aapko humare team se connect kar raha hoon. Wo aapki madad karenge. Thoda wait karein.",
            "marathi": "Mi tumhala aamchya team shi connect karto. Te tumchi madad kartil. Thoda thamba."
        }
    }
    
    return {
        "status": "conversation_ended",
        "reason": reason,
        "closing_message": closing_messages.get(reason, closing_messages["farmer_goodbye"]),
        "tasks_completed": tasks_completed or [],
        "pending_tasks": pending_tasks or [],
        "should_disconnect": reason != "transferred_to_human"
    }
