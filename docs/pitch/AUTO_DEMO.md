# Auto-demo: 5 speakers, 5 minutes

Page khud chalta hai. Har speaker apni lines bolta hai.

**Screen ke neeche right me scene number dikhta hai (jaise 7/22), wahi number yahan hai.** Number ke upar ki patli line bhar jaaye toh agli line. Atak jao toh **Space** dabao, demo ruk jaayega; dobara Space se chalega.

| Speaker | Naam | Scenes | Time |
|---|---|---|---|
| 1 | _____ | 1 to 3 | 0.9 min |
| 2 | _____ | 4 to 7 | 0.9 min |
| 3 | _____ | 8 to 12 | 1.1 min |
| 4 | _____ | 13 to 17 | 1.1 min |
| 5 | _____ | 18 to 22 | 1.0 min |

## Record karne ke steps

1. Ek baar practice karo. Speed dekhne ke liye page poora chala lo.
2. Chrome me kholo: https://pramaan-teal.vercel.app/?tour=1
3. Chrome full screen karo (Ctrl + Cmd + F).
4. **Cmd + Shift + 5**, Record Entire Screen, Options me mic select karo, Record dabao.
5. Page pe **Start demo** dabao aur Speaker 1 shuru kare.
6. Aakhri card pe 2 second ruk ke menu bar me Stop dabao.

Paanchon ek hi laptop ke paas baitho aur mic ke paas aake bolo. Alag jagah ho toh Google Meet pe aao, ek banda screen share kare aur Meet record ho.

## Speaker 1: Problem aur idea

| Scene | Sec | Bolo |
|---|---|---|
| 1 | 13 | Good morning. Hum team hain, aur hamara problem statement SIH26261 hai, AICTE ka: AI se application validation, document authentication aur compliance verification. Hamara solution hai Pramaan, jiska matlab hai proof. |
| 2 | 24 | AICTE approval ke liye har institution land deed, building certificate, fire certificate aur faculty list deta hai, aur officers ye sab haath se padhte hain. Isme teen problems hain. Ye slow hai. Edit kiya hua certificate aankh se asli lagta hai. Aur koi officer ek college ki faculty list ko baaki saare colleges se compare nahi kar sakta. |
| 3 | 17 | Pramaan poora application padhta hai aur teen me se ek verdict deta hai: compliant, reject, ya human review. Har finding ke saath document ki wahi line dikhti hai jahan se wo aayi. Jahan shak ho, wahan ye khud approve nahi karta. |

## Speaker 2: Clean application aur forgery ki shuruaat

| Scene | Sec | Bolo |
|---|---|---|
| 4 | 13 | Ab live demo dekhte hain. Ye ek fictional college ka sahi application hai, Shree Ram Institute of Technology. Ek click me Pramaan ne saare documents padh liye aur verdict diya: compliant. |
| 5 | 16 | Ye check dekhiye. 480 students pe 25 faculty hain, yaani 19.2 students per faculty. AICTE handbook ke Annexure 5 me limit 20 hai, isliye pass. Aur neeche wo exact line dikhti hai jahan se ye number aaya. |
| 6 | 13 | Building area bhi andaaze se nahi hai. Annexure 3 ke room-wise table se calculate hua hai: classrooms, labs, library, sab jod ke. 5,562 square metre chahiye, aur certificate pe 6,000 hai. |
| 7 | 11 | Ab forgery. Is college ka fire certificate March 2026 me expire ho chuka hai. Application September 2026 ki hai, toh ye reject hona chahiye. |

## Speaker 3: Forgery pakadna

| Scene | Sec | Bolo |
|---|---|---|
| 8 | 17 | Kisi ne date ke upar white box lagaya aur 2027 type kar diya. Page dekhiye, aankh se bilkul theek lagta hai. Officer ise pass kar sakta hai. Par laal box me Pramaan dikha raha hai ki chhedchhad kahan hui. |
| 9 | 13 | Pramaan ne white box, alag font, aur file ka dobara save hona, teeno pakde. Aur white box ke neeche asli date abhi bhi file me hai, Pramaan wahi padhta hai. |
| 10 | 10 | Saath hi land trust ke naam nahi, ek private person ke naam nikli. Pramaan ne do alag documents khud mila ke pakad liya. |
| 11 | 14 | Ab smart forger. Ye page ko print karke scan kar deta hai, taaki edit ka koi nishaan na bache. Ab white box nahi, alag font nahi, page pe seedha 2027 likha hai. |
| 12 | 10 | Par QR code me abhi bhi 2026 hai. Pramaan QR padhta hai, page se compare karta hai, aur reject kar deta hai. |

## Speaker 4: Ghost faculty, queue aur andar ka system

| Scene | Sec | Bolo |
|---|---|---|
| 13 | 13 | Ab sabse important case. Ye ek doosra college hai, Ganga College of Engineering. Iska har document apne aap me bilkul theek hai. Koi edit nahi, koi expired date nahi. |
| 14 | 15 | Par Pramaan purani applications yaad rakhta hai. Iski 25 faculty pehle se Shree Ram Institute ki list me hain. Yani ek hi log do colleges me dikhaye ja rahe hain. Isi ko ghost faculty kehte hain. |
| 15 | 10 | Fire certificate ka number bhi wahi hai jo pehle college ne diya tha. Ye ek file dekh ke kabhi nahi pakda ja sakta. |
| 16 | 15 | Ye officer ka screen hai. Saari applications ek queue me, sabse risky sabse upar, aur har application ki PDF report evidence ke saath. REST API bhi hai, toh AICTE portal seedha connect ho sakta hai. |
| 17 | 13 | Andar kya chalta hai? Document padha jaata hai, scanned ho toh offline OCR se. Phir norms check hote hain, forgery checks chalte hain, aur registry purani applications se milati hai. |

## Speaker 5: AI, feasibility, limits, close

| Scene | Sec | Bolo |
|---|---|---|
| 18 | 16 | Free-form letters Gemini padhta hai, par uski baat seedhi nahi maani jaati. Value tabhi rakhi jaati hai jab uski source line document me sach me ho, aur numbers exact match karein. Warna wo officer ke paas jaati hai. |
| 19 | 12 | Ye sirf idea nahi hai. Live link chal raha hai, 29 automated tests pass hain, aur norms seedhe AICTE Approval Process Handbook 2024-27 se liye gaye hain. |
| 20 | 16 | Hum limits bhi saaf batate hain. Abhi tak sirf synthetic documents pe test hua hai, asli scans mushkil honge. Aur photo pe bahut safai se ki gayi editing, agar QR ya signature na ho, abhi nahi pakdi jaati. |
| 21 | 12 | Officers ka time risky applications pe lagta hai, honest colleges ko pata chalta hai kya theek karna hai, aur students ko milti hai asli faculty aur safe building. |
| 22 | 4 | Pramaan: har verdict, proof ke saath. Thank you. |
