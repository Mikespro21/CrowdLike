from core import add_page


def register_pages():
    """Register the full Qubic UI pages (restored)."""

    # Hub (quick links)
    add_page("hub", "Hub", "Onboarding & Home", "hub")

    # 1-10 Entry & Auth
    add_page("landing_public", "Landing (Public)", "Entry & Auth", "landing")
    add_page("login", "Login", "Entry & Auth", "login")
    add_page("register", "Register / Sign Up", "Entry & Auth", "register")
    add_page("verify_email", "Email Verification", "Entry & Auth", "simple_info")
    add_page("forgot_password", "Forgot Password", "Entry & Auth", "forgot_password")
    add_page("reset_password", "Reset Password", "Entry & Auth", "reset_password")
    add_page("logged_out_upsell", "Logged-Out Upsell", "Entry & Auth", "simple_info")
    add_page("terms", "Terms of Service", "Entry & Auth", "legal")
    add_page("privacy", "Privacy Policy", "Entry & Auth", "legal")
    add_page("cookie_consent", "Cookie / Data Consent", "Entry & Auth", "simple_info")
    add_page("invest_case", "Why You Should Invest", "Onboarding & Home", "invest_case")
    add_page("ai_assistant", "AI Coach / Helper", "Onboarding & Home", "ai_assistant")

    # 11-20 Onboarding & Home
    add_page("onboard_subjects", "Onboarding: Choose Subjects", "Onboarding & Home", "onboard_subjects")
    add_page("onboard_goals", "Onboarding: Choose Study Goals", "Onboarding & Home", "onboard_goals")
    add_page("onboard_placement", "Onboarding: Quick Placement Test", "Onboarding & Home", "test_detail")
    add_page("welcome_tour", "Welcome Tour", "Onboarding & Home", "welcome_tour")
    add_page("home_dashboard", "Home Dashboard", "Onboarding & Home", "home_dashboard")
    add_page("subject_hub", "Subject Selection Hub", "Onboarding & Home", "subject_hub")
    add_page("daily_tasks", "Daily Tasks / Missions", "Onboarding & Home", "daily_tasks")
    add_page("streak_overview", "Streak Overview", "Onboarding & Home", "streak_overview")
    add_page("notifications_center", "Notifications Center", "Onboarding & Home", "notifications_center")
    add_page("announcements", "Announcements / Changelog", "Onboarding & Home", "simple_list")

    # 21-40 Account & Profile
    add_page("account_overview", "My Account Overview", "Account & Profile", "account_overview")
    add_page("edit_account", "Edit Account Info", "Account & Profile", "settings_form")
    add_page("change_password", "Change Password", "Account & Profile", "change_password")
    add_page("two_factor", "Two-Factor Auth Setup", "Account & Profile", "settings_form")
    add_page("linked_devices", "Linked Devices / Active Sessions", "Account & Profile", "simple_table")
    add_page("delete_account", "Delete / Deactivate Account", "Account & Profile", "danger_confirm")
    add_page("public_profile", "Public Profile View", "Account & Profile", "profile_public")
    add_page("profile_customization", "Profile Customization Hub", "Account & Profile", "profile_customization")
    add_page("profile_icon", "Profile Icon Selector", "Account & Profile", "simple_list")
    add_page("profile_banner", "Profile Banner Selector", "Account & Profile", "simple_list")
    add_page("profile_bio", "Profile Bio Editor", "Account & Profile", "settings_form")
    add_page("profile_badges", "Profile Badges Management", "Account & Profile", "simple_table")
    add_page("profile_privacy", "Profile Privacy Settings", "Account & Profile", "settings_form")
    add_page("view_other_profile", "View Another User’s Profile", "Account & Profile", "profile_public")
    add_page("block_user", "Block / Unblock User", "Account & Profile", "settings_form")
    add_page("friends_list", "Friends List", "Account & Profile", "simple_table")
    add_page("friend_requests", "Friend Requests", "Account & Profile", "simple_table")
    add_page("profile_visitors", "Recent Visitors to Profile", "Account & Profile", "simple_table")
    add_page("profile_activity_log", "Profile Activity Log", "Account & Profile", "simple_table")
    add_page("profile_theme_presets", "Profile Theme Presets", "Account & Profile", "simple_list")

    # 41-60 XP, Levels, Stats
    add_page("xp_overview", "XP Overview Dashboard", "XP & Stats", "xp_overview")
    add_page("level_up_detail", "Level-Up Detail", "XP & Stats", "simple_info")
    add_page("xp_history", "XP History Timeline", "XP & Stats", "simple_table")
    add_page("xp_subject_breakdown", "Subject-Specific XP Breakdown", "XP & Stats", "simple_table")
    add_page("xp_weekly_graph", "Weekly XP Graph", "XP & Stats", "simple_graph")
    add_page("xp_monthly_graph", "Monthly XP Graph", "XP & Stats", "simple_graph")
    add_page("lifetime_stats", "Lifetime Stats Overview", "XP & Stats", "simple_table")
    add_page("achievements_list", "Achievements List", "XP & Stats", "simple_table")
    add_page("achievement_detail", "Achievement Detail", "XP & Stats", "simple_info")
    add_page("milestones_roadmap", "Milestones Roadmap", "XP & Stats", "simple_list")
    add_page("streak_detail", "Streak Detail", "XP & Stats", "streak_overview")
    add_page("streak_freeze", "Streak Freeze / Recovery", "XP & Stats", "settings_form")
    add_page("goals_dashboard", "Goals Dashboard", "XP & Stats", "simple_table")
    add_page("goal_edit", "Create / Edit Custom Goal", "XP & Stats", "settings_form")
    add_page("leaderboards", "Leaderboards Overview", "XP & Stats", "simple_list")
    add_page("leaderboard_global", "Global Leaderboard", "XP & Stats", "simple_table")
    add_page("leaderboard_friends", "Friends-Only Leaderboard", "XP & Stats", "simple_table")
    add_page("leaderboard_subject", "Subject-Based Leaderboard", "XP & Stats", "simple_table")
    add_page("leaderboard_class", "School / Class Leaderboard", "XP & Stats", "simple_table")
    add_page("personal_bests", "Personal Bests Summary", "XP & Stats", "simple_table")
    add_page("metrics_lab", "Behavior Metrics Lab", "XP & Stats", "metrics_lab")

    # Behavior Scenarios (project-aligned)
    add_page("scenario_library", "Behavior Scenario Library", "Behavior Scenarios", "test_library")
    add_page("scenario_calibration", "Scenario: Momentum Calibration", "Behavior Scenarios", "test_detail")
    add_page("scenario_volatility", "Scenario: Volatility Stress Run", "Behavior Scenarios", "test_detail")
    add_page("scenario_governance", "Scenario: Governance Vote Cycle", "Behavior Scenarios", "test_detail")
    add_page("scenario_airdrop", "Scenario: Airdrop Farming Sprint", "Behavior Scenarios", "test_detail")
    add_page("scenario_social", "Scenario: Social Hype Spike", "Behavior Scenarios", "test_detail")
    add_page("scenario_execution", "Scenario: Execution Discipline Drill", "Behavior Scenarios", "test_detail")
    add_page("scenario_run", "Scenario Run (Simulated)", "Behavior Scenarios", "test_taking")
    add_page("scenario_results_summary", "Scenario Results Summary", "Behavior Scenarios", "test_results")
    add_page("scenario_feedback", "Scenario Feedback / Reflection", "Behavior Scenarios", "settings_form")
    add_page("scenario_share", "Share Scenario Outcome", "Behavior Scenarios", "simple_info")

    # 61-80 Test Library — General
    add_page("tests_all", "All Tests Library", "Test Library", "test_library")
    add_page("tests_math", "Test Category: Math", "Test Library", "test_library")
    add_page("tests_science", "Test Category: Science", "Test Library", "test_library")
    add_page("tests_programming", "Test Category: Programming", "Test Library", "test_library")
    add_page("tests_mixed", "Test Category: Mixed Random", "Test Library", "test_library")
    add_page("tests_search", "Test Search Results", "Test Library", "test_library")
    add_page("tests_filter_difficulty", "Filter Tests by Difficulty", "Test Library", "test_library")
    add_page("tests_filter_length", "Filter Tests by Time Length", "Test Library", "test_library")
    add_page("tests_saved", "Saved / Favorited Tests", "Test Library", "test_library")
    add_page("tests_recent", "Recently Attempted Tests", "Test Library", "test_library")
    add_page("tests_recommended", "Recommended Tests For You", "Test Library", "test_library")
    add_page("tests_new", "New / Recently Added", "Test Library", "test_library")
    add_page("tests_popular", "Popular This Week", "Test Library", "test_library")
    add_page("test_detail_generic", "Test Detail (Generic)", "Test Library", "test_detail")
    add_page("test_taking", "Test Taking (Generic)", "Test Library", "test_taking")
    add_page("test_pause_resume", "Test Pause / Resume", "Test Library", "simple_info")
    add_page("test_results_summary", "Test Results Summary", "Test Library", "test_results")
    add_page("test_review_questions", "Question-by-Question Review", "Test Library", "simple_table")
    add_page("test_feedback_rating", "Test Feedback / Rating", "Test Library", "settings_form")
    add_page("test_share_results", "Share Test Results", "Test Library", "simple_info")

    # 81-105 Algebra 1 Tests
    algebra_tests = [
        "Intro to Variables", "Evaluating Expressions", "One-Step Equations", "Two-Step Equations",
        "Multi-Step Equations", "Equations with Fractions", "Inequalities Basics", "Compound Inequalities",
        "Graphing on the Coordinate Plane", "Slope and Rate of Change", "Slope-Intercept Form",
        "Point-Slope Form", "Standard Form Linear Equations", "Systems (Substitution)", "Systems (Elimination)",
        "Systems Word Problems", "Functions Basics", "Function Notation", "Linear vs Nonlinear Functions",
        "Exponents and Powers", "Scientific Notation", "Polynomials Basics", "Factoring Quadratics",
        "Quadratic Formula",
    ]
    add_page("algebra_hub", "Algebra 1 Subject Hub", "Algebra 1", "simple_list")
    for idx, name in enumerate(algebra_tests):
        slug = f"alg_test_{idx+1}"
        add_page(slug, f"Algebra Test: {name}", "Algebra 1", "test_detail", meta={"test_name": name, "subject": "Algebra 1"})

    # 106-130 Physics & Science Tests
    physics_tests = [
        "Units and Measurements", "Motion in One Dimension", "Speed vs Velocity", "Acceleration Basics",
        "Newton’s Laws", "Forces and Free-Body Diagrams", "Work and Energy", "Power",
        "Momentum and Collisions", "Simple Machines", "Waves Basics", "Sound Waves",
        "Light and Optics", "Electricity Basics", "Circuits", "Magnetism", "Thermodynamics Basics",
        "Density and Buoyancy", "Pressure and Fluids", "Atoms and Elements", "Periodic Table",
        "Chemical Reactions", "Earth and Space Science", "Scientific Method",
    ]
    add_page("physics_hub", "Physics Subject Hub", "Physics & Science", "simple_list")
    for idx, name in enumerate(physics_tests):
        slug = f"phys_test_{idx+1}"
        add_page(slug, f"Science Test: {name}", "Physics & Science", "test_detail", meta={"test_name": name, "subject": "Physics & Science"})

    # 131-150 Practice & Training Modes
    add_page("practice_hub", "Practice Hub", "Practice & Training", "simple_list")
    add_page("practice_quick5", "Quick 5-Question Drill", "Practice & Training", "test_taking")
    add_page("practice_speedrun", "Timed Speed-Run Mode", "Practice & Training", "test_taking")
    add_page("practice_endless", "Endless Practice Mode", "Practice & Training", "test_taking")
    add_page("practice_errors", "Error Review Mode", "Practice & Training", "simple_table")
    add_page("practice_bookmarks", "Bookmark Question Review", "Practice & Training", "simple_table")
    add_page("flashcards_home", "Flashcards Mode Home", "Practice & Training", "simple_list")
    add_page("flashcards_session", "Flashcards Session", "simple", "simple_info")
    add_page("spaced_repetition", "Spaced Repetition Planner", "Practice & Training", "settings_form")
    add_page("custom_practice_builder", "Custom Practice Set Builder", "Practice & Training", "settings_form")
    add_page("daily_warmup", "Daily Warm-Up Quiz", "Practice & Training", "test_taking")
    add_page("weekly_challenge", "Weekly Challenge Quiz", "Practice & Training", "test_taking")
    add_page("boss_battle", "Boss Battle Test (Hard Mixed)", "Practice & Training", "test_taking")
    add_page("practice_by_difficulty", "Practice By Difficulty", "Practice & Training", "simple_list")
    add_page("practice_by_type", "Practice By Question Type", "Practice & Training", "simple_list")
    add_page("practice_history", "Practice History List", "Practice & Training", "simple_table")
    add_page("practice_session_detail", "Practice Session Detail", "Practice & Training", "test_results")
    add_page("practice_streak_detail", "Practice Streak Detail", "Practice & Training", "streak_overview")
    add_page("practice_suggested_after_test", "Suggested Practice After Test", "Practice & Training", "simple_list")
    add_page("practice_vs_past_self", "Practice Versus Past Self", "Practice & Training", "simple_table")

    # 151-170 Shop & Currency
    add_page("shop_home", "Shop Home", "Shop & Currency", "shop_page")
    add_page("currency_overview", "Currency Overview", "Shop & Currency", "simple_table")
    add_page("shop_themes", "Themes Shop", "Shop & Currency", "shop_page")
    add_page("shop_icons", "Icons / Avatars Shop", "Shop & Currency", "shop_page")
    add_page("shop_banners", "Banners Shop", "Shop & Currency", "shop_page")
    add_page("shop_title_badges", "Title Badges Shop", "Shop & Currency", "shop_page")
    add_page("shop_streak_freezes", "Streak Freezes Shop", "Shop & Currency", "shop_page")
    add_page("shop_xp_boosts", "XP Boosts Shop", "Shop & Currency", "shop_page")
    add_page("shop_practice_packs", "Extra Practice Packs Shop", "Shop & Currency", "shop_page")
    add_page("shop_custom_slots", "Custom Test Slots Shop", "Shop & Currency", "shop_page")
    add_page("shop_limited_offers", "Limited-Time Offers Shop", "Shop & Currency", "shop_page")
    add_page("shop_recommended", "Recommended Items For You", "Shop & Currency", "shop_page")
    add_page("token_trading", "Token Trading Desk", "Shop & Currency", "token_trading")
    add_page("wallet_dashboard", "Wallet & Market Overview", "Shop & Currency", "wallet_dashboard")
    add_page("market_pulse", "Market Pulse", "Shop & Currency", "market_pulse")
    add_page("market_live", "Live Market (Real)", "Shop & Currency", "market_live")
    add_page("shop_transactions", "Transaction History", "Shop & Currency", "simple_table")
    add_page("shop_purchase_confirm", "Purchase Confirmation", "Shop & Currency", "simple_info")
    add_page("shop_gift_items", "Gift Items To Friend", "Shop & Currency", "settings_form")
    add_page("shop_redeem_code", "Redeem Promo Code", "Shop & Currency", "settings_form")
    add_page("shop_earn_currency", "Earn Currency Tasks List", "Shop & Currency", "simple_list")
    add_page("shop_daily_reward", "Daily Free Reward Claim", "Shop & Currency", "simple_info")
    add_page("shop_refund_form", "Refund / Purchase Problem", "Shop & Currency", "settings_form")
    add_page("shop_parental_controls", "Parental Purchase Controls", "Shop & Currency", "settings_form")

    # 171-185 Social & Competition
    add_page("social_hub", "Social Hub", "Social & Competition", "simple_list")
    add_page("friends_activity", "Friends Activity Feed", "Social & Competition", "simple_list")
    add_page("global_activity", "Global Activity Feed", "Social & Competition", "simple_list")
    add_page("dm_inbox", "Direct Messages Inbox", "Social & Competition", "simple_table")
    add_page("dm_conversation", "Direct Message Conversation", "Social & Competition", "simple_info")
    add_page("create_study_group", "Create Study Group", "Social & Competition", "settings_form")
    add_page("study_group_lobby", "Study Group Lobby", "Social & Competition", "simple_info")
    add_page("study_group_chat", "Study Group Chat", "Social & Competition", "simple_list")
    add_page("group_test_lobby", "Group Test Session Lobby", "Social & Competition", "test_detail")
    add_page("group_test_results", "Group Test Results Comparison", "Social & Competition", "test_results")
    add_page("community_challenges", "Community Challenges List", "Social & Competition", "simple_list")
    add_page("join_challenge", "Join Community Challenge", "Social & Competition", "settings_form")
    add_page("past_challenge_results", "Past Challenge Results", "Social & Competition", "simple_table")
    add_page("report_user_content", "Report User / Content", "Social & Competition", "settings_form")
    add_page("community_guidelines", "Community Guidelines", "Social & Competition", "legal")

    # 186-195 Settings & System
    add_page("settings_home", "Settings Home", "Settings & System", "settings_list")
    add_page("settings_display", "Display Settings", "Settings & System", "settings_form")
    add_page("settings_notifications", "Notification Settings", "Settings & System", "settings_form")
    add_page("settings_sound", "Sound / Haptics Settings", "Settings & System", "settings_form")
    add_page("settings_language", "Language Settings", "Settings & System", "settings_form")
    add_page("settings_data_privacy", "Data and Privacy Settings", "Settings & System", "settings_form")
    add_page("settings_security", "Security Settings", "Settings & System", "settings_form")
    add_page("settings_storage", "Storage / Cache Management", "Settings & System", "simple_table")
    add_page("settings_shortcuts", "Keyboard Shortcuts Help", "Settings & System", "simple_list")
    add_page("settings_integrations", "Connected Apps / Integrations", "Settings & System", "simple_table")

    # 196-200 Admin & Dev
    add_page("admin_dashboard", "Admin Dashboard", "Admin & Dev", "simple_table")
    add_page("admin_question_bank", "Question Bank Manager", "Admin & Dev", "simple_table")
    add_page("admin_test_editor", "Test Creation and Editing", "Admin & Dev", "settings_form")
    add_page("admin_reports_queue", "User Reports Moderation Queue", "Admin & Dev", "simple_table")
    add_page("admin_system_status", "System Status / Logs", "Admin & Dev", "simple_table")

    # Qubic-specific
    add_page("qubic_network", "Qubic public testnet", "XP & Stats", "qubic_network")
