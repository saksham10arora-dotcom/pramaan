# Pramaan demo: video script

Runs about two and a half minutes. Everything on screen is the real app running on fictional sample applications.

| # | On screen | Narration |
|---|---|---|
| intro | Title card | Every year, thousands of institutions apply to AICTE for approval. Each application is a stack of land deeds, building certificates, fire safety certificates and faculty lists, and officials check them by hand. It is slow, and an edited certificate can slip through. This is Pramaan. |
| clean | Pick the `clean` demo, scroll the findings | Here is a complete application. Pramaan reads every document, checks it against the AICTE Approval Process Handbook, and checks the documents against each other. The verdict comes back in under a second: compliant. Every result shows its evidence. Faculty ratio against the one to twenty limit. Built-up area worked out room by room from Annexure three. |
| forged | Pick `forged`, scroll to the outlined date | Now a forgery. This fire certificate expired in March twenty twenty six. Someone covered the date with a white box and typed twenty twenty seven. By eye, it looks fine. Pramaan still reads the real date underneath, flags the white box and the odd font, and shows the reviewer exactly where. It also finds that the land belongs to a private person, not the trust. Rejected. |
| forged_scan | Pick `forged_scan` | A careful forger prints and scans the page, so no edit marks survive. The page now says twenty twenty seven. But the QR code from the fire department still says twenty twenty six. Pramaan decodes it, compares it with the page, and rejects the application. |
| ghost | Pick `ghost` | This is a different college. Every document looks fine on its own. But Pramaan remembers every application. These twenty five faculty members are already listed by another institution, and the fire certificate number is already in use. No check on a single file can catch ghost faculty. This one does. |
| queue | Open the Reviewer queue tab | Reviewers get one queue, riskiest first, and a downloadable report for each application. A REST API lets the AICTE portal plug straight in. |
| close | End card | Free-form documents go to an AI reader, but the AI only proposes. A value is kept only if its source line is really in the document. Anything uncertain goes to a human, with the reason. Pramaan: every verdict, with proof. |
