# Analyse van Recover-ETAP Repository

## 1. State Structuur

De applicatie maakt gebruik van Reflex's state management systeem. De structuur is hiërarchisch en modulair opgezet.

### Base State (`app/states/base_state.py`)
Dit is de fundering voor de meeste andere states.
-   **Functionaliteit:** Beheert de gebruikerssessie (`user`), de rol van de gebruiker (`user_role`), en basis authenticatie checks (`is_authenticated`, `is_admin`).
-   **Inheritance:** Erft van `RateLimitState`.

### Auth State (`app/states/auth_state.py`)
-   **Inheritance:** Erft van `BaseState`.
-   **Functionaliteit:** Behandelt alle authenticatie-gerelateerde acties zoals inloggen, registreren, wachtwoord resetten en sessiebeheer via Supabase. Bevat ook logica voor een demo-modus wanneer Supabase niet is geconfigureerd.

### Specifieke States
Er zijn diverse gespecialiseerde states voor verschillende onderdelen van de applicatie:
-   **`CMSContentState`:** Beheert het ophalen en cachen van content uit het CMS.
-   **`ResultsState`:** Beheert de opgeslagen berekeningen van de gebruiker, inclusief filteren en anonimiseren.
-   **`KnowledgeBaseState`, `BlogState`, `AdminAnalyticsState`, etc.:** Specifieke logica voor hun respectievelijke pagina's.

## 2. Gedefinieerde Pagina's

De applicatie heeft een uitgebreide set pagina's, onderverdeeld in publieke, beveiligde en admin-secties. De routing is gedefinieerd in `app/app.py`.

### Publieke Pagina's
-   **Home:** `/`
-   **Informatie:** `/aanleiding`, `/faq`, `/contact-about`, `/about`, `/wiki`
-   **Advies & Tools:**
    -   `/advice-themes` (Overzicht)
    -   `/solar` (Zonnepanelen)
    -   `/battery` (Batterij schatting)
    -   `/advice/simple/battery` (Eenvoudige batterij scan)
    -   `/advice/solar-theme` (Zonne-energie advies)
    -   `/warm-water` (Warm water)
    -   `/advice/contract-vergelijking` (Contract vergelijking)
-   **Content:**
    -   `/kb` & `/kb/[article_id]` (Kennisbank)
    -   `/blog` & `/blog/[slug]` (Blog)
-   **Juridisch:** `/algemene-voorwaarden`, `/privacybeleid`

### Authenticatie Pagina's
-   `/login`
-   `/signup`
-   `/forgot-password`
-   `/reset-password`

### Beveiligde / Gebruikers Pagina's
-   `/results` (Mijn Resultaten)
-   `/advice/advanced/battery` (Geavanceerde batterij simulatie)
-   `/dakscan` (Dakscan)

### Admin Pagina's
-   `/admin` (Dashboard)
-   `/admin/cms` & `/admin/cms/editor/[id]` (CMS beheer)
-   `/admin/categories` (Categorieën)
-   `/admin/users` (Gebruikersbeheer)
-   `/admin/settings` (Instellingen)
-   `/admin/analytics` (Analytics)

## 3. Custom Componenten

De applicatie maakt veelvuldig gebruik van herbruikbare componenten in `app/components/`.

### Layout & Navigatie
-   **`navbar` (`app/components/navbar.py`):** Een responsieve navigatiebalk. Bevat logica voor desktop en mobiele weergave (`mobile_menu`), actieve link styling, en toont verschillende opties afhankelijk van de authenticatiestatus (inloggen vs. uitloggen/profiel).
-   **`footer` (`app/components/footer.py`):** Een uitgebreide footer met links naar alle belangrijke secties, gegroepeerd per categorie. Toont admin-links indien de gebruiker admin-rechten heeft.
-   **`base_layout` (`app/components/layout.py`):** De hoofd-wrapper voor pagina's. Combineert de `navbar`, de pagina-content, `feedback_widget`, `footer` en `cookie_consent_banner`.
-   **`admin_sidebar` (`app/components/admin_sidebar.py`):** Een zijbalk specifiek voor de admin-omgeving met navigatie naar de verschillende beheertools.

### Functionele Componenten
-   **`protected_guard` (`app/components/protected_guard.py`):** Een Higher-Order Component (of wrapper functie) die controleert of een gebruiker is ingelogd voordat de pagina wordt getoond.
-   **`google_analytics`:** Script integratie voor tracking.
-   **`cookie_consent`:** Banner voor cookie toestemming.
-   **`feedback_widget`:** Een widget om feedback te verzamelen.
