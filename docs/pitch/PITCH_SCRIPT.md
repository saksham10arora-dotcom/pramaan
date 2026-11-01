# Pramaan: pitch aur demo script (Hinglish)

**Bolo** = kya bolna hai. *Italics* = us waqt screen pe kya karna hai.

Total: lagbhag 6 minute (pitch 4, demo andar hi chalta hai). Har number sach hai aur check kiya hua hai. Koi number apni taraf se mat badhana.

---

## Shuru hone se pehle (15 minute pehle)

*Charger lagao, Do Not Disturb on karo. Chrome me do tabs kholo:*

1. Slides: `docs/slides/Pramaan_SIH_deck.pptx`
2. Live demo: https://pramaan-teal.vercel.app

*Ek baar Clean aur Ghost faculty daba ke dekh lo, isse server jaag jaata hai.*

**Backup:** net na chale toh `docs/demo/pramaan_demo.mp4` chala do. Local version bhi chalao:

```bash
.venv/bin/streamlit run app.py
```

---

## Part 1: Problem (45 sec) · Slide 1

> Good morning. Hamara problem statement SIH26261 hai, AICTE ka: AI se application validation, document authentication aur compliance verification.
>
> Har institution ko AICTE approval ke liye documents ka poora set dena padta hai: land deed, building certificate, fire safety certificate, faculty list. Aaj officers ye sab haath se padhte hain.
>
> Isme teen problems hain. Ye slow hai. Edit kiya hua certificate aankh se asli lagta hai. Aur koi officer ek college ki faculty list ko baaki sab colleges se compare nahi kar sakta.

## Part 2: Hamara idea (40 sec) · Slide 2

> Humne banaya Pramaan. Pramaan matlab proof.
>
> Institution ka poora application do, aur ye teen me se ek verdict deta hai: compliant, reject, ya human review. Har finding ke saath document ki wahi line dikhti hai jahan se wo aayi.
>
> Aur ek rule pakka hai: jahan isko shak hai, wahan ye khud approve nahi karta. Officer ke paas bhejta hai, reason ke saath.

## Part 3: Live demo (2 min 15 sec)

*Demo tab pe jao.*

**Clean** · *Clean dabao. Student to faculty ratio aur built-up area wali lines kholo.*

> Ye ek sahi application hai. Verdict: compliant. Dekhiye, 480 students pe 25 faculty, yaani 19.2, aur handbook ki limit 20 hai. Building area bhi Annexure 3 ke room-wise table se calculate hua: 5,562 square metre chahiye, 6,000 bana hai.

**Forged PDF** · *Forged PDF dabao, neeche white box wali image tak scroll karo.*

> Ab forgery. Fire certificate March 2026 me expire ho gaya. Kisi ne date pe white box lagaya aur 2027 type kar diya. Aankh se bilkul theek lagta hai. Par Pramaan neeche chhupi asli date padh leta hai, aur laal box me dikhata hai ki kahan chhedchhad hui. Saath hi pakda ki land trust ke naam nahi, ek private person ke naam hai.

**Forged, then scanned** · *Button dabao.*

> Smart forger kya karega? Print karke scan kar dega, taaki edit ka koi nishaan na bache. Page pe ab 2027 hi likha hai. Par certificate ke QR code me abhi bhi 2026 hai. Pramaan dono compare karta hai aur reject kar deta hai.

**Ghost faculty** · *Button dabao.*

> Ye sabse important hai. Ye doosra college hai. Iska har document apne aap me theek hai. Par Pramaan purani applications yaad rakhta hai. Ye 25 faculty pehle se doosre institution ki list me hain, aur fire certificate ka number bhi wahi hai. Ek file dekh ke ye kabhi nahi pakda ja sakta.

**Reviewer queue** · *Tab kholo.*

> Officer ko ek hi queue milti hai, sabse risky pehle, aur har application ki PDF report. REST API bhi hai, toh AICTE portal seedha connect ho sakta hai.

## Part 4: Technology (30 sec) · Slide 3

> Hamara core idea hai: AI proposes, code verifies. Free-form letters Gemini padhta hai, par uski value tabhi rakhi jaati hai jab uski source line document me sach me ho, aur numbers exact match karein. AI kuch bana bhi de, toh wo officer ke paas jaata hai, verdict me nahi.
>
> Scanned documents ke liye OCR hamare server pe offline chalta hai. QR, PDF edits aur digital signature, sab alag se check hote hain.

## Part 5: Feasibility aur limits (30 sec) · Slide 4

> Ye sirf idea nahi, chal raha hai: live link hai, 29 automated tests pass hain, aur norms AICTE ke Approval Process Handbook 2024-27 se liye hain.
>
> Hum limits bhi saaf bata rahe hain. Abhi tak sirf synthetic documents pe test hua hai, real scans mushkil honge. Signature me hum check karte hain ki file badli nahi, ye nahi ki sahi office ne sign kiya. Aur photo pe bahut safai se ki gayi editing, agar QR ya signature na ho, abhi nahi pakdi jaati.

## Part 6: Impact aur close (30 sec) · Slide 5

> Officers ka time saaf applications se bachta hai aur risky applications pe lagta hai. Honest colleges ko pata chalta hai kya theek karna hai. Students ko milti hai asli faculty aur safe building.
>
> Pramaan: har verdict, proof ke saath. Thank you.

---

## Likely sawaal

**Accuracy kitni hai?**
> Abhi real documents pe measure nahi ki, isliye number nahi bolenge. Synthetic demo me sab cases pakde gaye, aur agla step real scans pe test karna hai.

**AI galat padh le toh?**
> Value tabhi rakhi jaati hai jab uski line document me ho aur numbers exact match karein. Warna officer ke paas jaati hai.

**Agar QR code hi na ho?**
> Toh baaki checks chalte hain: PDF edits, font, signature, cross-document. Scan pe bina QR ke safai se ki gayi editing abhi nahi pakdi jaati, ye hamari known limit hai.

**Land ka minimum check kyun nahi hai?**
> Handbook 2024-27 me fixed acre nahi hai, land local FSI/FAR se decide hoti hai. Isliye hum built-up area check karte hain.

**Data security?**
> Local version me OCR aur saare rules server pe chalte hain. AI reader optional hai, offline mode me kuch bahar nahi jaata.

**Dusre programmes?**
> Faculty ratio saare UG programmes ke liye loaded hai. Room-wise area abhi Engineering UG ke liye hai, baaki human review me jaata hai.

**Ghost faculty me galat flag ho gaya toh?**
> Faculty ID match pe based hai aur final decision officer ka hai, evidence uske saamne hota hai.

**Sign wala check kitna strong hai?**
> File sign ke baad badli toh pakad lete hain. Signer sahi office hai ya nahi, wo CCA root list maangta hai, jo abhi loaded nahi hai.
