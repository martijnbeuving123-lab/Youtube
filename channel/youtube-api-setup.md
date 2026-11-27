# Eigen YouTube-uploader instellen (eenmalig, ±30 minuten)

Doel: Claude kan video's, thumbnails en ondertitels zelf uploaden en inplannen via de officiële
YouTube-API, zonder vidIQ of Hermoso. Het draait als GitHub Actions-workflow
(`.github/workflows/youtube.yml`) met `tools/youtube_api.py`. De sleutels staan alleen als
geheime instellingen (secrets) in GitHub, nooit in de code of in de chat.

## Stap 1 — Google Cloud-project (gratis)
1. Ga naar https://console.cloud.google.com en log in met het Google-account dat **eigenaar is
   van The Defector Files**.
2. Bovenaan: projectkiezer → **Nieuw project** → naam `youtube-uploader` → Maken.
3. Menu **API's en services → Bibliotheek** → zoek **YouTube Data API v3** → **Inschakelen**.

## Stap 2 — Toestemmingsscherm (OAuth consent screen)
1. **API's en services → OAuth-toestemmingsscherm** (of "Google Auth Platform").
2. Type gebruiker: **Extern** → Maken.
3. App-naam `youtube-uploader`, je eigen e-mail bij ondersteuning en contact → Opslaan.
4. Bij **Doelgroep / Testgebruikers**: voeg je eigen Google-account toe.
5. Zet de publicatiestatus op **In productie** ("App publiceren"). Belangrijk: in de
   teststand verloopt de sleutel na 7 dagen. Google toont daarna bij het inloggen een
   waarschuwing "app niet geverifieerd"; dat is normaal voor je eigen app (klik "Geavanceerd" →
   "Doorgaan").

## Stap 3 — Inloggegevens (OAuth-client)
1. **API's en services → Inloggegevens → Inloggegevens maken → OAuth-client-ID**.
2. Type: **Webapplicatie**. Naam: `uploader`.
3. Bij **Geautoriseerde omleidings-URI's** voeg toe: `https://developers.google.com/oauthplayground`
4. Maken. Je krijgt een **Client-ID** en een **Clientgeheim**. Laat dit venster open.

## Stap 4 — De sleutel ophalen (refresh token), zonder dat iemand hem ziet
1. Ga naar https://developers.google.com/oauthplayground
2. Klik rechtsboven op het **tandwiel** → vink **Use your own OAuth credentials** aan → plak je
   Client-ID en Clientgeheim.
3. Links onderaan bij "Input your own scopes" plak:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.force-ssl`
   → **Authorize APIs**.
4. Log in, **kies het kanaal The Defector Files**, sta alles toe.
5. Klik **Exchange authorization code for tokens**. Kopieer de **Refresh token** (niet de access
   token). Deel hem met niemand, ook niet in de chat.

## Stap 5 — Sleutels in GitHub zetten
1. Ga naar https://github.com/martijnbeuving123-lab/Youtube → **Settings → Secrets and variables
   → Actions → New repository secret**.
2. Maak drie secrets:
   - `YT_CLIENT_ID` = de Client-ID
   - `YT_CLIENT_SECRET` = het Clientgeheim
   - `YT_REFRESH_TOKEN_DEFECTOR` = de refresh token van stap 4
   (Later voor Precinct Archive desgewenst `YT_REFRESH_TOKEN_PRECINCT`, via stap 4 met dat kanaal.)

## Stap 6 — Keuring aanvragen (gratis, belangrijk)
YouTube zet video's die via een nieuw, ongekeurd API-project worden geüpload vast op **privé**
tot het project een keuring heeft gehad. Vraag die meteen aan:
https://support.google.com/youtube/contact/yt_api_form
Kies de audit/keuring voor je project, beschrijf: "Private tool that uploads our own
documentaries to our own channel, scheduled publishing." Dit kan een paar weken duren.

## Stap 7 — Laat het Claude weten
Zeg "secrets staan erin". Claude start dan de workflow met `whoami` om te testen of de sleutel
bij The Defector Files hoort, en daarna een proefupload (privé).
